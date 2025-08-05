import pandas as pd

from src.utils.utils_clustering import prepare_field_data, calculate_cluster, interpret_signals

def strat_cluster_K_means(dic_main, dic_variables, num_stocks_available) :
    df_input = pd.DataFrame()
    for field in dic_variables :
        if "sector" in field.lower() and type(dic_variables[field]) == dict :
            dic_sectors = dic_variables[field]
            continue
        df_field = prepare_field_data(dic_variables[field], field)
        df_input = pd.concat([df_input, df_field], axis=1)

    # TODO: ajouter le PER au df général après avoir calculer les clusters ?
    df_PER = prepare_field_data(dic_main["PER"], "PER")
    df_input = pd.concat([df_input, df_PER], axis=1)

    df_input.reset_index(inplace=True)

    label_sector = {i:k for k, i in enumerate(list(set(dic_sectors.values())))}
    df_input["Sectors"] = df_input['Ticker'].map(dic_sectors).map(label_sector)
    df_input.dropna(inplace=True) # Implique qu'il faut qu'il y ait pas de trous de données  

    df_clustered = calculate_cluster(df_input)

    df_prise_position_clustering = interpret_signals(df_clustered, 0.2, num_stocks_available)
    return df_prise_position_clustering