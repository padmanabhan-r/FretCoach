import React from 'react';

const ControlPanel = ({ isRunning, onStart, onStop, onReconfigure, onChangePractice }) => {
  return (
    <div className="bg-card/50 backdrop-blur-sm border border-border rounded-xl p-6">
      <h2 className="text-xl font-semibold mb-4 text-foreground">Controls</h2>

      <div className="space-y-3">
        {!isRunning ? (
          <button
            onClick={onStart}
            className="w-full bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-400 text-white font-semibold py-4 px-6 rounded-lg transition-all duration-200 shadow-lg hover:shadow-primary-500/50 text-lg"
          >
            <div className="flex items-center justify-center space-x-2">
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
              </svg>
              <span>Start Session</span>
            </div>
          </button>
        ) : (
          <button
            onClick={onStop}
            className="w-full bg-gradient-to-r from-destructive to-red-500 hover:from-red-500 hover:to-red-400 text-white font-semibold py-4 px-6 rounded-lg transition-all duration-200 shadow-lg hover:shadow-red-500/50 text-lg"
          >
            <div className="flex items-center justify-center space-x-2">
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
              </svg>
              <span>Stop Session</span>
            </div>
          </button>
        )}

        {onChangePractice && !isRunning && (
          <button
            onClick={onChangePractice}
            className="w-full bg-gradient-to-r from-secondary to-accent hover:from-accent hover:to-secondary text-primary-foreground font-medium py-3 px-4 rounded-lg transition-all duration-200 border border-secondary/50"
          >
            <div className="flex items-center justify-center space-x-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <span>Change Practice</span>
            </div>
          </button>
        )}

        <button
          className="w-full bg-card hover:bg-card/80 text-foreground font-medium py-3 px-4 rounded-lg transition-all duration-200 border border-border hover:border-primary/30"
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
