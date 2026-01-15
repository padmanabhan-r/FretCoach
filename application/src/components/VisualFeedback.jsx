import React from 'react';

const VisualFeedback = ({ pitchAccuracy, scaleConformity, timingStability }) => {
  const overallScore = Math.round((pitchAccuracy + scaleConformity + timingStability) / 3);
  
  const getColor = (score) => {
    const hue = (score / 100) * 120;
    return `hsl(${hue}, 70%, 50%)`;
  };

  const color = getColor(overallScore);

  return (
    <div className="bg-slate-900/50 backdrop-blur-sm border border-slate-800 rounded-xl p-8">
      <h2 className="text-xl font-semibold mb-6 text-slate-200">Live Feedback</h2>
      
      <div className="flex items-center justify-center">
        <div className="relative">
          <div 
            className="absolute inset-0 rounded-full blur-2xl opacity-50 animate-pulse-slow"
            style={{ backgroundColor: color }}
          />
          
          <div 
            className="relative w-64 h-64 rounded-full flex items-center justify-center border-4 transition-all duration-500"
            style={{ 
              backgroundColor: `${color}20`,
              borderColor: color,
              boxShadow: `0 0 60px ${color}40`
            }}
          >
            <div className="text-center">
              <div className="text-6xl font-bold mb-2" style={{ color }}>
                {overallScore}
              </div>
              <div className="text-slate-400 text-sm uppercase tracking-wider">
                Performance
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-8 text-center text-slate-400 text-sm">
        Real-time audio analysis and feedback
      </div>
    </div>
  );
};

export default VisualFeedback;
