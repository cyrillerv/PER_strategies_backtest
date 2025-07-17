import pandas as pd
import numpy as np

from src.utils.utils_simple_strat import create_df_input

def historical_PER_strat(df_PER, num_stocks_available) :

    # Calcul du PER historique sur les deux dernières années
    historical_PER = df_PER.rolling(window=2*365).mean()
    # Calcul de la stdev à chaque date 
    stdev_historical_PER = historical_PER.shift(1).expanding().std()
    # Calcul des treshold de prise de position
    treshold_overvalued = historical_PER + stdev_historical_PER
    treshold_undervalued = historical_PER - stdev_historical_PER

    # Mise en forme du df de prise de position

    # Conditions
    conditions = [
        (df_PER > treshold_overvalued) & ((df_PER.shift(1) <= treshold_overvalued.shift(1)) | (df_PER.shift(1).isna())),  # Short
        (df_PER <= treshold_overvalued) & ((df_PER.shift(1) > treshold_overvalued.shift(1)) | (df_PER.shift(1).isna())),  # Cover Short
        (df_PER < treshold_undervalued) & ((df_PER.shift(1) >= treshold_undervalued.shift(1)) | (df_PER.shift(1).isna())),  # Long
        (df_PER >= treshold_undervalued) & ((df_PER.shift(1) < treshold_undervalued.shift(1)) | (df_PER.shift(1).isna()))  # Close Long
    ]

    # Valeurs correspondantes
    choices = ["short", "cover_short", "long", "close_long"]

    # Application des conditions avec np.select()
    data_prise_pos = np.select(conditions, choices, default="noPos")


    df_prise_position = pd.DataFrame(data_prise_pos, index=df_PER.index, columns=df_PER.columns)


    df_input_bt_histo = create_df_input(df_prise_position, num_stocks_available)
    return df_input_bt_histo