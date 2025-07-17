import sys
import os

# Ajoute le dossier racine du projet au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_loading import load_data
from src.preprocessing import clean_data
from src.strategies.strategy_baseline import strat_fixed_treshold
from src.strategies.strategy_historical import historical_PER_strat
from src.strategies.strategy_sector import strat_sector_PER
from src.strategies.strategy_distance_matrix_clustering import strategy_distance_matrix_clustering
from src.strategies.strategy_cluster import strat_cluster_K_means

df_MarketCap, df_PER, df_TotalAssets, df_TotalRevenue, df_stockPrices, dic_sectors = load_data()
df_MarketCap, df_PER, df_TotalAssets, df_TotalRevenue, df_stockPrices, dic_sectors = clean_data(df_MarketCap, df_PER, df_TotalAssets, df_TotalRevenue, df_stockPrices, dic_sectors)

# Nombre d'actions qu'on peut s'acheter à chaque date avec 1000$
num_stocks_available = 1000 // df_stockPrices

# strat_fixed_treshold(df_PER, num_stocks_available)
# historical_PER_strat(df_PER, num_stocks_available)
# strat_sector_PER(df_PER, dic_sectors, num_stocks_available)
# strategy_distance_matrix_clustering(df_MarketCap, df_TotalAssets, df_TotalRevenue, df_PER, dic_sectors, num_stocks_available)
strat_cluster_K_means(df_TotalRevenue, df_TotalAssets, df_MarketCap, df_PER, dic_sectors, num_stocks_available)