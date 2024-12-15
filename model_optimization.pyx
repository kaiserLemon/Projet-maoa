# model_optimization.pyx

from utils import *
from heuristique_glouton import *
from evaluation import *
df_ville,df_object,capacity=parse_ttp_file("a280_n279_bounded-strongly-corr_01.ttp")

import gurobipy as gp
import pandas as pd
import numpy as np
import gc

def optimize_model(df_ville, df_object, capacity):
    model = gp.Model()

    # Create variables
    list_index_ville = list(df_ville.index)
    dict_obj_ville = {}
    list_obj = []
    for index_ville in list_index_ville:
        dict_obj_ville[index_ville] = []
        list_index_obj = list(get_objects_of_ville(index_ville + 1, df_object).index)
        for index_obj in list_index_obj:
            x = model.addVar(vtype="B", name=f"X_{index_obj}")
            dict_obj_ville[index_ville].append(x)
            list_obj.append(x)

    matrix_distance = {index_ville: calcul_distance_de_ville(index_ville, df_ville) for index_ville in list_index_ville}

    pi = np.empty((len(list_index_ville), len(list_index_ville)), dtype=object)
    for i in range(len(list_index_ville)):
        for j in range(len(list_index_ville)):
            pi[i, j] = model.addVar(vtype="B", name=f"Pi_{i}-{j}")

    # Create constraints
    model.addConstr(pi[0, 0] == 1)
    for i in range(len(list_index_ville)):
        model.addConstr(sum([pi[i, j] for j in range(len(list_index_ville))]) == 1)
        model.addConstr(sum([pi[j, i] for j in range(len(list_index_ville))]) == 1)

    list_poids = df_object["Weight"].values

    model.addConstr(sum([list_poids[i] * list_obj[i] for i in range(len(list_poids))]) <= capacity)

    z = np.empty((len(list_index_ville) - 1, len(list_index_ville), len(list_index_ville)), dtype=object)
    for i in range(len(list_index_ville) - 1):
        for j in range(len(list_index_ville)):
            for k in range(len(list_index_ville)):
                z[i, j, k] = model.addVar(vtype="B", name=f"Z_{i}_{j}_{k}")
                model.addConstr(z[i, j, k] <= pi[i, j])
                model.addConstr(z[i, j, k] <= pi[i + 1, k])
                model.addConstr(z[i, j, k] >= pi[i, j] + pi[i + 1, k] - 1)

    list_benefits = df_object["Profit"].values

    benefit_tot = sum(list_benefits[i] * list_obj[i] for i in range(len(list_benefits)))

    total_distance_expr = 0
    poids_actu = 0

    for i in range(len(list_index_ville) - 1):
        for j in range(len(list_index_ville)):
            for k in range(len(list_index_ville)):
                total_distance_expr += z[i, j, k] * matrix_distance[j + 1][k + 1] * poids_actu
            list_index_obj = list(get_objects_of_ville(j + 1, df_object).index)
            poids_actu += sum([list_obj[obj_index - 1] * list_poids[obj_index - 1] * pi[i, j] for obj_index in list_index_obj])

    # Optional: Set this as an objective or constraint
    model.setObjective(benefit_tot - (1 / 1000) * total_distance_expr, gp.GRB.MAXIMIZE)  # Minimizing distance

    # Libérer la mémoire inutilisée
    #del list_index_ville, dict_obj_ville, list_obj, matrix_distance, pi, list_poids, z, list_benefits
    gc.collect()

    return model