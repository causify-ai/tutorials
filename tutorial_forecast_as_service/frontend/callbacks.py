"""
Import as:

import tutorial_forecast_as_service.frontend.callbacks as tfasfrca
"""

from typing import Any, Tuple

import dash

import tutorial_forecast_as_service.frontend.data_utils as tfasfdaut
import tutorial_forecast_as_service.frontend.ui_components as tfasfuico


def handle_upload(contents: str, filename: str) -> Any:
    """
    Handle file upload and send to API.

    :param contents: file contents
    :param filename: uploaded file
    :return: status UI component
    """
    if contents is None:
        return dash.html.Div()
    df = tfasfdaut.parse_csv_contents(contents, filename)
    if df is None:
        return tfasfuico.create_error_message(
            "Could not parse CSV file. Please ensure it has 'ds' and 'y' columns."
        )
    result = tfasfdaut.upload_data_to_api(df)
    if result["success"]:
        return tfasfuico.create_upload_success_info(filename, df)
    return tfasfuico.create_error_message(f"Upload failed: {result['error']}")


def handle_forecast(n_clicks: int) -> Tuple[Any, Any, Any]:
    """
    Handle forecast generation.

    :param n_clicks: number of forecast button clicks
    :return: success message, forecast plot, and summary table
    """
    if n_clicks == 0:
        return dash.html.Div(), {}, dash.html.Div()
    result = tfasfdaut.get_forecast_from_api()
    if not result["success"]:
        return (
            tfasfuico.create_error_message(f"Forecast failed: {result['error']}"),
            {},
            dash.html.Div(),
        )
    forecast_df = result["forecast"]
    fig = tfasfuico.create_forecast_plot(forecast_df)
    summary_table = tfasfuico.create_forecast_summary_table(forecast_df)
    success_msg = tfasfuico.create_success_message(
        "Forecast generated successfully!"
    )
    return success_msg, fig, summary_table


def register_callbacks(app: dash.Dash) -> None:
    """
    Register all callbacks with the Dash app.

    This function handles file uploads, API communication, and updates
    the UI components.

    :param app: Dash app instance
    """
    app.callback(
        dash.Output("upload-status", "children"),
        dash.Input("upload-data", "contents"),
        dash.State("upload-data", "filename"),
    )(handle_upload)
    app.callback(
        [
            dash.Output("forecast-status", "children"),
            dash.Output("forecast-plot", "figure"),
            dash.Output("forecast-table", "children"),
        ],
        dash.Input("forecast-button", "n_clicks"),
    )(handle_forecast)
