import json
import pandas as pd

def load_data(fields):
    valid_fields = {"MarketCap", "PER", "TotalAssets", "TotalRevenue", "StockPrices", "Sectors"}
    assert set(fields).issubset(valid_fields), "Un ou plusieurs champs invalides"

    dic_df = {}

    # Si "Sectors" est demandé, on charge le JSON séparément
    if "Sectors" in fields:
        with open(r"data\CompanySectors.json", "r") as f:
            dic_sectors = json.load(f)
        dic_df["Sectors"] = dic_sectors

    # On enlève "Sectors" car ce n'est pas un fichier Excel
    fields = set(fields) - {"Sectors"}

    # Chargement des fichiers Excel
    for field in fields:
        df_field = pd.read_excel(fr"data\{field}.xlsx")
        dic_df[field] = df_field

    return dic_df
