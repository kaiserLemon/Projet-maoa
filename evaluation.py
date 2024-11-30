import pandas as pd
from utils import *

def eval_non_lin(pi,df_ville,df_object,dict_ville_objet_pris,obj_pris,capacity):
    v_max=1
    v_min=0.1
    w=(v_max-v_min)/capacity
    benefice=0
    for i in range(len(list(df_object.index))):
        benefice=benefice+df_object.iloc[i]["Profit"]*obj_pris[i]

    cout=0
    poids=0
    for i in range(1,len(pi)):
        distance=calcul_distance_de_ville(pi[i-1],df_ville)[pi[i]]
        cout=cout+distance/(v_max-poids*w)
        list_objet_i_pris=dict_ville_objet_pris[pi[i]]
        for index in list_objet_i_pris:
            poids=poids+df_object.iloc[index-1]["Weight"]

    distance=calcul_distance_de_ville(pi[-1],df_ville)[1]

    cout=cout+distance/(v_max-poids*w)


    return benefice-cout

def eval_lin(pi,df_ville,df_object,dict_ville_objet_pris,obj_pris):
    benefice=0
    for i in range(len(list(df_object.index))):
        benefice=benefice+df_object.iloc[i]["Profit"]*obj_pris[i]

    cout=0
    poids=0
    for i in range(1,len(pi)):
        distance=calcul_distance_de_ville(pi[i-1],df_ville)[pi[i]]
        cout=cout+distance*poids
        list_objet_i_pris=dict_ville_objet_pris[pi[i]]
        for index in list_objet_i_pris:
            poids=poids+df_object.iloc[index-1]["Weight"]

    distance=calcul_distance_de_ville(pi[-1],df_ville)[1]

    cout=cout+distance*poids


    return benefice-cout