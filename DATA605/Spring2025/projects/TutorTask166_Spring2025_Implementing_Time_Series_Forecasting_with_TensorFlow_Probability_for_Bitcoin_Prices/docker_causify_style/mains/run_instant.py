#!/usr/bin/env python3
from utilities.config_parser import load_config
from utilities.logger import get_logger
from src.data_loader.instant_loader import InstantCSVLoader
from src.features.instant import InstantFeatureEngineer
from src.models.instant_model import InstantForecastModel
from src.trainers.instant_trainer import InstantTrainer

def main():
    config = load_config('configs/config.yaml')
    logger = get_logger('instant')
    loader = InstantCSVLoader(config['paths']['instant_raw_csv'])
    fe     = InstantFeatureEngineer(config)
    model  = InstantForecastModel(config)
    trainer = InstantTrainer(loader, fe, model, logger, config)
    trainer.run()

if __name__ == '__main__':
    main()