import React from 'react';

const StatCard = ({ title, value, icon, color = 'blue', trend, subtitle, onClick }) => {
  const colorClasses = {
    blue: 'bg-blue-50 dark:bg-blue-900 text-blue-600 dark:text-blue-300 border-blue-200 dark:border-blue-700',
    red: 'bg-red-50 dark:bg-red-900 text-red-600 dark:text-red-300 border-red-200 dark:border-red-700',
    green: 'bg-green-50 dark:bg-green-900 text-green-600 dark:text-green-300 border-green-200 dark:border-green-700',
    yellow: 'bg-yellow-50 dark:bg-yellow-900 text-yellow-600 dark:text-yellow-300 border-yellow-200 dark:border-yellow-700',
    purple: 'bg-purple-50 dark:bg-purple-900 text-purple-600 dark:text-purple-300 border-purple-200 dark:border-purple-700'
  };

  const trendColors = {
    up: 'text-green-600 dark:text-green-400',
    down: 'text-red-600 dark:text-red-400',
    neutral: 'text-gray-600 dark:text-gray-400'
  };

  return (
    <div className={`bg-white dark:bg-gray-800 overflow-hidden shadow-lg rounded-xl border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-all duration-300 ${onClick ? 'cursor-pointer hover:scale-105' : ''}`}
         onClick={onClick}>
      <div className="p-6">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className={`p-3 rounded-xl border ${colorClasses[color]}`}>
              {icon}
            </div>
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                {title}
              </dt>
              <dd className="flex items-baseline">
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {value}
                </div>
                {trend && (
                  <div className={`ml-2 flex items-baseline text-sm ${trendColors[trend.direction]}`}>
                    {trend.direction === 'up' ? (
                      <svg className="w-3 h-3 flex-shrink-0 self-center" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M5.293 9.707a1 1 0 010-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 01-1.414 1.414L10 6.414 6.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                      </svg>
                    ) : trend.direction === 'down' ? (
                      <svg className="w-3 h-3 flex-shrink-0 self-center" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M14.707 10.293a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L10 13.586l3.293-3.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    ) : null}
                    <span className="ml-1">{trend.value}</span>
                  </div>
                )}
              </dd>
              {subtitle && (
                <dd className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {subtitle}
                </dd>
              )}
            </dl>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatCard;
