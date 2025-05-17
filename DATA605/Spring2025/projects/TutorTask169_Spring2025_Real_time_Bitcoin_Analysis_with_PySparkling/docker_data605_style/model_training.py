from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import GBTRegressor
from pyspark.ml import Pipeline
from ai.h2o.sparkling import H2OContext

def train_model(input_parquet="data/processed_bitcoin_data.parquet",
                model_path="models/bitcoin_gbm_model"):
    # 1) Create Spark session
    spark = (
        SparkSession.builder
        .appName("BitcoinModelTraining")
        .master("local[*]")
        .getOrCreate()
    )

    # 2) Load processed data
    df = spark.read.parquet(input_parquet)

    # 3) Assemble features
    assembler = VectorAssembler(inputCols=["lag_1", "lag_2"], outputCol="features")
    gbm = GBTRegressor(featuresCol="features", labelCol="price", maxIter=50)

    pipeline = Pipeline(stages=[assembler, gbm])
    model = pipeline.fit(df)

    # 4) Save model
    model.write().overwrite().save(model_path)
    print(f"✅ Model trained and saved to {model_path}")

    spark.stop()

if __name__ == "__main__":
    train_model()
