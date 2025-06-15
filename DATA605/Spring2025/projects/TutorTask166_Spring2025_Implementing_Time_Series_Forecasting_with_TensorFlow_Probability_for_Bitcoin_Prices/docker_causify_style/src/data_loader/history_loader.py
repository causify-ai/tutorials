import pandas as pd

class HistoryCSVLoader:
    def __init__(self, path: str):
        self.path = path

    def fetch(self) -> pd.DataFrame:
        df = pd.read_csv(self.path, parse_dates=['timestamp'])
        df.set_index('timestamp', inplace=True)
        return df