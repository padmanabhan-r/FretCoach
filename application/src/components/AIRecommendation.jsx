import React from 'react';

function AIRecommendation({ recommendation, onAccept, onReject, loading }) {
  if (loading) {
    return (
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 p-6">
        <div className="flex items-center justify-center space-x-3">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
          <span className="text-slate-300">AI Coach is analyzing your practice history...</span>
        </div>
      </div>
    );
  }

  if (!recommendation) {
    return null;
  }

  // Extract fields from the response structure
  const { config = {}, focus_area, reasoning } = recommendation;
  const { scale_name, scale_type, strictness = 0, sensitivity = 0 } = config;

  return (
    <div className="bg-gradient-to-br from-purple-900/30 to-blue-900/30 backdrop-blur-sm rounded-xl border border-purple-500/50 p-6">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-bold text-purple-300 flex items-center space-x-2">
            <span className="text-2xl">🤖</span>
            <span>AI Coach Recommendation</span>
          </h3>
        </div>

        <div className="bg-slate-900/50 rounded-lg p-4 space-y-3">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-slate-400 text-sm">Recommended Scale</span>
              <p className="text-lg font-semibold text-white">
                {scale_name} {scale_type}
              </p>
            </div>
            <div>
              <span className="text-slate-400 text-sm">Focus Area</span>
              <p className="text-lg font-semibold text-white capitalize">
                {focus_area === 'pitch' && '🎵 Pitch Accuracy'}
                {focus_area === 'scale' && '🎼 Scale Conformity'}
                {focus_area === 'timing' && '⏱️ Timing Stability'}
              </p>
            </div>
          </div>

          <div>
            <span className="text-slate-400 text-sm">Reasoning</span>
            <p className="text-slate-200 mt-1">{reasoning}</p>
          </div>

          <div className="grid grid-cols-2 gap-4 pt-2 border-t border-slate-700">
            <div>
              <span className="text-slate-400 text-sm">Strictness</span>
              <div className="flex items-center space-x-2 mt-1">
                <div className="flex-1 bg-slate-700 rounded-full h-2">
                  <div 
                    className="bg-purple-500 h-2 rounded-full"
                    style={{ width: `${strictness * 100}%` }}
                  ></div>
                </div>
                <span className="text-slate-300 text-sm font-medium">
                  {Math.round(strictness * 100)}%
                </span>
              </div>
            </div>
            <div>
              <span className="text-slate-400 text-sm">Sensitivity</span>
              <div className="flex items-center space-x-2 mt-1">
                <div className="flex-1 bg-slate-700 rounded-full h-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full"
                    style={{ width: `${sensitivity * 100}%` }}
                  ></div>
                </div>
                <span className="text-slate-300 text-sm font-medium">
                  {Math.round(sensitivity * 100)}%
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="flex space-x-3">
          <button
            onClick={onAccept}
            className="flex-1 bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-6 rounded-lg transition-all shadow-lg shadow-purple-500/30"
          >
            ✓ Accept & Start Practice
          </button>
          <button
            onClick={onReject}
            className="bg-slate-700 hover:bg-slate-600 text-slate-300 font-semibold py-3 px-6 rounded-lg transition-all"
          >
            ✗ Reject
          </button>
        </div>
      </div>
    </div>
  );
}

export default AIRecommendation;
