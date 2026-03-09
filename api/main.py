import os
import tensorflow as tf

# FORCE APPLE SILICON TO USE CPU TO PREVENT GPU DEADLOCKS
tf.config.set_visible_devices([], 'GPU')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
import joblib

# Import our custom ML modules
from src.anomaly_detector import AnomalyDetector
from src.data_loader import load_cmapss_data
from src.preprocessing import preprocess_data
from src.window_generator import create_sequences

app = FastAPI(title="Flight Anomaly Detection API")

# --- CORS CONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --------------------------

# Global variables
model = None
scaler = None
detector = None
threshold = 0.0

@app.on_event("startup")
def startup_event():
    global model, scaler, detector, threshold
    print("--- Booting up API and Loading ML Assets ---")
    
    print("[DEBUG] 1. Loading Keras model...")
    model = load_model('models/lstm_autoencoder.keras')
    
    print("[DEBUG] 2. Loading Scaler...")
    scaler = joblib.load('models/scaler.pkl')
    
    print("[DEBUG] 3. Initializing Detector...")
    detector = AnomalyDetector(model)

    print("[DEBUG] 4. Loading baseline data for threshold...")
    df = load_cmapss_data('data/train_FD001.txt')
    
    print("[DEBUG] 5. Preprocessing data...")
    df_clean, features = preprocess_data(df, scaler_save_path='models/scaler.pkl')
    
    print("[DEBUG] 6. Creating healthy data sequences...")
    healthy_data = df_clean[df_clean['cycle'] <= 100]
    X_healthy = create_sequences(healthy_data, 30, features)

    print("[DEBUG] 7. Calculating threshold (Running first AI prediction)...")
    threshold = detector.compute_threshold(X_healthy, k=2)
    
    print(f"[DEBUG] 8. API Initialized. Threshold: {threshold:.4f}")
    print("INFO: Application startup complete. Ready for frontend!")

# NEW SCHEMA: Accepts full engine history
class EngineDataPayload(BaseModel):
    raw_rows: list[list[float]]

@app.post("/analyze_engine")
def analyze_engine(payload: EngineDataPayload):
    # 1. Define columns (2 columns for ID/Cycle + 24 features)
    columns = ['engine_id', 'cycle', 'op_setting_1', 'op_setting_2', 'op_setting_3'] + \
              [f'sensor_{i}' for i in range(1, 22)]

    df_incoming = pd.DataFrame(payload.raw_rows, columns=columns)

    # 2. Preprocessing
    cols_to_drop = ['op_setting_3', 'sensor_1', 'sensor_5',
                    'sensor_10', 'sensor_16', 'sensor_18', 'sensor_19']
    
    # Keep cycle for mapping errors back to time
    cycles_all = df_incoming['cycle'].values
    df_features = df_incoming.drop(
        columns=['engine_id', 'cycle'] + cols_to_drop)

    # 3. Scale and Sequence
    scaled_data = scaler.transform(df_features)

    window_size = 30
    if len(scaled_data) < window_size:
        raise HTTPException(
            status_code=400, detail="Need at least 30 cycles of data.")

    # Create sliding windows for the entire history
    sequences = []
    for i in range(len(scaled_data) - window_size + 1):
        sequences.append(scaled_data[i: i + window_size])
    X_input = np.array(sequences)

    # 4. Predict for all windows
    is_anomaly, errors = detector.detect_anomalies(X_input)

    # 5. Map results (The error for a window belongs to the last cycle of that window)
    result_cycles = cycles_all[window_size - 1:].tolist()
    errors_list = errors.flatten().tolist()

    # 6. Find the specific point where anomaly first occurs
    anomaly_indices = np.where(is_anomaly)[0]
    first_anomaly_cycle = None
    if len(anomaly_indices) > 0:
        first_anomaly_cycle = int(result_cycles[anomaly_indices[0]])

    return {
        "status": "success",
        "threshold": float(threshold),
        "cycles": result_cycles,
        "errors": errors_list,
        "first_anomaly_cycle": first_anomaly_cycle,
        "is_currently_failing": bool(is_anomaly[-1])
    }

# Keeping your old endpoint for backward compatibility
@app.post("/predict")
def predict_anomaly(data: EngineDataPayload):
    pass