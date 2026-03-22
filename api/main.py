import os
import tensorflow as tf

# FORCE APPLE SILICON TO USE CPU TO PREVENT GPU DEADLOCKS
tf.config.set_visible_devices([], 'GPU')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from tensorflow.keras.models import load_model
import joblib

# Import custom ML modules
from src.anomaly_detector import AnomalyDetector
from src.data_loader import load_cmapss_data
from src.preprocessing import preprocess_data
from src.window_generator import create_sequences

# --- NEW: Import our dedicated service layer ---
from src.engine_service import process_flight_data

app = FastAPI(title="Flight Anomaly Detection API")

# --- CORS CONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    """
    Receives flight telemetry from the Angular frontend and routes it 
    to the Engine Service for ML processing and formatting.
    """
    try:
        return process_flight_data(
            raw_rows=payload.raw_rows,
            scaler=scaler,
            detector=detector,
            threshold=threshold
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))