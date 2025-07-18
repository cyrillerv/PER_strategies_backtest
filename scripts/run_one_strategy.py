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

strat = strat_fixed_treshold

dic_strat_data = {
    strat_fixed_treshold : ["PER", "StockPrices"],
    historical_PER_strat : ["PER", "StockPrices"],
    strat_sector_PER : ["PER", "StockPrices"],
    strategy_distance_matrix_clustering : ['MarketCap', "TotalAssets", "TotalRevenue", "PER", "Sectors", "StockPrices"],
    strat_cluster_K_means : ['MarketCap', "TotalAssets", "TotalRevenue", "PER", "Sectors", "StockPrices"]
}

fields = list(dic_strat_data[strat])
dic_results = load_data(fields)
dic_results = clean_data(dic_results)
num_stocks_available = 1000 // dic_results['StockPrices']

result = strat(dic_results, num_stocks_available)


