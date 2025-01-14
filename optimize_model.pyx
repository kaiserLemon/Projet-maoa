import gurobipy as gp
from gurobipy import GRB
from utils import *
from libc.math cimport abs
from heuristique_glouton import *

def optimize_model(df_ville, df_object, double capacity):
    # Créer le modèle Gurobi
    model = gp.Model()

    # Déclaration des variables
    cdef list list_index_ville = list(df_ville.index)
    cdef dict dict_obj_ville = {}
    cdef list list_obj = []
    cdef int i, j, k

    # Variables pour les objets
    for index_ville in list_index_ville:
        dict_obj_ville[index_ville] = []
        list_index_obj = list(get_objects_of_ville(index_ville + 1, df_object).index)
        for index_obj in list_index_obj:
            x = model.addVar(vtype=GRB.BINARY, name=f"X_{index_obj}")
            dict_obj_ville[index_ville].append(x)
            list_obj.append(x)

    # Matrice des distances
    cdef dict matrix_distance = {index_ville: calcul_distance_de_ville(index_ville, df_ville) for index_ville in list_index_ville}

    # Variables pour la tournée (pi)
    cdef list pi = []
    for i in range(len(list_index_ville)):
        pi.append([])
        for j in range(len(list_index_ville)):
            pi[i].append(model.addVar(vtype=GRB.BINARY, name=f"Pi_{i}_{j}"))

    # Contraintes pour la tournée
    model.addConstr(pi[0][0] == 1)
    for i in range(len(list_index_ville)):
        model.addConstr(sum([pi[i][j] for j in range(len(pi[i]))]) == 1)
        model.addConstr(sum([pi[j][i] for j in range(len(pi[i]))]) == 1)

    # Contraintes pour la capacité
    cdef list list_poids = [df_object.iloc[i]["Weight"] for i in range(len(list_obj))]
    model.addConstr(sum([list_poids[i] * list_obj[i] for i in range(len(list_poids))]) <= capacity)

    # Variables Z pour les distances
    cdef list z = []
    for i in range(len(list_index_ville) - 1):
        z.append([])
        for j in range(len(list_index_ville)):
            z[i].append([])
            for k in range(len(list_index_ville)):
                z[i][j].append(model.addVar(vtype=GRB.BINARY, name=f"Z_{i}_{j}_{k}"))
                model.addConstr(z[i][j][k] <= pi[i][j])
                model.addConstr(z[i][j][k] <= pi[i + 1][k])
                model.addConstr(z[i][j][k] >= pi[i][j] + pi[i + 1][k] - 1)

    # Calcul des bénéfices
    cdef list list_benefits = [df_object.iloc[i]["Profit"] for i in range(len(list_obj))]
    cdef double benefit_tot = sum(list_benefits[i] * list_obj[i] for i in range(len(list_benefits)))

    # Calcul de la distance totale et mise à jour des poids
    cdef double total_distance_expr = 0
    cdef double poids_actu = 0

    for i in range(len(list_index_ville) - 1):
        for j in range(len(list_index_ville)):
            for k in range(len(list_index_ville)):
                total_distance_expr += z[i][j][k] * matrix_distance[int(j + 1)][int(k + 1)] * poids_actu
            list_index_obj = list(get_objects_of_ville(j + 1, df_object).index)
            poids_actu += sum([list_obj[int(obj_index - 1)] * list_poids[int(obj_index - 1)] * pi[i][j] for obj_index in list_index_obj])

    # Définir la fonction objective
    model.setObjective(benefit_tot - (1 / 1000) * total_distance_expr, GRB.MAXIMIZE)

    return model
