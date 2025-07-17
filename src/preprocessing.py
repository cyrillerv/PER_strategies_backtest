import numpy as np
import pandas as pd

def clean_data(df_MarketCap, df_PER, df_TotalAssets, df_TotalRevenue, df_stockPrices, dic_sectors) :
    # Enlever des df tous les tickers pour lesquels on n'a pas de stock price => if ticker not in df_stockPrices.columns
    df_MarketCap.set_index("Unnamed: 0", inplace=True)
    df_MarketCap.index.name = None
    df_MarketCap.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_MarketCap.dropna(axis=1, how='all', inplace=True)
    df_MarketCap.index = pd.to_datetime(df_MarketCap.index)

    df_PER.set_index("Unnamed: 0", inplace=True)
    df_PER.index.name = None
    df_PER.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_PER.dropna(axis=1, how='all', inplace=True)
    df_PER.index = pd.to_datetime(df_PER.index)
    # On reindex
    df_PER_reindex = df_PER.reindex(pd.date_range(df_PER.index.min(), df_PER.index.max()), method='ffill')
    # Enlever les PER négatifs

    df_TotalAssets.set_index("Unnamed: 0", inplace=True)
    df_TotalAssets.index.name = None
    df_TotalAssets.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_TotalAssets.dropna(axis=1, how='all', inplace=True)
    df_TotalAssets.index = pd.to_datetime(df_TotalAssets.index)

    df_TotalRevenue.set_index("Unnamed: 0", inplace=True)
    df_TotalRevenue.index.name = None
    df_TotalRevenue.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_TotalRevenue.dropna(axis=1, how='all', inplace=True)
    df_TotalRevenue.index = pd.to_datetime(df_TotalRevenue.index)

    df_stockPrices.set_index("Unnamed: 0", inplace=True)
    df_stockPrices.index.name = None
    df_stockPrices.replace([np.inf, -np.inf], np.nan, inplace=True)
    df_stockPrices.dropna(axis=1, how='all', inplace=True)
    df_stockPrices.index = pd.to_datetime(df_stockPrices.index)

    return df_MarketCap, df_PER_reindex, df_TotalAssets, df_TotalRevenue, df_stockPrices, dic_sectors

# We keep only the tickers for which we have data for everything => seulement pour clustering
# tickers = set.intersection(set(df_MarketCap.columns), set(df_PER.columns), set(df_TotalAssets.columns), set(df_TotalRevenue.columns), set(dic_sectors.keys()))