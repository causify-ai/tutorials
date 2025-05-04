"""
train_dqn.py

Main script to train a Deep Q-Network (DQN) agent for Bitcoin trading.
It sets up the environment, agent, replay buffer, data collection,
and executes the training loop using an in-memory TFUniformReplayBuffer.
"""

import tensorflow as tf
from tf_agents.environments import tf_environment  # For type hinting
from tf_agents.policies import random_tf_policy  # For initial collect
from tf_agents.utils import common  # For create_variable
import config
import tensorflow_agents_utils as utils

_LOG = utils.logging_setup(log_file="train_dqn.log")
if __name__ == "__main__":
    _LOG.info("Starting DQN Agent Training Script")
    # Set random seeds for reproducibility
    if config.RANDOM_SEED is not None:
        _LOG.info(f"Setting random seed to: {config.RANDOM_SEED}")
        tf.random.set_seed(config.RANDOM_SEED)
    # Create the environment
    _LOG.info("Creating training and evaluation environments...")
    try:
        train_tf_env: tf_environment.TFEnvironment = utils.create_btc_env(
            data_path=config.NORM_TRAIN_DATA_PATH,
            window_size=config.WINDOW_SIZE,
            fee=config.FEE,
            feature_columns=None,
            wrap_in_tf_env=True,
        )
        eval_tf_env: tf_environment.TFEnvironment = (
            utils.create_btc_env(  # For later evaluation
                data_path=config.NORM_VALIDATION_DATA_PATH,
                window_size=config.WINDOW_SIZE,
                fee=config.FEE,
                feature_columns=None,
                wrap_in_tf_env=True,
            )
        )
    except Exception as e:
        _LOG.error(f"Failed to create environments: {e}", exc_info=True)
        exit()
    _LOG.info("Environments created successfully.")
    _LOG.info(f"Train Env Observation Spec: {train_tf_env.observation_spec()}")
    # Create the DQN agent
    _LOG.info("Creating DQN agent...")
    try:
        train_step_counter = common.create_variable(
            "train_step_counter", initial_value=0
        )
        q_net = utils.create_q_network(
            observation_spec=train_tf_env.observation_spec(),
            action_spec=train_tf_env.action_spec(),
        )
        optimizer_instance = tf.keras.optimizers.Adam(
            learning_rate=config.LEARNING_RATE
        )
        agent = utils.create_dqn_agent(
            time_step_spec=train_tf_env.time_step_spec(),
            action_spec=train_tf_env.action_spec(),
            q_net=q_net,
            train_step_counter=train_step_counter,
            optimizer=optimizer_instance,
        )
    except Exception as e:
        _LOG.error(f"Failed to create DQN agent: {e}", exc_info=True)
        exit()
    _LOG.info("DQN Agent created and initialized.")
    # Create Replay Buffer (TFUniformReplayBuffer - in-memory)
    try:
        replay_buffer = utils.create_replay_buffer(
            tf_agent=agent, environment_batch_size=train_tf_env.batch_size
        )
    except Exception as e:
        _LOG.error(f"Failed to create replay buffer: {e}", exc_info=True)
        exit()
    _LOG.info("TFUniformReplayBuffer (in-memory) created.")
    # Create Epsilon Annealing Schedule & Collection Policy
    try:
        current_epsilon_tf_var = tf.Variable(
            config.INITIAL_EPSILON,
            dtype=tf.float32,
            trainable=False,
            name="CurrentEpsilon",
        )

        epsilon_decay_rate = (
            config.INITIAL_EPSILON - config.MIN_EPSILON
        ) / config.EPSILON_DECAY_TRAINING_STEPS

        def get_current_epsilon_fn() -> tf.Tensor:
            return current_epsilon_tf_var.value()

        collect_policy = utils.create_collection_policy(
            tf_agent=agent, epsilon_fn=get_current_epsilon_fn
        )
    except Exception as e:
        _LOG.error(f"Failed to create collection policy: {e}", exc_info=True)
        exit()
    # Create Data Collection Drivers
    try:
        initial_collect_tf_policy = random_tf_policy.RandomTFPolicy(
            train_tf_env.time_step_spec(), train_tf_env.action_spec()
        )
        initial_collect_driver = utils.create_data_collection_driver(
            train_tf_env=train_tf_env,
            collect_policy=initial_collect_tf_policy,
            replay_buffer=replay_buffer,
            steps_to_collect=config.INITIAL_COLLECT_STEPS,
        )
        training_collect_driver = utils.create_data_collection_driver(
            train_tf_env=train_tf_env,
            collect_policy=collect_policy,
            replay_buffer=replay_buffer,
            steps_to_collect=config.COLLECT_STEPS_PER_ITERATION,
        )
    except Exception as e:
        _LOG.error(f"Failed to create data collection drivers: {e}", exc_info=True)
        exit()
    # Create Training Dataset
    try:
        training_dataset = utils.create_training_dataset(
            replay_buffer=replay_buffer, tf_agent=agent
        )
        dataset_iterator = iter(training_dataset)
    except Exception as e:
        _LOG.error(f"Failed to create training dataset: {e}", exc_info=True)
        exit()
    # Initial Replay Buffer Population
    try:
        # Check if buffer needs filling. replay_buffer.num_frames() returns a tf.Tensor.
        # Use tf.compat.v1.get_static_value for a single check outside a tf.function.
        # Or just .numpy() if eager execution is default (TF2).
        buffer_frames = replay_buffer.num_frames().numpy()  # Get as Python value
        if buffer_frames < config.INITIAL_COLLECT_STEPS:
            _LOG.info(
                f"Replay buffer has {buffer_frames} frames. "
                f"Starting initial collection of {config.INITIAL_COLLECT_STEPS} steps..."
            )
            utils.initial_collect(initial_collect_driver, replay_buffer)
        else:
            _LOG.info(
                f"Replay buffer already has {buffer_frames} frames. "
                "Skipping initial collect."
            )
    except Exception as e:
        _LOG.error(f"Error during initial replay buffer population: {e}", exc_info=True)
        exit()
    # Training Loop
    _LOG.info(
        f"Starting training loop for {config.NUM_TRAINING_ITERATIONS} iterations..."
    )
    try:
        agent.train = common.function(agent.train)
        time_step = train_tf_env.reset()
        for iteration in range(config.NUM_TRAINING_ITERATIONS):
            time_step, _ = training_collect_driver.run(time_step=time_step)
            if time_step.is_last():
                time_step = train_tf_env.reset()
            train_loss = utils.train_one_iteration(
                dataset_iterator=dataset_iterator,
                tf_agent=agent,
            )
            current_step = train_step_counter.numpy()
            # Epsilon Annealing
            if current_step < config.EPSILON_DECAY_TRAINING_STEPS:
                new_epsilon = config.INITIAL_EPSILON - (
                    epsilon_decay_rate * current_step
                )
                current_epsilon_tf_var.assign(max(config.MIN_EPSILON, new_epsilon))
            else:
                current_epsilon_tf_var.assign(config.MIN_EPSILON)
            if current_step % config.LOG_INTERVAL == 0:
                _LOG.info(
                    f"Iteration: {iteration + 1}, Step: {current_step}, "
                    f"Loss: {train_loss.numpy():.5f} (avg), "
                    f"Epsilon: {get_current_epsilon_fn().numpy():.3f}",
                )
                # Monitor Q-value scale
                try:
                    obs_batch, _ = next(dataset_iterator)
                    q_vals, _ = q_net(obs_batch.observation)
                    _LOG.info(
                        f"Q-value range: {tf.reduce_min(q_vals).numpy():.3f} to {tf.reduce_max(q_vals).numpy():.3f}"
                    )
                    # Get target Q-values for same observations to monitor target network lag
                    target_q_vals, _ = agent._target_q_network(obs_batch.observation)
                    q_diff = tf.abs(q_vals - target_q_vals)
                    _LOG.info(
                        f"Target-network lag (mean absolute diff): {tf.reduce_mean(q_diff).numpy():.5f}"
                    )
                    # Monitor reward statistics (once every 5 log intervals to avoid slowing training)
                    if current_step % (config.LOG_INTERVAL * 5) == 0:
                        sample_traj, _ = replay_buffer.get_next(
                            sample_batch_size=min(
                                2048, replay_buffer.num_frames().numpy()
                            ),
                            num_steps=1,
                        )
                        r = sample_traj.reward
                        _LOG.info(
                            f"Reward stats - Mean: {tf.reduce_mean(r).numpy():.5f}, "
                            f"Std: {tf.math.reduce_std(r).numpy():.5f}, "
                            f"Min: {tf.reduce_min(r).numpy():.5f}, "
                            f"Max: {tf.reduce_max(r).numpy():.5f}"
                        )
                except Exception as e:
                    _LOG.warning(f"Error while collecting monitoring statistics: {e}")
    except Exception as e:
        _LOG.error(f"Error during training loop: {e}", exc_info=True)
    finally:
        _LOG.info(
            f"--- Training Loop Completed (or interrupted) at Step: {train_step_counter.numpy()} ---"
        )
        train_tf_env.close()
        eval_tf_env.close()
        _LOG.info("Environments closed.")
