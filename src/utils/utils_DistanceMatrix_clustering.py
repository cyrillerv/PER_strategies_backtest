import pandas as pd
import numpy as np
import scipy.cluster.hierarchy as sch
from scipy.cluster.hierarchy import fcluster
from k_means_constrained import KMeansConstrained
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm


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
    # Pour chaque field, on regarde le pourcentage de NaN
    perc_nan_per_field = row.notna().groupby(level=0).sum() / row.groupby(level=0).size()
    # On ne garde que les fields pour lesquels au moins 80% des tickers ont une valeur
    fields_to_drop = perc_nan_per_field[perc_nan_per_field <= 0.8].index
    row.drop(fields_to_drop, level=0, inplace=True)
    row.dropna(inplace=True)

    # On regarde le nombre de fields restants
    nb_fields_total = len(set(row.index.get_level_values(0)))
    # On regarde si les tickers ont une data pour chaque field
    nb_fields_per_ticker = row.index.get_level_values(1).value_counts()
    tickers_to_keep = list(nb_fields_per_ticker.loc[nb_fields_per_ticker == nb_fields_total].index)
    # On s'assure qu'on a au moins 50 tickers avec des données complètes pour cette date
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