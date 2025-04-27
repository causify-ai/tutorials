import matplotlib.pyplot as plt

def make_forecast(model, periods=30):
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)
    return forecast

def plot_forecast(model, forecast):
    fig = model.plot(forecast)
    plt.title("Bitcoin Price Forecast")
    plt.grid(True)
    plt.show()
