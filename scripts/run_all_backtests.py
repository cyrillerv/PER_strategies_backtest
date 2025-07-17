import sys
import os

# Ajoute le dossier racine du projet au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.data_loading import load_data
from src.preprocessing import clean_data
from src.strategies.strategy_baseline import strat_fixed_treshold

df_MarketCap, df_PER, df_TotalAssets, df_TotalRevenue, dic_sectors = load_data()
df_MarketCap, df_PER, df_TotalAssets, df_TotalRevenue, dic_sectors = clean_data(df_MarketCap, df_PER, df_TotalAssets, df_TotalRevenue, dic_sectors)

# First strat
strat_fixed_treshold(df_PER, threshold=15)
