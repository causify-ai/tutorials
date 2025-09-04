### Tech Description: Tianshou
Tianshou is a powerful reinforcement learning (RL) library designed for building and training RL agents. It provides a flexible and modular framework that supports various algorithms and environments, making it suitable for both research and practical applications. Key features include:
- Support for multiple RL algorithms (DQN, PPO, etc.)
- Easy integration with gym environments
- Customizable training loops and evaluation metrics
- Extensive documentation and community support

---

### Project Blueprint 1: Simple Game Agent (Difficulty: 1 - Easy)
**Project Objective**: Build a reinforcement learning agent that learns to play a simple game (e.g., CartPole) using Tianshou. The goal is to optimize the agent's performance to keep the pole balanced for the longest time.

**Dataset Suggestions**: Use the OpenAI Gym environments, which simulate various games including CartPole. The environment data is available through the OpenAI Gym library.

**Step-by-Step Plan**:
1. **Data Collection / Simulation**: Set up the CartPole environment using OpenAI Gym.
2. **Feature Engineering**: Identify relevant states (e.g., pole angle, cart position) from the environment.
3. **Model Training**: Implement a simple DQN algorithm using Tianshou to train the agent.
4. **Use of the Tool**: Utilize Tianshou's training loop to optimize the agent's policy.
5. **Evaluation Metrics**: Track the average reward per episode and the total number of episodes until the agent fails.
6. **Visualization or Reporting**: Plot the agent's performance over time and visualize the learning curve.

**Bonus Ideas**: Experiment with different hyperparameters (learning rate, discount factor) to see their impact on agent performance.

---

### Project Blueprint 2: Stock Trading Strategy (Difficulty: 2 - Medium)
**Project Objective**: Develop a reinforcement learning agent that learns to trade stocks by maximizing cumulative returns over a set period. The goal is to create a strategy that outperforms a buy-and-hold strategy.

**Dataset Suggestions**: Use historical stock price data available on Kaggle or Yahoo Finance (via API). Focus on a specific stock or a set of stocks within a given timeframe.

**Step-by-Step Plan**:
1. **Data Collection / Simulation**: Gather historical stock price data using a public API or Kaggle datasets.
2. **Feature Engineering**: Create features such as moving averages, price changes, and technical indicators.
3. **Model Training**: Implement a reinforcement learning algorithm (e.g., PPO) using Tianshou to train the trading agent.
4. **Use of the Tool**: Leverage Tianshou for training the trading agent, optimizing the policy based on rewards (profit/loss).
5. **Evaluation Metrics**: Evaluate performance using metrics like Sharpe Ratio, cumulative returns, and maximum drawdown.
6. **Visualization or Reporting**: Create visualizations of the trading strategy's performance compared to the buy-and-hold strategy.

**Bonus Ideas**: Test the agent on different stocks or market conditions, or incorporate transaction costs into the model.

---

### Project Blueprint 3: Autonomous Vehicle Navigation (Difficulty: 3 - Hard)
**Project Objective**: Design a reinforcement learning agent that navigates an autonomous vehicle through a simulated environment, optimizing for the shortest path while avoiding obstacles.

**Dataset Suggestions**: Use a simulated environment like the Unity ML-Agents toolkit or OpenAI Gym's CarRacing environment, which provides a rich set of states for training.

**Step-by-Step Plan**:
1. **Data Collection / Simulation**: Set up the CarRacing environment using OpenAI Gym or Unity ML-Agents.
2. **Feature Engineering**: Extract relevant features such as vehicle speed, distance to obstacles, and track boundaries.
3. **Model Training**: Implement a complex RL algorithm (e.g., DDPG or SAC) using Tianshou to train the vehicle's navigation policy.
4. **Use of the Tool**: Utilize Tianshou's advanced features for continuous action spaces and reward shaping.
5. **Evaluation Metrics**: Measure success based on average lap time, number of collisions, and successful completion of laps.
6. **Visualization or Reporting**: Create a dashboard to visualize the vehicle's path, speed, and performance metrics over multiple runs.

**Bonus Ideas**: Introduce varying levels of difficulty in the environment (e.g., different track layouts or weather conditions) and analyze how the agent adapts to these changes.

