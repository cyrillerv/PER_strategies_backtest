import sys
import os
import json
# Ajoute le dossier racine du projet au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_loading import load_data
from src.preprocessing import clean_data
from src.strategies.strategy_fixed_threshold import strat_fixed_treshold
from src.strategies.strategy_historical import historical_PER_strat
from src.strategies.strategy_sector import strat_sector_PER
from src.strategies.strategy_distance_matrix_clustering import strategy_distance_matrix_clustering
from src.strategies.strategy_cluster import strat_cluster_K_means

# We load our parameters from our config.json file
with open('config.json', 'r') as f:
    config = json.load(f)
rebalancing_dates = config["rebalancing_dates"]
money_per_transaction = config["money_per_transaction"]

strat = strategy_distance_matrix_clustering

dic_strat_data = {
    strat_fixed_treshold : ["PER", "StockPrices"],
    historical_PER_strat : ["PER", "StockPrices"],
    strat_sector_PER : ["PER", "StockPrices"],
    strat_cluster_K_means : ['MarketCap', "TotalAssets", "TotalRevenue", "PER", "Sectors", "StockPrices"],
    strategy_distance_matrix_clustering : ['MarketCap', "TotalAssets", "TotalRevenue", "PER", "Sectors", "StockPrices"]    
}

fields = list(dic_strat_data[strat])
dic_results = load_data(fields)
dic_results = clean_data(dic_results)
num_stocks_available = money_per_transaction // dic_results['StockPrices']

dic_args = {
    strat_fixed_treshold : (dic_results, num_stocks_available),
    historical_PER_strat : (dic_results, num_stocks_available),
    strat_sector_PER : (dic_results, num_stocks_available),
    strat_cluster_K_means : (dic_results, num_stocks_available),
    strategy_distance_matrix_clustering : (dic_results, num_stocks_available)
}

args = dic_args[strat]
result = strat(*args)


