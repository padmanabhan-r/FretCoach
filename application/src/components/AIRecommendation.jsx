import React, { useState } from 'react';

function AIRecommendation({ recommendation, onAccept, onReject, onTryAnother, loading, error }) {
  const [ambientLighting, setAmbientLighting] = useState(true);

  if (loading) {
    return (
      <div className="bg-card/50 backdrop-blur-sm rounded-xl border border-border p-6">
        <div className="flex items-center justify-center space-x-3">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent"></div>
          <span className="text-foreground">AI Coach is analyzing your practice history...</span>
        </div>
      </div>
    );
  }

  // Show error state with friendly message
  if (error) {
    return (
      <div className="bg-card/50 backdrop-blur-sm rounded-xl border border-border p-6">
        <div className="text-center space-y-4">
          <div className="text-4xl">🤖</div>
          <h3 className="text-xl font-semibold text-foreground">AI Coach Unavailable</h3>
          <p className="text-muted-foreground">{error}</p>
          <button
            onClick={onReject}
            className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold py-3 px-6 rounded-lg transition-all"
          >
            Switch to Manual Mode
          </button>
        </div>
      </div>
    );
  }

  if (!recommendation) {
    return null;
  }

  // Extract fields from the response structure
  const { config = {}, focus_area, reasoning, is_pending_plan, analysis } = recommendation;
  const { scale_name, scale_type, strictness = 0, sensitivity = 0 } = config;

  const handleAccept = () => {
    onAccept(ambientLighting);
  };

  return (
    <div className="bg-gradient-to-br from-accent/20 to-secondary/20 backdrop-blur-sm rounded-xl border border-accent/50 p-6">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-xl font-bold text-accent flex items-center space-x-2">
            <span className="text-2xl">🤖</span>
            <span>AI Coach Recommendation</span>
          </h3>
        </div>

        {/* Source Indicator */}
        <div className="flex items-center gap-2 text-sm">
          <span className={`px-2 py-1 rounded-full ${is_pending_plan ? 'bg-secondary/30 text-secondary' : 'bg-accent/30 text-accent'}`}>
            {is_pending_plan ? (
              <>
                <span className="mr-1">📋</span>
                Based on your previous practice plan
              </>
            ) : (
              <>
                <span className="mr-1">✨</span>
                Generated fresh by AI
              </>
            )}
          </span>
        </div>

        <div className="bg-background/50 rounded-lg p-4 space-y-3">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-muted-foreground text-sm">Recommended Scale</span>
              <p className="text-lg font-semibold text-foreground">
                {scale_name} {scale_type}
              </p>
            </div>
            <div>
              <span className="text-muted-foreground text-sm">Focus Area</span>
              <p className="text-lg font-semibold text-foreground capitalize">
                {focus_area === 'pitch' && 'Pitch Accuracy'}
                {focus_area === 'scale' && 'Scale Conformity'}
                {focus_area === 'timing' && 'Timing Stability'}
              </p>
            </div>
          </div>

          <div>
            <span className="text-muted-foreground text-sm">Reasoning</span>
            <p className="text-foreground/80 mt-1">{reasoning}</p>
          </div>

          {/* Show analysis metrics if available */}
          {analysis && analysis.total_sessions > 0 && (
            <div className="pt-2 border-t border-border">
              <span className="text-muted-foreground text-xs">Based on {analysis.total_sessions} practice session{analysis.total_sessions > 1 ? 's' : ''}</span>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4 pt-2 border-t border-border">
            <div>
              <span className="text-muted-foreground text-sm">Strictness</span>
              <div className="flex items-center space-x-2 mt-1">
                <div className="flex-1 bg-card rounded-full h-2">
                  <div
                    className="bg-primary h-2 rounded-full"
                    style={{ width: `${strictness * 100}%` }}
                  ></div>
                </div>
                <span className="text-foreground text-sm font-medium">
                  {Math.round(strictness * 100)}%
                </span>
              </div>
            </div>
            <div>
              <span className="text-muted-foreground text-sm">Sensitivity</span>
              <div className="flex items-center space-x-2 mt-1">
                <div className="flex-1 bg-card rounded-full h-2">
                  <div
                    className="bg-secondary h-2 rounded-full"
                    style={{ width: `${sensitivity * 100}%` }}
                  ></div>
                </div>
                <span className="text-foreground text-sm font-medium">
                  {Math.round(sensitivity * 100)}%
                </span>
              </div>
            </div>
          </div>

          {/* Ambient Lighting Toggle */}
          <div className="pt-2 border-t border-border">
            <label className="flex items-center justify-between p-3 bg-card/50 rounded-lg hover:bg-card cursor-pointer transition-all">
              <div>
                <div className="text-foreground font-medium">Ambient Lighting</div>
                <div className="text-muted-foreground text-sm">Enable smart bulb visual feedback</div>
              </div>
              <input
                type="checkbox"
                checked={ambientLighting}
                onChange={(e) => setAmbientLighting(e.target.checked)}
                className="w-5 h-5 text-accent bg-card border-border rounded focus:ring-accent focus:ring-2"
              />
            </label>
          </div>
        </div>

        <div className="flex flex-col space-y-2">
          <div className="flex space-x-3">
            <button
              onClick={handleAccept}
              className="flex-1 bg-accent hover:bg-accent/90 text-accent-foreground font-semibold py-3 px-6 rounded-lg transition-all shadow-lg"
              style={{ boxShadow: '0 0 20px hsl(34, 97%, 55%, 0.3)' }}
            >
              Accept & Start Practice
            </button>
            <button
              onClick={onReject}
              className="bg-card hover:bg-card/80 text-foreground font-semibold py-3 px-6 rounded-lg transition-all border border-border"
            >
              ← Back to mode selection
            </button>
          </div>
          {/* Try Another Button */}
          {onTryAnother && (
            <button
              onClick={onTryAnother}
              className="w-full text-sm text-muted-foreground hover:text-foreground transition-colors py-2"
            >
              <span className="mr-1">🔄</span>
              Try another AI suggestion
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default AIRecommendation;
