# Projet-maoa

Ce projet se concentre sur les problèmes de TTP et KCTSP.

TTP   = Travelling Thief Problem                                                                                                                                                                                
TSP   = Travelling Salesman Problem                                                                                                                                                                             
KP    = Knapsack Problem                                                                                                                                                                                        
KCTSP = Time and weight dependent TSP + contrainte de KP 

Nous réaliserons donc les points suivants:

1. Concevoir des heuristiques pour les problèmes de TTP et KCTSP
2. Implémenter ces heuristiques, les évaluer, et les comparer avec l’état de l’art
3. Documenter sous forme de rapport décrivant les solutions ainsi que les expérimentations
   réalisées avec une analyse critique des résultats


python main.py nom_fic heuristique_methode visualise_methode

nom_fic est le nom du fichier
heuristique_methode est la méthode heuristique utilisée, 0 pour Glouton , 1 pour itérative et 2 pour PL
visualise_methode est 0 pour pas de visualisation(affichage de pi et list des objets pris au terminal), 1 pour visualisation de pyplot