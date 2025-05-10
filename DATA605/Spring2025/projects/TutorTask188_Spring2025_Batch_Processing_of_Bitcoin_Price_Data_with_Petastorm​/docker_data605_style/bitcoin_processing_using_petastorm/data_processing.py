# data_processing.py
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

class BitcoinAnalyzer:
    def __init__(self, data):
        self.data = data
        self.df = self._prepare_data()
        
    def _prepare_data(self):
        """Convert raw data to DataFrame and preprocess"""
        df = pd.DataFrame(self.data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)
        return df
    
    def calculate_moving_average(self, window=7):
        """Calculate moving average"""
        self.df[f'ma_{window}'] = self.df['price_usd'].rolling(window=window).mean()
        return self.df
    
    def calculate_volatility(self, window=7):
        """Calculate rolling volatility"""
        self.df[f'volatility_{window}'] = self.df['price_usd'].pct_change().rolling(window=window).std()
        return self.df
    
    def plot_price_trend(self):
        """Plot Bitcoin price trend"""
        plt.figure(figsize=(12, 6))
        self.df['price_usd'].plot(title='Bitcoin Price Trend')
        if 'ma_7' in self.df.columns:
            self.df['ma_7'].plot(label='7-period MA')
            plt.legend()
        plt.ylabel('Price (USD)')
        plt.xlabel('Date')
        plt.grid()
        plt.show()
    
    def plot_volatility(self):
        """Plot Bitcoin price volatility"""
        if 'volatility_7' not in self.df.columns:
            self.calculate_volatility()
            
        plt.figure(figsize=(12, 6))
        self.df['volatility_7'].plot(title='Bitcoin Price Volatility (7-day)')
        plt.ylabel('Volatility')
        plt.xlabel('Date')
        plt.grid()
        plt.show()
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        self.calculate_moving_average()
        self.calculate_volatility()
        
        print("\n=== Bitcoin Price Analysis Report ===")
        print(f"Time Period: {self.df.index[0]} to {self.df.index[-1]}")
        print(f"Number of Data Points: {len(self.df)}")
        print(f"\nPrice Statistics:")
        print(self.df['price_usd'].describe())
        print(f"\nLatest Price: ${self.df['price_usd'].iloc[-1]:,.2f}")
        print(f"24h Change: {self.df['price_change_24h'].iloc[-1]:.2f}%")
        
        self.plot_price_trend()
        self.plot_volatility()