import logging
from typing import Dict

class InstantTrainer:
    def __init__(
        self,
        loader,
        feature_engineer,
        model,
        logger,
        config: dict,
    ):
        self.loader = loader
        self.fe = feature_engineer
        self.model = model
        self.logger = logger
        self.config = config
        self.horizon = config['instant']['forecast_horizon']

    def run(self) -> Dict[str, float]:
        # 1) load raw
        raw = self.loader.fetch()
        self.logger.info(f"Loaded {len(raw)} raw instant rows")

        # 2) features
        series = self.fe.transform(raw)
        self.logger.info(f"Transformed into {len(series)} feature rows")

        # 3) fit
        self.model.fit(series)
        self.logger.info("Instant model fit complete")

        # 4) forecast
        forecast_dist = self.model.forecast(self.horizon)
        self.logger.info(f"Forecasted next {self.horizon} steps")

        # 5) extract stats
        mean  = forecast_dist.mean().numpy()
        lower = forecast_dist.quantile(0.1).numpy()
        upper = forecast_dist.quantile(0.9).numpy()
        self.logger.info(f"Mean (head): {mean[:5]}")
        self.logger.info(f"90% CI lower (head): {lower[:5]}")
        self.logger.info(f"90% CI upper (head): {upper[:5]}")

        return {'mean': mean, 'lower': lower, 'upper': upper}