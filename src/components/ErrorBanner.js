import React from 'react';

const ErrorBanner = ({ message, onRetry }) => {
  return (
    <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 text-red-700 dark:text-red-200 px-4 py-3 rounded relative mb-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
          <span className="font-medium">Error:</span>
          <span>{message}</span>
        </div>
        {onRetry && (
          <button
            onClick={onRetry}
            className="bg-red-100 dark:bg-red-800 hover:bg-red-200 dark:hover:bg-red-700 px-3 py-1 rounded text-sm font-medium transition-colors"
          >
            Retry
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorBanner;
