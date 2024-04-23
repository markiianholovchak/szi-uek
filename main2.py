
import pandas as pd
import numpy as np
import math

materials = pd.read_json("./materials.json")
orders = pd.read_json("./orders.json")

ghp = pd.DataFrame(orders.transpose())
ghp.index = ["Tydzień", "Przewidywany popyt"]

skateboard_storage = materials.skateboard.storage
skateboards_per_order = materials.skateboard.units_per_order

# Initialize production and availability arrays
production = np.zeros(len(ghp.columns))
availability = np.zeros(len(ghp.columns))

# Initial availability
availability[0] = skateboard_storage - ghp.iloc[1, 0]

# Calculate production and availability for each week
breakpoint()
for index in range(1, len(ghp.columns)):
    remaining = availability[index - 1] + production[index] - ghp.iloc[1, index] 

    print(index, remaining)
    
    if(remaining > 0): 
        availability[index] = remaining
        continue
    stepsBack = math.ceil(-remaining / skateboard_storage)
    for i in range(stepsBack):
        start = index - stepsBack
        if start < 0:
            print("Error: can not build ghp")
            break
        backIndex = index - stepsBack + i
        production[backIndex] = skateboards_per_order
        availability[backIndex] = availability[backIndex - 1] + production[backIndex] - ghp.iloc[1, backIndex]

# Append production and availability to ghp DataFrame
ghp.loc[len(ghp.index)] = production
ghp.loc[len(ghp.index)] = availability

ghp.index = ["Tydzień", "Przewidywany popyt", "Produkcja", "Dostępne"]

print(materials.skateboard.storage)

print()
print("==============================================================", )
print("Główny harmonogram produkcji:")
print(ghp)
print(f"Na stanie: {skateboardStorage}")
print("==============================================================", )
print()