from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import torch
import pandas as pd
import os
import pandas as pd
import os

PERF_FILE = "database/evaluation_data/model_performance.csv"

def init_performance_file():
    if not os.path.exists(PERF_FILE):
        df = pd.DataFrame(columns=["model_name", "MAE", "RMSE", "R2", "notes"])
        df.to_csv(PERF_FILE, index=False)

def record_performance(model_name, mae, rmse, r2, notes=""):
    init_performance_file()
    df = pd.read_csv(PERF_FILE)
    new_row = pd.DataFrame([{
        "model_name": model_name,
        "MAE": round(mae, 6),
        "RMSE": round(rmse, 6),
        "R2": round(r2, 6),
        "notes": notes
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(PERF_FILE, index=False)
    print(f"✅ Logged performance for: {model_name}")

def print_all_performances(sort_by="R2", descending=True):
    init_performance_file()
    df = pd.read_csv(PERF_FILE)
    df = df.sort_values(by=sort_by, ascending=not descending)
    print("\n📊 Model Performance Comparison:")
    print(df.to_string(index=False))

def evaluate_and_record(model, val_loader, device, model_name, scaler=None, notes="", save_preds=True):

    model.eval()
    y_true, y_pred = [], []

    with torch.no_grad():
        for xb, yb in val_loader:
            xb = xb.to(device)
            preds = model(xb).cpu().numpy()
            y_true.extend(yb.numpy())
            y_pred.extend(preds)

    y_true = np.array(y_true).flatten()
    y_pred = np.array(y_pred).flatten()

    if scaler:
        y_true_unscaled = scaler.inverse_transform(
            np.c_[y_true, np.zeros((len(y_true), scaler.n_features_in_ - 1))]
        )[:, 0]
        y_pred_unscaled = scaler.inverse_transform(
            np.c_[y_pred, np.zeros((len(y_pred), scaler.n_features_in_ - 1))]
        )[:, 0]
    else:
        y_true_unscaled = y_true
        y_pred_unscaled = y_pred

    mae = mean_absolute_error(y_true_unscaled, y_pred_unscaled)
    rmse = mean_squared_error(y_true_unscaled, y_pred_unscaled, squared=False)
    r2 = r2_score(y_true_unscaled, y_pred_unscaled)

    record_performance(model_name, mae, rmse, r2, notes)

    if save_preds:
        pred_df = pd.DataFrame({
            "Actual": y_true_unscaled,
            "Predicted": y_pred_unscaled
        })
        os.makedirs("predictions", exist_ok=True)
        pred_df.to_csv(f"predictions/{model_name}_predictions.csv", index=False)

    return mae, rmse, r2