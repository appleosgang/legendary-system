import re
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.decomposition import PCA
from datetime import datetime

LOG_FILE = 'Linux_2k.log'

def parse_logs(file_path):
    """Parses the log file and extracts features."""
    log_pattern = re.compile(r'(\w+\s+\d+\s+\d+:\d+:\d+)\s+(\S+)\s+([^:]+): (.*)')
    
    data = []
    
    try:
        with open(file_path, 'r') as f:
            for line in f:
                match = log_pattern.match(line)
                if match:
                    timestamp_str, host, process, message = match.groups()
                    
                    # Clean process name (remove PID usually in brackets)
                    process_name = re.sub(r'\[\d+\]', '', process).strip()
                    process_name = re.sub(r'\(.*\)', '', process_name).strip() # Remove (pam_unix) etc

                    data.append({
                        'timestamp_str': timestamp_str,
                        'host': host,
                        'process': process_name,
                        'message_length': len(message)
                    })
    except Exception as e:
        print(f"Error reading log file: {e}")
        return None

    if not data:
        return None

    df = pd.DataFrame(data)
    
    # Feature Engineering
    # 1. Convert Timestamp to Hour of Day (float)
    year = 2005 
    df['timestamp'] = pd.to_datetime(df['timestamp_str'] + f' {year}', format='%b %d %H:%M:%S %Y')
    
    # Calculate hour as float (e.g., 14:30 -> 14.5)
    df['hour_numeric'] = df['timestamp'].dt.hour + df['timestamp'].dt.minute / 60.0
    
    # 2. Encode Process Name for Y-axis
    le_process = LabelEncoder()
    df['process_id'] = le_process.fit_transform(df['process'])
    
    # Create a mapping for the frontend (ID -> Name)
    process_mapping = dict(zip(le_process.transform(le_process.classes_), le_process.classes_))
    
    # Features for Anomaly Detection (using the visualization features for consistency)
    features = df[['hour_numeric', 'process_id']].values
    
    # DIRECT MAPPING for Visualization (No PCA)
    # X = Hour of Day (0-24)
    # Y = Process ID (0-N)
    df['x'] = df['hour_numeric']
    df['y'] = df['process_id']
    
    return df, features, process_mapping
