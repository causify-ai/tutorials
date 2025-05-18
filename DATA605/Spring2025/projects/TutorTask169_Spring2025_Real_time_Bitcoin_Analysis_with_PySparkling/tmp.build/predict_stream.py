# predict_stream.py

import time
from pyspark.ml.pipeline import PipelineModel
from pyspark.sql.functions import col
from spark_setup import init_spark_h2o

# point this at the actual directory where model_training.py wrote your pipeline
MODEL_DIR = "models/bitcoin_gbm_model"
# where your processed feature parquet lives
PROCESSED_DATA = "data/processed_bitcoin_data.parquet"

def predict_stream():
    # 1) initialize Spark & H2O
    spark, hc = init_spark_h2o()

    # 2) load your saved Spark ML PipelineModel
    model = PipelineModel.load(MODEL_DIR)

    # 3) load the feature-enriched historical data
    df = spark.read.parquet(PROCESSED_DATA)

    # 4) (very simple “stream” by iterating timestamps one at a time)
    for ts in df.select("timestamp") \
                .distinct() \
                .orderBy("timestamp") \
                .rdd \
                .map(lambda r: r[0]) \
                .collect():

        batch = df.filter(col("timestamp") == ts)
        preds = model.transform(batch)
        # just print one row of each micro-batch
        preds.select("timestamp", "prediction").show(1, truncate=False)

        # wait 10 s before next
        time.sleep(10)

if __name__ == "__main__":
    predict_stream()