# Analyzing Crypto Twitter Trends using spaCy NLP and CoinGecko API

## Objective

This example tutorial demonstrates how to scrape Twitter data, analyze it with spaCy NLP, and enrich the results with live CoinGecko cryptocurrency data.

## Architecture Overview

```mermaid
flowchart LR
    Twitter_Scraper --> Data_Cleaning
    Data_Cleaning --> spaCy_NLP
    spaCy_NLP --> Entity_Extraction
    Entity_Extraction --> Visualization
    CoinGecko_API --> Live_Price_Data
    Live_Price_Data --> Visualization
