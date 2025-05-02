from abc import ABC, abstractmethod

class ForecastModel(ABC):
    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def fit(self, series):
        pass

    @abstractmethod
    def forecast(self, steps: int):
        pass