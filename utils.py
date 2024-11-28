import pandas as pd
import numpy as np

def parse_ttp_file(file_path):
    # Open the TTP (Travelling Thief Problem) file and read its contents
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Extract capacity of knapsack
    capacity_line = [line for line in lines if line.startswith("CAPACITY OF KNAPSACK")][0]
    capacity = int(capacity_line.split(":")[1].strip())

    # Extract dimension(number of cities)
    dimension_line = [line for line in lines if line.startswith("DIMENSION")][0]
    dimension = int(dimension_line.split(":")[1].strip())

    # Extract number of items available
    number_of_items__line = [line for line in lines if line.startswith("NUMBER OF ITEMS")][0]
    nb_item = int(number_of_items__line.split(":")[1].strip())


    # Extract city coordinates
    city_coords_start = lines.index("NODE_COORD_SECTION\t(INDEX, X, Y): \n") + 1
    city_coords = []
    
    # Read city coordinates until encountering a blank line or items section
    for line in lines[city_coords_start:city_coords_start+dimension]:
        index, x, y = line.split()
        city_coords.append((int(x), int(y)))
    
    df_ville = pd.DataFrame(city_coords, columns=["X", "Y"]) # Create a DataFrame for city coordinates

    # Adjust DataFrame index to match city numbering (starting from 1)
    df_ville.index=df_ville.index+1

    # Extract item data
    item_section_start = lines.index("ITEMS SECTION\t(INDEX, PROFIT, WEIGHT, ASSIGNED NODE NUMBER): \n") + 1
    items = []
    
    # Read item data, assuming each line contains index, profit, weight, and assigned city
    for line in lines[item_section_start:item_section_start+nb_item]:
        index, profit, weight, city_index = map(int, line.split())
        items.append((profit, weight, city_index))
    
    df_object = pd.DataFrame(items, columns=["Profit", "Weight", "City_Index"])
    # Adjust DataFrame index to match object numbering (starting from 1)
    df_object.index=df_object.index+1
    
    # Return the city and item DataFrames, along with the knapsack capacity
    return df_ville, df_object, capacity


def calcul_distance_de_ville(index_ville,df_ville):
    # Extract the coordinates of the specified city
    city_1_coords = (df_ville.iloc[index_ville-1]["X"],df_ville.iloc[index_ville-1]["Y"])

    # Calculate the Euclidean distance from the specified city to all other cities
    distances = np.sqrt((df_ville['X'] - city_1_coords[0])**2 + (df_ville['Y'] - city_1_coords[1])**2)

    return distances # Return the calculated distances
