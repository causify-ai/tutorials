"""
Import as: 

import tutorial_forecast_as_service.frontend.callbacks as tfasacb
"""
import dash

import tutorial_forecast_as_service.frontend.data_utils as tfasadu
import tutorial_forecast_as_service.frontend.ui_components as tfasauic


def register_callbacks(app):
    """
    Register all callbacks with the Dash app.
    
    This function handles file uploads, API communication, and updates the UI components.

    :param app: Dash app instance
    """
    @app.callback(
        dash.Output('upload-status', 'children'),
        dash.Input('upload-data', 'contents'),
        dash.State('upload-data', 'filename')
    )

    def handle_upload(contents, filename):
        """
        Handle file upload and send to API.
        
        :param contents: Base64 encoded file contents
        """
        if contents is None:
            return dash.html.Div()
        df = tfasadu.parse_csv_contents(contents, filename)
        # Validate and parse CSV file
        if df is None:
            return tfasauic.create_error_message(
                "Could not parse CSV file. Please ensure it has 'ds' and 'y' columns."
            )
        result = tfasadu.upload_data_to_api(df)
        # Handle API response
        if result["success"]:
            return tfasauic.create_upload_success_info(filename, df)
        else:
            return tfasauic.create_error_message(f"Upload failed: {result['error']}")

    @app.callback(
        [dash.Output('forecast-status', 'children'),
         dash.Output('forecast-plot', 'figure'),
         dash.Output('forecast-table', 'children')],
         dash.Input('forecast-button', 'n_clicks')
    )
    
    def handle_forecast(n_clicks):
        """
        Handle forecast generation.
        
        :param n_clicks: Number of times the forecast button has been clicked
        :return: Success message, forecast plot, and summary table
        """
        if n_clicks == 0:
            return dash.html.Div(), {}, dash.html.Div()
        # Call and handle API to get forecast
        result = tfasadu.get_forecast_from_api()
        if not result["success"]:
            error_message = tfasauic.create_error_message(f"Forecast failed: {result['error']}")
            return error_message, {}, dash.html.Div()
        # Process forecast data and return plot and summary table
        forecast_df = result["forecast"]        
        fig = tfasauic.create_forecast_plot(forecast_df)
        summary_table = tfasauic.create_forecast_summary_table(forecast_df)
        success_msg = tfasauic.create_success_message("Forecast generated successfully!")
        
        return success_msg, fig, summary_table