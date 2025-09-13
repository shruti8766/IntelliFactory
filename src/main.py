import pandas as pd
from database import DatabaseManager
from detector import AnomalyDetector

def run_anomaly_detection(csv_file_path):
    """Run anomaly detection on CSV data."""
    try:
        df = pd.read_csv(csv_file_path)
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return

    db_manager = DatabaseManager()
    
    if db_manager.connection and db_manager.connection.is_connected():
        try:
            # Clear old anomalies
            db_manager.cursor.execute("DELETE FROM anomalies")
            db_manager.connection.commit()
            print("✅ Cleared old anomalies from the database.")
            
            detector = AnomalyDetector(db_manager)
            
            for _, row in df.iterrows():
                record = row.to_dict()
                anomalies = detector.detect_anomalies(record)
                
                for anomaly in anomalies:
                    db_manager.insert_anomaly(
                        anomaly['timestamp'],
                        anomaly['machine_id'], 
                        anomaly['anomaly_type'],
                        anomaly['value'],
                        anomaly['description']
                    )
            
            # Show all anomalies in database
            print("\n🔍 All anomalies in database:")
            all_anomalies = db_manager.get_recent_anomalies()
            for anomaly in all_anomalies:
                print(anomaly)
                
            print(f"\n📊 Total anomalies detected: {len(all_anomalies)}")
            
        except Exception as e:
            print(f"❌ Error during anomaly detection: {e}")
        finally:
            db_manager.close()
    else:
        print("❌ Database connection failed.")

if __name__ == '__main__':
    csv_file_path = r'data/manufacturing_logs.csv'
    print(f"📁 Reading CSV file: {csv_file_path}")
    run_anomaly_detection(csv_file_path)
