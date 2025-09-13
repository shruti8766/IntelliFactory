from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from dbHelper import DBHelper 
from datetime import datetime, timedelta 
import threading
import time
import json

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "https://intellifactory.netlify.app"])
socketio = SocketIO(app, 
    cors_allowed_origins=["http://localhost:3000", "https://intellifactory.netlify.app"],
    async_mode='eventlet',
    logger=True,
    engineio_logger=True,
    transports=['polling', 'websocket']
)
# CORS(app, origins=["http://localhost:3000"])
# socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3000"], async_mode='eventlet')

#db = DBHelper()

# Store connected clients
connected_clients = set()

def serialize_datetime_objects(obj):
    """Recursively convert datetime objects to ISO format strings"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: serialize_datetime_objects(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_datetime_objects(item) for item in obj]
    elif obj is None:
        return None
    else:
        return obj

# Helper functions defined FIRST
def process_temperature_data(readings):
    if not readings:
        return empty_chart_data("Temperature")
    
    # Group data by machine and time
    machines = {r['machine_id'] for r in readings}
    time_points = sorted({r['timestamp'].strftime('%H:%M') for r in readings})
    
    datasets = []
    colors = [
        ("rgba(255, 99, 132, 1)", "rgba(255, 99, 132, 0.2)"),
        ("rgba(54, 162, 235, 1)", "rgba(54, 162, 235, 0.2)")
    ]
    
    for i, machine_id in enumerate(machines):
        color = colors[i % len(colors)]
        data = [
            next((r['temperature'] for r in readings 
                 if r['machine_id'] == machine_id 
                 and r['timestamp'].strftime('%H:%M') == time), None)
            for time in time_points
        ]
        
        datasets.append({
            "label": f"{machine_id} Temperature",
            "data": data,
            "borderColor": color[0],
            "backgroundColor": color[1],
            "tension": 0.1
        })
    
    return {
        "labels": time_points,
        "datasets": datasets
    }

def process_production_data(readings):
    if not readings:
        return empty_chart_data("Production")
    
    # Similar to temperature but for production
    machines = {r['machine_id'] for r in readings}
    time_points = sorted({r['timestamp'].strftime('%H:%M') for r in readings})
    
    datasets = []
    for machine_id in machines:
        data = [
            next((r['units_produced'] for r in readings 
                 if r['machine_id'] == machine_id 
                 and r['timestamp'].strftime('%H:%M') == time), None)
            for time in time_points
        ]
        
        datasets.append({
            "label": f"{machine_id} Production",
            "data": data,
            "borderColor": "rgba(75, 192, 192, 1)",
            "backgroundColor": "rgba(75, 192, 192, 0.2)",
            "tension": 0.1
        })
    
    return {
        "labels": time_points,
        "datasets": datasets
    }

def empty_chart_data(title):
    return {
        "labels": [],
        "datasets": [{
            "label": title,
            "data": [],
            "borderColor": "rgba(200, 200, 200, 1)",
            "backgroundColor": "rgba(200, 200, 200, 0.1)"
        }]
    }

@socketio.on('connect')
def handle_connect():
    connected_clients.add(request.sid)
    print(f'✅ Client connected: {request.sid}')
    emit('status', {'msg': 'Connected to Manufacturing Monitor', 'timestamp': datetime.now().isoformat()})

@socketio.on('disconnect')
def handle_disconnect():
    connected_clients.discard(request.sid)
    print(f'❌ Client disconnected: {request.sid}')

def real_time_data_broadcaster():
    """Background task to broadcast real-time data"""
    print("🚀 Starting real-time data broadcaster...")
    
    while True:
        try:
            if connected_clients:
                # Get latest data
                anomalies = db.get_anomalies(limit=10)
                readings = db.get_machine_readings(hours=1)
                machines = db.get_machines()
                
                # Serialize all datetime objects BEFORE broadcasting
                anomalies_clean = serialize_datetime_objects(anomalies) if anomalies else []
                readings_clean = serialize_datetime_objects(readings[-10:]) if readings else []
                
                # Process data for charts
                temperature_data = process_temperature_data(readings) if readings else empty_chart_data("Temperature")
                production_data = process_production_data(readings) if readings else empty_chart_data("Production")
                
                # Create broadcast data with all datetime objects serialized
                broadcast_data = {
                    'timestamp': datetime.now().isoformat(),
                    'anomalies': anomalies_clean,
                    'readings': readings_clean,
                    'machine_count': len(machines) if machines else 0,
                    'anomaly_count': len(anomalies) if anomalies else 0,
                    'temperature_data': temperature_data,
                    'production_data': production_data
                }
                
                # Broadcast to all connected clients
                socketio.emit('liveupdate', broadcast_data, room=None)
                print(f"✅ Broadcasted update to {len(connected_clients)} clients - No errors!")
            
            time.sleep(5)  # Update every 5 seconds
            
        except Exception as e:
            print(f"❌ Real-time broadcast error: {e}")
            time.sleep(10)

# Start background thread
real_time_thread = threading.Thread(target=real_time_data_broadcaster)
real_time_thread.daemon = True
real_time_thread.start()

@app.route('/api/dashboard', methods=['GET'])
def dashboard():
    try:
        # Get dashboard data
        anomalies = db.get_anomalies(limit=5)
        machines = db.get_machines()
        readings = db.get_machine_readings(hours=24)
        
        # FIXED: Serialize datetime objects in anomalies
        anomalies_clean = serialize_datetime_objects(anomalies) if anomalies else []
        
        response_data = {
            "anomalyCount": len(anomalies) if anomalies else 0,
            "machineCount": len(machines) if machines else 0,
            "recentAnomalies": anomalies_clean,  # Now properly serialized
            "temperatureData": process_temperature_data(readings) if readings else empty_chart_data("Temperature"),
            "productionData": process_production_data(readings) if readings else empty_chart_data("Production"),
            "status": "✅ Enhanced Backend with WebSocket (FIXED!)",
            "timestamp": datetime.now().isoformat()
        }
        
        print(f"📊 Dashboard: {len(anomalies or [])} anomalies, {len(machines or [])} machines")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"❌ Dashboard error: {str(e)}")
        return jsonify({
            "error": str(e),
            "anomalyCount": 0,
            "machineCount": 0,
            "recentAnomalies": [],
            "temperatureData": empty_chart_data("Temperature"),
            "productionData": empty_chart_data("Production"),
            "status": "❌ Backend Error"
        }), 200

@app.route('/api/logs', methods=['GET'])
def get_logs():
    try:
        readings = db.get_machine_readings(hours=24)
        if not readings:
            return jsonify({"logs": []}), 200
            
        # Format for frontend with datetime serialization
        logs = [{
            "timestamp": r['timestamp'].isoformat() if r['timestamp'] else None,
            "machine_id": r['machine_id'],
            "temperature": r['temperature'],
            "units_produced": r['units_produced'],
            "error_flag": bool(r['error_flag']),
            "status": "anomaly" if r['error_flag'] else "normal"
        } for r in readings]
        
        return jsonify({"logs": logs})
        
    except Exception as e:
        print(f"❌ Logs error: {str(e)}")
        return jsonify({"error": str(e), "logs": []}), 200

@app.route('/api/system/health', methods=['GET'])
def system_health():
    """System health with WebSocket status"""
    try:
        machines = db.get_machines()
        db_status = "connected" if machines is not None else "error"
        
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "database": db_status,
            "websocket": {
                "connected_clients": len(connected_clients),
                "real_time_enabled": True
            },
            "message": "Enhanced backend with FIXED WebSocket support!"
        }
        
        return jsonify(health_data)
        
    except Exception as e:
        return jsonify({
            "timestamp": datetime.now().isoformat(),
            "status": "unhealthy", 
            "error": str(e)
        }), 500
    
@app.route('/api/debug', methods=['GET'])
def debug_data():
    """Debug route to check database contents."""
    try:
        db.debug_data()  # This will print to console
        
        # Get actual data for response
        anomalies = db.get_anomalies(limit=10)
        readings = db.get_machine_readings(hours=24)
        machines = db.get_machines()
        
        debug_info = {
            "anomalies_count": len(anomalies) if anomalies else 0,
            "readings_count": len(readings) if readings else 0,
            "machines_count": len(machines) if machines else 0,
            "sample_reading": readings[0] if readings else None,
            "sample_anomaly": anomalies[0] if anomalies else None,
            "machines_list": machines if machines else []
        }
        
        return jsonify(debug_info)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("🚀 Starting Enhanced Manufacturing Monitor with WebSocket...")
    print("📊 Dashboard API: http://localhost:5000/api/dashboard")
    print("🏥 Health Check: http://localhost:5000/api/system/health")
    print("🔗 WebSocket: Real-time updates enabled")
    print("🎯 CORS: Enabled for http://localhost:3000")
    socketio.run(app, debug=True, port=5000, host='0.0.0.0')






