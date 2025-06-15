from tensorflow.keras.models import Sequential, load_model
model = load_model("models/btc_usd_1m.h5")
all_weights = model.get_weights()
for i, w in enumerate(all_weights):
    print(f"Weight array {i}: shape = {w.shape}")
    print(w)