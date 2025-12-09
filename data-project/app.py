from flask import Flask, jsonify, request, render_template
import log_parser
import analysis
import os

app = Flask(__name__)

# Global storage for parsed data (in-memory for simplicity)
LOG_DATA_DF = None
LOG_FEATURES = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/load_data', methods=['GET'])
def load_data():
    global LOG_DATA_DF, LOG_FEATURES
    
    file_path = os.path.join(os.getcwd(), 'Linux_2k.log')
    if not os.path.exists(file_path):
        return jsonify({'error': 'Log file not found'}), 404
        
    LOG_DATA_DF, LOG_FEATURES, process_mapping = log_parser.parse_logs(file_path)
    
    if LOG_DATA_DF is None:
        return jsonify({'error': 'Failed to parse logs'}), 500
    
    # prepare simple response
    response_data = {
        'points': [],
        'process_mapping': {int(k): v for k, v in process_mapping.items()} # Ensure int keys for JSON
    }
    
    for i, row in LOG_DATA_DF.iterrows():
        response_data['points'].append({
            'x': row['x'],
            'y': row['y'],
            'original_log': f"{row['timestamp_str']} {row['process']}",
            'id': i
        })
        
    return jsonify(response_data)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    global LOG_FEATURES
    if LOG_FEATURES is None:
        return jsonify({'error': 'Data not loaded'}), 400
        
    method = request.json.get('method')
    
    if method == 'isolation_forest':
        labels = analysis.run_isolation_forest(LOG_FEATURES)
        return jsonify({'labels': labels, 'type': 'anomaly'}) # 1 = anomaly
        
    else:
        return jsonify({'error': 'Unknown method'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
