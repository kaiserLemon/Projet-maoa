from optimize_model import optimize_model
from utils import *


# Example usage
df_ville, df_object, capacity = parse_ttp_file("a280_n279_bounded-strongly-corr_01.ttp")
model = optimize_model(df_ville, df_object, capacity)
model.optimize()

# Print the results
for v in model.getVars():
    print(f"{v.varName}: {v.x}")

print(f"Objective value: {model.objVal}")