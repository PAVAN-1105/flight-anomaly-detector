import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_error_distribution(errors, threshold, save_path=None):
    """
    Plots the distribution of reconstruction errors and the anomaly threshold.
    """
    plt.figure(figsize=(10, 6))
    sns.histplot(errors, bins=50, kde=True, color='blue', alpha=0.6)
    plt.axvline(x=threshold, color='red', linestyle='--', linewidth=2, label=f'Threshold ({threshold:.4f})')
    
    plt.title('Reconstruction Error Distribution')
    plt.xlabel('Reconstruction Error (MSE)')
    plt.ylabel('Frequency')
    plt.legend()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        print(f"Saved error distribution plot to {save_path}")
    plt.show()

def plot_time_series_anomalies(engine_cycles, errors, threshold, engine_id, save_path=None):
    """
    Plots the reconstruction error over the lifecycle of a specific engine.
    """
    
    
    plt.figure(figsize=(12, 6))
    plt.plot(engine_cycles, errors, label='Reconstruction Error', color='blue')
    plt.axhline(y=threshold, color='red', linestyle='--', label='Anomaly Threshold')
    
    # Highlight the anomaly regions
    anomalies = errors > threshold
    plt.scatter(engine_cycles[anomalies], errors[anomalies], color='red', label='Anomaly Detected')
    
    plt.title(f'Engine {engine_id} Degradation Over Time')
    plt.xlabel('Flight Cycle (Time)')
    plt.ylabel('Reconstruction Error')
    plt.legend()
    
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path)
        print(f"Saved time-series plot to {save_path}")
    plt.show()