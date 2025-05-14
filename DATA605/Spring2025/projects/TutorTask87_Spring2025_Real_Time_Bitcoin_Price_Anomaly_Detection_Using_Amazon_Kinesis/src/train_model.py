import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib, os

# Load historical data (replace with your path)
csv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "btc_price_history.csv"))
df = pd.read_csv(csv_path)

# Select relevant features
X = df[["price", "volume"]]

# Train Isolation Forest model
model = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
model.fit(X)

# Save model to file
joblib.dump(model, "isolation_forest_model.pkl")

print("Model trained and saved as 'isolation_forest_model.pkl'")
