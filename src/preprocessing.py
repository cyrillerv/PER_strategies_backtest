import numpy as np
import pandas as pd

# TODO: enlever les valeurs négatives du df PER

def clean_data(dic_input) :
    valid_fields = {"MarketCap", "PER", "TotalAssets", "TotalRevenue", "StockPrices", "Sectors"}
    assert set(dic_input.keys()).issubset(valid_fields), "Un ou plusieurs champs invalides"

    dic_output = {}
    for field in dic_input :
        if field != "Sectors" :
            df = dic_input[field].copy()
            df.set_index("Unnamed: 0", inplace=True)
            df.index.name = None
            df.replace([np.inf, -np.inf], np.nan, inplace=True)
            df.dropna(axis=1, how='all', inplace=True)
            df.index = pd.to_datetime(df.index)
            df_reindexed = df.reindex(pd.date_range(df.index.min(), df.index.max()), method='ffill')
            dic_output[field] = df_reindexed
        else :
            dic_output[field] = dic_input[field]

    return dic_output


# We keep only the tickers for which we have data for everything => seulement pour clustering
# tickers = set.intersection(set(df_MarketCap.columns), set(df_PER.columns), set(df_TotalAssets.columns), set(df_TotalRevenue.columns), set(dic_sectors.keys()))