import sys
from heuristique_glouton import *
from heuristique_itérative import *
from Lin_prog import *
from utils import *
from visualize import *

def main():
    args = sys.argv[1:]
    if len(args) != 3:
        print("MAUVAIS ENTREE")
        return 1
    nom_fic=args[0]
    heuristique_method=int(args[1])
    visual_mode=int(args[2])
    
    df_ville,df_object,capacity=parse_ttp_file(nom_fic)
    pi=None
    obj_pris=None
    
    if heuristique_method==0:
        pi, obj_pris, poids_tot, dict_ville_objet_pris=algo_glouton(df_ville,df_object,capacity)
    
    if heuristique_method==1:
        pi, obj_pris, best_profit, dict_ville_objet_pris=algo_genetique(df_ville,df_object,capacity,10,10)
    if heuristique_method==2:
        pi,obj_pris=prog_lin(df_ville,df_object,capacity)
    
    if visual_mode==0:
        print("Pi[Route]",pi)
        print("Objet pris",obj_pris)
    
    if visual_mode==1:
        visualize(df_ville,pi,dict_ville_objet_pris)


main()