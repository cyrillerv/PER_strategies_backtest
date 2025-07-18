import pandas as pd

from src.utils.utils_clustering import prepare_field_data, calculate_cluster, interpret_signals

def strat_cluster_K_means(dic_inputs, num_stocks_available) :
    df_MarketCap, df_TotalAssets, df_TotalRevenue, df_PER, dic_sectors = tuple(dic_inputs[field] for field in ["MarketCap", "TotalAssets", "TotalRevenue", "PER", "Sectors"])
    
    # TODO: passer ces lignes ci dessous dans le fichier preprocessing.py
    df_TotalRevenue.ffill(inplace=True)
    df_TotalAssets.ffill(inplace=True)
    df_MarketCap.ffill(inplace=True)
    df_PER.ffill(inplace=True)
    # On fusionne toutes les infos en un seul df
    melted_MarketCap = prepare_field_data(df_MarketCap, 'MarketCap')
    melted_TotalRevenue = prepare_field_data(df_TotalRevenue, 'TotalRevenue')
    melted_TotalAssets = prepare_field_data(df_TotalAssets, 'TotalAssets')
    melted_PER = prepare_field_data(df_PER, 'PER')

    df_input = pd.concat([melted_MarketCap, melted_TotalRevenue, melted_TotalAssets, melted_PER], axis=1).dropna()
    df_input.reset_index(inplace=True)
    print("df_input created")

    label_sector = {i:k for k, i in enumerate(list(set(dic_sectors.values())))}
    df_input["Sector"] = df_input['Ticker'].map(dic_sectors).map(label_sector)
    df_input.dropna(inplace=True)

    print("Cluster calc")
    df_clustered = calculate_cluster(df_input)
    print(df_clustered)

    print("Interpreting signals")
    df_prise_position_clustering = interpret_signals(df_clustered, 0.2, num_stocks_available)
    return df_prise_position_clustering