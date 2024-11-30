import numpy as np
import copy
from utils import *
from heuristique_glouton import *


def algo_iteratif(df_ville, df_object, capacite, max_iterations=1):
    # Étape 1 : Générer une solution initiale avec l'algorithme glouton
    pi, obj_pris, poids_tot, dict_ville_objet_pris = algo_glouton(df_ville, df_object, capacite)

    #Étape 2 : Initialiser les variables
    best_pi = pi
    best_obj_pris = obj_pris
    best_dict_ville_objet_pris = copy.deepcopy(dict_ville_objet_pris)
    best_profit = calculer_profit(best_pi, best_obj_pris, df_ville, df_object, capacite)

    # Étape 3 : Itérations pour améliorer la solution
    for iteration in range(max_iterations):
        #Amélioration du chemin avec une approche 2-opt
        new_pi = amelioration_chemin_2opt(best_pi, df_ville)
        #Amélioration du choix des objets
        new_obj_pris, new_poids_tot, new_dict_ville_objet_pris = amelioration_objets(
            pi, df_object, capacite
        )

        # Calculer le profit de la nouvelle solution
        new_profit = calculer_profit(new_pi, new_obj_pris, df_ville, df_object, capacite)

        # Si la solution est meilleure, mettez à jour
        if new_profit > best_profit:
            best_pi = new_pi
            best_obj_pris = new_obj_pris
            best_dict_ville_objet_pris = new_dict_ville_objet_pris
            best_profit = new_profit
        else:
            # Arrêt si aucune amélioration significative
            break

    return pi, dict_ville_objet_pris


# **Fonction 1 : Amélioration du chemin avec 2-opt**

def amelioration_chemin_2opt(pi, df_ville):
    """
    Optimise la tournée pi en utilisant l'algorithme 2-opt avec vectorisation.
    """
    # Pré-calcul de la matrice des distances
    nb_villes = len(df_ville)
    matrice_distances = np.zeros((nb_villes, nb_villes))
    for i in range(nb_villes):
        distances_de_i = calcul_distance_de_ville(i + 1, df_ville)
        for j in range(nb_villes):
            matrice_distances[i, j] = distances_de_i[j + 1]

    # Conversion de la tournée en index basé sur 0 (Python)
    pi = np.array([ville - 1 for ville in pi])  # Les villes sont indexées de 1 dans le problème
    n = len(pi)
    improved = True

    while improved:
        improved = False

        # Calcul vectorisé des gains pour toutes les paires (i, j)
        for i in range(1, n - 2):  # Éviter la ville de départ/fin
            # Précalcul pour éviter les opérations inutiles
            d_pi_prev = matrice_distances[pi[i - 1], :]  # Distance de la ville avant i à toutes les autres
            d_pi_next = matrice_distances[:, pi[(i + 1) % n]]  # Distance de toutes les autres à la ville après i

            for j in range(i + 1, n):  # Vérifier toutes les paires possibles
                if j - i == 1:  # Pas d'inversion entre des villes adjacentes
                    continue
                
                # Distances avant et après l'inversion
                d_before = matrice_distances[pi[i - 1], pi[i]] + matrice_distances[pi[j], pi[(j + 1) % n]]
                d_after = d_pi_prev[pi[j]] + d_pi_next[pi[i]]

                # Gain
                gain = d_after - d_before

                # Appliquer l'amélioration si le gain est positif
                if gain < 0:
                    pi[i:j + 1] = pi[i:j + 1][::-1]  # Effectuer l'inversion
                    improved = True
                    break  # Sortir de la boucle j après une amélioration
            if improved:
                break  # Reprendre depuis le début après une amélioration

    # Re-conversion de la tournée en index basé sur 1
    return (pi + 1).tolist()




# **Fonction 2 : Amélioration des objets avec mise à jour de dict_ville_objet_pris**
def amelioration_objets(pi, df_object, capacite):
    new_obj_pris = [0] * len(df_object.index)
    new_poids_tot = 0
    new_dict_ville_objet_pris = {}

    for ville in pi:
        objets_disponibles = get_objects_of_ville(ville, df_object).index
        objets_tries = sorted(objets_disponibles, key=lambda obj: eval_obj(obj, df_object), reverse=True)

        objets_pris = []  # Liste des objets pris dans cette ville

        for obj in objets_tries:
            poids_obj = df_object.iloc[obj - 1]['Weight']
            if new_poids_tot + poids_obj <= capacite:
                new_obj_pris[obj - 1] = 1
                new_poids_tot += poids_obj
                objets_pris.append(obj)

        # Mise à jour des objets pris pour cette ville
        new_dict_ville_objet_pris[ville] = objets_pris

    return new_obj_pris, new_poids_tot, new_dict_ville_objet_pris


# **Fonction 3 : Calcul du profit**
def calculer_profit(pi, obj_pris, df_ville, df_object, capacite):
    # Profit total des objets pris
    profit_total = sum(df_object.iloc[i]['Profit'] for i, pris in enumerate(obj_pris) if pris == 1)
    
    # Calcul de la distance totale et du temps
    distance_totale = calcul_distance_totale(pi, df_ville)
    poids_transporté = sum(df_object.iloc[i]['Weight'] for i, pris in enumerate(obj_pris) if pris == 1)
    temps_total = distance_totale / max(1, (1 - 0.1 * poids_transporté / capacite))  # Exemple de calcul simplifié

    # Profit final
    return profit_total - temps_total


# **Fonction 4 : Calcul de la distance totale pour une tournée**
def calcul_distance_totale(pi, df_ville):
    distance_totale = 0
    for i in range(len(pi) - 1):
        distance_totale += calcul_distance_de_ville(pi[i], df_ville)[pi[i + 1]]
    distance_totale += calcul_distance_de_ville(pi[-1], df_ville)[pi[0]]  # Retour à la ville de départ
    return distance_totale



df_ville,df_object,capacity=parse_ttp_file("a280_n279_bounded-strongly-corr_01.ttp")

pi2,dict_ville_objet_pris2 = algo_iteratif(df_ville,df_object,capacity)
