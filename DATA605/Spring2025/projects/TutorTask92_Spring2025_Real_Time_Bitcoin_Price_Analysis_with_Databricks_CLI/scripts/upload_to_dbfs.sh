#!/bin/bash

LOCAL_FILE="data/bitcoin_price.json"
DBFS_PATH="dbfs:/bitcoin/bitcoin_price.json"

# Upload the file to DBFS
databricks fs cp $LOCAL_FILE $DBFS_PATH --overwrite

echo " Uploaded $LOCAL_FILE to $DBFS_PATH"
