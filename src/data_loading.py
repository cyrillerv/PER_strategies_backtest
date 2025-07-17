import pandas as pd
import json
import numpy as np

def load_data() :
    df_MarketCap = pd.read_excel(r"data\MarketCap.xlsx")
    df_PER = pd.read_excel(r"data\PER.xlsx")
    df_TotalAssets = pd.read_excel(r"data\TotalAssets.xlsx")
    df_TotalRevenue = pd.read_excel(r"data\TotalRevenue.xlsx")


    with open(r"data\CompanySectors.json", "r") as f:
        dic_sectors = json.load(f)

    return df_MarketCap, df_PER, df_TotalAssets, df_TotalRevenue, dic_sectors