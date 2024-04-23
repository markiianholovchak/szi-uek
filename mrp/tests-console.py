from mrp import create_and_print_mrp
from msp import create_and_print_msp

import pandas as pd

def main():
    materials = pd.read_json("data/materials.json")
    msp = create_and_print_msp(materials.skateboard)
    if msp is None:
        return

    mrp_elements = [materials.truck, materials.board, materials.wheel, materials.axle]

    for mrp_element in mrp_elements:
        mrp = create_and_print_mrp(mrp_element)
        if(mrp is None):
            return
    
    print("GHP AND MRP BUILT SUCCESSFULY!")
    


if __name__ == "__main__":
    main()
