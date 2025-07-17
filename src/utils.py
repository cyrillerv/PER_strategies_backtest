import numpy as np

def create_df_input(df_prise_position, num_stocks_available) :
    """Fonction qui transforme le df de prise de positn en un df d'input pour ma focntin de backtesting."""
    assert {"noPos", "long", "short", "cover_short", "close_long"} - set(df_prise_position.values.flatten()) == set(), "Vous devez rentrer un df qui contient uniquement ces valeurs là {'nada', 'long', 'short', 'cover_short', 'close_long'}"

    # Lorsqu'on prend position, on regarde pour combien d'actions (on part du principe qu'on met max 1000$ par transaction)
    df_prise_position_int = ((df_prise_position == "long").astype(int) - (df_prise_position == "short").astype(int)).replace(0, np.nan)
    df_volume_action_prise_pos = df_prise_position_int * num_stocks_available.reindex(df_prise_position_int.index, method='ffill')
    df_volume_action_prise_pos.dropna(how='all', axis=1, inplace=True)

    # Pour chaque clôture de position, on regarde ça concerne combien d'actions
    df_close_position_int = ((df_prise_position == "cover_short").astype(int) - (df_prise_position == "close_long").astype(int)).replace(0, np.nan)
    df_volume_action_close_pos = df_close_position_int * df_volume_action_prise_pos.ffill()

    # On combine dans le même df les volumes d'open position et de close position
    df_all_transactions = (df_volume_action_close_pos.fillna(0) + df_volume_action_prise_pos.fillna(0)).replace(0, np.nan)

    # On crée le df avec une ligne par transaction avec le ticker dans la colonne Symbol et la date dans la colonne Date
    df_input = df_all_transactions.reset_index().melt(id_vars=['index'], value_vars=df_all_transactions.columns, var_name='Symbol', value_name='valeur').replace(0, np.nan).dropna(subset=['valeur'])
    df_input.rename(columns={"index":"Date"}, inplace=True)
    df_input["Type"] = np.where(df_input['valeur'] > 0, "Buy", "Sell")
    df_input["Volume"] = df_input["valeur"].abs()
    df_input.drop(columns=["valeur"], inplace=True)
    df_input.reset_index(drop=True, inplace=True)
    return df_input