"""
Import as:

import tutorial_forecast_as_service.frontend.layout as tfasfrla
"""

import dash

import tutorial_forecast_as_service.frontend.config as tfasfrco


def create_upload_section() -> dash.html.Div:
    """
    Create the file upload section.

    This section allows users to upload a CSV file containing time
    series data.

    :return: the upload section
    """
    return dash.html.Div(
        [
            dash.html.H3("Step 1: Upload Time Series Data"),
            dash.html.P(
                "Upload a CSV file with time series data. "
                "The file should contain 'ds' (date) and 'y' (value) columns."
            ),
            dash.dcc.Upload(
                id="upload-data",
                children=dash.html.Div(
                    ["Drag and Drop or ", dash.html.A("Select CSV File")]
                ),
                style=tfasfrco.UPLOAD_STYLE,
                multiple=False,
                accept=".csv",
            ),
            dash.html.Div(id="upload-status"),
        ],
        style=tfasfrco.SECTION_STYLE,
    )


def create_forecast_section() -> dash.html.Div:
    """
    Create the forecast generation section.

    This section allows users to generate a forecast based on the
    uploaded data.

    :return: the forecast section
    """
    return dash.html.Div(
        [
            dash.html.H3("Step 2: Generate Forecast"),
            dash.html.Button(
                "Generate Forecast",
                id="forecast-button",
                n_clicks=0,
                style=tfasfrco.BUTTON_STYLE,
            ),
            dash.html.Div(id="forecast-status"),
        ],
        style=tfasfrco.SECTION_STYLE,
    )


def create_results_section() -> dash.html.Div:
    """
    Create the results display section.

    This section displays the forecast results including the plot and
    summary table.

    :return: the results section
    """
    return dash.html.Div(
        [
            dash.html.H3("Step 3: Forecast Results"),
            dash.dcc.Graph(id="forecast-plot"),
            dash.html.Div(id="forecast-table"),
        ],
        style=tfasfrco.SECTION_STYLE,
    )


def create_main_layout() -> dash.html.Div:
    """
    Create the main application layout.

    This function combines all sections into a single layout for the
    Dash app.

    :return: HTML Div containing the main layout
    """
    return dash.html.Div(
        [
            dash.html.Div(
                [
                    dash.html.H1(
                        "Forecast as a Service",
                        style=tfasfrco.HEADER_STYLE,
                    ),
                    create_upload_section(),
                    create_forecast_section(),
                    create_results_section(),
                ],
                style=tfasfrco.MAIN_STYLE,
            )
        ]
    )
