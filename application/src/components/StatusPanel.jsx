import React from 'react';

const StatusPanel = ({ isRunning, currentNote, targetScale }) => {
  return (
    <div className="bg-slate-900/50 backdrop-blur-sm border border-slate-800 rounded-xl p-6">
      <h2 className="text-xl font-semibold mb-4 text-slate-200">Status</h2>
      
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-slate-400">Engine</span>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isRunning ? 'bg-green-500 animate-pulse' : 'bg-slate-600'}`} />
            <span className={`font-medium ${isRunning ? 'text-green-400' : 'text-slate-500'}`}>
              {isRunning ? 'Running' : 'Stopped'}
            </span>
          </div>
        </div>

        <div className="h-px bg-slate-800" />

        <div>
          <div className="text-slate-400 text-sm mb-2">Current Note</div>
          <div className="text-3xl font-bold text-center py-4 bg-slate-800/50 rounded-lg text-glow">
            {currentNote}
          </div>
        </div>

        <div>
          <div className="text-slate-400 text-sm mb-2">Target Scale</div>
          <div className="text-lg font-medium text-center py-2 bg-slate-800/50 rounded-lg text-blue-400">
            {targetScale}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatusPanel;
