import sys
import os
import pandas as pd 
import json
from backtesting.core import BacktestEngine # Librairy I created available on GitHub


# Ajoute le dossier racine du projet au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_loading import load_data
from src.preprocessing import clean_data
from src.strategies.strategy_fixed_threshold import strat_fixed_treshold
from src.strategies.strategy_historical import historical_PER_strat
from src.strategies.strategy_sector import strat_sector_PER
from src.strategies.strategy_distance_matrix_clustering import strategy_distance_matrix_clustering
from src.strategies.strategy_cluster import strat_cluster_K_means
from src.utils.compute_results import *

# We load our parameters from our config.json file
with open('config.json', 'r') as f:
    config = json.load(f)
rebalancing_dates = config['rebalancing_dates']
fields = config["fields"]
money_per_transaction = config["money_per_transaction"]

print("Loading and prepararing data...")
dic_results = load_data(fields)
dic_results = clean_data(dic_results)
# Nombre d'actions qu'on peut s'acheter à chaque date avec x$
num_stocks_available = money_per_transaction // dic_results['StockPrices']

print("Launching fixedThreshold...")
order_table_fixed_threshold_strat = strat_fixed_treshold(dic_results, num_stocks_available)
print("Launching histoStrat...")
order_table_historical_strat = historical_PER_strat(dic_results, num_stocks_available)
print("Launching sectorStrat...")
order_table_sector_strat = strat_sector_PER(dic_results, num_stocks_available)
print("Launching clustering...")
order_table_clustering_strat = strat_cluster_K_means(dic_results, num_stocks_available)
print("Launching distanceMatrix...")
order_table_distance_matrix_strat = strategy_distance_matrix_clustering(dic_results, num_stocks_available, rebalancing_dates)

dic_launch_bt = {
    "fixedThreshold": order_table_fixed_threshold_strat,
    "histoStrat": order_table_historical_strat,
    "sectorStrat": order_table_sector_strat,
    "clustering": order_table_clustering_strat,
    "distanceMatrix": order_table_distance_matrix_strat,
}

dic_results_bt = {}
dic_strat_pnl = {}
dic_strat_portfolio_returns = {}
for nameStrat, df_strat in dic_launch_bt.items() :
    print(f"Starting {nameStrat} bt...")
    engine = BacktestEngine(df_strat.fillna(0), dic_results["StockPrices"])
    engine.run()
    dic_results_bt[nameStrat] = engine.summary()
    dic_strat_pnl[nameStrat] = engine.cumulative_pnl_portfolio
    dic_strat_portfolio_returns[nameStrat] = engine.portfolio_returns

compute_comparison_table(dic_results_bt)
plot_pnl_graph(dic_strat_pnl)
plot_density_returns_distrib(dic_strat_portfolio_returns)
