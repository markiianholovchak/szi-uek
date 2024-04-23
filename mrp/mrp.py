import pandas as pd
import math

MRP_ROW_OVERALL_DEMAND = "Całkowite zapotrzebowanie"
MRP_ROW_EXPECTED_DELIVERY = "Planowane przyjęcia"
MRP_ROW_IN_STOCK = "Przewidywanie na stanie"
MRP_ROW_DEMAND_NETTO = "Zapotrzebowanie netto"
MRP_ROW_PLANNED_ORDERS = "Planowane zamówienia"
MRP_ROW_PLANNED_ORDERS_DELIVERY = "Planowane przyjecie zamówień"


def mrp_place_order(mrp, weekColumnIndex, materialInformation):
    if(mrp.at[MRP_ROW_PLANNED_ORDERS, mrp.columns[weekColumnIndex]]):
        raise Exception("Order has already been placed for given week.")

    mrp.at[MRP_ROW_PLANNED_ORDERS, mrp.columns[weekColumnIndex]] = materialInformation.units_per_order
    mrp.at[MRP_ROW_PLANNED_ORDERS_DELIVERY, mrp.columns[weekColumnIndex+materialInformation.ready_in_weeks]] = materialInformation.units_per_order
    mrp.at[MRP_ROW_IN_STOCK, mrp.columns[weekColumnIndex+materialInformation.ready_in_weeks]] = mrp.at[MRP_ROW_IN_STOCK, mrp.columns[weekColumnIndex+materialInformation.ready_in_weeks]] + materialInformation.units_per_order
    return mrp

def mrp_calculate_in_stock(mrp,  weekColumnIndex):
    return ((mrp.loc[MRP_ROW_IN_STOCK, mrp.columns[weekColumnIndex - 1]] + mrp.loc[MRP_ROW_EXPECTED_DELIVERY, mrp.columns[weekColumnIndex]] + mrp.loc[MRP_ROW_PLANNED_ORDERS_DELIVERY, mrp.columns[weekColumnIndex]]) - mrp.loc[MRP_ROW_OVERALL_DEMAND, mrp.columns[weekColumnIndex]])

def build_mrp(demand, materialInformation):
    demandDict = {index + 1: [value, *[0] * 5] for index, value in enumerate(demand)}
    mrp = pd.DataFrame(demandDict)
    mrp.index = [MRP_ROW_OVERALL_DEMAND, MRP_ROW_EXPECTED_DELIVERY, MRP_ROW_IN_STOCK, MRP_ROW_DEMAND_NETTO, MRP_ROW_PLANNED_ORDERS, MRP_ROW_PLANNED_ORDERS_DELIVERY]

    for col_name in mrp.columns:
        column_index = mrp.columns.get_loc(col_name)
        expected_in_stock = None
        if(column_index == 0):
            expected_in_stock = ((materialInformation.storage + mrp.loc[MRP_ROW_EXPECTED_DELIVERY, col_name]) - (mrp.loc[MRP_ROW_OVERALL_DEMAND, col_name]))
        else: 
            expected_in_stock = mrp_calculate_in_stock(mrp, column_index)
        if expected_in_stock < 0:
            stepsBack = math.ceil(-expected_in_stock / materialInformation.units_per_order)
            mrp.at[MRP_ROW_DEMAND_NETTO, col_name] = -expected_in_stock

            if(column_index - stepsBack * materialInformation.ready_in_weeks < 0):
                raise Exception("Not enough time to place needed orders")

            for i in range(column_index - stepsBack * materialInformation.ready_in_weeks, column_index - materialInformation.ready_in_weeks + 1):
                mrp = mrp_place_order(mrp=mrp, weekColumnIndex=i, materialInformation=materialInformation)
            expected_in_stock = mrp_calculate_in_stock(mrp, column_index)
                
            #        print("Error: could not build MRP. The order is too big")
            #       return
        mrp.at[MRP_ROW_IN_STOCK, col_name] = expected_in_stock

    return mrp
    
def create_and_print_mrp(materialInformation):
    print("==============================================================", )
    print(f"MRP for: {materialInformation.name}")
    try:
        mrp = build_mrp(demand=[0,0,0,15,10,0], materialInformation=materialInformation)
        print(mrp)
        print(f"Czas realizacji: {materialInformation.ready_in_weeks}")
        print(f"Wielkość partii: {materialInformation.units_per_order}")
        print(f"Poziom BOM: {materialInformation.level}")
        print(f"Na stanie: {materialInformation.storage}")
        print("==============================================================", )
        print()
        return mrp
    except Exception as e:
        print(f"Could not build this mrp for the given production schedule")
        print(f"Error: {e}")
        return