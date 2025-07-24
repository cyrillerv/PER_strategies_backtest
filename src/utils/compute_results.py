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