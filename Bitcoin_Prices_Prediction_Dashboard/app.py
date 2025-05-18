from flask import Flask, render_template, jsonify
from ingestion.fetch import fetch_bitcoin
from processing.preprocess import load_all_btc_data
from processing.analysis import (
    decompose_price,
    compute_moving_avg,
    detect_anomalies,
    add_technical_indicators
)
from forecasting.prophet_model import run_prophet
from visualization.interactive import (
    plot_btc,
    plot_ma,
    plot_anomalies,
    plot_ma_comparison,
    plot_ema,
    plot_macd,
    plot_returns,
    plot_cumulative_returns,
    plot_price_change,
    plot_volatility,
    plot_forecast_interactive
)

app = Flask(__name__)

@app.route('/')
def dashboard():
    try:
        df = load_all_btc_data()
        print("✅ Data loaded!")
        print("Shape:", df.shape)
        print(df.head())


        df = compute_moving_avg(df)
        df = detect_anomalies(df)
        df = add_technical_indicators(df)

        print("Columns in dataframe:", df.columns.tolist())

        # Ensure all expected columns exist
        required_cols = [
            'MA_7', 'MA_30', 'EMA_12', 'EMA_26',
            'MACD', 'Signal', 'Returns', 'Cumulative_Return',
            'Price_Change', 'Volatility'
        ]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing column in df: {col}")

        forecast = run_prophet(df)

        try:
            btc_plot = plot_btc(df)
        except Exception as e:
            btc_plot = f"<div style='color:red;'>BTC Plot Error: {e}</div>"
            print("plot_btc error:", e)

        try:
            ma_plot = plot_ma(df)
        except Exception as e:
            ma_plot = f"<div style='color:red;'>MA Plot Error: {e}</div>"
            print("plot_ma error:", e)

        try:
            anomaly_plot = plot_anomalies(df)
        except Exception as e:
            anomaly_plot = f"<div style='color:red;'>Anomaly Plot Error: {e}</div>"
            print("plot_anomalies error:", e)

        try:
            ma_comparison_plot = plot_ma_comparison(df)
        except Exception as e:
            ma_comparison_plot = f"<div style='color:red;'>MA Comparison Plot Error: {e}</div>"
            print("plot_ma_comparison error:", e)

        try:
            ema_plot = plot_ema(df)
        except Exception as e:
            ema_plot = f"<div style='color:red;'>EMA Plot Error: {e}</div>"
            print("plot_ema error:", e)

        try:
            macd_plot = plot_macd(df)
        except Exception as e:
            macd_plot = f"<div style='color:red;'>MACD Plot Error: {e}</div>"
            print("plot_macd error:", e)

        try:
            returns_plot = plot_returns(df)
        except Exception as e:
            returns_plot = f"<div style='color:red;'>Returns Plot Error: {e}</div>"
            print("plot_returns error:", e)

        try:
            cumulative_plot = plot_cumulative_returns(df)
        except Exception as e:
            cumulative_plot = f"<div style='color:red;'>Cumulative Return Plot Error: {e}</div>"
            print("plot_cumulative_returns error:", e)

        try:
            price_change_plot = plot_price_change(df)
        except Exception as e:
            price_change_plot = f"<div style='color:red;'>Price Change Plot Error: {e}</div>"
            print("plot_price_change error:", e)

        try:
            volatility_plot = plot_volatility(df)
        except Exception as e:
            volatility_plot = f"<div style='color:red;'>Volatility Plot Error: {e}</div>"
            print("plot_volatility error:", e)

        try:
            forecast_plot = plot_forecast_interactive(forecast)
        except Exception as e:
            forecast_plot = f"<div style='color:red;'>Forecast Plot Error: {e}</div>"
            print("plot_forecast_interactive error:", e)

        forecast_table = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(10).round(2).to_html(index=False)

        return render_template("index.html",
                               btc_plot=btc_plot,
                               ma_plot=ma_plot,
                               anomaly_plot=anomaly_plot,
                               ma_comparison_plot=ma_comparison_plot,
                               ema_plot=ema_plot,
                               macd_plot=macd_plot,
                               returns_plot=returns_plot,
                               cumulative_plot=cumulative_plot,
                               price_change_plot=price_change_plot,
                               volatility_plot=volatility_plot,
                               forecast_table=forecast_table,
                               forecast_plot=forecast_plot)
    except Exception as e:
        print("Dashboard error:", e)
        return render_template("index.html", btc_plot=None, error=str(e))

@app.route('/api/refresh')
def refresh():
    try:
        fetch_bitcoin()
        return jsonify({"status": "updated"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5050)
