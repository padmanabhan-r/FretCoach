import React from 'react';

const ControlPanel = ({ isRunning, onStart, onStop, onReconfigure }) => {
  return (
    <div className="bg-slate-900/50 backdrop-blur-sm border border-slate-800 rounded-xl p-6">
      <h2 className="text-xl font-semibold mb-4 text-slate-200">Controls</h2>
      
      <div className="space-y-3">
        {!isRunning ? (
          <button
            onClick={onStart}
            className="w-full bg-gradient-to-r from-green-600 to-green-500 hover:from-green-500 hover:to-green-400 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 shadow-lg hover:shadow-green-500/50"
          >
            <div className="flex items-center justify-center space-x-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
              </svg>
              <span>Start Session</span>
            </div>
          </button>
        ) : (
          <button
            onClick={onStop}
            className="w-full bg-gradient-to-r from-red-600 to-red-500 hover:from-red-500 hover:to-red-400 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 shadow-lg hover:shadow-red-500/50"
          >
            <div className="flex items-center justify-center space-x-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
              </svg>
              <span>Stop Session</span>
            </div>
          </button>
        )}

        <button
          className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium py-3 px-4 rounded-lg transition-all duration-200 border border-slate-700"
          disabled={isRunning}
          onClick={onReconfigure}
        >
          Reconfigure Setup
        </button>
      </div>
    </div>
  );
};

export default ControlPanel;
