"""
train_dqn.py

Main script to train a Deep Q‑Network (DQN) agent for Bitcoin trading.
It sets up the environment, agent, replay buffer, data collection,
and executes the training loop using an in‑memory TFUniformReplayBuffer.
Includes evaluation on the validation set with return and directional accuracy.
Optionally displays training visualizations when the *visualize* flag is enabled.
"""

# #############################################################################
# Imports
# #############################################################################
import os
from typing import Dict, List

import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from tf_agents.environments import tf_environment
from tf_agents.policies import random_tf_policy, policy_saver
from tf_agents.utils import common

import config
import tensorflow_agents_utils as utils


_LOG = utils.logging_setup(log_file="train_dqn.log")


def main(visualize: bool = True) -> None:
    """Train a DQN trading agent.

    :param visualize: If ``True`` (default) show matplotlib plots of key
                      training metrics at the end of training. Set to
                      ``False`` to skip all plotting (useful for headless
                      runs or CI pipelines).

    :return: None
    """
    _LOG.info("Starting DQN Agent Training Script")
    # Reproducibility
    if config.RANDOM_SEED is not None:
        _LOG.info(f"Setting random seed to: {config.RANDOM_SEED}")
        tf.random.set_seed(config.RANDOM_SEED)
        np.random.seed(config.RANDOM_SEED)
    # Environment Creation
    _LOG.info("Creating training and evaluation environments…")
    train_tf_env: tf_environment.TFEnvironment = utils.create_btc_env(
        data_path=config.NORM_TRAIN_DATA_PATH,
        window_size=config.WINDOW_SIZE,
        fee=config.FEE,
        feature_columns=None,
        wrap_in_tf_env=True,
    )
    eval_tf_env: tf_environment.TFEnvironment = utils.create_btc_env(
        data_path=config.NORM_VALIDATION_DATA_PATH,
        window_size=config.WINDOW_SIZE,
        fee=config.FEE,
        feature_columns=None,
        wrap_in_tf_env=True,
    )
    # Agent, Replay Buffer, Policies
    train_step_counter = common.create_variable("train_step_counter", initial_value=0)
    q_net = utils.create_q_network(
        observation_spec=train_tf_env.observation_spec(),
        action_spec=train_tf_env.action_spec(),
    )
    optimizer_instance = tf.keras.optimizers.Adam(learning_rate=config.LEARNING_RATE)
    agent = utils.create_dqn_agent(
        time_step_spec=train_tf_env.time_step_spec(),
        action_spec=train_tf_env.action_spec(),
        q_net=q_net,
        train_step_counter=train_step_counter,
        optimizer=optimizer_instance,
    )
    replay_buffer = utils.create_replay_buffer(
        tf_agent=agent, environment_batch_size=train_tf_env.batch_size
    )
    # Epsilon‑greedy annealing
    current_epsilon = tf.Variable(
        config.INITIAL_EPSILON, dtype=tf.float32, trainable=False, name="CurrentEpsilon"
    )
    epsilon_decay_rate = (
        config.INITIAL_EPSILON - config.MIN_EPSILON
    ) / config.EPSILON_DECAY_TRAINING_STEPS

    def get_epsilon() -> tf.Tensor:
        return current_epsilon.value()

    collect_policy = utils.create_collection_policy(agent, get_epsilon)
    # Drivers
    initial_collect_driver = utils.create_data_collection_driver(
        train_tf_env,
        random_tf_policy.RandomTFPolicy(
            train_tf_env.time_step_spec(), train_tf_env.action_spec()
        ),
        replay_buffer,
        config.INITIAL_COLLECT_STEPS,
    )
    training_collect_driver = utils.create_data_collection_driver(
        train_tf_env,
        collect_policy,
        replay_buffer,
        config.COLLECT_STEPS_PER_ITERATION,
    )
    # Dataset
    training_dataset = utils.create_training_dataset(replay_buffer, agent)
    dataset_iterator = iter(training_dataset)
    # Buffer warm‑up
    if replay_buffer.num_frames().numpy() < config.INITIAL_COLLECT_STEPS:
        utils.initial_collect(initial_collect_driver, replay_buffer)
    # Training Loop
    metrics: Dict[str, List[float]] = {
        "loss": [],
        "epsilon": [],
        "avg_eval_reward": [],
        "directional_acc": [],
        "q_min": [],
        "q_max": [],
        "q_mean": [],
        "target_q_lag": [],
    }
    steps_logged: List[int] = []
    eval_steps: List[int] = []
    best_avg_eval_reward = -np.inf
    os.makedirs(config.POLICY_SAVE_PATH, exist_ok=True)
    agent.train = common.function(agent.train)  # TF graph for speed
    time_step = train_tf_env.reset()
    for iteration in range(config.NUM_TRAINING_ITERATIONS):
        time_step, _ = training_collect_driver.run(time_step=time_step)
        if time_step.is_last():
            time_step = train_tf_env.reset()
        train_loss = utils.train_one_iteration(dataset_iterator, agent)
        current_step = train_step_counter.numpy()
        # Epsilon decay
        if current_step < config.EPSILON_DECAY_TRAINING_STEPS:
            current_epsilon.assign(
                max(
                    config.MIN_EPSILON,
                    config.INITIAL_EPSILON - epsilon_decay_rate * current_step,
                )
            )
        else:
            current_epsilon.assign(config.MIN_EPSILON)
        # Periodic logging & metric capture
        if current_step % config.LOG_INTERVAL == 0:
            _LOG.info(
                f"Iter {iteration + 1} | Step {current_step} | Loss {train_loss.numpy():.5f} | "
                f"Eps {get_epsilon().numpy():.3f}"
            )
            # Retrieve a batch to monitor Q‑value statistics and target lag
            try:
                obs_batch, _ = next(dataset_iterator)
                q_vals, _ = q_net(obs_batch.observation)
                target_q_vals, _ = agent._target_q_network(obs_batch.observation)
                q_diff = tf.abs(q_vals - target_q_vals)

                metrics["q_min"].append(float(tf.reduce_min(q_vals).numpy()))
                metrics["q_max"].append(float(tf.reduce_max(q_vals).numpy()))
                metrics["q_mean"].append(float(tf.reduce_mean(q_vals).numpy()))
                metrics["target_q_lag"].append(float(tf.reduce_mean(q_diff).numpy()))
            except Exception as exc:
                _LOG.warning(f"Q‑stat monitoring failed: {exc}")
                metrics["q_min"].append(np.nan)
                metrics["q_max"].append(np.nan)
                metrics["q_mean"].append(np.nan)
                metrics["target_q_lag"].append(np.nan)

            metrics["loss"].append(float(train_loss.numpy()))
            metrics["epsilon"].append(float(get_epsilon().numpy()))
            steps_logged.append(current_step)
        # Evaluation
        if current_step > 0 and current_step % config.EVAL_INTERVAL == 0:
            eval_rewards: List[float] = []
            total_trades_taken_eval = 0
            total_correct_directions_eval = 0
            py_eval_env = eval_tf_env.pyenv.envs[0]

            for _ in range(config.NUM_EVAL_EPISODES):
                eval_ts = eval_tf_env.reset()
                ep_reward = 0.0
                while not eval_ts.is_last():
                    tick_before = py_eval_env._current_tick
                    current_price = py_eval_env._df.loc[tick_before, "Close"]

                    action_step = agent.policy.action(eval_ts)
                    chosen_action = action_step.action.numpy()[0]
                    eval_ts = eval_tf_env.step(action_step.action)

                    tick_after = py_eval_env._current_tick
                    next_price = py_eval_env._df.loc[tick_after, "Close"]

                    ep_reward += eval_ts.reward.numpy()[0]

                    if chosen_action in (0, 2):  # Short or Long
                        total_trades_taken_eval += 1
                        if (chosen_action == 2 and next_price > current_price) or (
                            chosen_action == 0 and next_price < current_price
                        ):
                            total_correct_directions_eval += 1
                eval_rewards.append(ep_reward)
            avg_reward = float(np.mean(eval_rewards))
            directional_acc = (
                total_correct_directions_eval / total_trades_taken_eval
                if total_trades_taken_eval > 0
                else 0.0
            )
            metrics["avg_eval_reward"].append(avg_reward)
            metrics["directional_acc"].append(directional_acc)
            eval_steps.append(current_step)
            _LOG.info(
                f"Step {current_step} | Eval Avg Reward {avg_reward:.5f} | Directional Acc {directional_acc:.3f}"
            )
            # Save best policy
            if avg_reward > best_avg_eval_reward:
                best_avg_eval_reward = avg_reward
                save_path = os.path.join(
                    config.POLICY_SAVE_PATH,
                    f"policy_step_{current_step}_reward_{avg_reward:.5f}.zip",
                )
                policy_saver.PolicySaver(agent.policy).save(save_path)
                _LOG.info(f"New best policy saved to {save_path}")
    _LOG.info("Training complete.")
    # Visualizations (Jupyter‑friendly)
    if visualize:
        _LOG.info("Displaying training visualizations…")
        plt.figure(figsize=(14, 6))
        plt.plot(steps_logged, metrics["q_min"], label="Q Min")
        plt.plot(steps_logged, metrics["q_max"], label="Q Max")
        plt.plot(steps_logged, metrics["q_mean"], label="Q Mean")
        plt.title("Q‑Value Range vs Training Steps")
        plt.xlabel("Training Step")
        plt.ylabel("Q‑Value")
        plt.legend()
        plt.show()
        plt.figure(figsize=(14, 6))
        plt.plot(steps_logged, metrics["target_q_lag"], label="Target‑Network Lag")
        plt.title("Target Network Lag vs Training Steps")
        plt.xlabel("Training Step")
        plt.ylabel("Mean |Q_online − Q_target|")
        plt.legend()
        plt.show()
    # Cleanup
    train_tf_env.close()
    eval_tf_env.close()
    _LOG.info("Environments closed.")


if __name__ == "__main__":
    try:
        main(visualize=False)
    except Exception as e:
        _LOG.error(f"Error in main execution: {e}", exc_info=True)
        exit()
