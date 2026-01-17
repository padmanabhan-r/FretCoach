import React from 'react';

const MetricsDisplay = ({ pitchAccuracy, scaleConformity, timingStability, isRunning }) => {
  const metrics = [
    {
      name: 'Pitch Accuracy',
      value: pitchAccuracy,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
        </svg>
      ),
      colorClass: 'primary',
    },
    {
      name: 'Scale Conformity',
      value: scaleConformity,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      colorClass: 'secondary',
    },
    {
      name: 'Timing Stability',
      value: timingStability,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      colorClass: 'accent',
    },
  ];

  // Get HSL color based on metric type
  const getMetricColor = (colorClass) => {
    switch (colorClass) {
      case 'primary':
        return 'hsl(14, 98%, 55%)'; // Orange-red
      case 'secondary':
        return 'hsl(25, 95%, 50%)'; // Orange
      case 'accent':
        return 'hsl(34, 97%, 55%)'; // Golden
      default:
        return 'hsl(14, 98%, 55%)';
    }
  };

  return (
    <div className="bg-card/50 backdrop-blur-sm border border-border rounded-xl p-6">
      <h2 className="text-xl font-semibold mb-4 text-foreground flex items-center gap-2">
        Metrics
        {isRunning && <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>}
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {metrics.map((metric) => {
          const color = getMetricColor(metric.colorClass);
          const displayValue = isRunning ? metric.value : '--';
          return (
            <div
              key={metric.name}
              className="bg-card border border-border rounded-lg p-4 hover:border-primary/50 transition-all"
            >
              <div className="flex items-center justify-between mb-3">
                <div style={{ color: isRunning ? color : 'hsl(0, 0%, 40%)' }}>
                  {metric.icon}
                </div>
                <div className={`text-2xl font-bold ${isRunning ? 'text-foreground' : 'text-muted-foreground'}`}>
                  {displayValue}{isRunning ? '%' : ''}
                </div>
              </div>

              <div className="mb-2">
                <div className="text-sm text-muted-foreground mb-1">{metric.name}</div>
                <div className="w-full bg-background rounded-full h-2">
                  <div
                    className="h-2 rounded-full transition-all duration-500"
                    style={{
                      width: isRunning ? `${metric.value}%` : '0%',
                      backgroundColor: color,
                      boxShadow: isRunning ? `0 0 8px ${color}60` : 'none'
                    }}
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
