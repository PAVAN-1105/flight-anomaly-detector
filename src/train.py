import os
import numpy as np
from tensorflow.keras.callbacks import EarlyStopping

# Import the modules we just built
from data_loader import load_cmapss_data
from preprocessing import preprocess_data
from window_generator import create_sequences
from model import build_lstm_autoencoder


def train_model():
    print("1. Loading and preprocessing data...")
    # Assuming the script is run from the root 'flight_anomaly_project' directory
    df = load_cmapss_data('data/train_FD001.txt')
    df_clean, features = preprocess_data(
        df, scaler_save_path='models/scaler.pkl')

    # 2. Filter for healthy data
    # We use the early life of the engines (first 100 cycles) to define "normal" behavior
    healthy_data = df_clean[df_clean['cycle'] <= 100]

    print("2. Generating sliding window sequences...")
    window_size = 30
    X_train = create_sequences(healthy_data, window_size, features)

    print(
        f"Training data shape: {X_train.shape} -> (samples, time_steps, features)")

    print("3. Building LSTM Autoencoder...")
    time_steps = X_train.shape[1]
    num_features = X_train.shape[2]
    model = build_lstm_autoencoder(time_steps, num_features)

    # Use Early Stopping to prevent over-training and save time
    early_stopping = EarlyStopping(
        monitor='val_loss',
        patience=5,             # Stop if validation loss doesn't improve for 5 epochs
        restore_best_weights=True
    )

    print("4. Training the model...")
    # Autoencoders predict their own input, so both input and target are X_train
    history = model.fit(
        X_train, X_train,
        epochs=50,              # Max epochs, early stopping will likely halt it sooner
        batch_size=64,
        validation_split=0.1,   # Use 10% of healthy data to validate
        callbacks=[early_stopping],
        verbose=1
    )

    print("5. Saving the model...")
    os.makedirs('models', exist_ok=True)
    # Save the trained weights for the backend API
    model.save('models/lstm_autoencoder.keras')
    print("Success! Model saved to models/lstm_autoencoder.keras")


if __name__ == '__main__':
    train_model()
