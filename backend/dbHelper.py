import mysql.connector
from mysql.connector import Error

# Add connection pooling to your DBHelper
app.config['SQLALCHEMY_POOL_SIZE'] = 5
app.config['SQLALCHEMY_MAX_OVERFLOW'] = 10
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30


class DBHelper:
    """Database helper class for MySQL operations."""
    
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root', 
            'password': '123456',
            'database': 'project',
            'charset': 'utf8mb4',
            'use_unicode': True
        }

    def connect(self):
        """Create a new database connection."""
        try:
            connection = mysql.connector.connect(**self.config)
            if connection.is_connected():
                print("✅ DBHelper: Successfully connected to MySQL database!")
                return connection
        except Error as e:
            print(f"❌ DBHelper: Error connecting to MySQL: {e}")
            return None

    def close(self, connection):
        """Close database connection."""
        if connection and connection.is_connected():
            connection.close()

    def execute_query(self, query, params=None):
        """Execute a query and return results."""
        connection = None
        try:
            connection = self.connect()
            if connection:
                cursor = connection.cursor(dictionary=True, buffered=True)
                cursor.execute(query, params or ())
                
                # Check if it's a SELECT query
                if query.strip().upper().startswith('SELECT'):
                    result = cursor.fetchall()
                else:
                    connection.commit()
                    result = cursor.rowcount
                    
                cursor.close()
                return result
        except Error as e:
            print(f"❌ DBHelper: Error executing query: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            return None
        finally:
            if connection:
                self.close(connection)

    def insert_anomaly(self, timestamp, machine_id, anomaly_type, value=None, message=None):
        """Insert an anomaly record."""
        query = '''
            INSERT INTO anomalies (timestamp, machine_id, anomaly_type, value, message) 
            VALUES (%s, %s, %s, %s, %s)
        '''
        params = (timestamp, machine_id, anomaly_type, value, message)
        return self.execute_query(query, params)

    def get_anomalies(self, limit=5):
        """Get recent anomalies - FIXED to get all anomalies if recent ones don't exist."""
        query = '''
            SELECT id, timestamp, machine_id, anomaly_type as type, value, message 
            FROM anomalies 
            ORDER BY timestamp DESC 
            LIMIT %s
        '''
        result = self.execute_query(query, (limit,))
        print(f"🔍 DBHelper: Found {len(result) if result else 0} anomalies")
        return result or []

    def get_machine_readings(self, hours=24):
        """Get machine readings - FIXED to handle older data."""
        # First try to get recent readings
        query_recent = '''
            SELECT timestamp, machine_id, temperature, units_produced, error_flag 
            FROM machine_readings 
            WHERE timestamp >= NOW() - INTERVAL %s HOUR 
            ORDER BY timestamp DESC
        '''
        result = self.execute_query(query_recent, (hours,))
        
        # If no recent data found, get the most recent available data
        if not result:
            print(f"⚠️ No readings found in last {hours} hours, getting most recent data...")
            query_latest = '''
                SELECT timestamp, machine_id, temperature, units_produced, error_flag 
                FROM machine_readings 
                ORDER BY timestamp DESC 
                LIMIT 50
            '''
            result = self.execute_query(query_latest)
        
        print(f"🔍 DBHelper: Found {len(result) if result else 0} machine readings")
        return result or []

    def get_machines(self):
        """Get all machines - FIXED to get unique machines from readings if machines table is empty."""
        # First try to get from machines table
        query_machines = 'SELECT machine_id, machine_id as name, "Factory Floor" as location FROM machines'
        result = self.execute_query(query_machines)
        
        # If no machines in table, get unique machines from readings
        if not result:
            print("⚠️ No machines found in machines table, extracting from readings...")
            query_from_readings = '''
                SELECT DISTINCT machine_id, machine_id as name, "Factory Floor" as location 
                FROM machine_readings 
                ORDER BY machine_id
            '''
            result = self.execute_query(query_from_readings)
        
        print(f"🔍 DBHelper: Found {len(result) if result else 0} machines")
        return result or []

    def debug_data(self):
        """Debug method to check what data exists."""
        print("\n🔍 DEBUG: Checking database contents...")
        
        # Check anomalies
        anomalies = self.execute_query("SELECT COUNT(*) as count FROM anomalies")
        print(f"Anomalies count: {anomalies[0]['count'] if anomalies else 0}")
        
        # Check machine_readings
        readings = self.execute_query("SELECT COUNT(*) as count FROM machine_readings")
        print(f"Machine readings count: {readings[0]['count'] if readings else 0}")
        
        # Check date range of readings
        date_range = self.execute_query("""
            SELECT 
                MIN(timestamp) as earliest, 
                MAX(timestamp) as latest 
            FROM machine_readings
        """)
        if date_range and date_range[0]['earliest']:
            print(f"Readings date range: {date_range[0]['earliest']} to {date_range[0]['latest']}")
        
        # Check unique machines
        unique_machines = self.execute_query("SELECT DISTINCT machine_id FROM machine_readings")
        if unique_machines:
            machines = [m['machine_id'] for m in unique_machines]
            print(f"Unique machines: {machines}")

