from database import DatabaseManager

class AnomalyDetector:
    """Anomaly detection logic for manufacturing data."""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def detect_anomalies(self, record):
        """Detect anomalies in a single record."""
        machine_id = record.get('machine_id')
        timestamp = record.get('timestamp')
        units_produced = record.get('units_produced')
        temperature = record.get('temperature')
        error_flag = record.get('error_flag')
        
        anomalies_found = []
        
        if not timestamp:
            print(f"⚠️ Warning: Record missing timestamp: {record}")
            return anomalies_found

        # Low production anomaly
        if units_produced is not None and units_produced < 50:
            anomalies_found.append({
                'machine_id': machine_id,
                'timestamp': timestamp,
                'anomaly_type': 'low_production',
                'value': units_produced,
                'description': f'Units produced ({units_produced}) below threshold (50).'
            })

        # High temperature anomaly  
        if temperature is not None and temperature > 75:
            anomalies_found.append({
                'machine_id': machine_id,
                'timestamp': timestamp,
                'anomaly_type': 'high_temperature',
                'value': temperature,
                'description': f'Temperature ({temperature}) above 75 degrees.'
            })

        # Error flag anomaly
        if error_flag == 1:
            anomalies_found.append({
                'machine_id': machine_id,
                'timestamp': timestamp,
                'anomaly_type': 'error_flag_raised',
                'value': error_flag,
                'description': 'Error flag raised.'
            })

        return anomalies_found
