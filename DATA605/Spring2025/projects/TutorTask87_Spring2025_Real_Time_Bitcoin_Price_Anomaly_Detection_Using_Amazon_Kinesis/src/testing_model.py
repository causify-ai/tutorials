import joblib
import numpy as np

model = joblib.load("isolation_forest_model.pkl")
scaler = joblib.load("scaler.pkl")
ANOMALY_SCORE_THRESHOLD = -0.001
data = {
        "price": 999999.0,  # way outside normal range
        "volume": 9999.0,

    }
price = data.get("price")
volume = data.get("volume")
features = np.array([[price, volume]])
scaled = scaler.transform(features)
score = model.decision_function(scaled)[0]
print(score)
if score < ANOMALY_SCORE_THRESHOLD:
    print("Anomaly detected")
# Normal data (should return 1)
print(model.predict([[65000.0, 300.0]]))

# Extreme anomaly (should return -1)
print(model.predict([[999999.0, 100000.0]]))
