import plotly.graph_objs as go
from plotly.offline import plot
from django.shortcuts import render
from bitcoin_app.models import BitcoinPrice
from django_orm_utils import (
    compute_average, compute_volatility, detect_peaks
)

from django_orm_utils import (
    fetch_and_store, get_last_n_prices,
    compute_average, compute_volatility, detect_peaks
)

def price_chart(request):
    # Retrieve the last 50 entries
    fetch_and_store()  # <-- this triggers new price fetch
    data = get_last_n_prices(50)

    # Extract time and price
    timestamps = [entry.timestamp.strftime('%H:%M') for entry in data]
    prices = [entry.price_usd for entry in data]

    # Compute statistics
    avg_price = compute_average(prices)
    volatility = compute_volatility(prices)
    peak_indices = detect_peaks(prices)
    peak_times = [timestamps[i] for i in peak_indices]
    peak_prices = [prices[i] for i in peak_indices]

    # Plotly chart
    fig = go.Figure()

    # Price line
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=prices,
        mode='lines+markers',
        name='Price',
        line=dict(color='cyan')
    ))

    # Peak markers
    fig.add_trace(go.Scatter(
        x=peak_times,
        y=peak_prices,
        mode='markers',
        name='Peaks',
        marker=dict(color='red', size=10, symbol='star')
    ))

    # Chart layout
    fig.update_layout(
        title="Bitcoin Price - Last 50",
        xaxis_title="Time",
        yaxis_title="Price (USD)",
        plot_bgcolor="#111",
        paper_bgcolor="#111",
        font=dict(color='white'),
        height=400
    )

    # Render to HTML
    chart_html = plot(fig, output_type='div', include_plotlyjs='cdn')

    return render(request, 'bitcoin_app/chart.html', {
        'chart': chart_html,
        'avg_price': avg_price,
        'volatility': volatility
    })
