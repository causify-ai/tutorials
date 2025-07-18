"""
Import as:

import tutorial_forecast_as_service.frontend.app as tfasfrap
"""

import dash

import tutorial_forecast_as_service.frontend.callbacks as tfasfrca
import tutorial_forecast_as_service.frontend.config as tfasfrco
import tutorial_forecast_as_service.frontend.layout as tfasfrla


def create_app() -> dash.Dash:
    """
    Create and configure the Dash application.

    :return: configured Dash app instance
    """
    app = dash.Dash(__name__)
    app.title = tfasfrco.APP_TITLE
    app.layout = tfasfrla.create_main_layout()
    tfasfrca.register_callbacks(app)
    return app


if __name__ == "__main__":
    print("Starting Dash app...")
    print(f"Make sure your FastAPI service is running on {tfasfrco.API_BASE_URL}")
    print(f"Open http://localhost:{tfasfrco.APP_PORT} in your browser")
    dash_app = create_app()
    dash_app.run(host="0.0.0.0", debug=tfasfrco.DEBUG_MODE, port=tfasfrco.APP_PORT)
