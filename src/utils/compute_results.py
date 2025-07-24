import pandas as pd
import plotly.graph_objs as go
# import webbrowser

def compute_comparison_table(dic_results_bt) :
    df_results_bt = pd.DataFrame.from_dict(
        dic_results_bt,
        orient='columns'
    )
    df_results_bt.to_excel(r'results\compTableBT.xlsx')

def plot_pnl_graph(dic_strat_pnl) :
    fig = go.Figure()
    for nameStrat, stratPnL in dic_strat_pnl.items() :
        fig.add_trace(go.Scatter(
            x=stratPnL.index,
            y=stratPnL.values,
            name=f"PnL {nameStrat}"
        ))
    fig.update_layout(
        title="Cumulative PnL",
        xaxis_title="Date",
        yaxis_title="PnL (€)",
        template="plotly_white",
        hovermode="x unified"
    )
    fig.write_html(r"results\PnL_Graph.html")
    
    # webbrowser.open("results/PnL_Graph.html")


import numpy as np
import plotly.graph_objs as go
from scipy.stats import gaussian_kde

def plot_density_returns_distrib(dic_strat_portfolio_returns):
    """
    Trace la densité (KDE) de la distribution des performances.
    """
    fig = go.Figure()
    for nameStrat, df_perf in dic_strat_portfolio_returns.items() :
        raw_data_perf = df_perf.values.flatten() * 100
        data_cleaned = raw_data_perf[~np.isnan(raw_data_perf)]

        # Estimation de densité par noyau
        kde = gaussian_kde(data_cleaned)
        x_vals = np.linspace(min(data_cleaned), max(data_cleaned), 500)
        y_vals = kde(x_vals)

        # Tracé avec Plotly
        fig.add_trace(go.Scatter(
            x=x_vals,
            y=y_vals,
            mode="lines",
            line=dict(width=2),
            # fill="tozeroy",
            name=f"PnL {nameStrat}"
        ))

    fig.update_layout(
        title="Densité estimée des rendements des opérations",
        xaxis_title="Performance en %",
        yaxis_title="Densité",
        template="plotly_dark",
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color="white", size=14)
    )

    fig.write_html(r"results\Returns_Distrib_Graph.html")
    
    # webbrowser.open("results/PnL_Graph.html")

