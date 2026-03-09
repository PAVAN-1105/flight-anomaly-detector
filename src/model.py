from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, RepeatVector, TimeDistributed, Input

def build_lstm_autoencoder(time_steps, features):
    """
    Builds and compiles an LSTM Autoencoder model.
    """
    model = Sequential([
        # Input shape requires (time_steps, number_of_features)
        Input(shape=(time_steps, features)),
        
        # --- ENCODER ---
        # Compress the sequence. return_sequences=True passes the sequence to the next LSTM
        LSTM(64, activation='relu', return_sequences=True),
        # Compress further into the latent representation. return_sequences=False outputs a single vector
        LSTM(32, activation='relu', return_sequences=False),
        
        # --- LATENT SPACE BRIDGE ---
        # Repeat the latent vector 'time_steps' times to prepare for the decoder
        RepeatVector(time_steps),
        
        # --- DECODER ---
        # Unfold the sequence back to its original temporal shape
        LSTM(32, activation='relu', return_sequences=True),
        LSTM(64, activation='relu', return_sequences=True),
        
        # --- OUTPUT ---
        # Reconstruct the original 17 features for every single time step
        TimeDistributed(Dense(features))
    ])
    
    # Compile with Mean Squared Error (MSE) to measure reconstruction loss
    model.compile(optimizer='adam', loss='mse')
    
    return model