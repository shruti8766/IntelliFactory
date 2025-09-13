import io from 'socket.io-client';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.listeners = new Map();
    this.isConnecting = false;
    this.connectionAttempts = 0;
    this.maxRetries = 3;
  }

  connect(url = 'http://localhost:5000') {
    // Prevent multiple connections and limit retries
    if (this.isConnecting || (this.socket && this.socket.connected)) {
      console.log('⏳ WebSocket already connecting or connected');
      return this.socket;
    }

    if (this.connectionAttempts >= this.maxRetries) {
      console.log('🚫 Max connection attempts reached');
      return null;
    }

    this.isConnecting = true;
    this.connectionAttempts++;

    // Clean disconnect any existing connection
    if (this.socket) {
      this.socket.removeAllListeners();
      this.socket.disconnect();
      this.socket = null;
    }

    console.log(`🔄 WebSocket connection attempt ${this.connectionAttempts}/${this.maxRetries} to:`, url);

    this.socket = io(url, {
      // Improved connection settings
      transports: ['polling', 'websocket'], // Start with polling, upgrade to websocket
      upgrade: true,
      rememberUpgrade: false, // Don't remember upgrades to prevent issues
      
      // Connection settings
      autoConnect: true,
      forceNew: true, // Force new connection
      
      // Timeout settings
      timeout: 10000, // 10 seconds connection timeout
      
      // Ping settings to prevent timeouts
      pingTimeout: 60000, // 60 seconds
      pingInterval: 25000, // 25 seconds
      
      // Reconnection settings - disabled to prevent loops
      reconnection: false, // We'll handle reconnection manually
    });

    this.setupEventListeners();
    return this.socket;
  }

  setupEventListeners() {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('✅ WebSocket connected successfully:', this.socket.id);
      this.isConnected = true;
      this.isConnecting = false;
      this.connectionAttempts = 0; // Reset attempts on successful connection
      this.notifyListeners('connection', { connected: true });
    });

    this.socket.on('disconnect', (reason) => {
      console.log('❌ WebSocket disconnected. Reason:', reason);
      this.isConnected = false;
      this.isConnecting = false;
      this.notifyListeners('connection', { connected: false });
      
      // Don't auto-reconnect to prevent loops
      if (reason === 'io server disconnect') {
        console.log('Server initiated disconnect - not reconnecting');
      }
    });

    this.socket.on('connect_error', (error) => {
      console.error('❌ WebSocket connection error:', error.message);
      this.isConnected = false;
      this.isConnecting = false;
      this.notifyListeners('error', { error: error.message });
    });

    this.socket.on('status', (data) => {
      console.log('📊 Status update received');
      this.notifyListeners('status', data);
    });

    this.socket.on('liveupdate', (data) => {
      console.log('🔄 Live update received');
      this.notifyListeners('liveupdate', data);
    });

    // Ping/Pong to keep connection alive
    this.socket.on('ping', () => {
      console.log('🏓 Ping received');
    });

    this.socket.on('pong', () => {
      console.log('🏓 Pong received');
    });
  }

  disconnect() {
    if (this.socket) {
      console.log('🔌 Manually disconnecting WebSocket...');
      this.socket.removeAllListeners();
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
      this.isConnecting = false;
      this.connectionAttempts = 0;
    }
  }

  // Manual reconnect method
  reconnect() {
    console.log('🔄 Manual reconnect requested');
    this.disconnect();
    setTimeout(() => {
      this.connect();
    }, 1000);
  }

  addListener(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event).add(callback);
  }

  removeListener(event, callback) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).delete(callback);
    }
  }

  removeAllListeners() {
    this.listeners.clear();
  }

  notifyListeners(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error('❌ Error in WebSocket listener:', error);
        }
      });
    }
  }

  getConnectionStatus() {
    return {
      connected: this.isConnected,
      socketId: this.socket?.id || null,
      isConnecting: this.isConnecting,
      attempts: this.connectionAttempts
    };
  }
}

// Export singleton instance
const websocketService = new WebSocketService();
export default websocketService;
