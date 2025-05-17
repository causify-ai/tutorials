#!/bin/bash

# Run the Bitcoin monitor in interactive mode
# 1. 確保映像最新
docker compose build bitcoin-monitor

# 2. 以互動模式執行 bitcoin-monitor
#    --rm         ：結束後自動刪除容器
#    --service-ports：如果 compose 檔有暴露埠，照樣開放
docker compose run --rm --service-ports bitcoin-monitor "$@"