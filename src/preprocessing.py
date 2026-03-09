import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import joblib
import os

def preprocess_data(df, scaler_save_path='../models/scaler.pkl'):
    """
    Drops constant columns and normalizes the sensor data.
    """
    # In FD001, these sensors and settings are flat/constant
    cols_to_drop = [
        'op_setting_3', 'sensor_1', 'sensor_5', 'sensor_10', 
        'sensor_16', 'sensor_18', 'sensor_19'
    ]
    
    # Drop them if they exist in the dataframe
    cols_to_drop = [col for col in cols_to_drop if col in df.columns]
    df_cleaned = df.drop(columns=cols_to_drop)
    
    # Identify the features to scale (skip engine_id and cycle)
    feature_cols = [col for col in df_cleaned.columns if col not in ['engine_id', 'cycle']]
    
    # Initialize and fit the scaler
    scaler = MinMaxScaler()
    df_cleaned[feature_cols] = scaler.fit_transform(df_cleaned[feature_cols])
    
    # Ensure the models directory exists and save the scaler
    os.makedirs(os.path.dirname(scaler_save_path), exist_ok=True)
    joblib.dump(scaler, scaler_save_path)
    
    return df_cleaned, feature_cols