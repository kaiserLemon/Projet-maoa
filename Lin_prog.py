import gurobipy as gp
from heuristique_glouton import get_objects_of_ville
from utils import *

def prog_lin(df_ville,df_object,capacity):

    # Initialize combined model
    model = gp.Model("CombinedModel")

    # Decision variables for object selection
    dict_obj_ville = {}
    list_index_ville = list(df_ville.index)
    list_obj = []

    for index_ville in list_index_ville:
        list_index_obj = list(get_objects_of_ville(index_ville + 1, df_object).index)
        dict_obj_ville[index_ville] = []
        for index_obj in list_index_obj:
            x = model.addVar(vtype=gp.GRB.BINARY, name=f"x_{index_ville}_{index_obj}")
            dict_obj_ville[index_ville].append(x)
            list_obj.append(x)


    # Decision variables for routing
    n = len(list_index_ville)
    y = [
        [model.addVar(vtype=gp.GRB.BINARY, name=f"y_{i}_{j}") for j in range(n)]
        for i in range(n)
    ]

# Auxiliary variables for cumulative weight
    w = model.addVars(n, vtype=gp.GRB.CONTINUOUS, lb=0, name="w")

    w_transfers=model.addVars(n, vtype=gp.GRB.CONTINUOUS, lb=0, name="w_transfer")

    model.addConstr(w_transfers[0]==0)

    # Auxiliary variables for MTZ constraints
    u = model.addVars(n, vtype=gp.GRB.CONTINUOUS, lb=1, ub=n, name="u")

    # Define weights and profits for object selection
    list_poids = [df_object.iloc[i]["Weight"] for i in range(len(list_obj))]
    list_benefits = [df_object.iloc[i]["Profit"] for i in range(len(list_obj))]

    # Define distance matrix
    matrix_distance = {i: calcul_distance_de_ville(i, df_ville) for i in list_index_ville}

    # Add capacity constraint
    model.addConstr(
        gp.quicksum(list_poids[i] * list_obj[i] for i in range(len(list_poids))) <= capacity,
        "Capacity"
    )

    # Add routing constraints
    model.addConstrs(
        (gp.quicksum(y[i][j] for j in range(n) if j != i) == 1 for i in range(n)), "Depart"
    )
    model.addConstrs(
        (gp.quicksum(y[i][j] for i in range(n) if i != j) == 1 for j in range(n)), "Arrive"
    )

    # Ensure objects are selected only if their cities are visited
    for index_ville, vars_list in dict_obj_ville.items():
        for obj_var in vars_list:
            model.addConstr(
                gp.quicksum(y[index_ville][j] for j in range(n) if j != index_ville) >= obj_var,
                f"ObjectSelectedIfCityVisited_{index_ville}"
            )

    # Add cumulative weight constraints
    for i in range(n):
        model.addConstr(
            w[i] == gp.quicksum(dict_obj_ville[i+1][k] * list_poids[k] for k in range(len(dict_obj_ville[i+1]))),
            f"CumulativeWeight_{i}"
        )
        if i > 0:
            model.addConstr(w_transfers[i] == w[i] + w_transfers[i-1],f"WeightTransfer_{i}")

    # Add MTZ constraints to eliminate subtours
    for i in range(1, n):  # Start from 1 since city 0 is the starting point
        for j in range(1, n):  # MTZ does not apply for starting city
            if i != j:
                model.addConstr(
                    u[i] - u[j] + n * y[i][j] <= n - 1,
                    name=f"SubtourElimination_{i}_{j}"
                )

    # Define objective function
    profit = gp.quicksum(list_benefits[i] * list_obj[i] for i in range(len(list_benefits)))
    routing_cost = gp.quicksum(
        matrix_distance[i + 1][j + 1] * y[i][j] * w_transfers[i] for i in range(n) for j in range(n)    
    )

    # Combine objectives: maximize profit and minimize routing cost
    alpha = 1  # Weight for profit
    beta = 1   # Weight for routing cost (adjust based on importance)
    model.setObjective(alpha * profit-beta*routing_cost, gp.GRB.MAXIMIZE)

    # Optimize the model
    model.optimize()

    # Extract solution
    pi = []
    obj_pris = {i: [] for i in range(n)}  # Initialize dictionary to store selected objects for each city
    if model.status == gp.GRB.OPTIMAL:
        print(f"Optimal combined objective value: {model.objVal}")
        print("Selected objects:")

        # Extract selected objects
        for index_ville, vars_list in dict_obj_ville.items():
            for obj_var in vars_list:
                if obj_var.x > 0.5:
                    obj_pris[index_ville].append(obj_var.varName)
                    print(f"Object {obj_var.varName} selected")

        # Build the path starting from city 0
        visited = set()
        current_city = 0
        while len(visited) < n:
            visited.add(current_city)
            pi.append(current_city)
            for j in range(n):
                if y[current_city][j].x > 0.5 and j not in visited:
                    current_city = j
                    break

        print("Optimal path:", pi)

    return pi, obj_pris


if __name__=="__main__":
    df_ville,df_object,capacity=parse_ttp_file("a280_n279_bounded-strongly-corr_01.ttp")
    pi,obj_pris=prog_lin(df_ville,df_object,capacity)
    print("Path (pi):", pi)
    print("Selected objects (obj_pris):", obj_pris)