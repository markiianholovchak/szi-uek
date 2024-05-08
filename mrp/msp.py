import pandas as pd
import math

MSP_ROW_EXPECTED_DEMAND = "Przewidywany popyt"
MSP_ROW_PRODUCE = "Produkcja"
MSP_ROW_IN_STOCK = "Dostępne"

def msp_calculate_in_stock(msp,  weekColumnIndex):
    return ((msp.loc[MSP_ROW_IN_STOCK, msp.columns[weekColumnIndex - 1]] + msp.loc[MSP_ROW_PRODUCE, msp.columns[weekColumnIndex]]) - msp.loc[MSP_ROW_EXPECTED_DEMAND, msp.columns[weekColumnIndex]])

def msp_place_order(msp, weekColumnIndex, materialInformation):
    if(msp.at[MSP_ROW_PRODUCE, msp.columns[weekColumnIndex]] > 0):
        raise Exception("Order has already been placed for given week.")

    msp.at[MSP_ROW_PRODUCE, msp.columns[weekColumnIndex]] = materialInformation.units_per_order
    msp.at[MSP_ROW_IN_STOCK, msp.columns[weekColumnIndex]] = msp.at[MSP_ROW_IN_STOCK, msp.columns[weekColumnIndex - 1]] + materialInformation.units_per_order
    return msp

def build_msp(productInformation):
    orders = pd.read_json("data/orders.json").transpose()
    demandDict = {orders.columns.get_loc(value) + 1: [orders.at['orders', value], *[0] * 2] for value in orders.columns}

    msp = pd.DataFrame(demandDict)
    msp.index = [MSP_ROW_EXPECTED_DEMAND, MSP_ROW_PRODUCE, MSP_ROW_IN_STOCK]

    for col_name in msp.columns:
        column_index = msp.columns.get_loc(col_name)
        expected_in_stock = None
        if column_index == 0: 
            expected_in_stock = (productInformation.storage - msp.at[MSP_ROW_EXPECTED_DEMAND, msp.columns[column_index]])
        else:
            expected_in_stock = msp_calculate_in_stock(msp, column_index)
        
        if expected_in_stock < 0:
            stepsBack = math.ceil(-expected_in_stock / productInformation.units_per_order)
            if(column_index - stepsBack * productInformation.ready_in_weeks < 0):
                raise Exception("Error: Can not build ghp: orders are too big")
            for i in range(column_index - stepsBack * productInformation.ready_in_weeks, column_index - productInformation.ready_in_weeks + 1):
                msp = msp_place_order(msp, i, productInformation)
            expected_in_stock = msp_calculate_in_stock(msp, column_index)

        msp.at[MSP_ROW_IN_STOCK, col_name] = expected_in_stock
        
    return msp

def create_and_print_msp(product_information):
    try:
        msp = build_msp(product_information)
        print()
        print("==============================================================", )
        print(f"Główny harmonogram produkcji dla {product_information.name}:")
        print(msp)
        print(f"Na stanie: {product_information.storage}")
        print("==============================================================", )
        print()
        return msp
    except Exception as e:
        print(f"Could not build this mrp for the given production schedule")
        print(f"Error: {e}")
        return