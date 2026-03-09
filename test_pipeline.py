import numpy as np
from tensorflow.keras.models import load_model

from src.data_loader import load_cmapss_data
from src.preprocessing import preprocess_data
from src.window_generator import create_sequences
from src.anomaly_detector import AnomalyDetector
from src.utils import plot_error_distribution, plot_time_series_anomalies

def main():
    print("--- Flight Data Anomaly Detection Pipeline ---")
    
    # 1. Load Data
    df = load_cmapss_data('data/train_FD001.txt')
    df_clean, features = preprocess_data(df, scaler_save_path='models/scaler.pkl')
    
    # 2. Define Window Size
    window_size = 30
    
    # 3. Load the Trained Model
    print("\nLoading trained LSTM Autoencoder...")
    model = load_model('models/lstm_autoencoder.keras')
    detector = AnomalyDetector(model)
    
    # 4. Calculate Threshold using Healthy Data (Cycles <= 100 across all engines)
    print("Calculating baseline threshold from healthy data...")
    healthy_data = df_clean[df_clean['cycle'] <= 100]
    X_healthy = create_sequences(healthy_data, window_size, features)
    threshold = detector.compute_threshold(X_healthy, k=3)
    
    # 5. Test on a Single Engine's Full Lifecycle (e.g., Engine 1)
    target_engine_id = 1
    print(f"\nAnalyzing full lifecycle for Engine {target_engine_id}...")
    engine_data = df_clean[df_clean['engine_id'] == target_engine_id]
    
    X_engine = create_sequences(engine_data, window_size, features)
    
    # Detect anomalies
    is_anomaly, errors = detector.detect_anomalies(X_engine)
    
    # Calculate the corresponding cycles for the plot (accounting for window size offset)
    # If engine has 192 cycles, sequence 0 corresponds to cycle 30
    cycles = engine_data['cycle'].values[window_size - 1:]
    
    # 6. Visualize Results
    print("\nGenerating visual reports...")
    plot_error_distribution(
        errors, 
        threshold, 
        save_path='results/plots/error_distribution.png'
    )
    
    plot_time_series_anomalies(
        cycles, 
        errors, 
        threshold, 
        target_engine_id, 
        save_path=f'results/plots/engine_{target_engine_id}_degradation.png'
    )
    
    print("\nPipeline execution complete. Check 'results/plots/' for output graphs.")

if __name__ == "__main__":
    main()