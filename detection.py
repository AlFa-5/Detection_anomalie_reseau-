import logging
import statistics
import networkx as nx
import numpy as np
import community as community_louvain

logger = logging.getLogger(__name__)  # logger du module

# libellés affichés pour chaque rôle structurel
ROLES = {
    "hub_coordinateur": "Coordinateur central",
    "pivot_reseau":     "Pont stratégique",
    "propagateur":      "Diffuseur d'information",
    "membre_anneau":    "Membre de cluster",
    "satellite":        "Nœud périphérique",
    "inconnu":          "Profil non classifié",
}

# couleur matplotlib associée à chaque rôle
COULEURS_ROLES = {
    "hub_coordinateur": "#e53935",
    "pivot_reseau":     "#ff7043",
    "propagateur":      "#8e24aa",
    "membre_anneau":    "#1e88e5",
    "satellite":        "#43a047",
    "inconnu":          "#b0bec5",
}


def _get_betweenness(G):
    # calcule betweenness une seule fois puis la met en cache sur G
    if not hasattr(G, "_betweenness_cache"):
        G._betweenness_cache = nx.betweenness_centrality(G, weight="weight", normalized=True)
    return G._betweenness_cache


def analyser_intensite_relations(G):
    # classifie chaque nœud par niveau d'activité (degré + poids max)
    degrees = dict(G.degree())  # degré de chaque nœud
    vals = list(degrees.values())
    moy = statistics.mean(vals) if vals else 0  # moyenne des degrés
    std = statistics.stdev(vals) if len(vals) > 1 else 0  # écart-type
    tous_poids = [d["weight"] for _, _, d in G.edges(data=True)]
    seuil_fort = np.percentile(tous_poids, 85) if tous_poids else 10  # seuil haut 85e percentile

    couleurs = []
    for n in G.nodes():
        d = degrees[n]  # degré du nœud courant
        voisins = list(G.neighbors(n))
        max_w = max([G[n][v].get("weight", 1) for v in voisins]) if voisins else 0  # poids max
        if d == 0:
            couleurs.append("#ffeb3b")   # jaune = isolé
        elif d > moy + 1.5 * std or max_w > seuil_fort:
            couleurs.append("#2196f3")   # bleu = très actif
        elif d > moy:
            couleurs.append("#4caf50")   # vert = activité moyenne
        else:
            couleurs.append("#9e9e9e")   # gris = standard
    return couleurs


def detecter_communautes(G):
    # détecte les groupes de nœuds proches via l'algo Louvain
    partition = community_louvain.best_partition(G, weight="weight")  # id de communauté par nœud
    comm_dict = {}
    for n, cid in partition.items():
        comm_dict.setdefault(cid, set()).add(n)  # regroupe les nœuds par communauté
    communautes = list(comm_dict.values())

    palette = [  # 15 couleurs distinctes pour les groupes
        "#e6194b","#3cb44b","#4363d8","#f58231","#911eb4",
        "#42d4f4","#f032e6","#bfef45","#fabed4","#469990",
        "#e6beff","#9a6324","#fffac8","#800000","#aaffc3",
    ]
    n2c = {n: palette[cid % len(palette)] for n, cid in partition.items()}  # nœud → couleur
    couleurs = [n2c.get(n, "#888888") for n in G.nodes()]
    return couleurs, communautes


def betweenness_centralite(G):
    # mesure combien de chemins courts passent par chaque nœud
    scores = _get_betweenness(G)  # lecture du cache
    max_s = max(scores.values()) if scores else 1
    tailles, couleurs = [], []
    for n in G.nodes():
        r = scores[n] / max_s if max_s > 0 else 0  # score relatif 0-1
        tailles.append(15 + r * 105)  # taille proportionnelle
        if r > 0.75:   couleurs.append("#d32f2f")   # pont critique
        elif r > 0.50: couleurs.append("#f44336")
        elif r > 0.25: couleurs.append("#ff9800")
        elif r > 0.05: couleurs.append("#ffc107")
        else:          couleurs.append("#b0bec5")
    top5 = sorted(scores, key=scores.get, reverse=True)[:5]  # 5 nœuds les plus centraux
    return tailles, couleurs, scores, top5


def degree_centralite(G):
    # mesure le nombre de connexions directes de chaque nœud
    scores = nx.degree_centrality(G)
    max_s = max(scores.values()) if scores else 1
    tailles, couleurs = [], []
    for n in G.nodes():
        r = scores[n] / max_s if max_s > 0 else 0
        tailles.append(15 + r * 105)
        if r > 0.75:   couleurs.append("#1565c0")   # très connecté
        elif r > 0.50: couleurs.append("#1e88e5")
        elif r > 0.25: couleurs.append("#64b5f6")
        elif r > 0.05: couleurs.append("#90caf9")
        else:          couleurs.append("#b0bec5")
    top5 = sorted(scores, key=scores.get, reverse=True)[:5]
    return tailles, couleurs, scores, top5


def closeness_centralite(G):
    # mesure à quelle vitesse un nœud peut atteindre tous les autres
    scores = nx.closeness_centrality(G, wf_improved=True)  # wf_improved = correction pour graphes non connexes
    max_s = max(scores.values()) if scores else 1
    tailles, couleurs = [], []
    for n in G.nodes():
        r = scores[n] / max_s if max_s > 0 else 0
        tailles.append(15 + r * 105)
        if r > 0.75:   couleurs.append("#6a1b9a")   # diffuseur optimal
        elif r > 0.50: couleurs.append("#8e24aa")
        elif r > 0.25: couleurs.append("#ba68c8")
        elif r > 0.05: couleurs.append("#ce93d8")
        else:          couleurs.append("#b0bec5")
    top5 = sorted(scores, key=scores.get, reverse=True)[:5]
    return tailles, couleurs, scores, top5


def score_risque(G):
    # score composite : 40% betweenness + 35% degré + 25% poids max
    bc = _get_betweenness(G)  # betweenness depuis le cache
    dc = nx.degree_centrality(G)
    tous_poids = [d["weight"] for _, _, d in G.edges(data=True)]
    poids_max_g = max(tous_poids) if tous_poids else 1  # normalisation des poids

    poids_noeud = {}
    for n in G.nodes():
        voisins = list(G.neighbors(n))
        aretes = [G[n][v].get("weight", 1) for v in voisins]
        poids_noeud[n] = max(aretes) / poids_max_g if aretes else 0.0  # poids relatif max

    scores = {
        n: round(0.40 * bc.get(n, 0) + 0.35 * dc.get(n, 0) + 0.25 * poids_noeud.get(n, 0), 4)
        for n in G.nodes()
    }
    top10 = sorted(scores, key=scores.get, reverse=True)[:10]
    return scores, top10


def inferer_roles(G):
    # classe chaque nœud dans un rôle structurel selon ses métriques
    dc = nx.degree_centrality(G)
    bc = _get_betweenness(G)  # betweenness depuis le cache
    cc = nx.closeness_centrality(G, wf_improved=True)

    vals_dc = list(dc.values())
    if len(vals_dc) >= 10:  # seuils percentile valides seulement si ≥ 10 nœuds
        seuil_hub   = np.percentile(vals_dc,       90)  # top 10% des degrés
        seuil_pivot = np.percentile(list(bc.values()), 85)  # top 15% betweenness
        seuil_prop  = np.percentile(list(cc.values()), 85)  # top 15% closeness
    else:
        seuil_hub = seuil_pivot = seuil_prop = float("inf")  # petit graphe : pas de seuil

    cycles_detectes = set()
    try:
        if len(G) <= 200:  # limité aux petits graphes pour la performance
            for cycle in nx.cycle_basis(G):
                if 3 <= len(cycle) <= 5:
                    cycles_detectes.update(cycle)  # nœuds dans des boucles courtes
    except Exception as e:
        logger.warning("Détection cycles échouée : %s", e)

    hubs = {n for n in G.nodes() if dc[n] >= seuil_hub}  # ensemble des nœuds hub

    roles = {}
    for n in G.nodes():
        if dc[n] >= seuil_hub:
            roles[n] = "hub_coordinateur"      # très connecté = cœur du réseau
        elif bc[n] >= seuil_pivot:
            roles[n] = "pivot_reseau"           # relie plusieurs communautés
        elif cc[n] >= seuil_prop:
            roles[n] = "propagateur"            # proche du centre = diffuse vite
        elif n in cycles_detectes:
            roles[n] = "membre_anneau"          # appartient à une boucle locale
        elif G.degree(n) <= 2 and any(v in hubs for v in G.neighbors(n)):
            roles[n] = "satellite"              # périphérique autour d'un hub
        else:
            roles[n] = "inconnu"               # aucun rôle structurel clair

    couleurs = [COULEURS_ROLES[roles[n]] for n in G.nodes()]
    return roles, couleurs