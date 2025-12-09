from sklearn.ensemble import IsolationForest
import numpy as np

def run_isolation_forest(features, contamination=0.05):
    """
    Runs Isolation Forest on the features.
    Returns:
        labels: -1 for anomalies, 1 for normal (mapped to 1 for anomaly, 0 normal for easier frontend handling potentially)
    """
    model = IsolationForest(contamination=contamination, random_state=42)
    pred = model.fit_predict(features)
    # Map: -1 (anomaly) -> 1, 1 (normal) -> 0
    anomalies = np.where(pred == -1, 1, 0)
    return anomalies.tolist()
