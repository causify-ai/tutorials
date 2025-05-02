#!/usr/bin/env python3
from utilities.config_parser import load_config
from utilities.logger import get_logger
from src.data_loader.history_loader import HistoryCSVLoader
from src.features.history import HistoryFeatureEngineer
from src.models.history_model import HistoryForecastModel
from src.trainers.history_trainer import HistoryTrainer

def main():
    config = load_config('configs/config.yaml')
    logger = get_logger('history')
    loader = HistoryCSVLoader(config['paths']['history_raw_csv'])
    fe     = HistoryFeatureEngineer(config)
    model  = HistoryForecastModel(config)
    trainer = HistoryTrainer(loader, fe, model, logger, config)
    trainer.run()

if __name__ == '__main__':
    main()