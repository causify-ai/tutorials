# visualization/system_dashboards.py

import pandas as pd
from config.clickhouse_client import client
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def fetch_dashboard_specs():
    """
    Returns a list of tuples: (dashboard, title, query)
    """
    sql = """
      SELECT dashboard, title, query
      FROM system.dashboards
      ORDER BY dashboard, title
    """
    return client.command(sql)


def build_dynamic_dashboard(name: str):
    """
    Given a dashboard name, runs each spec’s query and packs them into a vertical subplot.
    """
    specs = [spec for spec in fetch_dashboard_specs() if spec[0] == name]
    if not specs:
        raise KeyError(f"No dashboard named {name!r}")
    n = len(specs)
    fig = make_subplots(
        rows=n,
        cols=1,
        subplot_titles=[title for _, title, _ in specs],
        vertical_spacing=0.08,
    )
    for i, (_, title, query) in enumerate(specs, start=1):
        data = client.command(query)
        # assume each query returns two columns: x,timestamp-like, and y,value-like
        df = pd.DataFrame(data, columns=["t", "v"])
        fig.add_trace(
            go.Scatter(x=df["t"], y=df["v"], mode="lines", name=title), row=i, col=1
        )
    fig.update_layout(height=300 * n, title_text=f"Dashboard: {name}")
    return fig
