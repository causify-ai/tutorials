import logging
import tensorflow as tf
import tensorflow_probability as tfp

class HistoryTrainer:
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
        self.horizon = config['history']['forecast_horizon']

    def run(self):
        raw = self.loader.fetch()
        self.logger.info(f"Loaded {len(raw)} raw history rows")

        series = self.fe.transform(raw)
        self.logger.info(f"Transformed into {len(series)} feature rows")

        # only target series (e.g. price)
        self.model.fit(series['price'])
        self.logger.info("History model fit complete")

        forecast_dist = self.model.forecast(self.horizon)
        self.logger.info(f"Forecasted next {self.horizon} days")

        # Extract stats using samples since quantile is not implemented
        samples = forecast_dist.sample(1000)  # Get 1000 samples for better estimation
        mean = tf.reduce_mean(samples, axis=0).numpy()
        lower = tfp.stats.percentile(samples, 10.0, axis=0).numpy()
        upper = tfp.stats.percentile(samples, 90.0, axis=0).numpy()
        
        self.logger.info(f"Mean (head): {mean[:5]}")
        self.logger.info(f"90% CI lower (head): {lower[:5]}")
        self.logger.info(f"90% CI upper (head): {upper[:5]}")

        return {'mean': mean, 'lower': lower, 'upper': upper}