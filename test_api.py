import requests
import pandas as pd
from src.data_loader import load_cmapss_data

def test_api():
    print("Loading data to simulate a frontend request...")
    # Load the raw data
    df = load_cmapss_data('data/train_FD001.txt')
    
    # Let's grab 30 cycles of data from Engine 1 right before it fails (cycles 163 to 192)
    engine_1 = df[df['engine_id'] == 1]
    failing_sequence = engine_1.tail(30).copy()
    
    # Drop the engine_id and cycle columns to match the 24 inputs the API expects
    failing_sequence = failing_sequence.drop(columns=['engine_id', 'cycle'])
    
    # Convert to a list of lists (JSON format)
    payload = {
        "cycles": failing_sequence.values.tolist()
    }
    
    print("Sending failing engine data to the API...")
    response = requests.post("http://127.0.0.1:8000/predict", json=payload)
    
    print("\nAPI Response:")
    print(response.json())

if __name__ == "__main__":
    test_api()