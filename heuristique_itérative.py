import numpy as np
import copy
from utils import *
from heuristique_glouton import *
from evaluation import *

def algo_genetique(df_ville, df_object, capacite, population_size, max_iterations, mutation_rate=0.1):
    def generate_solution():
        pi = np.random.permutation(len(df_ville)) + 1
        obj_pris = np.random.randint(2, size=len(df_object))
        return pi, obj_pris

    def evaluate_solution(pi, obj_pris):
        dict_ville_objet_pris = {ville: [] for ville in pi}
        for i, ville in enumerate(pi):
            objets_disponibles = get_objects_of_ville(ville, df_object).index
            for obj in objets_disponibles:
                if obj_pris[obj-1] == 1:
                    dict_ville_objet_pris[ville].append(obj)
        return calculer_profit(pi, obj_pris, df_ville, df_object, capacite), dict_ville_objet_pris

    def crossover(parent1, parent2):
        cut = np.random.randint(1, len(parent1[0]))
        child1_pi = np.concatenate((parent1[0][:cut], parent2[0][cut:]))
        child2_pi = np.concatenate((parent2[0][:cut], parent1[0][cut:]))
        child1_obj_pris = np.concatenate((parent1[1][:cut], parent2[1][cut:]))
        child2_obj_pris = np.concatenate((parent2[1][:cut], parent1[1][cut:]))
        return (child1_pi, child1_obj_pris), (child2_pi, child2_obj_pris)

    def mutate(solution):
        pi, obj_pris = solution
        if np.random.rand() < mutation_rate:
            i, j = np.random.randint(0, len(pi), size=2)
            pi[i], pi[j] = pi[j], pi[i]
        if np.random.rand() < mutation_rate:
            i = np.random.randint(0, len(obj_pris))
            obj_pris[i] = 1 - obj_pris[i]
        return pi, obj_pris

    # Générer la population initiale
    population = [generate_solution() for _ in range(population_size)]
    best_solution = None
    best_profit = -np.inf

    for iteration in range(max_iterations):
        # Évaluer la population
        evaluated_population = [(evaluate_solution(pi, obj_pris), (pi, obj_pris)) for pi, obj_pris in population]
        evaluated_population.sort(reverse=True, key=lambda x: x[0][0])

        # Sélectionner les meilleures solutions
        population = [solution for _, solution in evaluated_population[:population_size // 2]]

        # Mettre à jour la meilleure solution
        if evaluated_population[0][0][0] > best_profit:
            best_profit = evaluated_population[0][0][0]
            best_solution = evaluated_population[0][1]

        # Générer la population enfant par croisement et mutation
        children = []
        while len(children) < population_size:
            parent_indices = np.random.choice(len(population), size=2, replace=False)
            # Select parents using the indices
            parents = [population[i] for i in parent_indices]
            child1, child2 = crossover(parents[0], parents[1])
            children.append(mutate(child1))
            if len(children) < population_size:
                children.append(mutate(child2))

        population = children

        # Vérifier la convergence
        if iteration > 0 and abs(evaluated_population[0][0][0] - best_profit) < 1e-6:
            break

    best_pi, best_obj_pris = best_solution
    best_profit, best_dict_ville_objet_pris = evaluate_solution(best_pi, best_obj_pris)
    return best_pi, best_obj_pris, best_profit, best_dict_ville_objet_pris


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

if __name__=="__main__":
    # Exemple d'utilisation
    df_ville, df_object, capacity = parse_ttp_file("a280_n279_bounded-strongly-corr_01.ttp")
    #pi, best_obj_pris, best_profit, dict_ville_objet_pris = algo_genetique(df_ville, df_object, capacity)
    #print(eval_lin(pi, df_ville, df_object, dict_ville_objet_pris, best_obj_pris))

    max_iterations_list = [50, 150, 250, 350, 400, 500]
    max_population_size = [50, 100, 150, 200, 250]

    with open("results_iteratif.md", "w") as file:
        file.write("# Résultats de l'algorithme génétique\n\n")
        for max_iterations in max_iterations_list:
            print(f"Running algo_genetique with max_iterations = {max_iterations}")
            for max_population in max_population_size:
                print(f"Running algo_genetique with max_iterationn = {max_iterations}")
                print(f"Running algo_genetique with max_population = {max_population}")
                pi, best_obj_pris, best_profit, dict_ville_objet_pris = algo_genetique(df_ville, df_object, capacity, population_size=max_population, max_iterations=max_iterations)
                eval_lin_result, benefice_lin, cout_lin = eval_lin(pi, df_ville, df_object, dict_ville_objet_pris, best_obj_pris)
                eval_non_lin_result, benefice_non_lin, cout_non_lin = eval_non_lin(pi, df_ville, df_object, dict_ville_objet_pris, best_obj_pris, capacity)
                file.write(f"## max_iterations = {max_iterations}\n")
                file.write(f"### max_population = {max_population}\n")
                file.write(f"- eval_lin_benefice = {benefice_lin}\n")
                file.write(f"- eval_lin_cout = {cout_lin}\n")
                file.write(f"- eval_lin_result = {eval_lin_result}\n")
                file.write(f"- eval_non_lin_benefice = {benefice_non_lin}\n")
                file.write(f"- eval_non_lin_cout = {cout_non_lin}\n")
                file.write(f"- eval_non_lin_result = {eval_non_lin_result}\n\n")
        print(f"max_iterations = {max_iterations}, eval_lin = {eval_lin_result}, eval_non_lin = {eval_non_lin_result}")