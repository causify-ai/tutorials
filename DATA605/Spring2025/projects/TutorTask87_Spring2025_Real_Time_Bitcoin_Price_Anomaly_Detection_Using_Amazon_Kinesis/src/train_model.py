import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib, os

from src.tutorials1.DATA605.Spring2025.projects.TutorTask87_Spring2025_Real_Time_Bitcoin_Price_Anomaly_Detection_Using_Amazon_Kinesis.utils.utils import \
    current_utc_time

# Load historical data (replace with your path)
csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "btc_price_history.csv"))
df = pd.read_csv(csv_path)

# Select relevant features
X = df[["price", "volume"]]

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train Isolation Forest model
model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
model.fit(X)
data = {
        "price": 999999.0,  # way outside normal range
        "volume": 9999.0,
        "timestamp": current_utc_time()
    }
price = data.get("price")
volume = data.get("volume")
features = np.array([[price, volume]])
result = model.predict(features)
if result[0] == -1:
    print("Anomaly detected")
# Save model to file
joblib.dump(model, "isolation_forest_model.pkl")
joblib.dump(scaler, "scaler.pkl")
print("Model trained and saved as 'isolation_forest_model.pkl'")
