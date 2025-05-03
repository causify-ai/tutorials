#!/usr/bin/env python3
import logging
import yaml
from src.data_loader.instant_loader import InstantCSVLoader
from src.features.instant_features import InstantFeatureExtractor
from src.models.instant_model import InstantForecastModel
from src.trainers.instant_trainer import InstantTrainer

def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

def main():
    # Load configuration
    with open("/app/configs/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    
    # Set up logging
    logger = setup_logging()
    
    # Initialize components
    loader = InstantCSVLoader(config)
    fe = InstantFeatureExtractor(config)
    model = InstantForecastModel(config)
    trainer = InstantTrainer(loader, fe, model, logger, config)
    
    # Run the trainer
    trainer.run()

if __name__ == "__main__":
    main()