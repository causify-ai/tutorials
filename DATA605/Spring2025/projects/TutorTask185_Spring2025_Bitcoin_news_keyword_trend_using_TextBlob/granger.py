import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import grangercausalitytests, adfuller
from statsmodels.tools.sm_exceptions import MissingDataError
import os
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

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

def run_granger_tests(top_n=10, max_lag=7, min_data_points=20):
    """
    Perform Granger causality tests between keyword frequencies and price changes.
    
    Args:
        top_n (int): Number of top keywords to analyze
        max_lag (int): Maximum lag to test for causality (will test lags 1 to max_lag)
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
        # Store results for each lag
        all_lag_results = []
        
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
                # Determine maximum lag for tests based on data availability
                # Use rule of thumb: max lag should not exceed 1/3 of available data points
                effective_max_lag = min(max_lag, len(test_data)//3)
                
                if effective_max_lag < 1:
                    print(f"\u26A0\uFE0F Skipping '{keyword}': insufficient data for lag testing")
                    continue
                    
                print(f"\ud83d\udcca Testing if '{keyword}' Granger-causes price changes with {effective_max_lag} lags...")
                
                # Test if keywords Granger-cause price changes
                keyword_to_price = grangercausalitytests(
                    test_data[['price', 'keyword']],
                    maxlag=effective_max_lag,
                    verbose=False
                )
                
                # Test if price changes Granger-cause keywords
                print(f"\ud83d\udcca Testing if price changes Granger-cause '{keyword}'...")
                price_to_keyword = grangercausalitytests(
                    test_data[['keyword', 'price']],
                    maxlag=effective_max_lag,
                    verbose=False
                )
                
                # Store results for each lag
                for lag in range(1, effective_max_lag + 1):
                    # Get p-values for this lag for both directions
                    k2p_pvalue = keyword_to_price[lag][0]['ssr_chi2test'][1]
                    p2k_pvalue = price_to_keyword[lag][0]['ssr_chi2test'][1]
                    
                    # Store individual lag results
                    all_lag_results.append({
                        'keyword': keyword,
                        'lag': lag,
                        'data_points': len(test_data),
                        'correlation': correlation,
                        'k2p_pvalue': k2p_pvalue,
                        'p2k_pvalue': p2k_pvalue,
                        'k2p_significant': k2p_pvalue < 0.05,
                        'p2k_significant': p2k_pvalue < 0.05
                    })
                
                # Find the best lag (lowest p-value) for each direction
                best_lag_k2p = min(
                    range(1, effective_max_lag + 1),
                    key=lambda x: keyword_to_price[x][0]['ssr_chi2test'][1]
                )
                
                best_lag_p2k = min(
                    range(1, effective_max_lag + 1),
                    key=lambda x: price_to_keyword[x][0]['ssr_chi2test'][1]
                )
                
                # Get p-values for best lags
                k2p_pvalue = keyword_to_price[best_lag_k2p][0]['ssr_chi2test'][1]
                p2k_pvalue = price_to_keyword[best_lag_p2k][0]['ssr_chi2test'][1]
                
                # Add summarized results
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
                
                print(f"\u2705 Tested '{keyword}': Best results - K→P p-value={k2p_pvalue:.4f} (lag {best_lag_k2p}), P→K p-value={p2k_pvalue:.4f} (lag {best_lag_p2k})")
                
            except (Exception, MissingDataError) as e:
                print(f"\u26A0\uFE0F Error testing '{keyword}': {str(e)}")
                continue
        
        if not results:
            print("\u274c No valid Granger causality tests could be performed")
            return None
            
        # Create results DataFrame
        results_df = pd.DataFrame(results)
        
        # Create detailed lag results DataFrame
        all_lag_results_df = pd.DataFrame(all_lag_results)
        
        # Save results
        os.makedirs('data', exist_ok=True)
        results_df.to_csv('data/granger_causality_results.csv', index=False)
        all_lag_results_df.to_csv('data/granger_causality_detailed_results.csv', index=False)
        
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
            # Create a more comprehensive visualization showing lags
            plt.figure(figsize=(16, 12))
            
            # Chart 1: Best K2P p-values by keyword
            plt.subplot(2, 2, 1)
            best_k2p_df = results_df.sort_values('k2p_pvalue').head(10)
            sns.barplot(y='keyword', x='k2p_pvalue', data=best_k2p_df)
            plt.axvline(0.05, color='red', linestyle='--')
            plt.xlabel('p-value')
            plt.title('Best Keywords → Price p-values')
            
            # Chart 2: Best P2K p-values by keyword
            plt.subplot(2, 2, 2)
            best_p2k_df = results_df.sort_values('p2k_pvalue').head(10)
            sns.barplot(y='keyword', x='p2k_pvalue', data=best_p2k_df)
            plt.axvline(0.05, color='red', linestyle='--')
            plt.xlabel('p-value')
            plt.title('Best Price → Keywords p-values')
            
            # Chart 3: P-values across lags for top significant keywords (K2P)
            plt.subplot(2, 2, 3)
            
            # Get significant keywords
            sig_keywords = results_df[results_df['k2p_significant']]['keyword'].unique().tolist()
            
            # If no significant keywords, use the top 3 lowest p-value keywords
            if not sig_keywords:
                sig_keywords = results_df.nsmallest(3, 'k2p_pvalue')['keyword'].tolist()
                
            # Filter lag data for these keywords
            sig_lag_data = all_lag_results_df[all_lag_results_df['keyword'].isin(sig_keywords)]
            
            if not sig_lag_data.empty:
                # Plot line chart of p-values across lags
                for keyword in sig_keywords:
                    keyword_data = sig_lag_data[sig_lag_data['keyword'] == keyword]
                    if not keyword_data.empty:
                        plt.plot(keyword_data['lag'], keyword_data['k2p_pvalue'], marker='o', label=keyword)
                
                plt.axhline(0.05, color='red', linestyle='--')
                plt.title('Keywords → Price: p-values across lags')
                plt.xlabel('Lag')
                plt.ylabel('p-value')
                plt.legend()
                plt.grid(alpha=0.3)
            else:
                plt.text(0.5, 0.5, 'No significant relationships found', 
                         horizontalalignment='center', verticalalignment='center')
            
            # Chart 4: Lag vs. p-value heatmap for top keywords
            plt.subplot(2, 2, 4)
            
            # Select top keywords for heatmap (either significant or lowest p-value)
            heatmap_keywords = results_df.nsmallest(5, 'k2p_pvalue')['keyword'].tolist()
            heatmap_data = all_lag_results_df[all_lag_results_df['keyword'].isin(heatmap_keywords)]
            
            if not heatmap_data.empty and len(heatmap_data['lag'].unique()) > 1:
                # Reshape data for heatmap
                heatmap_df = heatmap_data.pivot(index='keyword', columns='lag', values='k2p_pvalue')
                # Plot heatmap
                sns.heatmap(heatmap_df, cmap='YlOrRd_r', vmin=0, vmax=0.25, annot=True, fmt='.3f')
                plt.title('Keywords → Price: p-values by lag')
            else:
                plt.text(0.5, 0.5, 'Insufficient data for heatmap', 
                         horizontalalignment='center', verticalalignment='center')
            
            plt.tight_layout()
            
            # Save the figure
            os.makedirs('figures', exist_ok=True)
            plt.savefig('figures/granger_causality_tests.png', dpi=300, bbox_inches='tight')
            
            # Save a second version with current date for reference
            today_str = datetime.now().strftime('%Y%m%d')
            plt.savefig(f'figures/granger_causality_tests_{today_str}.png', dpi=300, bbox_inches='tight')
            
            print("\n\u2705 Saved enhanced Granger causality visualization to figures/granger_causality_tests.png")
            
            # Create additional visualization for lag analysis
            plt.figure(figsize=(14, 10))
            
            if not all_lag_results_df.empty:
                # Get top keywords by significance
                top_sig_keywords = results_df.nsmallest(5, 'k2p_pvalue')['keyword'].tolist()
                
                # Select data for these keywords
                top_lag_data = all_lag_results_df[all_lag_results_df['keyword'].isin(top_sig_keywords)]
                
                if not top_lag_data.empty:
                    # Create a long-format DataFrame for seaborn plotting
                    plt_data = pd.melt(
                        top_lag_data, 
                        id_vars=['keyword', 'lag'], 
                        value_vars=['k2p_pvalue', 'p2k_pvalue'],
                        var_name='direction', 
                        value_name='p_value'
                    )
                    
                    # Replace direction codes with readable labels
                    plt_data['direction'] = plt_data['direction'].replace({
                        'k2p_pvalue': 'Keyword → Price',
                        'p2k_pvalue': 'Price → Keyword'
                    })
                    
                    # Create a FacetGrid
                    g = sns.FacetGrid(plt_data, col='keyword', col_wrap=2, height=4)
                    g.map_dataframe(sns.lineplot, x='lag', y='p_value', hue='direction', marker='o')
                    g.add_horizontal(0.05, linestyle='--', color='red')  # Significance threshold
                    g.set_axis_labels('Lag', 'p-value')
                    g.set_titles('{col_name}')
                    g.add_legend()
                    g.fig.suptitle('Granger Causality p-values by Lag and Direction', fontsize=16)
                    g.fig.subplots_adjust(top=0.92)
                    
                    # Save this figure
                    plt.savefig('figures/granger_causality_lag_analysis.png', dpi=300, bbox_inches='tight')
                    print("\u2705 Saved lag analysis visualization to figures/granger_causality_lag_analysis.png")
            
            plt.close('all')
            
        except Exception as e:
            print(f"\u26A0\uFE0F Could not generate visualization: {str(e)}")
            
        return results_df
        
    except Exception as e:
        print(f"\u274c Error performing Granger causality tests: {str(e)}")
        return None 

if __name__ == "__main__":
    # Test the function
    run_granger_tests(max_lag=7, min_data_points=20)
