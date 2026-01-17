import React from 'react';

function ModeToggle({ mode, onModeChange, disabled }) {
  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6">
      <div className="flex flex-col space-y-4">
        <h3 className="text-lg font-semibold text-slate-200">Practice Mode</h3>
        
        <div className="flex space-x-4">
          <button
            onClick={() => onModeChange('manual')}
            disabled={disabled}
            className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all ${
              mode === 'manual'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/50'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <div className="flex flex-col items-center space-y-1">
              <span className="text-xl">🎯</span>
              <span>Manual</span>
              <span className="text-xs opacity-75">Choose your scale</span>
            </div>
          </button>

          <button
            onClick={() => onModeChange('ai')}
            disabled={disabled}
            className={`flex-1 py-3 px-4 rounded-lg font-medium transition-all ${
              mode === 'ai'
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/50'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <div className="flex flex-col items-center space-y-1">
              <span className="text-xl">🤖</span>
              <span>AI Coach</span>
              <span className="text-xs opacity-75">AI recommends</span>
            </div>
          </button>
        </div>

        <p className="text-sm text-slate-400">
          {mode === 'manual' 
            ? 'You select the scale and settings for your practice session.'
            : 'AI analyzes your performance and recommends optimal practice sessions.'
          }
        </p>
      </div>
    </div>
  );
}

export default ModeToggle;
