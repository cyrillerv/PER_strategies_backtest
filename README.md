# PER-based Strategies for Stock Valuation

This project explores and backtests a wide range of valuation strategies based on the Price-Earnings Ratio (PER), starting from classic rule-based methods (e.g. fixed thresholds) and gradually moving toward more complex approaches such as sector-relative analysis and clustering-based peer comparisons.  

The main goal is to identify under- or over-valued stocks relative to appropriate peer groups, and validate these signals through historical backtests using fundamental and price data.

## Project structure
```bash
PER_strategies_backtest/
├── data/ # Excel/JSON raw data
├── src/
│ ├── data_loading.py # Load and preprocess raw data
│ ├── preprocessing.py # Cleaning, feature engineering
│ └── strategies/
│ ├── strategy_fixed_threshold.py
│ ├── strategy_historical.py
│ ├── strategy_sector.py
│ ├── strategy_cluster.py
│ └── strategy_distance_matrix_clustering.py
├── scripts/
│ ├── run_all_backtests.py # Entry point to run all strategies
│ ├── run_one_strategy.py # Entry point to run a selected strategy
├── notebooks/ # EDA, visualization notebooks
└── README.md
```

## A. Getting started 
### 1. Clone the repository
```bash
git clone https://github.com/your_username/PER_strategies_backtest.git
cd PER_strategies_backtest
```

### 2. Create and activate a virtual environnement
```bash
python -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the main script
```bash
python run_all_backtests.py
```

## B. Implemented Strategies

### 1. Fixed-Threshold Strategy
A simple rule-based approach:
- **Buy** if `PER < 15`
- **Sell** if `PER > 25`

This strategy assumes fixed valuation levels considered attractive or expensive.

---

### 2. Historical-PER Strategy
This strategy uses the stock's own PER history over the last 2 years:
- Compute mean and standard deviation of historical PER
- **Buy** when `PER < mean - std`
- **Sell** when `PER > mean + std`

Objective: detect temporary valuation anomalies with the expectation of mean reversion.

---

### 3. Sector-Based Strategy
Stocks are compared against their sector peers:
- For each stock, compare PER to the **sector average PER**
- **Buy** if `PER < sector_mean - sector_std`
- **Sell** if `PER > sector_mean + sector_std`

This strategy relies on relative valuation within the same industry.


### 4. Clustering K-Means Strategy
**Data used**: `MarketCap`, `TotalRevenue`, `TotalAssets`, `Sector`  
**Method**: K-Means clustering with a maximum constraint of 20 companies per cluster.  
**Condition**: At least 20 companies must have data available on a given date to compute the clusters.

#### Challenges of integrating the `Sector` variable:
- Using **dummy variables** for sectors adds one column per sector, which **overweights** the sector variable in the clustering process.
- Using **integer encoding** for sectors (e.g., Energy = 1, Health = 9, Banking = 7) introduces an **artificial distance** between sectors. For instance, the algorithm might consider Health and Banking closer than Health and Energy, which is not economically meaningful.

---

### 5. Distance Matrix + Historical PER Strategy
To solve the issues mentioned above, we build a **distance matrix** between companies, ensuring equal weighting for each feature (e.g., sector, market cap, etc.). This leads to a more balanced clustering.

- We apply **hierarchical clustering** using the `ward` method, which minimizes intra-cluster variance and produces compact, well-separated clusters.
- Clusters are **recalculated quarterly**.
- We impose a minimum of **5 companies per cluster** and a maximum of **12 clusters** to maintain interpretability and comparability.
on utilise la méthode ward pour minimiser la variance intra-cluster à chaque étape de fusion. C'est généralement celle qui donne les clusters les plus compacts.

## C. Data Sources

- `PER.xlsx`: Price-Earnings Ratios per company  
- `MarketCap.xlsx`, `TotalAssets.xlsx`, `TotalRevenue.xlsx`: Company fundamentals  
- `StockPrices.xlsx`: Historical prices for backtesting  
- `CompanySectors.json`: Industry classification  

---

## D. Results & Visualization

The analysis notebook includes:

- Position heatmaps  *(coming soon)*  
- Cumulative returns charts  
- Cluster compositions by date  *(coming soon)*  
- Metrics: Sharpe ratio, volatility, max drawdown 

---

## E. Tools & Libraries

- `pandas`, `numpy`, `scikit-learn`  
- `k_means_constrained`  
- `tqdm`, `plotly`  
- Python 3.10+
---

## F. Author

**Cyrille Hervé**  
Quantitative Master’s Student  
[LinkedIn](https://www.linkedin.com/in/cyrilleherve) • [GitHub](https://github.com/cyrillerv)