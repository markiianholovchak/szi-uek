import pandas as pd


materials = pd.read_json("./materials.json")

orders = pd.read_json("./orders.json")


ghp = pd.DataFrame(orders.transpose())

ghp.index = ["Tydzień", "Przewidywany popyt"]

produkcja = [0] * len(ghp.columns)
dostepne = [0] * len(ghp.columns)

# Calculate GHP:
skateboardStorage = materials.skateboard.storage
skateboardsPerOted = materials.skateboard.units_per_order

for index, value in ghp.iloc[1].items():
    if index == 0: 
        dostepne[index] = (skateboardStorage - value)
    else:
        stepBack = 0
        dostepne[index] = dostepne[index-1] + produkcja[index] - value
        while dostepne[index] < 0:
            produkcja[index - stepBack] = skateboardsPerOted
            for i in range(index-stepBack, index + 1):
                dostepne[i] = dostepne[i - 1] + produkcja[i] - ghp.iloc[1, i] 
            stepBack += 1
        
        

ghp.loc[len(ghp.index)] = produkcja
ghp.loc[len(ghp.index)] = dostepne

ghp.index = ["Tydzień", "Przewidywany popyt", "Produkcja", "Dostępne"]

print(materials.skateboard.storage)

print()
print("==============================================================", )
print("Główny harmonogram produkcji:")
print(ghp)
print(f"Na stanie: {skateboardStorage}")
print("==============================================================", )
print()






