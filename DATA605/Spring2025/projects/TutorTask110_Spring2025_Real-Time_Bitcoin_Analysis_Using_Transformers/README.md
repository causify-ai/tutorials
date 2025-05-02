# Real-time Bitcoin Analysis using Transformers

All the dev work is inside the dev folder.
I have built a transformer model, stored it for reusability. It predicts the bitcoin prices by day using historical data of bitcoin till today. Steps performed for Data Processing, Model training and Model Evaluation can be found in the Jupyter notebook file: '1d_model_v1.ipynb'. Predictions can be monitored using streamlit dashboard by running 'btc_forecast_app.py'.

Next Steps:

1. Move the Development files and run it from inside the docker container.
2. Hyper-paramer tuning the tranformer model for better predictions.
3. Work with the realtime data with lesser intervals(say 5 minutes) for realtime predictions using dashboard like streamlit/dash.
