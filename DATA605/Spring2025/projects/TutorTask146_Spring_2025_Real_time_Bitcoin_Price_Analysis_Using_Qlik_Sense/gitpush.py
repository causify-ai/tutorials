# push_to_github.py

from QlikAnalysis_utils import push_csv_files_to_github

REPO_DIR = "/Users/aj/Library/CloudStorage/Dropbox/Bitcoin_Analysis"
CSV_FILES = ["bitcoin_realtime.csv", "bitcoin_forecast.csv", "bitcoin_analytics.csv"]

if __name__ == "__main__":
    push_csv_files_to_github(CSV_FILES, REPO_DIR)
