# Détection de Fraude et Analyse de Réseaux

## Description

Ce projet est une application Python permettant de générer, visualiser et analyser un réseau sous forme de graphe. L'objectif est de mettre en évidence les structures importantes d'un réseau à travers différentes métriques issues de la théorie des graphes.

L'application propose une interface graphique basée sur Matplotlib permettant d'explorer plusieurs analyses interactives :

- Intensité des relations
- Détection de communautés
- Centralité d'intermédiarité
- Centralité de degré
- Centralité de proximité
- Score d'impact composite
- Classification des rôles structurels

---
## Dépendances

Ce projet nécessite Python 3.10 ou supérieur.

### Modules Python utilisés

| Module | Utilisation |
|----------|------------|
| networkx | Construction et analyse des graphes |
| matplotlib | Visualisation du réseau et interface graphique |
| numpy | Calculs statistiques et percentiles |
| python-louvain | Détection des communautés (algorithme de Louvain) |
| statistics | Calculs statistiques (bibliothèque standard Python) |
| random | Génération aléatoire (bibliothèque standard Python) |
| logging | Journalisation des événements (bibliothèque standard Python) |
| collections | Comptage des rôles détectés (bibliothèque standard Python) |

### Installation

```bash
pip install networkx matplotlib numpy python-louvain
```

### Vérification

```bash
pip list
```

Vous devez retrouver notamment :

```text
networkx
matplotlib
numpy
python-louvain
```
## Fonctionnalités

### 1. Génération du réseau

Le programme génère automatiquement un graphe aléatoire :

- Entre 100 et 200 nœuds
- Graphe non orienté
- Graphe connexe
- Arêtes pondérées
- Attribution automatique de types de participants
- Attribution automatique de types de relations

Chaque relation possède :

- un poids compris entre 1 et 20
- une catégorie fonctionnelle

Exemples :

- TRANSMET_CONNAISSANCE
- ECHANGE_RESSOURCE
- ACCOMPAGNE_PROJET
- CO_PRODUIT
- COORDONNE_ACTION

---

### 2. Analyse de l'intensité des relations

Cette vue met en évidence :

- les nœuds très actifs
- les nœuds d'activité moyenne
- les nœuds standards
- les nœuds isolés

La classification repose sur :

- le degré du nœud
- l'intensité maximale de ses relations
- des seuils statistiques calculés automatiquement

---

### 3. Détection de communautés

Le projet utilise l'algorithme Louvain pour détecter automatiquement les groupes présents dans le réseau.

Cette analyse permet :

- d'identifier les communautés
- de mesurer leur taille
- de visualiser les clusters grâce à des couleurs distinctes

---

### 4. Centralité d'intermédiarité

Cette métrique permet d'identifier les nœuds servant de pont entre plusieurs parties du réseau.

Les nœuds possédant une forte centralité d'intermédiarité sont souvent :

- des intermédiaires stratégiques
- des points critiques de communication
- des acteurs importants dans la propagation d'informations

---

### 5. Centralité de degré

Cette analyse mesure le nombre de connexions directes d'un participant.

Elle permet d'identifier :

- les hubs du réseau
- les acteurs les plus connectés
- les centres locaux d'activité

---

### 6. Centralité de proximité

Cette métrique mesure la capacité d'un nœud à atteindre rapidement tous les autres.

Elle permet de détecter :

- les meilleurs diffuseurs d'information
- les acteurs les plus proches du centre du réseau

---

### 7. Score d'impact composite

Le projet calcule un score global basé sur :

- 40 % Centralité d'intermédiarité
- 35 % Centralité de degré
- 25 % Intensité des relations

Cette métrique permet d'obtenir un classement général des participants les plus influents.

---

### 8. Classification automatique des rôles

Chaque participant reçoit automatiquement un rôle structurel :

| Rôle | Description |
|--------|------------|
| Coordinateur central | Nœud très connecté |
| Pont stratégique | Relie plusieurs groupes |
| Diffuseur d'information | Accède rapidement au reste du réseau |
| Membre de cluster | Appartient à un cycle local |
| Nœud périphérique | Relié à un hub mais peu connecté |
| Profil non classifié | Aucun rôle dominant détecté |

---

## Architecture du projet

```text
.
├── main.py
├── detection.py
├── presentation_societe.py
└── README.md
