"""
Import as:

import tutorial_forecast_as_service.frontend.ui_components as tfasfuico
"""

import dash
import pandas as pd
import plotly

import tutorial_forecast_as_service.frontend.config as tfasfrco


def create_success_message(message: str) -> dash.html.Div:
    """
    Create a success message component.

    :param message: success message to display
    :return: the success message
    """
    return dash.html.Div(
        [
            dash.html.P(
                f"Success: {message}", style={"color": tfasfrco.SUCCESS_COLOR}
            )
        ]
    )


def create_error_message(message: str) -> dash.html.Div:
    """
    Create an error message component.

    :param message: error message to display
    :return: the error message
    """
    return dash.html.Div(
        [dash.html.P(f"Error: {message}", style={"color": tfasfrco.ERROR_COLOR})]
    )


def create_upload_success_info(filename: str, df: pd.DataFrame) -> dash.html.Div:
    """
    Create upload success information display.

    :param filename: name of the uploaded file
    :return: upload success details
    """
    return dash.html.Div(
        [
            dash.html.P(
                f"Success: File '{filename}' uploaded successfully!",
                style={"color": tfasfrco.SUCCESS_COLOR},
            ),
            dash.html.P(f"Data shape: {df.shape[0]} rows, {df.shape[1]} columns"),
            dash.html.P(f"Date range: {df['ds'].min()} to {df['ds'].max()}"),
        ]
    )


def create_forecast_plot(
    forecast_df: pd.DataFrame,
) -> plotly.graph_objects.Figure:
    """
    Create the forecast plot.

    :param forecast_df: DataFrame containing forecast data
    :return: Plotly Figure object with the forecast plot
    """
    fig = plotly.graph_objects.Figure()
    fig.add_trace(
        plotly.graph_objects.Scatter(
            x=forecast_df["ds"],
            y=forecast_df["yhat"],
            mode="lines+markers",
            name="Forecast",
            line={"color": "blue", "width": 2},
            marker={"size": 4},
        )
    )
    fig.update_layout(
        title="Time Series Forecast",
        xaxis_title="Date",
        yaxis_title="Value",
        hovermode="x unified",
        template="plotly_white",
        height=500,
    )
    return fig


def create_forecast_summary_table(forecast_df: pd.DataFrame) -> dash.html.Div:
    """
    Create the forecast summary table.

    :param forecast_df: DataFrame containing forecast data
    :return: HTML Div containing the summary table
    """
    return dash.html.Div(
        [
            dash.html.H4("Forecast Summary"),
            dash.html.Table(
                [
                    dash.html.Tr(
                        [
                            dash.html.Td("Data Points:"),
                            dash.html.Td(len(forecast_df)),
                        ]
                    ),
                    dash.html.Tr(
                        [
                            dash.html.Td("Date Range:"),
                            dash.html.Td(
                                f"{forecast_df['ds'].min()} to {forecast_df['ds'].max()}"
                            ),
                        ]
                    ),
                    dash.html.Tr(
                        [
                            dash.html.Td("Min Value:"),
                            dash.html.Td(f"{forecast_df['yhat'].min():.2f}"),
                        ]
                    ),
                    dash.html.Tr(
                        [
                            dash.html.Td("Max Value:"),
                            dash.html.Td(f"{forecast_df['yhat'].max():.2f}"),
                        ]
                    ),
                    dash.html.Tr(
                        [
                            dash.html.Td("Mean Value:"),
                            dash.html.Td(f"{forecast_df['yhat'].mean():.2f}"),
                        ]
                    ),
                ],
                style=tfasfrco.TABLE_STYLE,
            ),
        ]
    )
