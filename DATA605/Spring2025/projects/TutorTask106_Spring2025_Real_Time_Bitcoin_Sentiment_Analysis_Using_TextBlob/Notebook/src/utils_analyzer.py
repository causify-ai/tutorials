from src.logger import get_logger
import pandas as pd
import numpy as np
from textblob import TextBlob
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta
from sklearn.metrics import mean_absolute_percentage_error


logger = get_logger(__name__)


def analyze_sentiment(articles_df):
    """
    Analyze sentiment of news articles using TextBlob.

    Args:
        articles_df (pandas.DataFrame): DataFrame containing news articles.

    Returns:
        pandas.DataFrame: DataFrame with added sentiment scores and categories.
    """
    if articles_df is None or articles_df.empty:
        logger.warning("No articles to analyze.")
        return None

    logger.info("Analyzing sentiment of news articles...")

    df = articles_df.copy()
    df['polarity'] = np.nan
    df['subjectivity'] = np.nan

    def get_sentiment(text):
        if not isinstance(text, str) or not text.strip():
            return 0.0, 0.0
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity, blob.sentiment.subjectivity
        except Exception as e:
            logger.warning(f"Error analyzing sentiment: {e}")
            return 0.0, 0.0

    # Apply sentiment analysis
    for idx, row in df.iterrows():
        text = row.get('content') or row.get('description') or row.get('title')
        polarity, subjectivity = get_sentiment(text)
        df.at[idx, 'polarity'] = polarity
        df.at[idx, 'subjectivity'] = subjectivity

    # Classify sentiment category
    df['sentiment_category'] = pd.cut(
        df['polarity'],
        bins=[-1.1, -0.5, -0.1, 0.1, 0.5, 1.1],
        labels=['Very Negative', 'Negative', 'Neutral', 'Positive', 'Very Positive']
    )

    logger.info(f"Sentiment analysis completed for {len(df)} articles.")
    return df

def aggregate_sentiment(articles_with_sentiment):
    """
    Aggregate sentiment scores by date.

    Args:
        articles_with_sentiment (pandas.DataFrame): DataFrame containing articles with sentiment scores

    Returns:
        pandas.DataFrame: DataFrame with aggregated sentiment scores by date
    """
    if articles_with_sentiment is None or articles_with_sentiment.empty:
        logger.warning("No sentiment data to aggregate.")
        return None

    logger.info("Aggregating sentiment data by date...")

    # Ensure 'date' is in datetime format
    if 'date' in articles_with_sentiment.columns:
        articles_with_sentiment['date'] = pd.to_datetime(articles_with_sentiment['date'])

    logger.info(f"Articles date range: {articles_with_sentiment['date'].min()} to {articles_with_sentiment['date'].max()}")
    logger.info(f"Total articles by date: {articles_with_sentiment.groupby('date').size().to_dict()}")

    # Aggregate numeric sentiment features
    aggregated = articles_with_sentiment.groupby(pd.Grouper(key='date', freq='h')).agg(
        avg_polarity=('polarity', 'mean'),
        avg_subjectivity=('subjectivity', 'mean'),
        max_polarity=('polarity', 'max'),
        min_polarity=('polarity', 'min'),
        article_count=('polarity', 'count')
    ).reset_index()

    # Add polarity volatility
    volatility = articles_with_sentiment.groupby(pd.Grouper(key='date', freq='h'))['polarity'].std().reset_index()
    volatility.columns = ['date', 'polarity_volatility']
    aggregated = pd.merge(aggregated, volatility, on='date', how='left')
    aggregated['polarity_volatility'] = aggregated['polarity_volatility'].fillna(0)

    # Add sentiment category distribution (as percentages)
    sentiment_distribution = (
        articles_with_sentiment
        .groupby([pd.Grouper(key='date', freq='h'), 'sentiment_category'], observed=True)
        .size()
        .unstack(fill_value=0)
    )
    for category in sentiment_distribution.columns:
        sentiment_distribution[f'{category}_pct'] = sentiment_distribution[category] / sentiment_distribution.sum(axis=1) * 100
    sentiment_distribution = sentiment_distribution[[col for col in sentiment_distribution.columns if '_pct' in col]]
    sentiment_distribution = sentiment_distribution.reset_index()

    aggregated = pd.merge(aggregated, sentiment_distribution, on='date', how='left')

    # Ensure full hourly continuity using interpolation
    aggregated['date'] = pd.to_datetime(aggregated['date'])
    min_date = aggregated['date'].min()
    max_date = aggregated['date'].max()
    full_dates = pd.date_range(start=min_date, end=max_date, freq='h')
    full_df = pd.DataFrame({'date': full_dates})

    # Merge and interpolate missing values
    aggregated = pd.merge(full_df, aggregated, on='date', how='left')
    aggregated = aggregated.set_index('date')
    aggregated = aggregated.ffill().bfill().reset_index()
    aggregated = aggregated.sort_values('date')

    logger.info(f"Interpolated data covers {len(aggregated)} hours from {min_date} to {max_date}")
    logger.info(f"Sentiment aggregation completed for {len(aggregated)} hours.")

    return aggregated


def prepare_time_series_data(sentiment_data, price_data):
    """
    Prepare time series data by merging sentiment and price data.

    Args:
        sentiment_data (pandas.DataFrame): DataFrame with aggregated sentiment scores by date
        price_data (pandas.DataFrame): DataFrame with Bitcoin price data by date

    Returns:
        pandas.DataFrame: Merged DataFrame with aligned sentiment and price data
    """
    if sentiment_data is None or price_data is None:
        logger.warning("Missing data for time series preparation.")
        return None

    logger.info("Preparing time series data...")

    try:
        # Ensure date columns are in datetime format
        sentiment_data['date'] = pd.to_datetime(sentiment_data['date'])
        price_data['date'] = pd.to_datetime(price_data['date'])

        logger.info(f"Sentiment date range: {sentiment_data['date'].min()} to {sentiment_data['date'].max()}")
        logger.info(f"Price date range: {price_data['date'].min()} to {price_data['date'].max()}")

        # Identify common dates
        common_dates = set(sentiment_data['date']).intersection(set(price_data['date']))

        if not common_dates:
            logger.info("No exact overlap — using forward fill merge strategy.")
            all_dates = pd.date_range(
                start=min(sentiment_data['date'].min(), price_data['date'].min()),
                end=max(sentiment_data['date'].max(), price_data['date'].max())
            )

            date_df = pd.DataFrame({'date': all_dates})
            sentiment_filled = pd.merge(date_df, sentiment_data, on='date', how='left').ffill()
            merged_data = pd.merge(sentiment_filled, price_data, on='date', how='inner')

            if merged_data.empty:
                logger.warning("Forward fill failed — trying backward fill.")
                sentiment_filled = pd.merge(date_df, sentiment_data, on='date', how='left').bfill()
                merged_data = pd.merge(sentiment_filled, price_data, on='date', how='inner')

                if merged_data.empty:
                    if not sentiment_data.empty and not price_data.empty:
                        latest_sentiment = sentiment_data.iloc[-1].drop('date')
                        merged_data = price_data.copy()
                        for col, val in latest_sentiment.items():
                            merged_data[col] = val
                    else:
                        logger.warning("No usable sentiment or price data.")
                        return None
        else:
            merged_data = pd.merge(sentiment_data, price_data, on='date', how='inner')

        # Ensure consistent 'price' column
        merged_data['price'] = merged_data['close_price']

        # Handle missing columns
        if 'article_count' not in merged_data.columns:
            merged_data['article_count'] = 1
        if 'polarity_volatility' not in merged_data.columns:
            merged_data['polarity_volatility'] = (
                merged_data['avg_polarity'].rolling(window=min(3, len(merged_data))).std().fillna(0)
                if len(merged_data) >= 3 else 0
            )

        # Feature engineering
        if len(merged_data) > 1:
            merged_data['price_lag1'] = merged_data['close_price'].shift(1)
            merged_data['polarity_lag1'] = merged_data['avg_polarity'].shift(1)
            merged_data['price_momentum'] = merged_data['close_price'] - merged_data['price_lag1']
            merged_data['sentiment_momentum'] = merged_data['avg_polarity'] - merged_data['polarity_lag1']
            merged_data['price_volatility'] = (
                (merged_data['high_price'] - merged_data['low_price']) / merged_data['close_price']
            )

            if len(merged_data) > 2:
                merged_data = merged_data.dropna()

        merged_data = merged_data.sort_values('date')
        logger.info(f"Time series data prepared with {len(merged_data)} days.")
        return merged_data

    except Exception as e:
        logger.error(f"Error preparing time series data: {str(e)}")
        logger.error(f"Error in prepare_time_series_data: {str(e)}")
        return None
    

def extrapolate_future_exog(merged_data, forecast_hours=24, window=3):
    """
    Extrapolate future exogenous features based on the recent trend.

    Returns:
        np.ndarray: Forecast exog matrix for future steps
    """
    exog_cols = ['avg_polarity', 'polarity_volatility']
    last_n = merged_data[exog_cols].tail(window).values

    # Calculate average slope for each feature
    slope = (last_n[-1] - last_n[0]) / (window - 1)

    # Extrapolate linearly across forecast steps
    future_exog = np.array([last_n[-1] + i * slope for i in range(1, forecast_hours + 1)])
    return future_exog    

def run_forecast(merged_data, forecast_hours=(24*7)):
    """
    Run time series forecasting on the merged data with improved ARIMA consistency.

    Args:
        merged_data (pandas.DataFrame): DataFrame with merged sentiment and price data
        forecast_hours (int): Number of hours to forecast ahead

    Returns:
        pandas.DataFrame: DataFrame with actual and forecasted values + future forecast as attribute
    """
    if merged_data is None or len(merged_data) < 24:
        logger.warning("Insufficient data for forecasting. Need at least 24 hours of data.")
        return None

    logger.info("Running time series forecasting (hourly)...")

    try:
        # Train-test split with minimum test size
        train_size = max(int(len(merged_data) * 0.8), len(merged_data) - forecast_hours)
        train_data = merged_data.iloc[:train_size]
        test_data = merged_data.iloc[train_size:]

        y_train = train_data['close_price'].values
        y_test = test_data['close_price'].values

        X_train = train_data[['avg_polarity', 'polarity_volatility']].values
        X_test = test_data[['avg_polarity', 'polarity_volatility']].values



        def find_best_arima_params(y, max_p=10, max_d=2, max_q=5, use_mape=True):
            """
            Find optimal ARIMA parameters using AIC and optionally MAPE on validation split.

            Args:
                y (array-like): Time series
                max_p (int): Max AR order
                max_d (int): Max differencing
                max_q (int): Max MA order
                use_mape (bool): If True, prefer lower MAPE over lower AIC

            Returns:
                tuple: (best_p, best_d, best_q)
            """
            best_score = float('inf')
            best_params = None

            # Train/validation split (last 20%)
            split = int(len(y) * 0.9)
            y_train, y_val = y[:split], y[split:]

            for p in range(max_p + 1):
                for d in range(max_d + 1):
                    for q in range(max_q + 1):
                        try:
                            model = ARIMA(y_train, order=(p, d, q), enforce_stationarity=False, enforce_invertibility=False)
                            result = model.fit()

                            # Forecast on validation set
                            forecast = result.forecast(steps=len(y_val))
                            if not np.all(np.isfinite(forecast)):
                                continue

                            mape = mean_absolute_percentage_error(y_val, forecast) * 100
                            score = mape if use_mape else result.aic

                            if score < best_score:
                                best_score = score
                                best_params = (p, d, q)

                        except Exception:
                            continue

            return best_params
        # def find_best_arima_params(y, max_p=5, max_d=2, max_q=5):
        #     """Find optimal ARIMA parameters using AIC"""
        #     best_aic = float('inf')
        #     best_params = None
            
        #     for p in range(max_p + 1):
        #         for d in range(max_d + 1):
        #             for q in range(max_q + 1):
        #                 try:
        #                     model = ARIMA(y, order=(p, d, q))
        #                     results = model.fit()
        #                     if results.aic < best_aic:
        #                         best_aic = results.aic
        #                         best_params = (p, d, q)
        #                 except:
        #                     continue
        #     return best_params

        try:
            # Find optimal ARIMA parameters
            # best_params = find_best_arima_params(y_train)
            # if best_params is None:
            #     best_params = (1, 1, 0)  # Default fallback
            best_params = (5, 2, 2)  
            # best_params = (0,2, 2)     
            logger.info(f"Using ARIMA parameters: {best_params}")
            
            # ARIMAX Model with optimal parameters
            model = ARIMA(y_train, exog=X_train, order=best_params)
            fitted_model = model.fit()

            # Validate model assumptions
            residuals = fitted_model.resid
            if not np.all(np.isfinite(residuals)):
                raise ValueError("Model residuals contain non-finite values")

            # Make predictions
            predictions = fitted_model.forecast(steps=len(test_data), exog=X_test)

            # Calculate error metrics
            mape = mean_absolute_percentage_error(y_test, predictions) * 100
            rmse = np.sqrt(mean_squared_error(y_test, predictions))
            
            # Validate predictions
            if not np.all(np.isfinite(predictions)):
                raise ValueError("Predictions contain non-finite values")
                
            logger.info(f"Model MAPE: {mape:.2f}%")
            logger.info(f"Model RMSE: {rmse:.2f}")

            
            last_rows = merged_data[['avg_polarity', 'polarity_volatility']].tail(3).values
            avg_slope = (last_rows[-1] - last_rows[0]) / 2
            

            # rolling_sentiment = merged_data[['avg_polarity', 'polarity_volatility']].rolling(window=3).mean().iloc[-1].values
            # future_exog = np.tile(rolling_sentiment, (forecast_hours, 1))
            future_exog = extrapolate_future_exog(merged_data, forecast_hours=forecast_hours, window=3)
            exog_cols = ['avg_polarity', 'polarity_volatility']
            future_exog = np.clip(future_exog, a_min=merged_data[exog_cols].quantile(0.25).values, a_max=None)
            # future_exog = np.array([
            #     last_rows[-1] + (i * avg_slope)
            #     for i in range(1, forecast_hours + 1)
            # ])
            

            # Prepare future forecast
            # rolling_sentiment = merged_data[['avg_polarity', 'polarity_volatility']].rolling(window=3).mean().iloc[-1].values
            # future_exog = np.tile(rolling_sentiment, (forecast_hours, 1))
            future_predictions = fitted_model.forecast(steps=forecast_hours, exog=future_exog)

            # Validate future predictions
            if not np.all(np.isfinite(future_predictions)):
                raise ValueError("Future predictions contain non-finite values")

            # Generate future hourly timestamps
            last_date = merged_data['date'].iloc[-1]
            dates = pd.date_range(start=last_date + pd.Timedelta(hours=1), periods=forecast_hours, freq='h')
            future_forecast = pd.DataFrame({'date': dates, 'predicted_price': future_predictions})

            forecast_results = pd.DataFrame({
                'date': test_data['date'].values,
                'actual_price': y_test,
                'predicted_price': predictions,
                'avg_polarity': test_data['avg_polarity'].values
            })

            # Add confidence intervals
            forecast_results['upper_ci'] = forecast_results['predicted_price'] + 1.96 * rmse
            forecast_results['lower_ci'] = forecast_results['predicted_price'] - 1.96 * rmse
            forecast_results['mape'] = mape
            forecast_results['rmse'] = rmse

            logger.info("Forecast completed successfully (hourly).")
            return forecast_results, future_forecast

        except Exception as e:
            logger.warning(f"ARIMAX failed: {str(e)}. Using ARIMA fallback...")

            # Use same optimal parameters for fallback
            model = ARIMA(y_train, order=best_params if 'best_params' in locals() else (1, 1, 0))
            fitted_model = model.fit()

            predictions = fitted_model.forecast(steps=len(test_data))
            mape = mean_absolute_percentage_error(y_test, predictions) * 100
            rmse = np.sqrt(mean_squared_error(y_test, predictions))

            future_predictions = fitted_model.forecast(steps=forecast_hours)
            last_date = merged_data['date'].iloc[-1]
            dates = pd.date_range(start=last_date + pd.Timedelta(hours=1), periods=forecast_hours, freq='h')
            future_forecast = pd.DataFrame({'date': dates, 'predicted_price': future_predictions})

            forecast_results = pd.DataFrame({
                'date': test_data['date'].values,
                'actual_price': y_test,
                'predicted_price': predictions,
                'avg_polarity': test_data['avg_polarity'].values
            })

            forecast_results['upper_ci'] = forecast_results['predicted_price'] + 1.96 * rmse
            forecast_results['lower_ci'] = forecast_results['predicted_price'] - 1.96 * rmse
            forecast_results['mape'] = mape
            forecast_results['rmse'] = rmse

            logger.info("Forecast completed with fallback model (hourly).")
            return forecast_results, future_forecast

    except Exception as e:
        logger.error(f"Error running forecast: {str(e)}")
        return None, None
    

def compare_historical_sentiment(base_date, comparison_date, sentiment_df, price_df):
    """
    Compare sentiment and price data between two dates to find patterns.

    Args:
        base_date (str): Base date in 'YYYY-MM-DD' format
        comparison_date (str): Date to compare against in 'YYYY-MM-DD' format
        sentiment_df (pandas.DataFrame): DataFrame containing aggregated sentiment data
        price_df (pandas.DataFrame): DataFrame containing price data

    Returns:
        dict or None: Dictionary with comparison metrics, or None if data is missing
    """
    try:
        base_date_obj = pd.to_datetime(base_date).date()
        comparison_date_obj = pd.to_datetime(comparison_date).date()

        # Ensure date columns are in datetime.date format
        sentiment_df['date'] = pd.to_datetime(sentiment_df['date']).dt.date
        price_df['date'] = pd.to_datetime(price_df['date']).dt.date

        # Lookup rows
        base_sentiment = sentiment_df[sentiment_df['date'] == base_date_obj]
        comparison_sentiment = sentiment_df[sentiment_df['date'] == comparison_date_obj]
        base_price = price_df[price_df['date'] == base_date_obj]
        comparison_price = price_df[price_df['date'] == comparison_date_obj]

        if base_sentiment.empty or comparison_sentiment.empty or base_price.empty or comparison_price.empty:
            logger.warning(f"Missing data for comparison between {base_date} and {comparison_date}")
            return None

        # Extract values
        base_sentiment = base_sentiment.iloc[0]
        comparison_sentiment = comparison_sentiment.iloc[0]
        base_price = base_price.iloc[0]
        comparison_price = comparison_price.iloc[0]

        price_difference = base_price['close_price'] - comparison_price['close_price']
        price_pct_change = (price_difference / comparison_price['close_price']) * 100

        sentiment_difference = base_sentiment['avg_polarity'] - comparison_sentiment['avg_polarity']
        sentiment_pct_change = (
            (sentiment_difference / abs(comparison_sentiment['avg_polarity'])) * 100
            if comparison_sentiment['avg_polarity'] != 0 else
            float('inf') if sentiment_difference > 0 else float('-inf') if sentiment_difference < 0 else 0
        )

        # Correlation direction
        correlation_coefficient = 1.0 if (
            (price_difference > 0 and sentiment_difference > 0) or
            (price_difference < 0 and sentiment_difference < 0)
        ) else -1.0

        categories = ['Very Negative', 'Negative', 'Neutral', 'Positive', 'Very Positive']
        total_diff = 0

        for category in categories:
            base_val = base_sentiment.get(f'{category}_pct', 0.0)
            comp_val = comparison_sentiment.get(f'{category}_pct', 0.0)
            total_diff += abs(base_val - comp_val)

        pattern_similarity = 1 - (total_diff / 500)

        return {
            'base_date': base_date,
            'comparison_date': comparison_date,
            'price_difference': price_difference,
            'price_pct_change': price_pct_change,
            'sentiment_difference': sentiment_difference,
            'sentiment_pct_change': sentiment_pct_change,
            'correlation_coefficient': correlation_coefficient,
            'pattern_similarity': pattern_similarity
        }

    except Exception as e:
        logger.error(f"Error comparing historical sentiment: {str(e)}")
        return None

def update_data_file(new_data, filename, unique_col='date'):
    """
    Update a CSV file with new data, appending only new rows and avoiding duplicates based on a unique column.
    Args:
        new_data (pd.DataFrame): Newly fetched data to append
        filename (str): Path to the CSV file to update
        unique_col (str): Column to use for identifying duplicates (default 'date')
    Returns:
        pd.DataFrame: The updated DataFrame
    """
    import os
    import pandas as pd
    if os.path.exists(filename):
        existing_df = pd.read_csv(filename, parse_dates=[unique_col])
    else:
        existing_df = pd.DataFrame()
    if not existing_df.empty:
        combined_df = pd.concat([existing_df, new_data], ignore_index=True)
    else:
        combined_df = new_data.copy()
    combined_df = combined_df.drop_duplicates(subset=unique_col, keep='last')
    combined_df = combined_df.sort_values(unique_col)
    combined_df.to_csv(filename, index=False)
    return combined_df