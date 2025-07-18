import pandas as pd
import numpy as np

from src.utils.utils_simple_strat import create_df_input

def strat_sector_PER(dic_inputs, num_stocks_available) :
    df_PER, dic_sectors = tuple(dic_inputs[field] for field in ["PER", "Sectors"])

    df_PER_reindex = df_PER.copy()

    df_PER_reindex = df_PER_reindex[[i for i in df_PER_reindex.columns if i in dic_sectors.keys()]]

    # Création d'une liste de tuples pour les secteurs associés aux tickers
    sectors = [(dic_sectors[ticker], ticker) for ticker in df_PER_reindex.columns]

    # On ajoute les secteurs aux colonnes du df
    df_PER_reindex.columns = pd.MultiIndex.from_tuples(sectors, names=['Sector', 'Ticker'])

    # On calcule la moyenne des PER par secteur
    df_PER_per_sector = df_PER_reindex.groupby(level='Sector', axis=1).mean()
    df_PER_per_sector


    # On reindex pour que les deux df aient les même colonnes
    df_PER_per_sector_reindex = df_PER_per_sector.reindex(df_PER_reindex.columns.get_level_values(0), axis=1)
    df_PER_per_sector_reindex.columns = df_PER_reindex.columns

    # Calcul de la stdev à chaque date 
    stdev_PER_sector = df_PER_per_sector_reindex.shift(1).expanding().std()
    # Calcul des treshold de prise de position
    treshold_overvalued = df_PER_per_sector_reindex + stdev_PER_sector
    treshold_undervalued = df_PER_per_sector_reindex - stdev_PER_sector



    # Mise en forme du df de prise de position

    # Conditions
    conditions = [
        (df_PER_reindex > treshold_overvalued) & ((df_PER_reindex.shift(1) <= treshold_overvalued.shift(1)) | (df_PER_reindex.shift(1).isna())),  # Short
        (df_PER_reindex <= treshold_overvalued) & ((df_PER_reindex.shift(1) > treshold_overvalued.shift(1)) | (df_PER_reindex.shift(1).isna())),  # Cover Short
        (df_PER_reindex < treshold_undervalued) & ((df_PER_reindex.shift(1) >= treshold_undervalued.shift(1)) | (df_PER_reindex.shift(1).isna())),  # Long
        (df_PER_reindex >= treshold_undervalued) & ((df_PER_reindex.shift(1) < treshold_undervalued.shift(1)) | (df_PER_reindex.shift(1).isna()))  # Close Long
    ]

    # Valeurs correspondantes
    choices = ["short", "cover_short", "long", "close_long"]

    # Application des conditions avec np.select()
    data_prise_pos = np.select(conditions, choices, default="noPos")


    df_prise_position = pd.DataFrame(data_prise_pos, index=df_PER_reindex.index, columns=df_PER_reindex.columns)
    df_prise_position.columns = df_prise_position.columns.get_level_values(1)
    df_prise_position


    df_input_bt_Sector = create_df_input(df_prise_position, num_stocks_available)
    return df_input_bt_Sector