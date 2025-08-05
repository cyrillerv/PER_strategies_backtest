import sys
import os
import json
from backtesting.core import BacktestEngine # Librairy I created available on GitHub

# Ajoute le dossier racine du projet au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_loading import *
from src.preprocessing import clean_data
from src.strategies.strategy_fixed_threshold import strat_fixed_treshold
from src.strategies.strategy_historical import historical_PER_strat
from src.strategies.strategy_sector import strat_sector_PER
from src.strategies.clustering import strategy_distance_matrix_clustering, strat_cluster_K_means

# We load our parameters from our config.json file
with open('config.json', 'r') as f:
    config = json.load(f)
rebalancing_dates = config["rebalancing_dates"]
money_per_transaction = config["money_per_transaction"]

strat = strategy_distance_matrix_clustering

dic_strat_data = {
    strat_fixed_treshold : ["Sectors"], # Sector field is useful to give insights when backtesting even thpugh we won't use it in this strat
    historical_PER_strat : ["Sectors"], # Sector field is useful to give insights when backtesting even thpugh we won't use it in this strat
    strat_sector_PER : ["Sectors"], # Sector field is useful to give insights when backtesting even thpugh we won't use it in this strat
    strat_cluster_K_means : ["all"],
    strategy_distance_matrix_clustering : ["all"]  
}

fields = list(dic_strat_data[strat])
dic_variables = load_variables(fields)
dic_variables = clean_data(dic_variables)
dic_main = load_main_data()
dic_main = clean_data(dic_main)

num_stocks_available = money_per_transaction // dic_main['StockPrices']

dic_args = {
    strat_fixed_treshold : (dic_main, num_stocks_available),
    historical_PER_strat : (dic_main, num_stocks_available),
    strat_sector_PER : (dic_main, dic_variables, num_stocks_available),
    strat_cluster_K_means : (dic_main, dic_variables, num_stocks_available, rebalancing_dates),
    strategy_distance_matrix_clustering : (dic_main, dic_variables, num_stocks_available, rebalancing_dates)
}

args = dic_args[strat]
result = strat(*args)
print(result)
engine = BacktestEngine(result.fillna(0), dic_main["StockPrices"], bench_df_input=dic_main["Factors"], sector_mapping=dic_variables["Sectors"], close_all=True)
engine.run()
print(engine.summary())


