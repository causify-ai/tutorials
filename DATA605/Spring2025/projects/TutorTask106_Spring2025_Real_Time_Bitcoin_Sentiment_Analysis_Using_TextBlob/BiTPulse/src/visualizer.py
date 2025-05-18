import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple, Any, Optional, Union

def plot_price_with_forecast(
    historical_data: pd.DataFrame,
    forecast_data: Union[pd.DataFrame, Dict[str, Any]],
    confidence_level: float = 0.95
) -> go.Figure:
    """
    Plot historical Bitcoin price with forecast and confidence intervals.
    
    Args:
        historical_data (pd.DataFrame): Historical price data
        forecast_data (Union[pd.DataFrame, Dict[str, Any]]): Forecast data (either DataFrame or dict with 'forecast' key)
        confidence_level (float): Confidence level for intervals (default: 0.95)
        
    Returns:
        go.Figure: Plotly figure object
    """
    # Create figure
    fig = go.Figure()
    
    # Extract forecast data based on format
    if isinstance(forecast_data, dict):
        if 'forecast' in forecast_data:
            forecast_dict = forecast_data['forecast']
            if isinstance(forecast_dict, dict):
                # Convert dictionary format to DataFrame
                forecast_df = pd.DataFrame({
                    'Forecast': forecast_dict['mean'],
                    'Lower_CI': forecast_dict['lower'],
                    'Upper_CI': forecast_dict['upper']
                }, index=forecast_dict['dates'])
            else:
                forecast_df = forecast_dict
        else:
            forecast_df = pd.DataFrame(forecast_data)
    else:
        forecast_df = forecast_data
    
    # Get price column name (handle both 'Close' and 'price' columns)
    price_column = 'Close' if 'Close' in historical_data.columns else 'price'
    
    # Plot historical data
    fig.add_trace(go.Scatter(
        x=historical_data.index,
        y=historical_data[price_column],
        name='Historical Price',
        line=dict(color='blue')
    ))
    
    # Plot forecast
    fig.add_trace(go.Scatter(
        x=forecast_df.index,
        y=forecast_df['Forecast'],
        name='Forecast',
        line=dict(color='red', dash='dash')
    ))
    
    # Plot confidence intervals
    fig.add_trace(go.Scatter(
        x=forecast_df.index,
        y=forecast_df['Upper_CI'],
        name=f'Upper {confidence_level*100:.0f}% CI',
        line=dict(width=0),
        showlegend=False
    ))
    
    fig.add_trace(go.Scatter(
        x=forecast_df.index,
        y=forecast_df['Lower_CI'],
        name=f'Lower {confidence_level*100:.0f}% CI',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(255,0,0,0.1)',
        showlegend=False
    ))
    
    # Update layout
    fig.update_layout(
        title='Bitcoin Price Forecast',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    return fig

def plot_technical_indicators(
    indicators_data: pd.DataFrame,
    show_rsi: bool = True,
    show_macd: bool = True
) -> go.Figure:
    """
    Plot technical indicators for Bitcoin.
    
    Args:
        indicators_data (pd.DataFrame): DataFrame with technical indicators
        show_rsi (bool): Whether to show RSI chart
        show_macd (bool): Whether to show MACD chart
        
    Returns:
        go.Figure: Plotly figure with technical indicators
    """
    # Determine the number of rows based on which indicators to show
    indicators_to_show = []
    if show_rsi:
        indicators_to_show.append('rsi')
    if show_macd:
        indicators_to_show.append('macd')
    
    num_rows = len(indicators_to_show)
    
    if num_rows == 0:
        # Return empty figure if no indicators selected
        return go.Figure()
    
    # Create subplots
    fig = make_subplots(
        rows=num_rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=[title for title, show in zip(['RSI', 'MACD'], [show_rsi, show_macd]) if show]
    )
    
    # Current row tracker
    current_row = 1
    
    # Add RSI if enabled
    if show_rsi:
        # First calculate RSI if it doesn't exist
        if 'rsi' not in indicators_data.columns:
            # Use closing price to calculate RSI
            if 'Close' in indicators_data.columns:
                close_series = indicators_data['Close']
            elif 'price' in indicators_data.columns:
                close_series = indicators_data['price']
            else:
                # Fallback to the first numeric column
                close_series = indicators_data.select_dtypes(include=['number']).iloc[:, 0]
                
            # Calculate RSI (14-period)
            delta = close_series.diff()
            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        else:
            rsi = indicators_data['rsi']
            
        fig.add_trace(
            go.Scatter(
                x=indicators_data.index,
                y=rsi,
                mode='lines',
                name='RSI',
                line=dict(color='#26A69A', width=1.5)
            ),
            row=current_row,
            col=1
        )
        
        # Add RSI overbought/oversold lines
        fig.add_trace(
            go.Scatter(
                x=[indicators_data.index[0], indicators_data.index[-1]],
                y=[70, 70],
                mode='lines',
                line=dict(color='red', width=1, dash='dash'),
                showlegend=False
            ),
            row=current_row,
            col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=[indicators_data.index[0], indicators_data.index[-1]],
                y=[30, 30],
                mode='lines',
                line=dict(color='green', width=1, dash='dash'),
                showlegend=False
            ),
            row=current_row,
            col=1
        )
        
        # Update y-axis range for RSI
        fig.update_yaxes(title_text="RSI", range=[0, 100], row=current_row, col=1)
        
        current_row += 1
    
    # Add MACD if enabled
    if show_macd:
        # Calculate MACD if it doesn't exist
        if 'macd' not in indicators_data.columns or 'macd_signal' not in indicators_data.columns:
            # Use closing price to calculate MACD
            if 'Close' in indicators_data.columns:
                close_series = indicators_data['Close']
            elif 'price' in indicators_data.columns:
                close_series = indicators_data['price']
            else:
                # Fallback to the first numeric column
                close_series = indicators_data.select_dtypes(include=['number']).iloc[:, 0]
                
            # Calculate MACD (12, 26, 9)
            exp1 = close_series.ewm(span=12, adjust=False).mean()
            exp2 = close_series.ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            macd_signal = macd.ewm(span=9, adjust=False).mean()
            macd_hist = macd - macd_signal
        else:
            macd = indicators_data['macd']
            macd_signal = indicators_data['macd_signal']
            macd_hist = indicators_data['macd_hist']
        
        # MACD line
        fig.add_trace(
            go.Scatter(
                x=indicators_data.index,
                y=macd,
                mode='lines',
                name='MACD',
                line=dict(color='#2962FF', width=1.5)
            ),
            row=current_row,
            col=1
        )
        
        # Signal line
        fig.add_trace(
            go.Scatter(
                x=indicators_data.index,
                y=macd_signal,
                mode='lines',
                name='Signal',
                line=dict(color='#FF6D00', width=1.5)
            ),
            row=current_row,
            col=1
        )
        
        # Histogram
        fig.add_trace(
            go.Bar(
                x=indicators_data.index,
                y=macd_hist,
                name='Histogram',
                marker=dict(
                    color=np.where(macd_hist >= 0, '#26A69A', '#EF5350'),
                    line=dict(color='rgba(0,0,0,0)', width=0)
                ),
                opacity=0.7
            ),
            row=current_row,
            col=1
        )
        
        # Update y-axis title for MACD
        fig.update_yaxes(title_text="MACD", row=current_row, col=1)
    
    # Update layout
    fig.update_layout(
        height=300 * num_rows,
        template='plotly_dark',
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    
    return fig

def plot_forecast_components(components: Dict[str, np.ndarray]) -> go.Figure:
    """
    Plot the decomposed components of the forecast.
    
    Args:
        components (Dict[str, np.ndarray]): Dictionary with component arrays
        
    Returns:
        go.Figure: Plotly figure with forecast components
    """
    # Create subplots
    num_components = len(components)
    
    if num_components == 0:
        # Return empty figure if no components
        return go.Figure()
    
    fig = make_subplots(
        rows=num_components,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        subplot_titles=list(components.keys())
    )
    
    # Colors for different components
    colors = {
        'trend': '#F63366',
        'seasonality': '#26A69A',
        'autoregressive': '#2962FF'
    }
    
    # Add each component to the plot
    for i, (component_name, component_values) in enumerate(components.items(), 1):
        fig.add_trace(
            go.Scatter(
                y=component_values,
                mode='lines',
                name=component_name.capitalize(),
                line=dict(color=colors.get(component_name, '#F9A825'), width=1.5)
            ),
            row=i,
            col=1
        )
    
    # Update layout
    fig.update_layout(
        height=250 * num_components,
        template='plotly_dark',
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )
    
    return fig

def plot_model_metrics(metrics: Dict[str, float]) -> go.Figure:
    """
    Plot model performance metrics.
    
    Args:
        metrics (Dict[str, float]): Dictionary with metric values
        
    Returns:
        go.Figure: Plotly figure with model metrics
    """
    # Create bar chart for metrics
    fig = go.Figure()
    
    # Filter out non-numeric metrics and R²
    error_metrics = {
        k: v for k, v in metrics.items() 
        if isinstance(v, (int, float)) and k not in ['r2', 'model_type', 'lookback_window', 'forecast_horizon', 'used_sentiment']
    }
    
    if not error_metrics:
        # If no numeric metrics, show a message
        fig.add_annotation(
            text="No numeric metrics available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False
        )
    else:
        # Add error metrics
        fig.add_trace(
            go.Bar(
                x=list(error_metrics.keys()),
                y=list(error_metrics.values()),
                marker_color=['#F63366', '#F9A825', '#26A69A'],
                text=[f"{v:.2f}" if isinstance(v, float) else str(v) for v in error_metrics.values()],
                textposition='auto'
            )
        )
    
    # Update layout
    fig.update_layout(
        title='Model Error Metrics',
        xaxis_title='Metric',
        yaxis_title='Value',
        template='plotly_dark',
        xaxis={'categoryorder': 'array', 'categoryarray': ['mae', 'rmse', 'mape']}
    )
    
    return fig

def plot_uncertainty(
    forecast_data: Union[pd.DataFrame, Dict[str, Any]],
    confidence_level: float = 0.95
) -> go.Figure:
    """
    Plot uncertainty analysis of the forecast.
    
    Args:
        forecast_data (Union[pd.DataFrame, Dict[str, Any]]): Forecast data (either DataFrame or dict with 'forecast' key)
        confidence_level (float): Confidence level for intervals (default: 0.95)
        
    Returns:
        go.Figure: Plotly figure object
    """
    # Create figure
    fig = go.Figure()
    
    # Extract forecast data based on format
    if isinstance(forecast_data, dict):
        if 'forecast' in forecast_data:
            forecast_dict = forecast_data['forecast']
            if isinstance(forecast_dict, dict):
                # Convert dictionary format to DataFrame
                forecast_df = pd.DataFrame({
                    'Forecast': forecast_dict.get('mean', []),
                    'Lower_CI': forecast_dict.get('lower', []),
                    'Upper_CI': forecast_dict.get('upper', [])
                }, index=forecast_dict.get('dates', []))
            else:
                forecast_df = forecast_dict
        else:
            forecast_df = pd.DataFrame(forecast_data)
    else:
        forecast_df = forecast_data
    
    # Check if we have the required columns
    has_confidence_intervals = False
    
    # Try different column name formats
    if all(col in forecast_df.columns for col in ['Upper_CI', 'Lower_CI', 'Forecast']):
        has_confidence_intervals = True
        forecast_df['CV'] = (forecast_df['Upper_CI'] - forecast_df['Lower_CI']) / (2 * forecast_df['Forecast'])
        forecast_df['CI_Width'] = forecast_df['Upper_CI'] - forecast_df['Lower_CI']
    elif all(col in forecast_df.columns for col in ['upper', 'lower', 'mean']):
        has_confidence_intervals = True
        forecast_df['CV'] = (forecast_df['upper'] - forecast_df['lower']) / (2 * forecast_df['mean'])
        forecast_df['CI_Width'] = forecast_df['upper'] - forecast_df['lower']
    
    if not has_confidence_intervals:
        # If no confidence intervals available, return empty figure with message
        fig.add_annotation(
            text="No uncertainty data available for this forecast",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False
        )
        return fig
    
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add CV trace
    fig.add_trace(
        go.Scatter(
            x=forecast_df.index,
            y=forecast_df['CV'],
            name='Coefficient of Variation',
            line=dict(color='blue')
        ),
        secondary_y=False
    )
    
    # Add CI Width trace
    fig.add_trace(
        go.Scatter(
            x=forecast_df.index,
            y=forecast_df['CI_Width'],
            name='Confidence Interval Width',
            line=dict(color='red')
        ),
        secondary_y=True
    )
    
    # Update layout
    fig.update_layout(
        title='Forecast Uncertainty Analysis',
        xaxis_title='Date',
        hovermode='x unified',
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    # Update y-axes labels
    fig.update_yaxes(title_text="Coefficient of Variation", secondary_y=False)
    fig.update_yaxes(title_text="Confidence Interval Width (USD)", secondary_y=True)
    
    return fig
