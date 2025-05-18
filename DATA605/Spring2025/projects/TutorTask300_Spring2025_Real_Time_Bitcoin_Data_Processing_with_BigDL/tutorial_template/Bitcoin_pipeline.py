import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# BigDL utilities (engine initialization and Sample)
from bigdl.dllib.utils.common import init_engine, Sample

from bitcoin_api import (
    get_spark_session,
    fetch_bitcoin_prices,
    process_bitcoin_data,
    transform_bitcoin_data,
    load_bitcoin_data
)

# BigDL DLlib imports for Spark 3
from bigdl.dllib.nn.layer import (
    Sequential, Reshape, Recurrent, LSTM,
    TimeDistributed, Linear, Select         # ← no LastTimeStep
)
from bigdl.dllib.nn.criterion import MSECriterion
from bigdl.dllib.optim.optimizer import Optimizer, Adam, MaxEpoch
from pyspark.sql import DataFrame


def etl_pipeline(days: int, output_path: str) -> DataFrame:
    """
    Complete ETL: ingest, clean, transform, and load Bitcoin data.
    """
    spark = get_spark_session()

    # Ingest
    raw_df = fetch_bitcoin_prices(days=days)

    # Clean
    clean_df = process_bitcoin_data(raw_df)

    # Transform
    transformed_df = transform_bitcoin_data(clean_df)

    # Load
    load_bitcoin_data(transformed_df, output_path)

    return transformed_df


def prepare_sequences(prices: list, time_steps: int):
    """
    Build input/output sequences for time series forecasting.
    """
    X, y = [], []
    for i in range(len(prices) - time_steps):
        X.append(prices[i: i + time_steps])
        y.append(prices[i + time_steps])
    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)


def train_rnn_model(
    df: DataFrame,
    time_steps: int = 10,
    hidden_size: int = 50,
    epochs: int = 5
):
    """
    Train a simple RNN (LSTM) on historical Bitcoin prices.
    """
    # Initialize BigDL engine
    init_engine()

    spark = get_spark_session()
    prices = df.select("price").rdd.map(lambda r: r[0]).collect()
    X, y = prepare_sequences(prices, time_steps)

    # Build model
    model = Sequential()
    model.add(Reshape([time_steps, 1]))
    model.add(
        Recurrent().add(
            LSTM(input_size=1, hidden_size=hidden_size)  # ← delete return_sequences
        )
    )
    model.add(TimeDistributed(Linear(hidden_size, 1)))
    model.add(Select(2, -1))

    # Prepare training RDD as BigDL Sample objects
    samples = []
    for i in range(len(y)):
        features = X[i].reshape((time_steps, 1))
        label = np.array([y[i]])
        samples.append(Sample.from_ndarray(features, label))
    training_rdd = spark.sparkContext.parallelize(samples)

    # Configure optimizer
    optimizer = Optimizer(
        model=model,
        training_rdd=training_rdd,
        criterion=MSECriterion(),
        optim_method=Adam(),
        batch_size=32,
        end_trigger=MaxEpoch(epochs)
    )
    trained_model = optimizer.optimize()
    return trained_model


def predict_future(
    model,
    recent_seq: list,
    future_steps: int = 10
) -> list:
    """
    Autoregressively predict future price points.
    """
    seq = recent_seq.copy()
    preds = []
    for _ in range(future_steps):
        arr = np.array(seq, dtype=np.float32).reshape((1, len(seq), 1))
        pred = model.predict(arr)[0][0]
        preds.append(pred)
        seq = seq[1:] + [pred]
    return preds


def visualize_results(
    df: DataFrame,
    predictions: list,
    freq: str = 'H'
):
    """
    Plot actual vs. predicted Bitcoin prices.
    """
    pdf = df.toPandas()
    times = pdf['time']
    prices = pdf['price']

    # Generate prediction timestamps
    future_times = pd.date_range(
        start=times.iloc[-1],
        periods=len(predictions) + 1,
        freq=freq
    )[1:]

    plt.figure(figsize=(10, 6))
    plt.plot(times, prices, label='Actual')
    plt.plot(future_times, predictions, label='Predicted')
    plt.xlabel('Time')
    plt.ylabel('Price (USD)')
    plt.title('Bitcoin Price Forecast')
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    OUTPUT_PATH = './output/bitcoin'
    DAYS = 30  # Historical window

    # Run ETL pipeline
    df_transformed = etl_pipeline(DAYS, OUTPUT_PATH)

    # Train model
    model = train_rnn_model(
        df_transformed,
        time_steps=20,
        hidden_size=64,
        epochs=5
    )

    # Predict future
    recent_prices = (
        df_transformed.select('price')
        .rdd.map(lambda r: r[0])
        .collect()[-20:]
    )
    future_preds = predict_future(model, recent_prices, future_steps=10)

    # Visualize
    visualize_results(df_transformed, future_preds)
