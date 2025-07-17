import dash

import tutorial_forecast_as_service.api.config as tfasaconf
import tutorial_forecast_as_service.api.layout as tfasapl 
import tutorial_forecast_as_service.api.callbacks as tfasacb 


def create_app():
    """
    Create and configure the Dash application.
    
    :return: Configured Dash app instance
    """
    app = dash.Dash(__name__)
    app.title = tfasaconf.APP_TITLE
    app.layout = tfasapl.create_main_layout()
    tfasacb.register_callbacks(app)
    return app


if __name__ == '__main__':
    print("Starting Dash app...")
    print(f"Make sure your FastAPI service is running on {tfasaconf.API_BASE_URL}")
    print(f"Open http://localhost:{tfasaconf.APP_PORT} in your browser")

    app = create_app()
    app.run(debug=tfasaconf.DEBUG_MODE, port=tfasaconf.APP_PORT)