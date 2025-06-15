import tensorflow as tf
import tensorflow_probability as tfp

class HistoryForecastModel:
    def __init__(self, config: dict):
        self.config = config
        self.model = None
        self.posterior = None
        self.observed_time_series = None

    def fit(self, series):
        # store for forecasting
        self.observed_time_series = series

        # build trend + seasonal
        trend = tfp.sts.LocalLinearTrend(
            observed_time_series=series, name="history_trend"
        )
        seasonal = tfp.sts.Seasonal(
            num_seasons=self.config['history']['num_seasons'],
            observed_time_series=series,
            name="history_seasonal"
        )
        self.model = tfp.sts.Sum([trend, seasonal], name="history_model")

        # build surrogate
        surrogate = tfp.sts.build_factored_surrogate_posterior(self.model)

        # target log-prob using new API
        def target_log_prob_fn(**params):
            return self.model.joint_distribution(
                observed_time_series=series
            ).log_prob(**params)

        # train
        optimizer = tf.optimizers.Adam(
            learning_rate=self.config['history']['learning_rate']
        )
        losses = tfp.vi.fit_surrogate_posterior(
            target_log_prob_fn=target_log_prob_fn,
            surrogate_posterior=surrogate,
            optimizer=optimizer,
            num_steps=self.config['history']['vi_steps']
        )

        self.posterior = surrogate
        return self.posterior

    def forecast(self, steps: int):
        samples = self.posterior.sample(self.config['history']['num_samples'])
        return tfp.sts.forecast(
            model=self.model,
            observed_time_series=self.observed_time_series,
            parameter_samples=samples,
            num_steps_forecast=steps
        )