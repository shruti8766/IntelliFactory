import React, { useState, useEffect, useCallback } from 'react';
import { apiService } from '../services/api';
import websocketService from '../services/websocket';
import StatCard from '../components/StatCard';
import LineChart from '../components/LineChart';
import AnomalyTable from '../components/AnomalyTable';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBanner from '../components/ErrorBanner';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [liveData, setLiveData] = useState(null);

  // WebSocket event handlers
  const handleConnectionChange = useCallback((connectionData) => {
    setIsConnected(connectionData.connected);
  }, []);

  const handleLiveUpdate = useCallback((updateData) => {
    console.log('Received live update:', updateData);
    setLastUpdate(new Date(updateData.timestamp));
    setLiveData(updateData);
    
    // Update dashboard data with live data
    setData(prevData => ({
      ...prevData,
      anomalyCount: updateData.anomaly_count,
      machineCount: updateData.machine_count,
      recentAnomalies: updateData.anomalies,
      temperatureData: updateData.temperature_data,
      productionData: updateData.production_data,
    }));
  }, []);

  const handleWebSocketError = useCallback((errorData) => {
    console.error('WebSocket error:', errorData);
    setError(`WebSocket error: ${errorData.error}`);
  }, []);

  useEffect(() => {
    // Connect to WebSocket
    websocketService.connect();
    
    // Add event listeners
    websocketService.addListener('connection', handleConnectionChange);
    websocketService.addListener('liveupdate', handleLiveUpdate);
    websocketService.addListener('error', handleWebSocketError);
    
    // Initial data fetch
    fetchInitialData();
    
    // Cleanup
    return () => {
      websocketService.removeListener('connection', handleConnectionChange);
      websocketService.removeListener('liveupdate', handleLiveUpdate);
      websocketService.removeListener('error', handleWebSocketError);
    };
  }, [handleConnectionChange, handleLiveUpdate, handleWebSocketError]);

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      setError(null);
      const dashboardData = await apiService.getDashboard();
      setData(dashboardData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 pt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <LoadingSpinner size="large" />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                Manufacturing Dashboard
              </h1>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                Real-time monitoring of manufacturing operations and anomaly detection
              </p>
            </div>
            
            {/* Connection Status */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center">
                <div className={`w-3 h-3 rounded-full mr-2 ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              {lastUpdate && (
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  Last update: {lastUpdate.toLocaleTimeString()}
                </div>
              )}
            </div>
          </div>
        </div>

        {error && (
          <ErrorBanner message={error} onRetry={fetchInitialData} />
        )}

        {data && (
          <>
            {/* Live Update Indicator */}
            {liveData && (
              <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900 border border-blue-200 dark:border-blue-700 rounded-lg">
                <div className="flex items-center">
                  <div className="animate-pulse w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
                  <span className="text-sm text-blue-700 dark:text-blue-300">
                    Live data streaming - Last update: {new Date(liveData.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            )}

            {/* Statistics Cards */}
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
              <StatCard
                title="Critical Anomalies"
                value={data.anomalyCount || 0}
                color="red"
                subtitle="Requires immediate attention"
                trend={{ direction: 'down', value: '12% vs yesterday' }}
                icon={
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                }
              />
              <StatCard
                title="Active Machines"
                value={data.machineCount || 0}
                color="blue"
                subtitle="Currently online"
                trend={{ direction: 'up', value: '2 new today' }}
                icon={
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                  </svg>
                }
              />
              <StatCard
                title="Production Efficiency"
                value="94.2%"
                color="green"
                subtitle="Above target (90%)"
                trend={{ direction: 'up', value: '2.1% improvement' }}
                icon={
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                }
              />
              <StatCard
                title="System Health"
                value="Excellent"
                color="green"
                subtitle="All systems operational"
                icon={
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                  </svg>
                }
              />
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
              <LineChart 
                data={data.temperatureData?.labels && data.temperatureData?.datasets ? data.temperatureData : { labels: [], datasets: [] }}
                title="Temperature Monitoring (Live)" 
                height={350} 
              />
              <LineChart 
                data={data.productionData?.labels && data.productionData?.datasets ? data.productionData : { labels: [], datasets: [] }}
                title="Production Monitoring (Live)" 
                height={350} 
              />
            </div>

            {/* Recent Anomalies Table */}
            <AnomalyTable anomalies={data.recentAnomalies || []} />
          </>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
