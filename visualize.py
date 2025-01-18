import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from heuristique_glouton import *




def visualize(df_ville,pi,dict_ville_objet_pris):
    # Création du graphe de base
    fig = go.Figure()

    # Ajout des villes
    for idx, row in df_ville.iterrows():
        objets_pris=dict_ville_objet_pris[idx]
        hovertemplate = f"Nom de la ville : {idx}"
        for obj in objets_pris:
            hovertemplate += f"<br>Nom de l'objet : {obj}"
    
        hovertemplate+="<extra></extra>"

        fig.add_trace(go.Scatter(
            x=[row["X"]],
            y=[row["Y"]],
            mode="markers+text",
            text=f"V {idx}",
            name=f"Ville {idx}",
            #textposition="top center",
            marker=dict(size=10),
            hoverinfo="text",
            customdata=[dict_ville_objet_pris[idx]],  # Ajout du texte et des objets
            hovertemplate=hovertemplate
        ))

    # Ajout des lignes représentant l'ordre de passage
    for i in range(len(pi) - 1):
        start = pi[i]
        end = pi[i + 1]
        fig.add_trace(go.Scatter(
            x=[df_ville.iloc[start-1]["X"], df_ville.iloc[end-1]["X"]],
            y=[df_ville.iloc[start-1]["Y"], df_ville.iloc[end-1]["Y"]],
            mode="lines",
            line=dict(color="blue"),
            showlegend=False
        ))

# Mise en page
    fig.update_layout(
        title="Visualisation du parcours TTCP",
        xaxis_title="Coordonnée X",
        yaxis_title="Coordonnée Y",
        xaxis=dict(scaleanchor="y"),  # Assure une échelle égale
        height=600,
        width=800
    )

    # Afficher l'interaction
    fig.show()
    
    
if __name__=="__main__":
    df_ville,df_object,capacity=parse_ttp_file("a280_n2790_uncorr_10.ttp")
    pi,obj_pris,poids_tot,dict_ville_objet_pris=algo_glouton(df_ville,df_object,capacity)
    visualize(df_ville,pi,dict_ville_objet_pris)
