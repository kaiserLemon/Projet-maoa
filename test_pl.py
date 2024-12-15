from utils import *
from heuristique_glouton import *
from evaluation import *

df_ville,df_object,capacity=parse_ttp_file("a280_n279_bounded-strongly-corr_01.ttp")

import model_optimization

model = model_optimization.optimize_model(df_ville, df_object, capacity)
model.optimize()