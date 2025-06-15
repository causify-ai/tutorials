import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
from itertools import groupby

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLOT_DIR = os.path.join(os.path.dirname(__file__), "plots")
os.makedirs(PLOT_DIR, exist_ok=True)


def load_stream_output(folder):
    """
    Loads and concatenates CSV files from the specified folder,
    parses timestamp and numeric fields, and returns a sorted DataFrame.

    Args:
        folder (str): Path to the folder containing stream output CSV files.

    Returns:
        pd.DataFrame: Cleaned and sorted DataFrame with columns:
                      ["window_start", "moving_avg"]
    """
    full_path = os.path.join(BASE_DIR, folder)
    files = glob.glob(os.path.join(full_path, "*.csv"))
    df_list = [
        pd.read_csv(f, header=0, names=["moving_avg", "window_start", "window_end"])
        for f in files if os.path.getsize(f) > 0
    ]
    if not df_list:
        return pd.DataFrame(columns=["window_start", "moving_avg"])
    df = pd.concat(df_list, ignore_index=True)
    df = df.dropna(subset=["window_start", "moving_avg"])
    df["window_start"] = pd.to_datetime(df["window_start"], errors='coerce')
    df["moving_avg"] = pd.to_numeric(df["moving_avg"], errors="coerce")
    return df.dropna(subset=["window_start", "moving_avg"]).sort_values("window_start")


def plot_peaks_and_valleys(df, title):
    """
    Plots a moving average time series with peaks and valleys highlighted,
    using a 5-point local extrema rule and a rolling standard deviation band.

    Args:
        df (pd.DataFrame): DataFrame with "window_start" and "moving_avg".
        title (str): Title for the chart.
    """
    df["roll_mean"] = df["moving_avg"].rolling(window=5, center=True).mean()
    df["roll_std"] = df["moving_avg"].rolling(window=5, center=True).std()
    df = df.dropna(subset=["roll_mean", "roll_std"])

    # 5-point local extrema check
    df["is_peak"] = (
        (df["moving_avg"].shift(0) > df["moving_avg"].shift(1)) &
        (df["moving_avg"].shift(0) > df["moving_avg"].shift(2)) &
        (df["moving_avg"].shift(0) > df["moving_avg"].shift(-1)) &
        (df["moving_avg"].shift(0) > df["moving_avg"].shift(-2))
    )

    df["is_valley"] = (
        (df["moving_avg"].shift(0) < df["moving_avg"].shift(1)) &
        (df["moving_avg"].shift(0) < df["moving_avg"].shift(2)) &
        (df["moving_avg"].shift(0) < df["moving_avg"].shift(-1)) &
        (df["moving_avg"].shift(0) < df["moving_avg"].shift(-2))
    )

    # Adaptive label offset
    y_min, y_max = df["moving_avg"].min(), df["moving_avg"].max()
    label_offset = (y_max - y_min) * 0.02

    # Plot setup
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df["window_start"], df["moving_avg"], marker='o', label="Moving Avg", alpha=0.2)
    ax.plot(df["window_start"], df["roll_mean"], linestyle='--', color='gray', label="Rolling Mean")
    ax.fill_between(df["window_start"],
                    df["roll_mean"] + 1.2 * df["roll_std"],
                    df["roll_mean"] - 1.2 * df["roll_std"],
                    color='gray', alpha=0.1, label=f"± 1.2σ")

    ax.scatter(df.loc[df["is_peak"], "window_start"],
               df.loc[df["is_peak"], "moving_avg"],
               color='red', label='Peak', zorder=5)

    ax.scatter(df.loc[df["is_valley"], "window_start"],
               df.loc[df["is_valley"], "moving_avg"],
               color='green', label='Valley', zorder=5)

    for _, row in df[df["is_peak"]].iterrows():
        ax.text(row["window_start"], row["moving_avg"] + label_offset,
                f'{row["moving_avg"]:.2f}', color='red', fontsize=8,
                ha='center', va='bottom')

    for _, row in df[df["is_valley"]].iterrows():
        ax.text(row["window_start"], row["moving_avg"] - label_offset,
                f'{row["moving_avg"]:.2f}', color='green', fontsize=8,
                ha='center', va='top')

    ax.margins(x=0.05, y=0.1)
    ax.set_title(title + " — Peaks & Valleys")
    ax.set_xlabel("Time")
    ax.set_ylabel("Price (USD)")
    ax.legend()
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True)
    plt.tight_layout(pad=2.0, w_pad=2.0, h_pad=2.0)
    filename = f"{title.replace(' ', '_').lower()}_peaks.png"
    plt.savefig(os.path.join(PLOT_DIR, filename))
    # plt.show()
    plt.close()


def plot_trends(df, title):
    """
    Plots uptrends and downtrends by grouping continuous segments of rising or falling prices.
    Annotates them with shaded regions and directional arrows.

    Args:
        df (pd.DataFrame): DataFrame with "window_start" and "moving_avg".
        title (str): Title for the chart.
    """
    df["trend"] = df["moving_avg"].diff().apply(lambda x: "up" if x > 0 else ("down" if x < 0 else "flat"))
    df["is_up"] = df["trend"] == "up"
    df["is_down"] = df["trend"] == "down"

    y_min, y_max = df["moving_avg"].min(), df["moving_avg"].max()
    y_label = y_max - (y_max - y_min) * 0.01

    uptrends, downtrends = [], []
    start_up = start_down = None
    min_trend_length = 8  # Minimum segment length to be considered a trend

    for i in range(len(df)):
        if df["is_up"].iloc[i] and start_up is None:
            start_up = i
        elif not df["is_up"].iloc[i] and start_up is not None:
            if i - start_up >= min_trend_length:
                uptrends.append((start_up, i - 1))
            start_up = None

        if df["is_down"].iloc[i] and start_down is None:
            start_down = i
        elif not df["is_down"].iloc[i] and start_down is not None:
            if i - start_down >= min_trend_length:
                downtrends.append((start_down, i - 1))
            start_down = None

    if start_up is not None and len(df) - start_up >= min_trend_length:
        uptrends.append((start_up, len(df) - 1))
    if start_down is not None and len(df) - start_down >= min_trend_length:
        downtrends.append((start_down, len(df) - 1))

    # Plot setup
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df["window_start"], df["moving_avg"], marker='o', label="Moving Avg", color='black', alpha=0.2)
    ax.margins(x=0.05, y=0.1)

    for start, end in uptrends:
        x_start = df.iloc[start]["window_start"]
        x_end = df.iloc[end]["window_start"]
        y_start = df.iloc[start]["moving_avg"]
        y_end = df.iloc[end]["moving_avg"]
        ax.axvspan(x_start, x_end, color='green', alpha=0.1, zorder=1)
        ax.annotate('', xy=(x_end, y_end), xytext=(x_start, y_start),
                    arrowprops=dict(arrowstyle="->", color='green', lw=2), zorder=10)

    for start, end in downtrends:
        x_start = df.iloc[start]["window_start"]
        x_end = df.iloc[end]["window_start"]
        y_start = df.iloc[start]["moving_avg"]
        y_end = df.iloc[end]["moving_avg"]
        ax.axvspan(x_start, x_end, color='red', alpha=0.1, zorder=1)
        ax.annotate('', xy=(x_end, y_end), xytext=(x_start, y_start),
                    arrowprops=dict(arrowstyle="->", color='red', lw=2), zorder=10)

    ax.set_title(title + " — Trend Shading")
    ax.set_xlabel("Time")
    ax.set_ylabel("Price (USD)")
    ax.legend(loc="lower left")
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True)
    plt.tight_layout(pad=2.0, w_pad=2.0, h_pad=2.0)
    filename = f"{title.replace(' ', '_').lower()}_trends.png"
    plt.savefig(os.path.join(PLOT_DIR, filename))
    # plt.show()
    plt.close()


def plot_overlay(window_sizes):
    """
    Plots overlay of multiple moving average series with different window sizes for comparison.

    Args:
        window_sizes (list): List of window sizes as strings, e.g., ["2 minutes", "3 minutes"]
    """
    plt.figure(figsize=(14, 6))
    colors = ['blue', 'orange', 'green', 'purple', 'brown']

    for idx, win in enumerate(window_sizes):
        folder = f"moving_avg_output_{win.replace(' ', '_')}"
        df = load_stream_output(folder)
        if df.empty:
            print(f"[WARN] No data found in {folder}, skipping.")
            continue
        plt.plot(df["window_start"], df["moving_avg"], label=f"{win}", color=colors[idx % len(colors)], alpha=0.7)

    plt.title("Bitcoin Moving Averages for Multiple Window Sizes")
    plt.xlabel("Time")
    plt.ylabel("Price (USD)")
    plt.xticks(rotation=45)
    plt.legend(title="Window Size")
    plt.grid(True)
    plt.tight_layout(pad=2.0, w_pad=2.0, h_pad=2.0)
    filename = f"window_sizes_overlaid.png"
    plt.savefig(os.path.join(PLOT_DIR, filename))
    # plt.show()
    plt.close()


if __name__ == "__main__":
    # - Might not detect peaks and valleys for very short duration data
    # - Increase NUM_POINTS and WRITER_DURATION in Bitcoin.example.ipynb
    # Sample usage on 2 hours worth of data with different window sizes
    WINDOW_SIZES = ["2 minutes", "3 minutes", "5 minutes"]
    for win in WINDOW_SIZES:
        folder = f"moving_avg_output_{win.replace(' ', '_')}"
        df = load_stream_output(folder)
        if df.empty:
            print(f"[SKIP] No data in {folder}")
            continue
        title = f"Window {win}"
        plot_peaks_and_valleys(df.copy(), title)
        plot_trends(df.copy(), title)

    plot_overlay(WINDOW_SIZES)
