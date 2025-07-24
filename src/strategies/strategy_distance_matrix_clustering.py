import pandas as pd
import numpy as np
from tqdm import tqdm
tqdm.pandas()
from functools import partial

from src.utils.utils_clustering import *


def strategy_distance_matrix_clustering(dic_inputs, num_stocks_available, rebalancing_dates) :

    df_MarketCap, df_TotalAssets, df_TotalRevenue, df_PER, dic_sectors = tuple(dic_inputs[field] for field in ["MarketCap", "TotalAssets", "TotalRevenue", "PER", "Sectors"])

    # On concatène toutes les df en un seul
    concat_data = pd.concat([df_MarketCap, df_TotalAssets, df_TotalRevenue], axis=1, keys=['MarketCap', 'TotalAssets', 'TotalRevenue'])
    concat_data.ffill(inplace=True)
    
    # Si on veut recalculer les clusters à chaque fois => on commente la ligne d'en dessous.
    concat_data = concat_data.loc[concat_data.index.isin([pd.to_datetime(date) for date in rebalancing_dates])]

    # On crée le df de penalty pour le field 'sector'
    df_sector = create_df_sector_penalty(dic_sectors)

    # On crée une fontion partielle pour pouvoir donner deux arguments en input de notre fonction calc_cluster_distance_matrix
    func = partial(calc_cluster_distance_matrix, df_sector=df_sector)
    # Pour chaque date, on crée les clusters à partir de notre matrice de distance
    y = concat_data.progress_apply(func, axis=1)

    # On formatte le résultat pour avoir un df propre
    df_all_cluster_distance_matrix = pd.concat(y.to_list())
    df_all_cluster_distance_matrix.index.name = "date"
    df_all_cluster_distance_matrix.reset_index(inplace=True)



    # On ajoute le PER au df
    reindexed_PER = df_PER.copy().reindex(
        list(set(df_all_cluster_distance_matrix["date"]))
        , method='ffill'
        )
    df_all_cluster_distance_matrix["PER"] = df_all_cluster_distance_matrix.progress_apply(
        lambda row: reindexed_PER.loc[row["date"], 
                                      row["Ticker"]] if row["date"] in reindexed_PER.index and row["Ticker"] in reindexed_PER.columns else np.nan
                                      , axis=1
                                      )
    df_all_cluster_distance_matrix.dropna(inplace=True)

    nb_min_ticker_per_cluster = 5
    index_ok_cluster = df_all_cluster_distance_matrix.groupby(["date", "Cluster"]).count()['Ticker'][df_all_cluster_distance_matrix.groupby(["date", "Cluster"]).count()['Ticker'] > nb_min_ticker_per_cluster].index
    df_all_cluster_distance_matrix = df_all_cluster_distance_matrix.set_index(["date", "Cluster"])[df_all_cluster_distance_matrix.set_index(["date", "Cluster"]).index.isin(index_ok_cluster)].reset_index()
    # Ensuite pour chaque entreprise on va acheter ou vendre en fonction du PER des autres entreprises dans le cluster
    df_prise_positions_distance_matrix = interpret_signals(df_all_cluster_distance_matrix, 0.2, num_stocks_available)
    return df_prise_positions_distance_matrix

