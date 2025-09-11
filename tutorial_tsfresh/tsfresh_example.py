# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.17.1
#   kernelspec:
#     display_name: Python 3
#     name: python3
# ---

# %% [markdown]
# CONTENTS:
# - [tsfresh Example](#tsfresh-example)
#   - [0) Setup](#0)-setup)
#   - [1) Import Packages](#1)-import-packages)
#   - [3) Load HAR data (train/test splits)](#3)-load-har-data-(train/test-splits))
#   - [4) Convert to **long format** for tsfresh](#4)-convert-to-**long-format**-for-tsfresh)
#   - [5) Feature extraction with tsfresh](#5)-feature-extraction-with-tsfresh)
#   - [6) Feature Selection](#6)-feature-selection)
#   - [7) Train a classifier and evaluate](#7)-train-a-classifier-and-evaluate)

# %% [markdown] id="da41fba7"
# <a name='tsfresh-example'></a>
#
# # tsfresh Example
#
# This notebook shows an end-to-end workflow using
# [tsfresh](https://tsfresh.readthedocs.io/) on the
# UCI HAR dataset (smartphone accelerometer
# & gyroscope data).
#
# The main objective of this notebook is to
#  show tsfresh can be used to create multiple
# new features through feature engineering to
# help predict 6 different motions using the
# accelerometer and gyroscope time series data.
# The main function of tsfresh is to engineer features.
# However, it also does have functionalities for
# certain ML models built-in to perform predictions too.
#
# We will:
# 1. Download & load the dataset
# 2. Reshape to long format suitable for tsfresh (columns: `id`, `time`, `kind`, `value`)
# 3. Extract features with `tsfresh.extract_features`
# 4. Select relevant features with `tsfresh.select_features`
# 5. Train a RandomForest model and predict the 6
#  different motions and evaluate.
# 6. Inspect top feature importances
#
#

# %% [markdown] id="ec6a280e"
# <a name='0)-setup'></a>
#
# ## 0) Setup
#
# Uncomment as per your requirement
#

# %% id="3aa7ce61"

# # %pip install -q tsfresh scikit-learn pandas numpy matplotlib requests tqdm


# %% [markdown] id="5ce4441f"
# <a name='1)-import-packages'></a>
# ## 1) Import Packages

# %% id="17e69980"

import pathlib.Path as path
import zipfile

import numpy as np
import requests
import tqdm.tqdm as tq_vis

np.random.seed(42)

DATA_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/00240/UCI%20HAR%20Dataset.zip"
DATA_DIR = path("./uci_har_data")


# ## 2) Download the UCI HAR dataset
#
# If the dataset hasn't been downloaded, this function will download it.


def fetch_data(url=DATA_URL, out_dir=DATA_DIR):
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / "UCI_HAR_Dataset.zip"
    if not zip_path.exists():
        resp = requests.get(url, stream=True, timeout=20)
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))
        with open(zip_path, "wb") as f, tq_vis(
            total=total, unit="B", unit_scale=True
        ) as pbar:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(out_dir)
    return out_dir / "UCI HAR Dataset"


har_root = fetch_data()


# %% [markdown] id="e1de6453"
# <a name='3)-load-har-data-(train/test-splits)'></a>
#
# ## 3) Load HAR data (train/test splits)
#
# Here we extract the raw signals captured by the sensors.
# Each example has 128 time steps for each sensor/channel.
#
#
# def load_inertial_split(split="train", root=None):
#     root = path(root) if root else har_root
#     base = root / split / "Inertial Signals"
#     channels = [
#         "body_acc_x",
#         "body_acc_y",
#         "body_acc_z",
#         "body_gyro_x",
#         "body_gyro_y",
#         "body_gyro_z",
#         "total_acc_x",
#         "total_acc_y",
#         "total_acc_z",
#     ]
#     arrays = {}
#     for ch in channels:
#         fn = base / f"{ch}_{split}.txt"
#         arr = np.loadtxt(fn)
#         arrays[ch] = arr
#     y = np.loadtxt(root / split / f"y_{split}.txt").astype(int)
#     subjects = np.loadtxt(root / split / f"subject_{split}.txt").astype(int)
#     return arrays, y, subjects
#
#
# train_arrays, y_train_raw, subj_train = load_inertial_split("train", har_root)
# test_arrays, y_test_raw, subj_test = load_inertial_split("test", har_root)
#
# channels = list(train_arrays.keys())
# n_train = train_arrays[channels[0]].shape[0]
# n_test = test_arrays[channels[0]].shape[0]
# n_time = train_arrays[channels[0]].shape[1]
#
# print(
#     f"Train: {n_train}, Test: {n_test}, Timesteps: {n_time}, Channels: {len(channels)}"
# )


# %% [markdown] id="d79fbe00"
# <a name='4)-convert-to-**long-format**-for-tsfresh'></a>
#
# ## 4) Convert to **long format** for tsfresh
#
# We build a DataFrame with columns:
# - `id` : row id (unique per series example)
# - `time` : timestep (0..127)
# - `kind` : sensor name (e.g., `body_acc_x`, `body_gyro_z`, ...)
# - `value` : observed value
#
# This lets tsfresh handle **multivariate** time series via the `kind` column.
#
#
#
# def to_long(arrays, start_id=0):
#     n_samples = arrays[next(iter(arrays))].shape[0]
#     n_time = arrays[next(iter(arrays))].shape[1]
#     frames = []
#     for i in range(n_samples):
#         for ch, mat in arrays.items():
#             df = pd.DataFrame(
#                 {
#                     "id": start_id + i,
#                     "time": np.arange(n_time, dtype=int),
#                     "kind": ch,
#                     "value": mat[i, :].astype(float),
#                 }
#             )
#             frames.append(df)
#     return pd.concat(frames, ignore_index=True)
#
#
# X_long_train = to_long(train_arrays, start_id=0)
# X_long_test = to_long(test_arrays, start_id=train_arrays[channels[0]].shape[0])
#
# Build labels aligned with id space
# y_train_df = pd.DataFrame(
#     {"id": np.arange(0, train_arrays[channels[0]].shape[0]), "label": y_train_raw}
# )
# y_test_df = pd.DataFrame(
#     {
#         "id": np.arange(
#             train_arrays[channels[0]].shape[0],
#             train_arrays[channels[0]].shape[0]
#             + test_arrays[channels[0]].shape[0],
#         ),
#         "label": y_test_raw,
#     }
# )
#
# X_long_train.head(), X_long_train.shape, y_train_df.head()


# %% [markdown] id="ec07d094"
# <a name='5)-feature-extraction-with-tsfresh'></a>
#
# ## 5) Feature extraction with tsfresh
#
# There are many different parameter values
# that decide the extent of feature engineering.
#  For our case, we'll use `MinimalFCParameters`
#  that extracts features like mean, standard deviation,
#  length, max value, min value etc. This is the
# best argument to be passed for fast and
# lighweight use-cases. For more features,
# use the `ComprehensiveFCParameters()` class
# which extracts >800 features.
#
# settings = fe.MinimalFCP()
#
# X_feat_train = ext_feat(
#     X_long_train,
#     column_id="id",
#     column_sort="time",
#     column_kind="kind",
#     column_value="value",
#     default_fc_parameters=settings,
#     n_jobs=0,
#     disable_progressbar=False,
# )
# X_feat_train = df_utils.imp(X_feat_train)
# X_feat_train.shape
#
#
# Here we transform the test set using the same settings.
#
# X_feat_test = ext_feat(
#     X_long_test,
#     column_id="id",
#     column_sort="time",
#     column_kind="kind",
#     column_value="value",
#     default_fc_parameters=settings,
#     n_jobs=0,
#     disable_progressbar=False,
# )
# X_feat_test = df_utils.imp(X_feat_test)
# X_feat_test.shape


# %% [markdown] id="3b2ddd0a"
# <a name='6)-feature-selection'></a>
#
# ## 6) Feature Selection
#
# Tsfresh has built-in functionality to
# select the best features out of all the ones artificially
#  created. We select features most relevant
# to distinguishing the 6 classes/motions.
# le = label_e()
# y_train = pd.Series(
#     le.fit_transform(y_train_df.set_index("id")["label"]),
#     index=y_train_df["id"].values,
# )
# y_test = pd.Series(
#     le.transform(y_test_df.set_index("id")["label"]), index=y_test_df["id"].values
# )
#
# X_sel_train = sel_feat(X_feat_train, y_train)
# X_sel_train.shape


# %% [markdown] id="5e135626"
#
# Align the **test** feature matrix to the **selected** training columns.
# X_feat_test = X_feat_test.reindex(columns=X_sel_train.columns, fill_value=0.0)
# X_feat_test.shape


# %% [markdown] id="57ff6e5c"
# <a name='7)-train-a-classifier-and-evaluate'></a>
#
# ## 7) Train a classifier and evaluate
#
# We use a `RandomForestClassifier` and report:
# - **Accuracy** and **Macro-F1**
# - **Macro ROC-AUC** (via one-vs-rest)
# clf = RFCLass(n_estimators=500, max_depth=None, n_jobs=-1, random_state=42)
# clf.fit(X_sel_train, y_train)
#
# proba = clf.predict_proba(X_feat_test)  # shape [n_samples, n_classes]
# pred = np.argmax(proba, axis=1)
#
# acc = metrics.accuracy_score(y_test, pred)
# f1 = metrics.f1_score(y_test, pred, average="macro")
#
# y_test_labels = label_b(y_test, classes=np.arange(len(le.classes_)))
# roc = metrics.roc_auc_score(y_test, proba, average="macro", multi_class="ovr")
#
# print(f"Test Accuracy: {acc:.3f}")
# print(f"Test Macro-F1: {f1:.3f}")
# print(f"Test Macro ROC-AUC: {roc:.3f}")
# print(
#     "\nClassification report:\n",
#     metrics.classification_report(
#         y_test, pred, target_names=[str(c) for c in le.classes_]
#     ),
# )
# <a name='one-vs-rest-roc-curves-(per-class)'></a>
# One-vs-Rest ROC Curves (per class)
# plt.figure(figsize=(8, 6))
# for k, cls in enumerate(le.classes_):
#     fpr, tpr, _ = metrics.roc_curve(y_test_labels[:, k], proba[:, k])
#     roc_auc = metrics.auc(fpr, tpr)
#     plt.plot(fpr, tpr, label=f"Class {cls} (AUC={roc_auc:.3f})")
# plt.plot([0, 1], [0, 1], "--")
# plt.xlabel("False Positive Rate")
# plt.ylabel("True Positive Rate")
# plt.title("One-vs-Rest ROC on HAR (RandomForest + tsfresh)")
# plt.legend(loc="lower right")
# plt.tight_layout()
# plt.show()


# %% [markdown] id="8a85ec83"
# <a name='top-feature-importances'></a>
# Top Feature Importances
# plt.figure(figsize=(8, 4))
# importances = pd.Series(
#     clf.feature_importances_, index=X_sel_train.columns
# ).sort_values(ascending=False)
# topk = 25
# ax = importances.iloc[:topk].sort_values().plot(kind="barh")
# ax.set_title(f"Top {topk} Features")
# ax.set_xlabel("Importance")
# plt.tight_layout()
# plt.show()
