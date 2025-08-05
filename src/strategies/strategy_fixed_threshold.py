# Pour cette strategy on applique un seuil fixe arbitraire: si on est en dessous on achète, sinon on vend
import numpy as np
import pandas as pd
from src.utils.utils_simple_strat import create_df_input

def strat_fixed_treshold(dic_main, num_stocks_available) :
    df_PER = dic_main["PER"]
    # Conditions
    conditions = [
        (df_PER > 25) & ((df_PER.shift(1) <= 25) | (df_PER.shift(1).isna())),  # Short
        (df_PER <= 25) & ((df_PER.shift(1) > 25) | (df_PER.shift(1).isna())),  # Cover Short
        (df_PER < 15) & ((df_PER.shift(1) >= 15) | (df_PER.shift(1).isna())),  # Long
        (df_PER >= 15) & ((df_PER.shift(1) < 15) | (df_PER.shift(1).isna()))   # Close Long
    ]

    # Valeurs correspondantes
    choices = ["short", "cover_short", "long", "close_long"]

    # Application des conditions avec np.select()
    data_prise_pos = np.select(conditions, choices, default="noPos")

    # Création du DataFrame
    df_prise_position = pd.DataFrame(data_prise_pos, index=df_PER.index, columns=df_PER.columns)

    df_input_bt_const = create_df_input(df_prise_position, num_stocks_available)
    return df_input_bt_const