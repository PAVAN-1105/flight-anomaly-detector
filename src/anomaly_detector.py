import numpy as np

class AnomalyDetector:
    def __init__(self, model):
        self.model = model
        self.threshold = None

    def calculate_reconstruction_error(self, X, return_feature_errors=False):
        """
        Passes data through the autoencoder and calculates the MSE.
        Can optionally return the error broken down by individual features (sensors).
        """
        # Bypass the buggy model.predict() API and use a raw tensor forward pass.
        # This prevents the Uvicorn background-thread deadlock.
        X_pred_tensor = self.model(X, training=False)
        
        # Convert the raw TensorFlow tensor back into a standard Numpy array
        X_pred = X_pred_tensor.numpy()

        # Calculate the raw squared error (Shape: samples, time_steps, features)
        squared_error = np.power(X - X_pred, 2)

        # 1. Average across the time steps (axis=1).
        feature_mse = np.mean(squared_error, axis=1)

        # 2. Average across the sensors (axis=1 of the new array).
        total_mse = np.mean(feature_mse, axis=1)

        if return_feature_errors:
            return total_mse, feature_mse
        return total_mse

    def compute_threshold(self, X_normal, k=3):
        """
        Calculates the threshold using normal/healthy data.
        Formula: Mean + (k * Standard Deviation)
        """
        errors = self.calculate_reconstruction_error(X_normal)
        self.threshold = np.mean(errors) + k * np.std(errors)
        print(f"Calculated Anomaly Threshold: {self.threshold:.4f}")
        return self.threshold

    def detect_anomalies(self, X):
        """
        Flags sequences as anomalies if their error exceeds the threshold.
        Returns the boolean flags, the total errors, AND the specific sensor errors.
        """
        if self.threshold is None:
            raise ValueError("Threshold not set. Call compute_threshold() first.")

        # Grab BOTH the total errors for the line chart, and the feature errors for the bar chart
        total_errors, feature_errors = self.calculate_reconstruction_error(
            X, return_feature_errors=True)

        # Boolean array: True if anomaly, False if normal
        anomalies = total_errors > self.threshold

        return anomalies, total_errors, feature_errors