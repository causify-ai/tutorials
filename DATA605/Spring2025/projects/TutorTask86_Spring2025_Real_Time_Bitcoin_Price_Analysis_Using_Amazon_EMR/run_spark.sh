#!/bin/bash
$SPARK_HOME/bin/spark-submit \
  --conf "spark.metrics.conf.*.sink.jmx.class=org.apache.spark.metrics.sink.ConsoleSink" \
  --conf "spark.metrics.namespace=local" \
  --conf "spark.metrics.appStatusSource.enabled=false" \
  --conf "spark.metrics.executorSource.enabled=false" \
  --conf "spark.metrics.driverSource.enabled=false" \
  /app/bitcoin_windowed_batch_output.py



