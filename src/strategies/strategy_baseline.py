# Pour cette strategy on applique un seuil fixe arbitraire: si on est en dessous on achète, sinon on vend
import numpy as np
import pandas as pd

def strat_fixed_treshold(df_PER: pd.DataFrame, threshold: int) -> pd.DataFrame:
    """
    On achète si on est en dessous du threshold et on vend sinon.
    """
    signal = np.where(
        (df_PER < threshold) & (~df_PER.isna()),
        1,
        np.where(
            (df_PER > threshold) & (~df_PER.isna()),
            -1,
            np.nan
        )
    )

    df_signal = pd.DataFrame(signal, df_PER.index, df_PER.columns)
    return df_signal