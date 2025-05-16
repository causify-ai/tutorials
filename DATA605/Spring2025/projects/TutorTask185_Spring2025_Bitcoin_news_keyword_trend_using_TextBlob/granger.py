import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import grangercausalitytests, adfuller
from statsmodels.tools.sm_exceptions import MissingDataError
import os
import warnings
import matplotlib.pyplot as plt
import seaborn as sns

def run_stationarity_test(series):
    """
    Test if a time series is stationary using the Augmented Dickey-Fuller test.
    
    Args:
        series (array-like): The time series to test
        
    Returns:
        tuple: (is_stationary, p_value)
    """
    # Handle special cases
    if len(series) < 5:  # Need enough data points
        return False, 1.0
    if len(np.unique(series)) < 2:  # Constant series
        return False, 1.0
        
    try:
        # Run ADF test
        result = adfuller(series, autolag='AIC')
        p_value = result[1]
        return p_value < 0.05, p_value
    except Exception as e:
        print(f"\u26A0\uFE0F Error in stationarity test: {str(e)}")
        return False, 1.0

def make_stationary(series):
    """
    Transform a series to make it stationary.
    First tries differencing, then differencing of logs if needed.
    
    Args:
        series (array-like): The time series to transform
        
    Returns:
        array: The stationary series, or the original if transformation failed
    """
    # Check if already stationary
    is_stationary, _ = run_stationarity_test(series)
    if is_stationary:
        return series
        
    # Try first differencing
    diff = np.diff(series)
    is_stationary, _ = run_stationarity_test(diff)
    if is_stationary:
        return diff
        
    # Try log transform + differencing for non-negative series
    if np.all(series > 0):
        try:
            log_diff = np.diff(np.log(series))
            is_stationary, _ = run_stationarity_test(log_diff)
            if is_stationary:
                return log_diff
        except Exception:
            pass
            
    # Return original differenced series as fallback
    return diff

def run_granger_tests(top_n=10, max_lag=3, min_data_points=10):
    """
    Perform Granger causality tests between keyword frequencies and price changes.
    
    Args:
        top_n (int): Number of top keywords to analyze
        max_lag (int): Maximum lag to test for causality
        min_data_points (int): Minimum number of data points required for testing
    """
    try:
        # Load data
        if not os.path.exists('data/merged_keyword_price.csv'):
            print("\u274c No merged data found. Please run analyze_trends() first.")
            return None
            
        df = pd.read_csv('data/merged_keyword_price.csv')
        
        # Convert date column
        df['time_window'] = pd.to_datetime(df['time_window'])
        
        # Get top N keywords by frequency
        keyword_counts = df['keyword'].value_counts()
        print(f"\ud83d\udcca Found {len(keyword_counts)} unique keywords")
        print(f"\ud83d\udcca Top keywords by frequency: {', '.join(keyword_counts.nlargest(min(10, len(keyword_counts))).index.tolist())}")
        
        top_keywords = keyword_counts.nlargest(top_n).index.tolist()
        
        # Store results
        results = []
        
        # Process each keyword
        for i, keyword in enumerate(top_keywords):
            # Filter data for this keyword
            keyword_data = df[df['keyword'] == keyword].sort_values('time_window')
            
            # Skip if not enough data points
            if len(keyword_data) < min_data_points:
                print(f"\u26A0\uFE0F Skipping '{keyword}': only {len(keyword_data)} data points (need {min_data_points})")
                continue
                
            # Prepare time series
            keyword_series = keyword_data['count'].values
            price_series = keyword_data['price'].values
            
            # Check stationarity
            kw_stationary, kw_p = run_stationarity_test(keyword_series)
            price_stationary, price_p = run_stationarity_test(price_series)
            
            if not kw_stationary:
                print(f"\ud83d\udcca '{keyword}' frequency is not stationary (p={kw_p:.4f}), applying transformation")
                keyword_series = make_stationary(keyword_series)
                
            if not price_stationary:
                print(f"\ud83d\udcca Price series for '{keyword}' is not stationary (p={price_p:.4f}), applying transformation")
                price_series = make_stationary(price_series)
            
            # Make sure we still have enough data after transformations
            if len(keyword_series) < min_data_points or len(price_series) < min_data_points:
                print(f"\u26A0\uFE0F Skipping '{keyword}': insufficient data after transformations")
                continue
                
            # Create DataFrame for Granger test with equal length series
            min_len = min(len(keyword_series), len(price_series))
            test_data = pd.DataFrame({
                'keyword': keyword_series[:min_len],
                'price': price_series[:min_len]
            })
            
            # Calculate correlation
            correlation = test_data['keyword'].corr(test_data['price'])
            
            # Perform Granger causality tests
            try:
                # Test if keywords Granger-cause price changes
                print(f"\ud83d\udcca Testing if '{keyword}' Granger-causes price changes...")
                keyword_to_price = grangercausalitytests(
                    test_data[['price', 'keyword']],
                    maxlag=min(max_lag, len(test_data)//3),  # Ensure we don't use too many lags
                    verbose=False
                )
                
                # Test if price changes Granger-cause keywords
                print(f"\ud83d\udcca Testing if price changes Granger-cause '{keyword}'...")
                price_to_keyword = grangercausalitytests(
                    test_data[['keyword', 'price']],
                    maxlag=min(max_lag, len(test_data)//3),
                    verbose=False
                )
                
                # Get best lag results
                best_lag_k2p = max(
                    range(1, min(max_lag, len(test_data)//3) + 1),
                    key=lambda x: 1 - keyword_to_price[x][0]['ssr_chi2test'][1]
                )
                
                best_lag_p2k = max(
                    range(1, min(max_lag, len(test_data)//3) + 1),
                    key=lambda x: 1 - price_to_keyword[x][0]['ssr_chi2test'][1]
                )
                
                # Get p-values for best lags
                k2p_pvalue = keyword_to_price[best_lag_k2p][0]['ssr_chi2test'][1]
                p2k_pvalue = price_to_keyword[best_lag_p2k][0]['ssr_chi2test'][1]
                
                # Add results
                results.append({
                    'keyword': keyword,
                    'data_points': len(test_data),
                    'correlation': correlation,
                    'best_lag_k2p': best_lag_k2p,
                    'best_lag_p2k': best_lag_p2k,
                    'k2p_pvalue': k2p_pvalue,
                    'p2k_pvalue': p2k_pvalue,
                    'k2p_significant': k2p_pvalue < 0.05,
                    'p2k_significant': p2k_pvalue < 0.05
                })
                
                print(f"\u2705 Tested '{keyword}': K→P p-value={k2p_pvalue:.4f}, P→K p-value={p2k_pvalue:.4f}")
                
            except (Exception, MissingDataError) as e:
                print(f"\u26A0\uFE0F Error testing '{keyword}': {str(e)}")
                continue
        
        if not results:
            print("\u274c No valid Granger causality tests could be performed")
            return None
            
        # Create results DataFrame
        results_df = pd.DataFrame(results)
        
        # Save results
        results_df.to_csv('data/granger_causality_results.csv', index=False)
        
        # Print summary
        print("\n\ud83d\udcca Granger Causality Test Results")
        print("="*60)
        
        # Summary of significant relationships
        k2p_sig = results_df[results_df['k2p_significant']]['keyword'].tolist()
        p2k_sig = results_df[results_df['p2k_significant']]['keyword'].tolist()
        
        if k2p_sig:
            print(f"\n\ud83d\udcca Keywords that Granger-cause price changes: {', '.join(k2p_sig)}")
        else:
            print("\n\ud83d\udcca No keywords were found to Granger-cause price changes")
            
        if p2k_sig:
            print(f"\ud83d\udcca Price changes Granger-cause these keywords: {', '.join(p2k_sig)}")
        else:
            print("\ud83d\udcca No keywords were found to be Granger-caused by price changes")
            
        # Detailed results
        print("\nDetailed results by keyword:")
        for _, row in results_df.iterrows():
            print(f"\n- {row['keyword']} (correlation: {row['correlation']:.3f})")
            k2p_result = "→ Significant \u2705" if row['k2p_significant'] else "→ Not significant"
            p2k_result = "→ Significant \u2705" if row['p2k_significant'] else "→ Not significant"
            print(f"  Keywords → Price: p-value = {row['k2p_pvalue']:.4f}, lag = {row['best_lag_k2p']} {k2p_result}")
            print(f"  Price → Keywords: p-value = {row['p2k_pvalue']:.4f}, lag = {row['best_lag_p2k']} {p2k_result}")
            
        # Generate visualization if possible
        try:
            fig, axs = plt.subplots(1, 2, figsize=(16, 6))
            
            # Sort by p-value
            k2p_df = results_df.sort_values('k2p_pvalue').head(10)
            p2k_df = results_df.sort_values('p2k_pvalue').head(10)
            
            # Plot K2P
            sns.barplot(y='keyword', x='k2p_pvalue', data=k2p_df, ax=axs[0])
            axs[0].axvline(0.05, color='red', linestyle='--')
            axs[0].set_xlabel('p-value')
            axs[0].set_title('Keywords → Price')
            
            # Plot P2K
            sns.barplot(y='keyword', x='p2k_pvalue', data=p2k_df, ax=axs[1])
            axs[1].axvline(0.05, color='red', linestyle='--')
            axs[1].set_xlabel('p-value')
            axs[1].set_title('Price → Keywords')
            
            plt.tight_layout()
            os.makedirs('figures', exist_ok=True)
            plt.savefig('figures/granger_causality_tests.png')
            print("\n\u2705 Saved Granger causality visualization to figures/granger_causality_tests.png")
            
        except Exception as e:
            print(f"\u26A0\uFE0F Could not generate visualization: {str(e)}")
            
        return results_df
        
    except Exception as e:
        print(f"\u274c Error performing Granger causality tests: {str(e)}")
        return None

if __name__ == "__main__":
    # Test the function
    run_granger_tests()
