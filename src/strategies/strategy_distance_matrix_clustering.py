import pandas as pd
import numpy as np
from tqdm import tqdm
tqdm.pandas()
from functools import partial

from src.utils.distance_matrix_utils import *




def strategy_distance_matrix_clustering(df_MarketCap, df_TotalAssets, df_TotalRevenue, df_PER, dic_sectors, num_stocks_available) :

    # On concatène toutes les df en un seul
    concat_data = pd.concat([df_MarketCap, df_TotalAssets, df_TotalRevenue], axis=1, keys=['MarketCap', 'TotalAssets', 'TotalRevenue'])
    concat_data.ffill(inplace=True)

    # On crée le df de penalty pour le field 'sector'
    df_sector = create_df_sector_penalty(dic_sectors)
    recalculate_clusters = True
    if recalculate_clusters :
        # On crée une fontion partielle pour pouvoir donner deux arguments en input de notre fonction calc_cluster_distance_matrix
        func = partial(calc_cluster_distance_matrix, df_sector=df_sector)
        # Pour chaque date, on crée les clusters à partir de notre matrice de distance
        y = concat_data.progress_apply(func, axis=1)

        # On formatte le résultat pour avoir un df propre
        df_all_cluster_distance_matrix = pd.concat(y.to_list())
        df_all_cluster_distance_matrix.index.name = "date"
        df_all_cluster_distance_matrix.reset_index(inplace=True)
        # df_all_cluster_distance_matrix.to_excel(r"PER_STRATEGIES_BACKTEST\temp.xlsx")
    else :
        df_all_cluster_distance_matrix = pd.read_excel(r"PER_STRATEGIES_BACKTEST\temp.xlsx")
        df_all_cluster_distance_matrix.drop(columns=["Unnamed: 0"], inplace=True)


    # On ajoute le PER au df
    reindexed_PER = df_PER.reindex(list(set(df_all_cluster_distance_matrix["date"])), method='ffill')
    df_all_cluster_distance_matrix["PER"] = df_all_cluster_distance_matrix.progress_apply(lambda row: reindexed_PER.loc[row["date"], row["Ticker"]] if row["date"] in reindexed_PER.index and row["Ticker"] in reindexed_PER.columns else np.nan, axis=1)
    df_all_cluster_distance_matrix.dropna(inplace=True)

    # Ensuite pour chaque entreprise on va acheter ou vendre en fonction du PER des autres entreprises dans le cluster
    df_prise_positions_distance_matrix = interpret_signals(df_all_cluster_distance_matrix, 5, 0.2, num_stocks_available)
    return df_prise_positions_distance_matrix

