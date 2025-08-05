import pandas as pd
import numpy as np
from tqdm import tqdm
tqdm.pandas()
from functools import partial

# from src.utils.utils_clustering import *
from src.utils.utils_Kmeans_clustering import *
from src.utils.utils_DistanceMatrix_clustering import *

def strat_cluster_K_means(dic_main, dic_variables, num_stocks_available, rebalancing_dates) :
    clustering_type = "Kmeans"
    return strategy_clustering(dic_main, dic_variables, num_stocks_available, rebalancing_dates, clustering_type)

def strategy_distance_matrix_clustering(dic_main, dic_variables, num_stocks_available, rebalancing_dates) :
    clustering_type = "distance_matrix"
    return strategy_clustering(dic_main, dic_variables, num_stocks_available, rebalancing_dates, clustering_type)



def interpret_signals(df_clustered_date_filtered, tolerance_around_mean, num_stocks_available):
    dic_test = df_clustered_date_filtered.groupby(["date", "Cluster"])["PER"].mean().to_frame().unstack(level=0).T.droplevel(0).to_dict()
    df_clustered_date_filtered["Cluster_mean"] = df_clustered_date_filtered.apply(lambda row: dic_test[row["Cluster"]][row['date']], axis=1)
    df_clustered_date_filtered

    tolerance_around_mean = 0.2
    df_clustered_date_filtered["Position"] = np.where(df_clustered_date_filtered["PER"] < ((1-tolerance_around_mean)*df_clustered_date_filtered["Cluster_mean"]), 1,
            np.where(
                df_clustered_date_filtered["PER"] > ((1+tolerance_around_mean)*df_clustered_date_filtered["Cluster_mean"]), -1, 0
            ))
    df_clustered_date_filtered

    df_positions = df_clustered_date_filtered.pivot_table("Position", "date", "Ticker")
    # On rajoute une ligne vide pour que lorsqu'on fasse le .diff() pour détecter les prise de positon, les positions prises le premier jour soient quand même détectée
    df_positions = pd.concat([df_positions, pd.DataFrame(index=[df_positions.index.min() - pd.Timedelta(days=1)])])
    df_positions.sort_index(inplace=True)

    df_prise_positions = df_positions.ffill().fillna(0).diff().replace(0, np.nan)
    df_prise_positions_melted = df_prise_positions.reset_index().melt(id_vars=['index'], var_name='Ticker', value_name='Value').dropna().copy()

    num_stocks_available_clustering = num_stocks_available.reindex(list(set(df_prise_positions_melted["index"])), method='ffill')
    df_prise_positions_melted["Volume"] = df_prise_positions_melted.apply(
        lambda row: num_stocks_available_clustering.loc[row['index'], row['Ticker']] if row['Ticker'] in num_stocks_available.columns else np.nan,
        axis=1)
    df_prise_positions_melted["Type"] = np.where(df_prise_positions_melted["Value"] == 1, "Buy", "Sell")
    df_prise_positions_melted.rename(columns={"index":"Date", "Ticker":"Symbol"}, inplace=True)
    df_prise_positions_melted.drop(columns=["Value"], inplace=True)
    return df_prise_positions_melted



def strategy_clustering(dic_main, dic_variables, num_stocks_available, rebalancing_dates, clustering_type) :
    list_name_df = []
    list_df = []
    for field in dic_variables :
        if "sector" in field.lower() and type(dic_variables[field]) == dict :
            dic_sectors = dic_variables[field]
            continue
        list_df.append(dic_variables[field])
        list_name_df.append(field)
    df_PER = dic_main["PER"].copy()
    
    concat_data = pd.concat(list_df, axis=1, keys=list_name_df)
    concat_data.ffill(inplace=True)
    
    # Si on veut recalculer les clusters à chaque fois => on commente la ligne d'en dessous.
    concat_data = concat_data.loc[concat_data.index.isin([pd.to_datetime(date) for date in rebalancing_dates])]

    if clustering_type == 'distance_matrix' :
        # On crée le df de penalty pour le field 'sector'
        df_sector = create_df_sector_penalty(dic_sectors)
        # On crée une fontion partielle pour pouvoir donner deux arguments en input de notre fonction calc_cluster_distance_matrix
        func = partial(calc_cluster_distance_matrix, df_sector=df_sector)
    elif clustering_type == 'Kmeans' :

        df_sectors_labeled = create_sector_label(dic_sectors, concat_data)
        concat_data = pd.concat([concat_data, df_sectors_labeled], axis=1)
        
        func = calc_cluster_kmeans

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
