from prophet import Prophet

def create_prophet_model():
    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False
    )
    return model

def train_prophet_model(model, data):
    model.fit(data)
    return model
