"""
Database connection and management for Manufacturing Anomaly Detection System.
Handles MySQL connections, table creation, and basic database operations.
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime

class DatabaseManager:
    def __init__(self):
        """Initialize database manager with connection parameters."""
        self.connection = None
        self.cursor = None
        self.connect()
        
        if self.connection and self.connection.is_connected():
            self.create_tables()
            print("✅ Database Manager initialized successfully!")

    def connect(self):
        """Establish connection to MySQL database."""
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                database='project', 
                user='root',
                password='123456',
                charset='utf8mb4',
                use_unicode=True
            )
            
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(buffered=True)
                print("✅ Successfully connected to MySQL database!")
            else:
                print("❌ Failed to establish connection to MySQL!")
                self.connection = None
                
        except Error as err:
            print(f"❌ Error connecting to MySQL: {err}")
            self.connection = None
            self.cursor = None

    def create_tables(self):
        """Create all necessary tables if they don't exist."""
        tables = {
            'anomalies': '''
                CREATE TABLE IF NOT EXISTS anomalies (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME NOT NULL,
                    machine_id VARCHAR(50) NOT NULL,
                    anomaly_type VARCHAR(100) NOT NULL,
                    value DECIMAL(10,2),
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_machine_id (machine_id),
                    INDEX idx_type (anomaly_type)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''',
            
            'machine_readings': '''
                CREATE TABLE IF NOT EXISTS machine_readings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    timestamp DATETIME NOT NULL,
                    machine_id VARCHAR(50) NOT NULL,
                    temperature DECIMAL(5,2),
                    units_produced INT,
                    error_flag BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_machine_id (machine_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''',
            
            'machines': '''
                CREATE TABLE IF NOT EXISTS machines (
                    machine_id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    location VARCHAR(100),
                    status ENUM('online', 'offline', 'maintenance') DEFAULT 'online',
                    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            '''
        }
        
        try:
            for table_name, create_sql in tables.items():
                self.cursor.execute(create_sql)
                self.connection.commit()
                print(f"✅ Table '{table_name}' ready")
                
        except Error as err:
            print(f"❌ Error creating tables: {err}")

    def insert_anomaly(self, timestamp, machine_id, anomaly_type, value=None, message=None):
        """Insert a new anomaly record."""
        if not self.connection or not self.connection.is_connected():
            print("❌ Database not connected. Attempting to reconnect...")
            self.connect()
            
        if not self.connection or not self.connection.is_connected():
            print("❌ Failed to reconnect. Cannot insert anomaly.")
            return False

        insert_sql = '''
            INSERT INTO anomalies (timestamp, machine_id, anomaly_type, value, message) 
            VALUES (%s, %s, %s, %s, %s)
        '''
        
        try:
            self.cursor.execute(insert_sql, (timestamp, machine_id, anomaly_type, str(value), message))
            self.connection.commit()
            print(f"✅ Anomaly inserted: {anomaly_type} for {machine_id} at {timestamp}")
            return True
            
        except Error as err:
            print(f"❌ Error inserting anomaly: {err}")
            self.connection.rollback()
            return False

    def insert_machine_reading(self, timestamp, machine_id, temperature=None, units_produced=None, error_flag=False):
        """Insert a new machine reading."""
        insert_sql = '''
            INSERT INTO machine_readings (timestamp, machine_id, temperature, units_produced, error_flag) 
            VALUES (%s, %s, %s, %s, %s)
        '''
        
        try:
            self.cursor.execute(insert_sql, (timestamp, machine_id, temperature, units_produced, error_flag))
            self.connection.commit()
            return True
            
        except Error as err:
            print(f"❌ Error inserting machine reading: {err}")
            self.connection.rollback()
            return False

    def get_recent_anomalies(self, limit=10):
        """Fetch recent anomalies."""
        try:
            query = '''
                SELECT id, timestamp, machine_id, anomaly_type, value, message 
                FROM anomalies 
                ORDER BY timestamp DESC 
                LIMIT %s
            '''
            self.cursor.execute(query, (limit,))
            results = self.cursor.fetchall()
            
            # Convert to list of dictionaries
            columns = ['id', 'timestamp', 'machine_id', 'anomaly_type', 'value', 'message']
            return [dict(zip(columns, row)) for row in results]
            
        except Error as err:
            print(f"❌ Error fetching anomalies: {err}")
            return []

    def get_machine_readings(self, hours=24):
        """Fetch recent machine readings."""
        try:
            query = '''
                SELECT timestamp, machine_id, temperature, units_produced, error_flag 
                FROM machine_readings 
                WHERE timestamp >= NOW() - INTERVAL %s HOUR 
                ORDER BY timestamp DESC
            '''
            self.cursor.execute(query, (hours,))
            results = self.cursor.fetchall()
            
            columns = ['timestamp', 'machine_id', 'temperature', 'units_produced', 'error_flag']
            return [dict(zip(columns, row)) for row in results]
            
        except Error as err:
            print(f"❌ Error fetching machine readings: {err}")
            return []

    def get_machines(self):
        """Get all registered machines."""
        try:
            query = 'SELECT machine_id, name, location, status FROM machines'
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            
            columns = ['machine_id', 'name', 'location', 'status']
            return [dict(zip(columns, row)) for row in results]
            
        except Error as err:
            print(f"❌ Error fetching machines: {err}")
            return []

    def close(self):
        """Close database connections."""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ MySQL connection closed.")
