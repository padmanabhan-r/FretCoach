import React from 'react';

const MetricsDisplay = ({ pitchAccuracy, scaleConformity, timingStability }) => {
  const metrics = [
    {
      name: 'Pitch Accuracy',
      value: pitchAccuracy,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
        </svg>
      ),
      color: 'blue',
    },
    {
      name: 'Scale Conformity',
      value: scaleConformity,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      color: 'green',
    },
    {
      name: 'Timing Stability',
      value: timingStability,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      color: 'purple',
    },
  ];

  const getColorClasses = (color, value) => {
    const intensity = value > 66 ? '500' : value > 33 ? '600' : '700';
    return {
      bg: `bg-${color}-${intensity}/20`,
      border: `border-${color}-${intensity}`,
      text: `text-${color}-400`,
    };
  };

  return (
    <div className="bg-slate-900/50 backdrop-blur-sm border border-slate-800 rounded-xl p-6">
      <h2 className="text-xl font-semibold mb-4 text-slate-200">Metrics</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {metrics.map((metric) => {
          const colors = getColorClasses(metric.color, metric.value);
          return (
            <div
              key={metric.name}
              className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 hover:border-slate-600 transition-all"
            >
              <div className="flex items-center justify-between mb-3">
                <div className={colors.text}>
                  {metric.icon}
                </div>
                <div className="text-2xl font-bold text-slate-200">
                  {metric.value}%
                </div>
              </div>
              
              <div className="mb-2">
                <div className="text-sm text-slate-400 mb-1">{metric.name}</div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all duration-500 ${colors.bg} ${colors.border} border`}
                    style={{ width: `${metric.value}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default MetricsDisplay;
