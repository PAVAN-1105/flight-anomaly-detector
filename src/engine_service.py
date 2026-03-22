import pandas as pd
import numpy as np
from fastapi import HTTPException

def process_flight_data(raw_rows, scaler, detector, threshold):
    """
    Core business logic for the Flight Anomaly pipeline.
    Takes raw network data, processes it, runs the AI, and formats the response.
    """
    # 1. Define columns (2 columns for ID/Cycle + 21 features)
    columns = ['engine_id', 'cycle', 'op_setting_1', 'op_setting_2', 'op_setting_3'] + \
              [f'sensor_{i}' for i in range(1, 22)]

    df_incoming = pd.DataFrame(raw_rows, columns=columns)

    # 2. Preprocessing
    cols_to_drop = ['op_setting_3', 'sensor_1', 'sensor_5',
                    'sensor_10', 'sensor_16', 'sensor_18', 'sensor_19']
    
    cycles_all = df_incoming['cycle'].values
    df_features = df_incoming.drop(columns=['engine_id', 'cycle'] + cols_to_drop)

    # Map the remaining 14 sensors to their actual physical names for the UI
    active_sensor_names = [
        "Altitude", "Mach Speed", "LPC Temp", "HPC Temp", "LPT Temp", 
        "Bypass Pressure", "HPC Pressure", "Fan Speed", "Core Speed", 
        "Static Pressure", "Fuel Flow Ratio", "Corr. Fan Speed", 
        "Corr. Core Speed", "Bypass Ratio", "Bleed Enthalpy", 
        "HPT Coolant", "LPT Coolant"
    ]

    # 3. Scale and Sequence
    scaled_data = scaler.transform(df_features)
    window_size = 30
    
    if len(scaled_data) < window_size:
        raise HTTPException(status_code=400, detail="Need at least 30 cycles of data.")

    sequences = []
    for i in range(len(scaled_data) - window_size + 1):
        sequences.append(scaled_data[i: i + window_size])
    X_input = np.array(sequences)

    # 4. Predict using the Anomaly Detector
    is_anomaly, total_errors, feature_errors = detector.detect_anomalies(X_input)

    # 5. Map results 
    result_cycles = cycles_all[window_size - 1:].tolist()
    errors_list = total_errors.flatten().tolist()

    anomaly_indices = np.where(is_anomaly)[0]
    first_anomaly_cycle = None
    if len(anomaly_indices) > 0:
        first_anomaly_cycle = int(result_cycles[anomaly_indices[0]])

    # 6. Format and return the final Payload
    return {
        "status": "success",
        "threshold": float(threshold),
        "cycles": result_cycles,
        "errors": errors_list,
        "first_anomaly_cycle": first_anomaly_cycle,
        "is_currently_failing": bool(is_anomaly[-1]),
        "sensor_names": active_sensor_names,
        "all_feature_errors": feature_errors.tolist()
    }