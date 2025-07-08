#!/bin/bash -e

# 1. Check for Kaggle API key
if [[ ! -f ~/.kaggle/kaggle.json ]]; then
  echo "❌ Kaggle API key not found at ~/.kaggle/kaggle.json"
  echo "👉 Download it from https://www.kaggle.com/account and place it in ~/.kaggle/"
  exit 1
fi

chmod 600 ~/.kaggle/kaggle.json

# 2. Create temp directory and download dataset
TMP_DIR=$(mktemp -d)
cd $TMP_DIR

echo "📥 Downloading dataset from Kaggle..."
kaggle datasets download -d mczielinski/bitcoin-historical-data

echo "📦 Unzipping dataset..."
unzip bitcoin-historical-data.zip

# 3. Replace your target file (update the path to your target)
TARGET_PATH="$OLDPWD/database/btc_data/btcusd_1-min_data.csv"
SOURCE_FILE=$(find . -maxdepth 1 -iname "*.csv" | head -n 1)

mkdir -p "$(dirname "$TARGET_PATH")"

if [[ -f "$SOURCE_FILE" ]]; then
  echo "♻️ Replacing $TARGET_PATH with latest dataset..."
  cp "$SOURCE_FILE" "$TARGET_PATH"
  echo "✅ Replacement complete."
else
  echo "❌ Dataset file not found in archive."
fi

# 4. Cleanup
cd -
rm -rf "$TMP_DIR"
