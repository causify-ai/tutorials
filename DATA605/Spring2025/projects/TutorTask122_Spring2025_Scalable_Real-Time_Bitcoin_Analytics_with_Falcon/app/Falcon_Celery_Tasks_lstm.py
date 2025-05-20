"""
Utilize Celery to distribute lstm tasks.
Runs a separate celery worker than the Falcon_Celery_Tasks focused on ingesting/processing data.

1. Celery documentation: https://docs.celeryq.dev/en/stable/getting-started/introduction.html

Task mapping:
1) train
2) predict
3) train_n
4) predict_n

"""
# ------------------------------------------------------------------------------
# Import packages.
# -----------------------------------------------------------------------------
from celery import Celery
from Falcon_utils import train_lstm_and_save, load_lstm_and_predict
from Falcon_utils_extended import train_lstm_and_save_future, load_lstm_and_predict_future

app = Celery("lstm_tasks",
              broker="redis://redis:6379/0",
                backend="redis://redis:6379/0")

# ------------------------------------------------------------------------------
# 1. train_lstm
# -----------------------------------------------------------------------------

@app.task(name="Falcon_Celery_Tasks_lstm.train_lstm", queue='lstm')
def train(model_name="",symbol="btc_usd", resolution="1d", seq_len=10, model_id=1):
    symbol = symbol.lower().replace("-", "_")
    return train_lstm_and_save(model_name, symbol, resolution, seq_len, model_id)

# ------------------------------------------------------------------------------
# 2. predict_lstm
# -----------------------------------------------------------------------------
@app.task(name="Falcon_Celery_Tasks_lstm.predict_price", queue='lstm')
def predict(model_name="",symbol="btc_usd", resolution="1d", seq_len=10, model_id=1):
    symbol = symbol.lower().replace("-", "_")
    return load_lstm_and_predict(model_name,symbol, resolution, seq_len, model_id)


# ------------------------------------------------------------------------------
# 3. train_lstm n steps ahead
# -----------------------------------------------------------------------------

@app.task(name="Falcon_Celery_Tasks_lstm.train_nsteps", queue='lstm')
def train_n(model_name="",symbol="btc_usd", resolution="1d", seq_len=10, model_id=1,
            nsteps=1, training_epochs=5):
    symbol = symbol.lower().replace("-", "_")
    return train_lstm_and_save_future(model_name,symbol, resolution, seq_len, model_id, nsteps, training_epochs)

# ------------------------------------------------------------------------------
# 4. predict_lstm n steps ahead
# -----------------------------------------------------------------------------
@app.task(name="Falcon_Celery_Tasks_lstm.predict_pnrices", queue='lstm')
def predict_n(model_name="",symbol="btc_usd", resolution="1d", seq_len=10, model_id=1):
    symbol = symbol.lower().replace("-", "_")
    return load_lstm_and_predict_future(model_name,symbol, resolution, seq_len, model_id)

