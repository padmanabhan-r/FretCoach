import React, { useState, useEffect, useRef, useCallback } from 'react';
import { api } from '../api';

const INTERVAL_OPTIONS = [
  { value: 30, label: '30s' },
  { value: 60, label: '1 min' },
  { value: 120, label: '2 min' },
  { value: 300, label: '5 min' },
];

const LiveCoachFeedback = ({
  isRunning,
  pitchAccuracy,
  scaleConformity,
  timingStability,
  scaleName,
  sessionId,
  onEnabledChange,
  onFeedbackReceived
}) => {
  const [enabled, setEnabled] = useState(true); // Default ON
  const [feedbackInterval, setFeedbackInterval] = useState(60); // Default 1 minute
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [feedbackHistory, setFeedbackHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false); // Hidden by default
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const lastFetchRef = useRef(0);
  const metricsRef = useRef({ pitchAccuracy, scaleConformity, timingStability });

  // Keep metrics ref updated
  useEffect(() => {
    metricsRef.current = { pitchAccuracy, scaleConformity, timingStability };
  }, [pitchAccuracy, scaleConformity, timingStability]);

  // Fetch coaching feedback
  const fetchFeedback = useCallback(async (elapsed) => {
    if (!isRunning || !enabled) return;

    setLoading(true);
    setError(null);

    try {
      const metrics = metricsRef.current;
      const result = await api.getLiveCoachFeedback({
        pitch_accuracy: metrics.pitchAccuracy / 100, // Convert back to 0-1 range
        scale_conformity: metrics.scaleConformity / 100,
        timing_stability: metrics.timingStability / 100,
        scale_name: scaleName || 'Unknown Scale',
        elapsed_seconds: elapsed,
        session_id: sessionId
      });

      if (result.success) {
        setFeedback(result);
        setFeedbackHistory(prev => [...prev, result].slice(-5)); // Keep last 5
        lastFetchRef.current = elapsed;
        // Notify parent of new feedback
        if (onFeedbackReceived) {
          onFeedbackReceived(result.feedback);
        }
      } else {
        setError('Failed to get feedback');
      }
    } catch (err) {
      console.error('Live coach error:', err);
      setError('Coach unavailable');
    } finally {
      setLoading(false);
    }
  }, [isRunning, enabled, scaleName, sessionId]);

  // Timer for elapsed time and feedback intervals
  useEffect(() => {
    let timer = null;

    if (isRunning && enabled) {
      timer = window.setInterval(() => {
        setElapsedSeconds(prev => {
          const newElapsed = prev + 1;

          // Check if it's time to fetch feedback (wait at least 10 seconds before first fetch)
          if (newElapsed >= 10 && newElapsed - lastFetchRef.current >= feedbackInterval) {
            fetchFeedback(newElapsed);
          }

          return newElapsed;
        });
      }, 1000);

      // Fetch initial feedback after 15 seconds (give time to play some notes)
      const initialTimer = setTimeout(() => {
        if (lastFetchRef.current === 0) {
          fetchFeedback(15);
        }
      }, 15000);

      return () => {
        if (timer) clearInterval(timer);
        clearTimeout(initialTimer);
      };
    } else if (!isRunning) {
      // Reset when stopped
      setElapsedSeconds(0);
      lastFetchRef.current = 0;
      setFeedbackHistory([]);
      setFeedback(null);
    }

    return () => {
      if (timer) clearInterval(timer);
    };
  }, [isRunning, enabled, feedbackInterval, fetchFeedback]);

  // Handle enable toggle
  const handleToggle = () => {
    const newEnabled = !enabled;
    setEnabled(newEnabled);
    if (onEnabledChange) {
      onEnabledChange(newEnabled);
    }
    if (!newEnabled) {
      setFeedback(null);
      setFeedbackHistory([]);
    }
  };

  return (
    <div className={`backdrop-blur-sm border rounded-xl p-6 ${enabled && isRunning ? 'bg-accent/10 border-accent/50' : 'bg-card/50 border-border'}`}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-foreground flex items-center gap-2">
          <span className="text-2xl">🎤</span>
          Live AI Coach
          {enabled && isRunning && (
            <span className="ml-2 px-2 py-0.5 text-xs font-medium bg-accent/20 text-accent rounded-full flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse"></span>
              Active
            </span>
          )}
        </h2>
        <label className="flex items-center gap-2 cursor-pointer">
          <span className="text-sm text-muted-foreground">
            {enabled ? 'On' : 'Off'}
          </span>
          <button
            onClick={handleToggle}
            className={`relative w-12 h-6 rounded-full transition-colors ${
              enabled ? 'bg-accent' : 'bg-card'
            }`}
          >
            <span
              className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
                enabled ? 'translate-x-7' : 'translate-x-1'
              }`}
            />
          </button>
        </label>
      </div>

      {/* Interval Selection */}
      {enabled && (
        <div className="mb-4">
          <label className="block text-sm text-muted-foreground mb-2">
            Feedback Interval
          </label>
          <div className="flex gap-2">
            {INTERVAL_OPTIONS.map(option => (
              <button
                key={option.value}
                onClick={() => setFeedbackInterval(option.value)}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                  feedbackInterval === option.value
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-card text-foreground hover:bg-card/80'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Feedback Display */}
      {enabled && isRunning && (
        <div className="space-y-4">
          {/* Current Feedback */}
          <div className="bg-gradient-to-r from-accent/20 to-secondary/20 rounded-lg p-4 border border-accent/30">
            {loading && !feedback && (
              <div className="flex items-center gap-2 text-muted-foreground">
                <div className="animate-spin w-4 h-4 border-2 border-accent border-t-transparent rounded-full" />
                <span>Coach is analyzing...</span>
              </div>
            )}

            {error && (
              <div className="text-destructive text-sm">{error}</div>
            )}

            {feedback && (
              <div>
                <div className="flex items-start gap-3">
                  <span className="text-2xl">💬</span>
                  <div className="flex-1">
                    <p className="text-foreground font-medium leading-relaxed">
                      {feedback.feedback}
                    </p>
                    {loading && (
                      <div className="mt-2 text-xs text-muted-foreground animate-pulse">Updating...</div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {!feedback && !loading && !error && (
              <p className="text-muted-foreground text-sm">
                {elapsedSeconds < 15
                  ? `Warming up... feedback in ${15 - elapsedSeconds}s`
                  : `Feedback will appear every ${INTERVAL_OPTIONS.find(o => o.value === feedbackInterval)?.label}`
                }
              </p>
            )}
          </div>

          {/* Feedback History - Hidden by default */}
          {feedbackHistory.length > 1 && (
            <div>
              <button
                onClick={() => setShowHistory(!showHistory)}
                className="text-xs text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
              >
                <svg className={`w-3 h-3 transition-transform ${showHistory ? 'rotate-90' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
                Previous ({feedbackHistory.length - 1})
              </button>
              {showHistory && (
                <div className="mt-2 space-y-1">
                  {feedbackHistory.slice(-3, -1).reverse().map((fb, index) => (
                    <div
                      key={index}
                      className="bg-card rounded-lg p-2 text-xs text-muted-foreground line-clamp-2"
                    >
                      {fb.feedback}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Disabled State */}
      {!enabled && (
        <p className="text-muted-foreground text-sm">
          Enable to receive real-time coaching feedback during your practice session.
          The AI coach will give you brief, motivational tips at your chosen interval.
        </p>
      )}

      {/* Not Running State */}
      {enabled && !isRunning && (
        <div className="bg-card rounded-lg p-4 text-center">
          <p className="text-muted-foreground">
            Start a session to receive live coaching feedback
          </p>
        </div>
      )}
    </div>
  );
};

export default LiveCoachFeedback;
