import logging
import random
from collections import Counter
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.widgets import Button

from detection import (COULEURS_ROLES, ROLES, analyser_intensite_relations,
                       betweenness_centralite, closeness_centralite,
                       degree_centralite, detecter_communautes,
                       inferer_roles, score_risque)
from presentation_societe import affichage_initiale, construction

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class AnalysisCache:
    # stocke les résultats des analyses pour éviter les recalculs
    def __init__(self):
        self.intensite = self.communautes = self.betweenness = None
        self.degree = self.closeness = self.risque = self.roles = None

    def invalidate(self):
        self.__init__()  # vide tout le cache si le graphe change


cache = AnalysisCache()  # instance globale du cache

n = random.randint(100, 200)  # taille du graphe
G = construction(n, seed=None)  # graphe synthétique reproductible
pos, fig, ax, btn, valeurs_poids = affichage_initiale(G)  # fenêtre Matplotlib


def _calculer_tout():
    # lance tous les calculs une seule fois et remplit le cache
    logger.info("Calcul des métriques…")
    cache.intensite   = analyser_intensite_relations(G)
    cache.communautes = detecter_communautes(G)
    cache.betweenness = betweenness_centralite(G)
    cache.degree      = degree_centralite(G)
    cache.closeness   = closeness_centralite(G)
    cache.risque      = score_risque(G)
    cache.roles       = inferer_roles(G)
    logger.info("Métriques prêtes.")


def _base(titre):
    ax.cla()  # efface le dessin précédent
    ax.set_title(titre, fontsize=12, fontweight="bold")
    ax.axis("off")  # masque les axes cartésiens


def _refresh():
    fig.canvas.draw_idle()  # rafraîchit sans bloquer l'UI


# ── callbacks des boutons ──────────────────────────────────────────────────

def lancer_analyse(event):
    # vue 1 : intensité des relations (couleur = niveau d'activité du nœud)
    if not cache.intensite: _calculer_tout()
    _base("Intensité des échanges entre participants")
    nx.draw_networkx_nodes(G, pos, node_size=30, node_color=cache.intensite, alpha=0.8, ax=ax)
    edge_colors = []
    for u, v in G.edges():
        w = G[u][v].get("weight", 1)
        edge_colors.append("#e53935" if w > 12 else "#ff9800" if w > 7 else "#bdbdbd")  # rouge/orange/gris
    nx.draw_networkx_edges(G, pos, width=1.0, edge_color=edge_colors, alpha=0.4, ax=ax, arrows=False)
    ax.legend(handles=[
        Line2D([0],[0], marker="o", color="w", markerfacecolor="#2196f3", markersize=8, label="Très actif"),
        Line2D([0],[0], marker="o", color="w", markerfacecolor="#4caf50", markersize=8, label="Actif"),
        Line2D([0],[0], marker="o", color="w", markerfacecolor="#9e9e9e", markersize=8, label="Standard"),
        Line2D([0],[0], marker="o", color="w", markerfacecolor="#ffeb3b", markersize=8, label="Isolé"),
    ], loc="upper right", fontsize=7, framealpha=0.8)
    _refresh()


def lancer_communautes(event):
    # vue 2 : groupes détectés par l'algo Louvain
    if not cache.communautes: _calculer_tout()
    couleurs, communautes = cache.communautes
    _base(f"Communautés Louvain — {len(communautes)} groupes détectés")
    nx.draw_networkx_nodes(G, pos, node_size=30, node_color=couleurs, alpha=0.85, ax=ax)
    nx.draw_networkx_edges(G, pos, width=0.4, edge_color="gray", alpha=0.15, ax=ax, arrows=False)
    palette = ["#e6194b","#3cb44b","#4363d8","#f58231","#911eb4","#42d4f4","#f032e6","#bfef45","#fabed4","#469990"]
    ax.legend(handles=[Patch(facecolor=palette[i % len(palette)], label=f"Groupe {i+1} ({len(c)} membres)")
                       for i, c in enumerate(communautes[:8])],  # max 8 entrées de légende
              loc="upper right", fontsize=6, framealpha=0.8)
    _refresh()


def lancer_betweenness(event):
    # vue 3 : nœuds-ponts (betweenness) — les plus gros/rouges sont incontournables
    if not cache.betweenness: _calculer_tout()
    tailles, couleurs, scores, top5 = cache.betweenness
    _base("Ponts stratégiques — Centralité d'intermédiarité")
    nx.draw_networkx_nodes(G, pos, node_size=tailles, node_color=couleurs, alpha=0.9, ax=ax)
    nx.draw_networkx_edges(G, pos, width=0.4, edge_color="gray", alpha=0.15, ax=ax, arrows=False)
    nx.draw_networkx_labels(G, pos, labels={n: f"#{n}\n{scores[n]:.3f}" for n in top5},  # annote le top 5
                            font_size=6, font_color="black", font_weight="bold", ax=ax)
    ax.legend(handles=[
        Patch(facecolor="#d32f2f", label="Pont critique (>75%)"),
        Patch(facecolor="#f44336", label="Intermédiaire fort (>50%)"),
        Patch(facecolor="#ff9800", label="Pivot local (>25%)"),
        Patch(facecolor="#ffc107", label="Passerelle (>5%)"),
        Patch(facecolor="#b0bec5", label="Standard"),
    ], loc="upper right", fontsize=6, framealpha=0.8)
    _refresh()


def lancer_degree(event):
    # vue 4 : nœuds les plus connectés directement (degré)
    if not cache.degree: _calculer_tout()
    tailles, couleurs, scores, top5 = cache.degree
    _base("Participants les plus connectés — Centralité de degré")
    nx.draw_networkx_nodes(G, pos, node_size=tailles, node_color=couleurs, alpha=0.9, ax=ax)
    nx.draw_networkx_edges(G, pos, width=0.4, edge_color="gray", alpha=0.15, ax=ax, arrows=False)
    nx.draw_networkx_labels(G, pos, labels={n: f"#{n}\n{scores[n]:.3f}" for n in top5},
                            font_size=6, font_color="black", font_weight="bold", ax=ax)
    ax.legend(handles=[
        Patch(facecolor="#1565c0", label="Carrefour majeur (>75%)"),
        Patch(facecolor="#1e88e5", label="Connectivité forte (>50%)"),
        Patch(facecolor="#64b5f6", label="Actif (>25%)"),
        Patch(facecolor="#90caf9", label="Émergent (>5%)"),
        Patch(facecolor="#b0bec5", label="Discret"),
    ], loc="upper right", fontsize=6, framealpha=0.8)
    _refresh()


def lancer_closeness(event):
    # vue 5 : nœuds qui diffusent l'info le plus vite (proximité)
    if not cache.closeness: _calculer_tout()
    tailles, couleurs, scores, top5 = cache.closeness
    _base("Diffuseurs d'information — Centralité de proximité")
    nx.draw_networkx_nodes(G, pos, node_size=tailles, node_color=couleurs, alpha=0.9, ax=ax)
    nx.draw_networkx_edges(G, pos, width=0.4, edge_color="gray", alpha=0.15, ax=ax, arrows=False)
    nx.draw_networkx_labels(G, pos, labels={n: f"#{n}\n{scores[n]:.3f}" for n in top5},
                            font_size=6, font_color="black", font_weight="bold", ax=ax)
    ax.legend(handles=[
        Patch(facecolor="#6a1b9a", label="Diffuseur optimal (>75%)"),
        Patch(facecolor="#8e24aa", label="Proche du centre (>50%)"),
        Patch(facecolor="#ba68c8", label="Bien connecté (>25%)"),
        Patch(facecolor="#ce93d8", label="Périphérique (>5%)"),
        Patch(facecolor="#b0bec5", label="Isolé"),
    ], loc="upper right", fontsize=6, framealpha=0.8)
    _refresh()


def lancer_score_risque(event):
    # vue 6 : score composite (40% betweenness + 35% degré + 25% poids)
    if not cache.risque: _calculer_tout()
    scores, top10 = cache.risque
    max_s = max(scores.values()) if scores else 1  # normalisation
    _base("Score d'impact composite — Betweenness(40%) + Degré(35%) + Poids(25%)")
    couleurs, tailles = [], []
    for nd in G.nodes():
        r = scores[nd] / max_s if max_s > 0 else 0  # score relatif 0-1
        tailles.append(15 + r * 110)
        couleurs.append(
            "#b71c1c" if r > 0.75 else
            "#e53935" if r > 0.50 else
            "#ff7043" if r > 0.25 else
            "#ffb74d" if r > 0.10 else "#b0bec5"
        )
    nx.draw_networkx_nodes(G, pos, node_size=tailles, node_color=couleurs, alpha=0.9, ax=ax)
    nx.draw_networkx_edges(G, pos, width=0.3, edge_color="gray", alpha=0.12, ax=ax, arrows=False)
    nx.draw_networkx_labels(G, pos, labels={n: f"#{n}\n{scores[n]:.3f}" for n in top10[:5]},  # top 5 annoté
                            font_size=6, font_color="black", font_weight="bold", ax=ax)
    ax.legend(handles=[
        Patch(facecolor="#b71c1c", label="Impact critique (>75%)"),
        Patch(facecolor="#e53935", label="Impact élevé (>50%)"),
        Patch(facecolor="#ff7043", label="Impact modéré (>25%)"),
        Patch(facecolor="#ffb74d", label="Impact faible (>10%)"),
        Patch(facecolor="#b0bec5", label="Neutre"),
    ], loc="upper right", fontsize=6, framealpha=0.8)
    _refresh()


def lancer_roles(event):
    # vue 7 : rôle structurel de chaque nœud
    if not cache.roles: _calculer_tout()
    roles, couleurs = cache.roles
    _base("Classification des profils réseau — Rôles structurels")
    nx.draw_networkx_nodes(G, pos, node_size=35, node_color=couleurs, alpha=0.9, ax=ax)
    nx.draw_networkx_edges(G, pos, width=0.4, edge_color="gray", alpha=0.15, ax=ax, arrows=False)
    labels = {n: f"#{n}" for n in G.nodes() if roles[n] != "inconnu"}  # labels seulement pour les rôles identifiés
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=6, font_color="white", font_weight="bold", ax=ax)
    ax.legend(handles=[Patch(facecolor=COULEURS_ROLES[k], label=ROLES[k]) for k in ROLES],
              loc="upper right", fontsize=7, framealpha=0.8)
    comptage = Counter(roles.values())  # compte le nombre de nœuds par rôle
    resume = "\n".join(f"  {ROLES[k]} : {comptage.get(k,0)}" for k in ROLES if comptage.get(k,0) > 0)
    ax.text(0.01, 0.99, f"Rôles détectés :\n{resume}", transform=ax.transAxes,
            fontsize=8, verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.85))
    _refresh()


def reset_view(event):
    # réinitialise la vue sans vider le cache
    _base("Réseau communautaire — Vue initiale")
    nx.draw_networkx_nodes(G, pos, node_size=20, node_color="#888888", alpha=0.7, ax=ax)
    nx.draw_networkx_edges(G, pos, alpha=0.2, ax=ax, arrows=False)
    _refresh()


# ── câblage des boutons ────────────────────────────────────────────────────

btn.ax.set_position([0.01, 0.02, 0.12, 0.06])  # repositionne le bouton principal
btn.on_clicked(lancer_analyse)

positions_x    = [0.15,   0.27,             0.39,          0.51,       0.63,             0.75]
labels_boutons = ["Communautés","Intermédiarité","Degré","Proximité","Score composite","Rôles"]
callbacks      = [lancer_communautes, lancer_betweenness, lancer_degree,
                  lancer_closeness,   lancer_score_risque, lancer_roles]

boutons = []  # liste conservée pour éviter la suppression par le garbage collector
for x, label, cb in zip(positions_x, labels_boutons, callbacks):
    ax_b = plt.axes([x, 0.02, 0.11, 0.06])  # position et taille du bouton
    b = Button(ax_b, label)
    b.on_clicked(cb)
    boutons.append(b)

ax_reset = plt.axes([0.88, 0.02, 0.11, 0.06])
btn_reset = Button(ax_reset, "Réinitialiser", color="#ffcdd2", hovercolor="#ef9a9a")
btn_reset.on_clicked(reset_view)

plt.show()  # démarre la boucle d'événements Matplotlib