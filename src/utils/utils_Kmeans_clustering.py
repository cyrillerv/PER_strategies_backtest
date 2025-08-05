import pandas as pd
import numpy as np
import scipy.cluster.hierarchy as sch
from scipy.cluster.hierarchy import fcluster
from k_means_constrained import KMeansConstrained
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm


def create_sector_label(dic_sectors, concat_data) :
    # Création d’un DataFrame à partir du dictionnaire
    tickers = list(dic_sectors.keys())
    sectors = list(dic_sectors.values())

    # Créer un DataFrame d'une ligne avec colonnes multi-indexées
    columns = pd.MultiIndex.from_product([["Sectors"], tickers])
    row = pd.DataFrame([sectors], columns=columns)

    # Répéter cette ligne pour chaque index de concat_data
    df_sectors = pd.concat([row]*len(concat_data), ignore_index=True)
    df_sectors.index = concat_data.index

    # Étape 2 : créer un dictionnaire de labellisation
    unique_sectors = sorted(set(dic_sectors.values()))
    label_sector = {sector: idx for idx, sector in enumerate(unique_sectors)}

    # Étape 3 : appliquer le mapping des labels aux valeurs du DataFrame
    df_sectors_labeled = df_sectors.applymap(label_sector.get)

    return df_sectors_labeled



def calc_cluster_kmeans(row) :
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

    X = row.unstack(level=0)

    # Standardisation des données
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Déterminer le nombre de clusters initial
    n_clusters = max(1, len(tickers_to_keep) // 20)  # On ajuste dynamiquement le nombre de clusters
    
    # Ajuster `n_clusters` si nécessaire
    while n_clusters * 20 < len(tickers_to_keep):  
        n_clusters += 1  # Augmenter le nombre de clusters pour éviter l'erreur
    
    # Clustering avec contrainte (max 20 tickers par cluster)
    kmeans = KMeansConstrained(
        n_clusters=n_clusters,  # Nombre de clusters ajusté
        size_max=20,   # Contrainte : max 20 valeurs par cluster
        random_state=42
    )
    
    clusters = kmeans.fit_predict(X_scaled)

    df_clusters = pd.DataFrame({'Ticker': X.index, 'Cluster': clusters}, index=[row.name for i in range(len(clusters))])

    return df_clusters
