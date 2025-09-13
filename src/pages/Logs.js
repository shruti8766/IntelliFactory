import React, { useState, useEffect, useCallback, useRef } from 'react';
import { apiService } from '../services/api';
import LogsTable from '../components/LogsTable';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBanner from '../components/ErrorBanner';

const Logs = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const isMounted = useRef(true);

  const fetchLogs = useCallback(async () => {
    if (!isMounted.current) return;
    
    try {
      setLoading(true);
      setError(null);
      
      console.log('🔍 Fetching logs...');
      const logsData = await apiService.getLogs();
      console.log('📊 Received logs data:', logsData);
      
      if (isMounted.current) {
        setLogs(logsData.logs || []);
      }
    } catch (err) {
      console.error('❌ Error fetching logs:', err);
      if (isMounted.current) {
        setError(err.message);
      }
    } finally {
      if (isMounted.current) {
        setLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    fetchLogs();
    
    return () => {
      isMounted.current = false;
    };
  }, [fetchLogs]);

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
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            Machine Logs
          </h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            View detailed machine readings and performance data
          </p>
          <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
            📊 Showing {logs.length} machine readings • ✅ Real-time connection active
          </div>
        </div>

        {error && (
          <ErrorBanner message={error} onRetry={fetchLogs} />
        )}

        <LogsTable logs={logs} onRefresh={fetchLogs} />
      </div>
    </div>
  );
};

export default Logs;
