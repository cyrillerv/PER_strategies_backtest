import numpy as np
import pandas as pd

# TODO: enlever les valeurs négatives du df PER
#     # TODO: mettre ça en preprocessing
#     # 3. Si c'est le PER, on filtre les valeurs aberrantes
#     if field.lower() == 'per':
#         melted = melted[(melted[field] > 0) & (melted[field] < 80)].copy()

def clean_data(dic_input) :
    dic_output = {}
    for field in dic_input :
        if type(dic_input[field]) == dict :
            dic_output[field] = dic_input[field]
            continue
        else : 
            df = dic_input[field].copy()
            df.set_index("Unnamed: 0", inplace=True)
            df.index.name = None
            df.replace([np.inf, -np.inf], np.nan, inplace=True)
            df.dropna(axis=1, how='all', inplace=True)
            df.index = pd.to_datetime(df.index)
            df.sort_index(inplace=True)
            df_reindexed = df.reindex(pd.date_range(df.index.min(), df.index.max()), method='ffill')
            df_reindexed.ffill(inplace=True)   
        if field == "Factors":
            dic_factor_name = {
                'SPY': 'S&P 500',
                'IWM': 'Russell 2000',
                'VTV': 'Value',
                'VUG': 'Growth',
                'MTUM': 'Momentum',
                'USMV': 'Minimum Volatility',
                'QUAL': 'Quality',
                'VYM': 'High Dividend Yield',
                'SPHQ': 'S&P 500 Quality',
                'VLUE': 'Value',
                'PDP': 'Momentum'
            }        
            df_reindexed.columns = df_reindexed.columns.map(lambda col: dic_factor_name.get(col, col))

        dic_output[field] = df_reindexed 

    return dic_output


# We keep only the tickers for which we have data for everything => seulement pour clustering
# tickers = set.intersection(set(df_MarketCap.columns), set(df_PER.columns), set(df_TotalAssets.columns), set(df_TotalRevenue.columns), set(dic_sectors.keys()))