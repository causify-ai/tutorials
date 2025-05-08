import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import grangercausalitytests
import os
import warnings

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
            print("❌ No merged data found. Please run analyze_trends() first.")
            return None
            
        df = pd.read_csv('data/merged_keyword_price.csv')
        
        # Convert date column
        df['time_window'] = pd.to_datetime(df['time_window'])
        
        # Get top N keywords by frequency
        top_keywords = df['keyword'].value_counts().nlargest(top_n).index.tolist()
        
        # Store results
        results = []
        
        for keyword in top_keywords:
            # Filter data for this keyword
            keyword_data = df[df['keyword'] == keyword].sort_values('time_window')
            
            # Skip if not enough data points
            if len(keyword_data) < min_data_points:
                continue
                
            # Prepare time series
            keyword_series = keyword_data['count'].values
            price_series = keyword_data['price'].values
            
            # Calculate price changes
            price_changes = np.diff(price_series)
            keyword_changes = np.diff(keyword_series)
            
            # Create DataFrame for Granger test
            test_data = pd.DataFrame({
                'keyword': keyword_changes,
                'price': price_changes
            })
            
            # Perform Granger causality tests
            try:
                # Test if keywords Granger-cause price changes
                keyword_to_price = grangercausalitytests(
                    test_data[['price', 'keyword']],
                    maxlag=max_lag,
                    verbose=False
                )
                
                # Test if price changes Granger-cause keywords
                price_to_keyword = grangercausalitytests(
                    test_data[['keyword', 'price']],
                    maxlag=max_lag,
                    verbose=False
                )
                
                # Get best lag for each direction
                best_lag_k2p = max(
                    range(1, max_lag + 1),
                    key=lambda x: 1 - keyword_to_price[x][0]['ssr_chi2test'][1]
                )
                best_lag_p2k = max(
                    range(1, max_lag + 1),
                    key=lambda x: 1 - price_to_keyword[x][0]['ssr_chi2test'][1]
                )
                
                # Get p-values for best lags
                k2p_pvalue = keyword_to_price[best_lag_k2p][0]['ssr_chi2test'][1]
                p2k_pvalue = price_to_keyword[best_lag_p2k][0]['ssr_chi2test'][1]
                
                # Add results
                results.append({
                    'keyword': keyword,
                    'best_lag_k2p': best_lag_k2p,
                    'best_lag_p2k': best_lag_p2k,
                    'k2p_pvalue': k2p_pvalue,
                    'p2k_pvalue': p2k_pvalue,
                    'k2p_significant': k2p_pvalue < 0.05,
                    'p2k_significant': p2k_pvalue < 0.05
                })
                
            except Exception as e:
                print(f"⚠️ Error testing {keyword}: {str(e)}")
                continue
        
        if not results:
            print("❌ No valid Granger causality tests could be performed")
            return None
            
        # Create results DataFrame
        results_df = pd.DataFrame(results)
        
        # Save results
        results_df.to_csv('data/granger_causality_results.csv', index=False)
        
        # Print summary
        print("\n📊 Granger Causality Test Results")
        print("="*60)
        
        for _, row in results_df.iterrows():
            print(f"\nKeyword: {row['keyword']}")
            print(f"Keywords → Price: p-value = {row['k2p_pvalue']:.4f} (significant: {row['k2p_significant']})")
            print(f"Price → Keywords: p-value = {row['p2k_pvalue']:.4f} (significant: {row['p2k_significant']})")
            
        return results_df
        
    except Exception as e:
        print(f"❌ Error performing Granger causality tests: {str(e)}")
        return None

if __name__ == "__main__":
    # Test the function
    run_granger_tests()
