import pulp
from utils import *
from heuristique_glouton import get_objects_of_ville 

def solve_prog_lin(df_ville,df_object):

    # Create a linear programming problem
    model = pulp.LpProblem("Routing_Profit_Maximization", pulp.LpMaximize)

    list_index_ville=list(df_ville.index)
    dict_obj_ville={}
    list_obj=[]
    for index_ville in list_index_ville:
        dict_obj_ville[index_ville]=[]

    # Define variables for city and object selections
    pi = [[pulp.LpVariable(f"pi_{i}_{j}", cat="Binary") for j in range(len(list_index_ville))] for i in range(len(list_index_ville))]

    x = []  # Object variables list
    dict_obj_ville = {}  # Objects for each city
    for index_ville in list_index_ville:
        dict_obj_ville[index_ville] = []
        list_index_obj = list(get_objects_of_ville(index_ville + 1, df_object).index)
        for index_obj in list_index_obj:
            var = pulp.LpVariable(f"x_{index_obj}", cat="Binary")
            dict_obj_ville[index_ville].append(var)
            x.append(var)

    # Add constraints: visiting cities
    model += pi[0][0] == 1  # Start at city 0
    for i in range(len(list_index_ville)):
        model += pulp.lpSum(pi[i]) == 1  # Visit one city per step
        model += pulp.lpSum([pi[j][i] for j in range(len(list_index_ville))]) == 1  # Each city is visited once

    # Linearization: Create z variables
    z = [[[pulp.LpVariable(f"z_{i}_{j}_{k}", cat="Binary") 
      for k in range(len(list_index_ville))] for j in range(len(list_index_ville))] 
      for i in range(len(list_index_ville) - 1)]

    # Add linearization constraints for z
    for i in range(len(list_index_ville) - 1):
        for j in range(len(list_index_ville)):
            for k in range(len(list_index_ville)):
                model += z[i][j][k] <= pi[i][j]
                model += z[i][j][k] <= pi[i + 1][k]
                model += z[i][j][k] >= pi[i][j] + pi[i + 1][k] - 1

    # Add weight constraint for objects
    list_poids = [df_object.iloc[i]["Weight"] for i in range(len(x))]
    capacity = 50  # Example capacity
    model += pulp.lpSum(list_poids[i] * x[i] for i in range(len(x))) <= capacity

    # Define benefits
    list_benefits = [df_object.iloc[i]["Profit"] for i in range(len(x))]
    total_benefit = pulp.lpSum(list_benefits[i] * x[i] for i in range(len(x)))

    # Define the total distance
    distance_matrix = {ville: calcul_distance_de_ville(ville, df_ville) for ville in df_ville.index}
    total_distance = pulp.lpSum(
        distance_matrix[j][k] * z[i][j][k]
        for i in range(len(list_index_ville) - 1)
        for j in range(len(list_index_ville))
        for k in range(len(list_index_ville))
    )

    # Set the objective: maximize profit minus distance
    model += total_benefit - total_distance

    # Solve using GLPK solver
    model.solve(pulp.GLPK(msg=True))

    # Display results
    if pulp.LpStatus[model.status] == "Optimal":
        print(f"Total Objective Value: {pulp.value(model.objective)}")
        for i in range(len(list_index_ville)):
            for j in range(len(list_index_ville)):
                if pulp.value(pi[i][j]) == 1:
                    print(f"At time {i}, visit city {j}")
    else:
        print("No optimal solution found.")
