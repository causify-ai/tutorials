import shap_utils
import matplotlib.pyplot as plt
import shap


class SHAPAnalyzer:
    def __init__(self, model):
        """
        Initialize the SHAP analyzer with a trained model.

        Args:
            model: Trained machine learning model (e.g., XGBoost)
        """
        self.model = model
        self.explainer = shap.Explainer(self.model)
        self.shap_values = None

    def compute_shap_values(self, X):
        """
        Compute SHAP values for the input feature set.

        Args:
            X (pd.DataFrame): Feature data to explain

        Returns:
            shap.Explanation object
        """
        self.shap_values = self.explainer(X)
        return self.shap_values

    def plot_global_importance(self, max_display=10):
        """
        Plot bar chart of mean absolute SHAP values for global feature importance.

        Args:
            max_display (int): Maximum number of features to display
        """
        if self.shap_values is not None:
            shap.plots.bar(self.shap_values, max_display=max_display)
        else:
            raise ValueError("Call compute_shap_values() first.")

    def plot_summary_beeswarm(self, X):
        """
        Plot summary beeswarm plot to visualize feature impacts across all predictions.

        Args:
            X (pd.DataFrame): The same feature dataset used for SHAP calculation
        """
        if self.shap_values is not None:
            shap.summary_plot(self.shap_values.values, X, plot_type="dot")
        else:
            raise ValueError("Call compute_shap_values() first.")

    def plot_local_waterfall(self, index=0):
        """
        Plot local explanation using a waterfall plot for a specific prediction.

        Args:
            index (int): Index of the sample to explain
        """
        if self.shap_values is not None:
            shap.plots.waterfall(self.shap_values[index])
        else:
            raise ValueError("Call compute_shap_values() first.")
    
    def plot_dependence(self, feature_name, X):
        """
        Plot SHAP dependence plot for a given feature.

        Args:
            feature_name (str): Feature to visualize
            X (pd.DataFrame): The dataset used for SHAP value computation
        """
        if self.shap_values is not None:
            shap.dependence_plot(feature_name, self.shap_values.values, X)
        else:
            raise ValueError("Call compute_shap_values() first.")

    def plot_decision(self, X_subset=None):
        """
        Plot SHAP decision plot for a subset of instances.

        Args:
            X_subset (pd.DataFrame or None): Optional subset of X to display
        """
        if self.shap_values is not None:
            if X_subset is None:
                X_subset = self.shap_values.data
            shap.decision_plot(self.explainer.expected_value, self.shap_values.values, X_subset)
        else:
            raise ValueError("Call compute_shap_values() first.")
