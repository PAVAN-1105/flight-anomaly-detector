import pandas as pd

def load_cmapss_data(file_path):
    """
    Loads the C-MAPSS dataset and assigns standard column names.
    """
    # Define column names: 2 IDs, 3 Operational Settings, 21 Sensors
    columns = ['engine_id', 'cycle', 'op_setting_1', 'op_setting_2', 'op_setting_3'] + \
              [f'sensor_{i}' for i in range(1, 22)]
    
    # Read the text file (space-separated)
    df = pd.read_csv(file_path, sep=r'\s+', header=None, names=columns)
    
    return df