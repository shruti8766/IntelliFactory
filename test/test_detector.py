import sys
import os
from datetime import datetime

# Correct path resolution for imports
backend_src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if backend_src_path not in sys.path:
    sys.path.insert(0, backend_src_path)

try:
    from database import DatabaseManager
    from detector import AnomalyDetector
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure:")
    print("1. The backend/src directory exists")
    print("2. It contains database.py and detector.py files")
    print(f"Current Python path: {sys.path}")
    sys.exit(1)

def test_detector():
    db_manager = DatabaseManager()
    
    if db_manager.connection and db_manager.connection.is_connected():
        try:
            # Fixed: SQL query assuming table is named 'anomalies' not 'anomaly'
            db_manager.cursor.execute("DELETE FROM anomalies")
            db_manager.connection.commit()
            print("✅ Cleared old anomalies from the database before testing.")
        except Exception as e:
            print(f"❌ Error clearing anomalies: {e}")
            db_manager.close()
            return
    else:
        print("❌ Database connection failed.")
        return
    
    detector = AnomalyDetector(db_manager)
    
    # Fixed: test records corrected timestamp typo and added proper datetime format
    test_records = [
        {
            'machine_id': 'M1',
            'timestamp': datetime.strptime('2025-03-07 09:00', '%Y-%m-%d %H:%M'),
            'units_produced': 80,
            'temperature': 60.0,
            'error_flag': 0
        },
        {
            'machine_id': 'M2', 
            'timestamp': datetime.strptime('2025-03-07 09:05', '%Y-%m-%d %H:%M'),
            'units_produced': 40,  # Low production
            'temperature': 70.0,
            'error_flag': 0
        },
        {
            'machine_id': 'M3',
            'timestamp': datetime.strptime('2025-03-07 09:10', '%Y-%m-%d %H:%M'),
            'units_produced': 90,
            'temperature': 85.0,  # High temperature
            'error_flag': 0
        },
        {
            'machine_id': 'M4',
            'timestamp': datetime.strptime('2025-03-07 09:15', '%Y-%m-%d %H:%M'),
            'units_produced': 100,
            'temperature': 65.0,
            'error_flag': 1  # Error flag
        },
        {
            'machine_id': 'M5',
            'timestamp': datetime.strptime('2025-03-07 09:20', '%Y-%m-%d %H:%M'),
            'units_produced': 30,  # Low production
            'temperature': 90.0,   # High temperature
            'error_flag': 1        # Error flag - Multiple anomalies
        }
    ]
    
    total_anomalies = 0
    
    try:
        for record in test_records:
            try:
                anomalies = detector.detect_anomalies(record)
                print(f"Input: {record}")
                
                if anomalies:
                    print("🚨 Detected anomalies:")
                    for anomaly in anomalies:
                        print(f"  - {anomaly}")
                        total_anomalies += len(anomalies)
                else:
                    print("✅ No anomalies detected.")
                print("-" * 40)
                
            except Exception as e:
                print(f"❌ Error processing record {record}: {e}")
                continue
                
        print(f"📊 Total anomalies detected in test: {total_anomalies}")
        
    finally:
        db_manager.close()

if __name__ == '__main__':
    test_detector()
