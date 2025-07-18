import sys
import os

# Ajoute le dossier racine du projet au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_loading import load_data
from src.preprocessing import clean_data
from src.strategies.strategy_fixed_threshold import strat_fixed_treshold
from src.strategies.strategy_historical import historical_PER_strat
from src.strategies.strategy_sector import strat_sector_PER
from src.strategies.strategy_distance_matrix_clustering import strategy_distance_matrix_clustering
from src.strategies.strategy_cluster import strat_cluster_K_means

fields = ["MarketCap", "PER", "TotalAssets", "TotalRevenue", "StockPrices", "Sectors"]
dic_results = load_data(fields)
dic_results = clean_data(dic_results)
# df_MarketCap, df_PER, df_TotalAssets, df_TotalRevenue, df_stockPrices, dic_sectors = tuple(dic_results[field] for field in fields)
# Nombre d'actions qu'on peut s'acheter à chaque date avec 1000$
num_stocks_available = 1000 // dic_results['StockPrices']

order_table_fixed_threshold_strat = strat_fixed_treshold(dic_results, num_stocks_available)
order_table_historical_strat = historical_PER_strat(dic_results, num_stocks_available)
order_table_sector_strat = strat_sector_PER(dic_results, num_stocks_available)
order_table_distance_matrix_strat = strategy_distance_matrix_clustering(dic_results, num_stocks_available)
order_table_clustering_strat = strat_cluster_K_means(dic_results, num_stocks_available)