# Bitcoin Forecasting Performance Metrics

## Understanding the Performance Metrics

The Bitcoin Price Forecasting model uses several performance metrics to evaluate prediction accuracy and model performance. This document explains these metrics in detail, with specific focus on the Mean Absolute Error (MAE) visualization.

## Mean Absolute Error (MAE)

### Definition

The Mean Absolute Error (MAE) between true target values (y) and predictions (ŷ) is defined as:

```
MAE = (1/N) * Σ|y_i - ŷ_i|
```

Where:
- N is the number of examples
- y_i is the true value for example i
- ŷ_i is the model's predicted value for the same example

In simple terms, MAE is the average of the absolute differences between predictions and actual values.

### Why MAE Fluctuates in the Visualization

Looking at the dashboard visualization, you may notice that the MAE values fluctuate significantly over time. This is **expected behavior** and not an error. Here's why:

1. **Point-wise MAE**: The chart shows the absolute error for each individual prediction point (|actual - predicted|), not a rolling or cumulative average.

2. **Volatile Asset**: Bitcoin prices are inherently volatile, with rapid and unpredictable price movements. This makes prediction errors variable.

3. **Real-time Updates**: The model makes real-time predictions at short intervals, capturing many small price movements that can be difficult to predict.

4. **Adaptation Period**: When market conditions change, the model needs time to adapt, causing temporary increases in error.

5. **Market Events**: News, regulatory announcements, and whale transactions can cause sudden price movements that are impossible to predict from historical data alone.

### Interpreting the MAE Chart

- **Individual Spikes**: Individual high MAE values represent specific predictions with larger errors, often during unexpected price movements.
  
- **Clusters of Higher MAE**: Periods with consistently higher MAE values often indicate changing market conditions that the model is adapting to.
  
- **Lower MAE Periods**: Times with consistently low MAE indicate stable market conditions where the model is performing well.

- **Average MAE**: The dotted line showing average MAE is a better indicator of overall model performance than individual points.

## Other Performance Metrics

### Root Mean Square Error (RMSE)

RMSE is the square root of the average of squared differences between predictions and actual values:

```
RMSE = sqrt((1/N) * Σ(y_i - ŷ_i)²)
```

RMSE gives higher weight to larger errors, which is useful for applications where larger errors are disproportionately more problematic.

### Percentage Error

Percentage error represents the relative error as a percentage of the actual price:

```
Percentage Error = ((y_i - ŷ_i) / y_i) * 100%
```

This helps understand the significance of the error relative to the price magnitude.

### Standard Deviation of Predictions

The standard deviation is calculated from the model's uncertainty estimates and represents the confidence interval of predictions. Lower values indicate more confident predictions.

### Z-score

Z-scores standardize errors to identify anomalous predictions:

```
Z-score = (error - mean_error) / error_std_dev
```

High Z-scores flag potentially problematic predictions that deviate significantly from typical error patterns.

## Improvement Strategies

If you want to improve the model's performance metrics:

1. **Increase Training Data**: More historical data can help capture longer-term patterns.

2. **Feature Engineering**: Adding technical indicators, sentiment analysis, or on-chain metrics could improve predictive power.

3. **Model Tuning**: Adjusting hyperparameters like the number of variational inference steps or component combinations.

4. **Adaptive Learning Rate**: The model currently uses adaptive learning rates, but further tuning can help.

5. **Ensemble Approaches**: Combining multiple models with different strengths can improve overall performance.

## Conclusion

Performance metrics like MAE are essential for understanding model accuracy, but they must be interpreted in the context of the specific use case. For Bitcoin price prediction, fluctuations in error metrics are normal due to the volatile nature of the asset. The goal is not to eliminate all errors (which would be impossible for cryptocurrency prices) but to maintain consistent performance with reasonable error bounds across different market conditions. 