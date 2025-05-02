import tensorflow as tf
import tensorflow_probability as tfp

class InstantForecastModel:
    def __init__(self, config):
        self.config = config
        self.model = None
        self.posterior = None
        self.observed_time_series = None

    def fit(self, series):
        self.observed_time_series = series
        sts_model = tfp.sts.LocalLinearTrend(observed_time_series=series)
        self.model = sts_model

        surrogate = tfp.sts.build_factored_surrogate_posterior(model=sts_model)

        # Define joint_log_prob fn using the new API
        def target_log_prob_fn(**params):
            return self.model.joint_distribution(
                observed_time_series=series
            ).log_prob(**params)

        # Fit the surrogate posterior
        losses = tfp.vi.fit_surrogate_posterior(
            target_log_prob_fn=target_log_prob_fn,
            surrogate_posterior=surrogate,
            optimizer=tf.optimizers.Adam(
                learning_rate=self.config['instant']['learning_rate']
            ),
            num_steps=self.config['instant']['vi_steps']
        )

        self.posterior = surrogate
        return surrogate

    def forecast(self, steps: int):
        samples = self.posterior.sample(self.config['instant']['num_samples'])
        return tfp.sts.forecast(
            model=self.model,
            observed_time_series=self.observed_time_series,
            parameter_samples=samples,
            num_steps_forecast=steps
        )