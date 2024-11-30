from utils import *
import tqdm

def eval1(ville_cible,df_object,dist,list_objects):
    list_eval=[]
    for obj in list_objects:
        pd_obj=df_object.iloc[obj-1]
        weight=pd_obj["Weight"]
        profit=pd_obj["Profit"]
        list_eval.append(profit/(weight))
    max_eval=max(list_eval)
    if dist==0:
        return max_eval
    return max_eval/dist

def eval2(ville_cible,df_object):
    obj1=df_object.loc[df_object["City_Index"]==ville_cible]
    weight=obj1["Weight"].values[0]
    return weight

def get_objects_of_ville(index_ville,df_object):
    return df_object.loc[df_object["City_Index"]==index_ville]

def eval_obj(obj_index,df_object):
    pd_obj=df_object.iloc[obj_index-1]
    weight=pd_obj["Weight"]
    profit=pd_obj["Profit"]
    return weight/profit

def algo_glouton(df_ville, df_object, capacite):
    poids_tot = 0
    nb_objet = len(df_object.index)
    obj_pris = [0] * nb_objet  # Object index is 1 if the object is taken, otherwise 0
    nb_ville = len(df_ville.index)
    villes_dispo = list(df_ville.index)
    ville_actuelle = 1
    villes_dispo.remove(ville_actuelle)
    pi = []
    dict_ville_objet = {}  # Dictionary to track which objects are available in each city
    dict_ville_objet_pris = {}  # Dictionary to track which objects are taken in each city
    dict_ville_objet_pris[ville_actuelle] = []

    for index_ville in villes_dispo:
        dict_ville_objet[index_ville] = list(get_objects_of_ville(index_ville, df_object).index)

    deposed = True
    
    # Initialize tqdm progress bar
    with tqdm.tqdm(total=capacite, desc="Loading", unit="weight unit") as pbar:
        while capacite > poids_tot and deposed and villes_dispo != []:
            distance_table = calcul_distance_de_ville(ville_actuelle, df_ville)
            ville_cible_best = max(
                villes_dispo, 
                key=lambda ville_cible: (
                    eval1(ville_cible, df_object, distance_table[ville_cible], dict_ville_objet[ville_cible]),
                    eval2(ville_cible, df_object)
                )
            )
            dict_ville_objet_pris[ville_cible_best] = []
            list_obj_possible_a_choisir = dict_ville_objet[ville_cible_best]
            list_obj_sorted = sorted(
                list_obj_possible_a_choisir, 
                key=lambda obj_index: eval_obj(obj_index, df_object)
            )
            pi.append(ville_cible_best)
            ville_actuelle = ville_cible_best
            villes_dispo.remove(ville_cible_best)
            obj_best = list_obj_sorted[0]
            deposed = False

            for obj in list_obj_sorted:
                poids_obj = df_object.iloc[obj - 1]['Weight']
                if poids_obj <= capacite - poids_tot:
                    deposed = True
                    if eval_obj(obj_best, df_object) * 1.6 >= eval_obj(obj, df_object):
                        dict_ville_objet_pris[ville_cible_best].append(obj)
                        poids_tot += poids_obj
                        obj_pris[obj - 1] = 1
                        
                        # Update tqdm progress bar
                        pbar.update(poids_obj)
                        pbar.set_postfix({"Current Weight": poids_tot,"Nb_ville":len(pi)})

    while villes_dispo != []:
        distance_table = calcul_distance_de_ville(ville_actuelle, df_ville)
        ville_cible_best = min(villes_dispo, key=lambda ville: distance_table[ville])
        dict_ville_objet_pris[ville_cible_best] = []
        pi.append(ville_cible_best)
        ville_actuelle = ville_cible_best
        villes_dispo.remove(ville_cible_best)

    pi.append(1)
    pi.reverse()
    return pi, obj_pris, poids_tot, dict_ville_objet_pris
        