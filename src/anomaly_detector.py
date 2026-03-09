import numpy as np

class AnomalyDetector:
    def __init__(self, model):
        self.model = model
        self.threshold = None

    def calculate_reconstruction_error(self, X):
        """
        Passes data through the autoencoder and calculates the MSE 
        for each sequence.
        """
        # Get the model's reconstruction
        X_pred = self.model.predict(X)
        
        # Calculate Mean Squared Error across the features and time steps
        # X shape: (samples, time_steps, features)
        mse = np.mean(np.power(X - X_pred, 2), axis=(1, 2))
        return mse

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
        """
        if self.threshold is None:
            raise ValueError("Threshold not set. Call compute_threshold() first.")
            
        errors = self.calculate_reconstruction_error(X)
        
        # Boolean array: True if anomaly, False if normal
        anomalies = errors > self.threshold
        return anomalies, errors