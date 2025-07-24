import sys
import os
import pandas as pd 
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

fields = ["MarketCap", "PER", "TotalAssets", "TotalRevenue", "StockPrices", "Sectors"]
print("Loading and prepararing data...")
dic_results = load_data(fields)
dic_results = clean_data(dic_results)
# df_MarketCap, df_PER, df_TotalAssets, df_TotalRevenue, df_stockPrices, dic_sectors = tuple(dic_results[field] for field in fields)
# Nombre d'actions qu'on peut s'acheter à chaque date avec 1000$
num_stocks_available = 1000 // dic_results['StockPrices']

print("Launching fixedThreshold...")
order_table_fixed_threshold_strat = strat_fixed_treshold(dic_results, num_stocks_available)
print("Launching histoStrat...")
order_table_historical_strat = historical_PER_strat(dic_results, num_stocks_available)
print("Launching sectorStrat...")
order_table_sector_strat = strat_sector_PER(dic_results, num_stocks_available)
print("Launching distanceMatrix...")
order_table_distance_matrix_strat = strategy_distance_matrix_clustering(dic_results, num_stocks_available)
print("Launching clustering...")
order_table_clustering_strat = strat_cluster_K_means(dic_results, num_stocks_available)


dic_launch_bt = {
    "fixedThreshold": order_table_fixed_threshold_strat,
    "histoStrat": order_table_historical_strat,
    "sectorStrat": order_table_sector_strat,
    "distanceMatrix": order_table_distance_matrix_strat,
    "clustering": order_table_clustering_strat,
}

dic_results_bt = {}

for nameStrat, df_strat in dic_launch_bt.items() :
    print(f"Starting {nameStrat} bt...")
    engine = BacktestEngine(df_strat.fillna(0), dic_results["StockPrices"])
    engine.run()
    dic_results_bt[nameStrat] = engine.summary()

df_results_bt = pd.DataFrame.from_dict(
    dic_results_bt,
    orient='columns'
)
print(df_results_bt.round(4))

df_results_bt.to_excel(r'results\compTableBT.xlsx')


# Sauvegarde dans un fichier Excel avec un sheet par DataFrame
with pd.ExcelWriter('results.xlsx') as writer:
    order_table_fixed_threshold_strat.to_excel(writer, sheet_name='fixedThreshold', index=False)
    order_table_historical_strat.to_excel(writer, sheet_name='Historical', index=False)
    order_table_sector_strat.to_excel(writer, sheet_name='Sector', index=False)
    order_table_distance_matrix_strat.to_excel(writer, sheet_name='distanceMatrix', index=False)
    order_table_clustering_strat.to_excel(writer, sheet_name='clustering', index=False)