// import axios from 'axios';


// const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

// const api = axios.create({
//   baseURL: API_BASE_URL,
//   timeout: 10000,
//   headers: {
//     'Content-Type': 'application/json',
//   },
// });

// // Response interceptor for error handling
// api.interceptors.response.use(
//   response => response,
//   error => {
//     console.error('API Error:', error);
//     return Promise.reject(error);
//   }
// );

// export const apiService = {
//   // Get dashboard data
//   getDashboard: async () => {
//     try {
//       const response = await api.get('/api/dashboard');
//       return response.data;
//     } catch (error) {
//       throw new Error(`Failed to fetch dashboard data: ${error.message}`);
//     }
//   },

//   // Get logs data
//   getLogs: async () => {
//     try {
//       const response = await api.get('/api/logs');
//       return response.data;
//     } catch (error) {
//       throw new Error(`Failed to fetch logs data: ${error.message}`);
//     }
//   },

//   // Get system health
//   getSystemHealth: async () => {
//     try {
//       const response = await api.get('/api/systemhealth');
//       return response.data;
//     } catch (error) {
//       throw new Error(`Failed to fetch system health: ${error.message}`);
//     }
//   }
// };

// export default api;
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'https://intellifactory-1.onrender.com';

// const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_URL,  // ← FIXED: Changed from API_BASE_URL to API_URL
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const apiService = {
  // Get dashboard data
  getDashboard: async () => {
    try {
      const response = await api.get('/api/dashboard');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch dashboard data: ${error.message}`);
    }
  },

  // Get logs data
  getLogs: async () => {
    try {
      const response = await api.get('/api/logs');
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch logs data: ${error.message}`);
    }
  },

  // Get system health
  getSystemHealth: async () => {
    try {
      const response = await api.get('/api/system/health'); // Fixed endpoint name
      return response.data;
    } catch (error) {
      throw new Error(`Failed to fetch system health: ${error.message}`);
    }
  }
};

export default api;
