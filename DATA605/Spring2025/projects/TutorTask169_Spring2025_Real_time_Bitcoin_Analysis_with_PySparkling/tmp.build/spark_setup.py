from pyspark.sql import SparkSession
from ai.h2o.sparkling import H2OContext, H2OConf

def init_spark_h2o():
    """
    Initialize or retrieve a SparkSession configured for Sparkling Water,
    including the necessary --add-opens flags for Java 11+ reflective access.
    """
    spark = (
        SparkSession.builder
        .appName("RealTimeBitcoinAnalysis")
        .master("local[*]")
        .config("spark.driver.memory", "2g")
        .config("spark.ext.h2o.cloud.name", "bitcoin_h2o_cluster")
        .config("spark.ext.h2o.client.ip", "127.0.0.1")
        # ← Add these two lines to allow H2O to use java.nio reflectively
        .config(
            "spark.driver.extraJavaOptions",
            "--add-opens java.base/java.nio=ALL-UNNAMED"
        )
        .config(
            "spark.executor.extraJavaOptions",
            "--add-opens java.base/java.nio=ALL-UNNAMED"
        )
        .getOrCreate()
    )

    # Any additional H2O-specific settings can go on this H2OConf
    h2o_conf = H2OConf()
    # e.g.: h2o_conf.setH2OClientLanguage("python")

    # Create (or get) the H2OContext from your Spark session
    hc = H2OContext.getOrCreate(h2o_conf)

    return spark, hc

# Expose a singleton Spark + H2O context for import by your other scripts:
spark, hc = init_spark_h2o()

if __name__ == "__main__":
    print("✅ Spark and H2O contexts initialized.")