import logging
import random
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.widgets import Button

logger = logging.getLogger(__name__)  # logger du module

# types de personnes assignés aléatoirement aux nœuds
TYPES_PERSONNES = ["Animateur", "Facilitateur", "Participant", "Médiateur", "Observateur"]

# types de relations entre nœuds (nature fonctionnelle du lien)
TYPES_RELATIONS = [
    "TRANSMET_CONNAISSANCE",  # l'un apprend à l'autre
    "ECHANGE_RESSOURCE",      # partage bidirectionnel d'outils ou de docs
    "ACCOMPAGNE_PROJET",      # soutien actif sur une tâche
    "CO_PRODUIT",             # création commune d'un livrable
    "COORDONNE_ACTION",       # synchronisation régulière des actions
]


def construction(n, p=0.03, seed=None):
    # génère un graphe simple classique (Erdős-Rényi) globalement connexe
    if seed is not None:
        random.seed(seed)  # graine pour la reproductibilité

    # 1. Génération d'un graphe aléatoire classique (avec cycles et clusters)
    p_ajuste = p if n > 0 else 0.03
    if n > 150:
        p_ajuste = 0.015  # Évite la surcharge d'arêtes sur les grands graphes
        
    G = nx.fast_gnp_random_graph(n, p_ajuste, seed=seed)
    
    # 2. Sécurité : Assurer la connexité (relier les morceaux isolés s'il y en a)
    comps = list(nx.connected_components(G))
    while len(comps) > 1:
        n1 = random.choice(list(comps[0]))  # un nœud de la première composante
        n2 = random.choice(list(comps[1]))  # un nœud de la deuxième
        G.add_edge(n1, n2)
        comps = list(nx.connected_components(G))  # recalcul après fusion

    # 3. Remplissage des attributs (types de personnes, poids et relations)
    for nd in G.nodes():
        G.nodes[nd]["type"] = random.choice(TYPES_PERSONNES)  # type de personne
        
    for u, v in G.edges():
        G[u][v]["weight"] = random.randint(1, 20)
        G[u][v]["relation"] = random.choice(TYPES_RELATIONS)

    logger.info("Graphe simple généré : %d nœuds, %d arêtes", G.number_of_nodes(), G.number_of_edges())
    return G


def affichage_initiale(G):
    # initialise la fenêtre Matplotlib avec le graphe brut (vue neutre)
    pos = nx.spring_layout(G, k=0.15, seed=42, iterations=50)  # positions spring-layout
    fig, ax = plt.subplots(figsize=(12, 8))
    plt.subplots_adjust(bottom=0.12)  # espace en bas pour les boutons

    nx.draw_networkx_nodes(G, pos, node_size=20, node_color="#888888", alpha=0.7, ax=ax)
    nx.draw_networkx_edges(G, pos, alpha=0.2, ax=ax, arrows=False)

    valeurs_poids = nx.get_edge_attributes(G, "weight")
    if len(G.edges()) < 50:  # labels de poids seulement si graphe petit
        nx.draw_networkx_edge_labels(G, pos, edge_labels=valeurs_poids, font_size=4, ax=ax)

    ax.legend(handles=[Line2D([0],[0], color="#888888", marker="o", linestyle="",
              label="Participant (données brutes)")], loc="upper right", fontsize=8)
    ax.set_title("Réseau communautaire — En attente d'analyse")
    ax.axis("off")  # masque les axes cartésiens

    ax_btn = plt.axes([0.01, 0.02, 0.12, 0.06])
    btn = Button(ax_btn, "Lancer l'Analyse", color="#e0e0e0", hovercolor="#b0bec5")
    return pos, fig, ax, btn, valeurs_poids