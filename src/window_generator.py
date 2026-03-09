import numpy as np

def create_sequences(df, window_size, feature_cols):
    """
    Transforms 2D tabular data into 3D sequences for LSTM input.
    Shape becomes: (samples, time_steps, features)
    """
    sequences = []
    
    # We must group by engine_id so we don't accidentally create a sequence 
    # that crosses over from one engine's data into another's.
    for engine_id in df['engine_id'].unique():
        # Extract just the feature columns for this specific engine
        engine_data = df[df['engine_id'] == engine_id][feature_cols].values
        
        # Slide the window across the engine's timeline
        for i in range(len(engine_data) - window_size + 1):
            window = engine_data[i : i + window_size]
            sequences.append(window)
            
    # Convert list of arrays into a single 3D numpy array
    return np.array(sequences)