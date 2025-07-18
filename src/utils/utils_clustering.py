import pandas as pd
import numpy as np
import scipy.cluster.hierarchy as sch
from scipy.cluster.hierarchy import fcluster

def create_df_sector_penalty(dic_sectors) :
    # Créer une série à partir du dictionnaire des secteurs
    sector_series = pd.Series(dic_sectors)

    # Créer une matrice de comparaison en utilisant la vectorisation
    sector_matrix = sector_series.values.reshape(-1, 1) == sector_series.values

    # Créer un DataFrame avec les tickers en index et en colonnes
    df_sector = pd.DataFrame(sector_matrix, index=sector_series.index, columns=sector_series.index)

    # Convertir en 1/0
    df_sector = (~df_sector).astype(int)

    # Afficher le DataFrame résultant
    return df_sector

def calc_cluster_distance_matrix(row, df_sector) :
    """
    Fonction pour calculer la distance entre deux tickers à une date donnée à partir de leur secteur et des field renseigné dans row.
    En gros, on ajoute des pénalités: si pas le même secteur alors +1 de pénalités, si marketcap trop éloignée, plus 1 de pénalité, si c'est la même, 0 de pénalité
    On a fixé arbitrairement à 50 le nombre minimal de tickers (avec toutes les données) qu'il faut à une date donnée pour qu'on calcule les clusters.
    """
    row = row.dropna()
    # On regarde si on a une valeur pour chaque field
    nb_fields_per_ticker = row.index.get_level_values(1).value_counts()
    tickers_to_keep = list(nb_fields_per_ticker.loc[nb_fields_per_ticker == 3].index)
    if row.empty or len(tickers_to_keep) < 50 :
        return pd.DataFrame()
    
    # On filtre pour ne garder que les tickers qui ont des données pour toutes les dates.
    row = row.loc[row.index.get_level_values(1).isin(tickers_to_keep)]
    
    
    distance_matrix = df_sector.copy()
    for field in list(set(row.index.get_level_values(0))) :
        field_row = row.loc[field]
        field_std_row = (field_row - field_row.mean()) / field_row.std()
        # Créer une série à partir du dictionnaire des secteurs
        field_series = pd.Series(field_std_row.to_dict())

        # Créer une matrice de comparaison en utilisant la vectorisation
        field_matrix = abs(field_series.values.reshape(-1, 1) - field_series.values)

        # Créer un DataFrame avec les tickers en index et en colonnes
        field_distance = pd.DataFrame(field_matrix, index=field_series.index, columns=field_series.index)

        # On scale les distances pour qu'elles soient comprises entre 0 et 1 (pénalité pour la marketCap)
        scaled_distance_field = ((field_distance - field_distance.min()) / (field_distance.max() - field_distance.min()))

        distance_matrix += scaled_distance_field



    distance_matrix.dropna(how='all', inplace=True)
    distance_matrix.dropna(how='all', axis=1, inplace=True)

    # Appliquer le clustering hiérarchique avec la méthode 'ward'
    linkage_matrix = sch.linkage(distance_matrix, method='ward')

    # Déterminer le nombre de clusters que tu veux, par exemple 2
    clusters = fcluster(linkage_matrix, t=12, criterion='maxclust')


    # Ajouter les résultats du clustering au DataFrame des tickers
    df_clusters = pd.DataFrame({'Ticker': distance_matrix.index, 'Cluster': clusters}, index=[row.name for i in range(len(clusters))])
    return df_clusters


def interpret_signals1(df_all_cluster_distance_matrix, nb_min_ticker_per_cluster, tolerance_around_mean, num_stocks_available):
    # Last function
    # On enlève les cluster pour lesquels il n'y a qu'un seul ticker à cette date là
    

    dic_test = df_all_cluster_distance_matrix.groupby(["date", "Cluster"])["PER"].mean().to_frame().unstack(level=0).T.droplevel(0).to_dict()
    df_all_cluster_distance_matrix["Cluster_mean"] = df_all_cluster_distance_matrix.apply(lambda row: dic_test[row["Cluster"]][row['date']], axis=1)
    df_all_cluster_distance_matrix

    
    df_all_cluster_distance_matrix["Position"] = np.where(df_all_cluster_distance_matrix["PER"] < ((1-tolerance_around_mean)*df_all_cluster_distance_matrix["Cluster_mean"]), 1,
            np.where(
                df_all_cluster_distance_matrix["PER"] > ((1+tolerance_around_mean)*df_all_cluster_distance_matrix["Cluster_mean"]), -1, 0
            ))
    df_all_cluster_distance_matrix

    df_positions = df_all_cluster_distance_matrix.pivot_table("Position", "date", "Ticker")
    # On rajoute une ligne vide pour que lorsqu'on fasse le .diff() pour détecter les prise de positon, les positions prises le premier jour soient quand même détectée
    df_positions = pd.concat([df_positions, pd.DataFrame(index=[df_positions.index.min() - pd.Timedelta(days=1)])])
    df_positions.sort_index(inplace=True)

    df_prise_positions = df_positions.ffill().fillna(0).diff().replace(0, np.nan)
    df_prise_positions_distance_matrix = df_prise_positions.reset_index().melt(id_vars=['index'], var_name='Ticker', value_name='Value').dropna().copy()

    num_stocks_available_clustering = num_stocks_available.reindex(list(set(df_prise_positions_distance_matrix["index"])), method='ffill')
    df_prise_positions_distance_matrix["Volume"] = df_prise_positions_distance_matrix.apply(
        lambda row: num_stocks_available_clustering.loc[row['index'], row['Ticker']] if row['Ticker'] in num_stocks_available.columns else np.nan,
        axis=1)
    df_prise_positions_distance_matrix["Type"] = np.where(df_prise_positions_distance_matrix["Value"] == 1, "Buy", "Sell")
    df_prise_positions_distance_matrix.rename(columns={"index":"Date", "Ticker":"Symbol"}, inplace=True)
    df_prise_positions_distance_matrix.drop(columns=["Value"], inplace=True)
    return df_prise_positions_distance_matrix


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





def prepare_field_data(df: pd.DataFrame, field: str) -> pd.DataFrame:
    """
    Transforme un DataFrame large en format long indexé par (date, Ticker).
    
    Paramètres :
        df (pd.DataFrame) : DataFrame avec dates en index et tickers en colonnes
        field (str) : Nom du champ cible ('PER', 'MarketCap', etc.)

    Retourne :
        pd.DataFrame : DataFrame indexé par (date, Ticker), avec une seule colonne : field
    """
    # 1. Remettre la date en colonne
    melted = df.reset_index().melt(
        id_vars=['index'], var_name='Ticker', value_name=field
    ).dropna()

    # 2. Renommer 'index' en 'date'
    melted.rename(columns={'index': 'date'}, inplace=True)

    # TODO: mettre ça en preprocessing
    # 3. Si c'est le PER, on filtre les valeurs aberrantes
    if field.lower() == 'per':
        melted = melted[(melted[field] > 0) & (melted[field] < 80)].copy()

    # 4. Supprimer les doublons
    melted.drop_duplicates(['Ticker', field], keep='first', inplace=True)

    # 5. Mettre l'index sur (date, Ticker)
    melted.set_index(['date', 'Ticker'], inplace=True)

    return melted


import pandas as pd
import numpy as np
from k_means_constrained import KMeansConstrained
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm

def calculate_cluster(df_input) :
    # Convertir la colonne Date en format datetime
    df_input['date'] = pd.to_datetime(df_input['date'])

    # Liste pour stocker les résultats de clustering
    results = []

    # Appliquer le clustering pour chaque date
    for date, group in tqdm(df_input.groupby('date')):
        X = group[['MarketCap', 'TotalRevenue', 'TotalAssets', 'Sector']].values  # Features utilisées pour le clustering
        # print(X.shape[1])
        if X.shape[0] < 20 :
            continue
        
        # Standardisation des données
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Déterminer le nombre de clusters initial
        n_clusters = max(1, len(group) // 20)  # On ajuste dynamiquement le nombre de clusters
        
        # Ajuster `n_clusters` si nécessaire
        while n_clusters * 20 < len(group):  
            n_clusters += 1  # Augmenter le nombre de clusters pour éviter l'erreur
        
        # Clustering avec contrainte (max 20 tickers par cluster)
        kmeans = KMeansConstrained(
            n_clusters=n_clusters,  # Nombre de clusters ajusté
            size_max=20,   # Contrainte : max 20 valeurs par cluster
            random_state=42
        )
        
        clusters = kmeans.fit_predict(X_scaled)
        
        # Ajouter les clusters au DataFrame
        group['Cluster'] = clusters
        
        # Stocker les résultats
        results.append(group)

    # Concaténer tous les résultats en un seul DataFrame
    df_clustered = pd.concat(results)
    return df_clustered