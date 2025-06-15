import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Core Time Series Plots
def plot_price_over_time(df):
    plt.figure(figsize=(12, 4))
    plt.plot(df["timestamp"], df["price"])
    plt.title("Bitcoin Price Over Time")
    plt.xlabel("Timestamp")
    plt.ylabel("Price (USD)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_volume_over_time(df):
    plt.figure(figsize=(12, 4))
    plt.plot(df["timestamp"], df["volume"], color="orange")
    plt.title("Bitcoin Volume Over Time")
    plt.xlabel("Timestamp")
    plt.ylabel("Volume (USD)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_market_cap_over_time(df):
    plt.figure(figsize=(12, 4))
    plt.plot(df["timestamp"], df["market_cap"], color="green")
    plt.title("Bitcoin Market Cap Over Time")
    plt.xlabel("Timestamp")
    plt.ylabel("Market Cap (USD)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# 2. Rolling Averages
def plot_rolling_mean(df, column="price", window=24):
    plt.figure(figsize=(12, 4))
    plt.plot(df["timestamp"], df[column].rolling(window).mean(), label=f"{window}-period rolling mean")
    plt.title(f"Rolling Mean of {column} (Window={window})")
    plt.xlabel("Timestamp")
    plt.ylabel(column)
    plt.grid(True)
    plt.tight_layout()
    plt.legend()
    plt.show()

def plot_multiple_rolling_means(df, column="price", windows=[6, 24, 72]):
    plt.figure(figsize=(12, 4))
    for w in windows:
        plt.plot(df["timestamp"], df[column].rolling(w).mean(), label=f"{w}-period")
    plt.title(f"Multiple Rolling Means for {column}")
    plt.xlabel("Timestamp")
    plt.ylabel(column)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# 3. Distributions & Outliers
def plot_distribution(df, column="price"):
    plt.figure(figsize=(8, 4))
    sns.histplot(df[column], kde=True, bins=50)
    plt.title(f"Distribution of {column}")
    plt.xlabel(column)
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.show()

def plot_boxplot_by_hour(df, column="price"):
    df_temp = df.copy()
    df_temp["hour"] = pd.to_datetime(df_temp["timestamp"]).dt.hour
    plt.figure(figsize=(10, 5))
    sns.boxplot(data=df_temp, x="hour", y=column)
    plt.title(f"{column} by Hour of Day")
    plt.xlabel("Hour")
    plt.ylabel(column)
    plt.tight_layout()
    plt.show()

# 4. Price vs Volume/Market Cap
def plot_scatter_price_vs_volume(df):
    plt.figure(figsize=(6, 6))
    sns.scatterplot(data=df, x="volume", y="price", alpha=0.5)
    plt.title("Price vs Volume")
    plt.xlabel("Volume")
    plt.ylabel("Price")
    plt.tight_layout()
    plt.show()

def plot_scatter_price_vs_marketcap(df):
    plt.figure(figsize=(6, 6))
    sns.scatterplot(data=df, x="market_cap", y="price", alpha=0.5)
    plt.title("Price vs Market Cap")
    plt.xlabel("Market Cap")
    plt.ylabel("Price")
    plt.tight_layout()
    plt.show()

# 5. Correlation Heatmap
def plot_correlation_heatmap(df):
    cols = ["price", "volume", "market_cap"]
    corr = df[cols].corr()
    plt.figure(figsize=(6, 4))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Correlation Matrix")
    plt.tight_layout()
    plt.show()

# 6. Hourly Seasonality
def plot_hourly_average(df, column="price"):
    df_temp = df.copy()
    df_temp["hour"] = pd.to_datetime(df_temp["timestamp"]).dt.hour
    hourly_avg = df_temp.groupby("hour")[column].mean()
    plt.figure(figsize=(10, 4))
    plt.plot(hourly_avg.index, hourly_avg.values, marker="o")
    plt.title(f"Average {column} by Hour of Day")
    plt.xlabel("Hour of Day")
    plt.ylabel(f"Average {column}")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

