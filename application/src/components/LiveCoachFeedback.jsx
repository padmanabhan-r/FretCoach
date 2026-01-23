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
  isPaused = false,
  pitchAccuracy,
  scaleConformity,
  timingStability,
  scaleName,
  sessionId,
  totalNotesPlayed = 0,
  correctNotes = 0,
  wrongNotes = 0,
  onEnabledChange
}) => {
  const [enabled, setEnabled] = useState(true); // Default ON
  const [feedbackInterval, setFeedbackInterval] = useState(60); // Default 1 minute
  const [feedback, setFeedback] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const lastFetchRef = useRef(0);
  const audioPlayingRef = useRef(false);
  const metricsRef = useRef({ pitchAccuracy, scaleConformity, timingStability, totalNotesPlayed, correctNotes, wrongNotes });

  // Keep metrics ref updated
  useEffect(() => {
    metricsRef.current = { pitchAccuracy, scaleConformity, timingStability, totalNotesPlayed, correctNotes, wrongNotes };
  }, [pitchAccuracy, scaleConformity, timingStability, totalNotesPlayed, correctNotes, wrongNotes]);

  // Stop audio when paused or stopped
  useEffect(() => {
    if (!isRunning || isPaused) {
      audioPlayingRef.current = false;
      api.stopAudioPlayback().catch(() => {});
    }
  }, [isRunning, isPaused]);

  // Fetch coaching feedback
  const fetchFeedback = useCallback(async (elapsed) => {
    if (!isRunning || !enabled) return;

    // Clear previous feedback before loading new one for seamless transition
    setFeedback(null);
    setLoading(true);
    setError(null);

    try {
      const metrics = metricsRef.current;
      const result = await api.getLiveCoachFeedback({
        pitch_accuracy: metrics.pitchAccuracy,
        scale_conformity: metrics.scaleConformity,
        timing_stability: metrics.timingStability,
        scale_name: scaleName || 'Unknown Scale',
        elapsed_seconds: elapsed,
        session_id: sessionId,
        total_notes_played: metrics.totalNotesPlayed || 0,
        correct_notes: metrics.correctNotes || 0,
        wrong_notes: metrics.wrongNotes || 0
      });

      if (result.success) {
        setFeedback(result);
        lastFetchRef.current = elapsed;

        // Stop any currently playing audio BEFORE starting new audio
        // This ensures UI and audio are always in sync
        // Await the stop to prevent audio overlap
        await api.stopAudioPlayback().catch(() => {});

        // Play audio AFTER text is displayed and old audio is stopped
        if (!audioPlayingRef.current) {
          audioPlayingRef.current = true;
          api.playFeedbackAudio(result.feedback, sessionId).finally(() => {
            audioPlayingRef.current = false;
          }).catch(err => {
            console.warn('Audio playback failed:', err);
          });
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

    if (isRunning && enabled && !isPaused) {
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
      audioPlayingRef.current = false;
      setFeedback(null);
    }

    return () => {
      if (timer) clearInterval(timer);
    };
  }, [isRunning, isPaused, enabled, feedbackInterval, fetchFeedback]);

  // Handle enable toggle
  const handleToggle = () => {
    const newEnabled = !enabled;
    setEnabled(newEnabled);
    if (onEnabledChange) {
      onEnabledChange(newEnabled);
    }
    if (!newEnabled) {
      setFeedback(null);
    }
  };

  return (
    <div className={`backdrop-blur-sm border rounded-xl p-6 h-full flex flex-col ${enabled && isRunning ? 'bg-accent/10 border-accent/50' : 'bg-card/50 border-border'}`}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-foreground flex items-center gap-2">
          <span className="text-2xl">🎤</span>
          Live AI Coach
          {enabled && isRunning && !isPaused && (
            <span className="ml-2 px-2 py-0.5 text-xs font-medium bg-accent/20 text-accent rounded-full flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-accent animate-pulse"></span>
              Active
            </span>
          )}
          {enabled && isRunning && isPaused && (
            <span className="ml-2 px-2 py-0.5 text-xs font-medium bg-muted/20 text-muted-foreground rounded-full flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-muted-foreground"></span>
              Paused
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
        <div className="space-y-4 flex-1 flex flex-col">
          {/* Current Feedback - Grows to fill available space */}
          <div className="bg-gradient-to-r from-accent/20 to-secondary/20 rounded-lg p-4 border border-accent/30 min-h-[80px] flex-1 overflow-y-auto">
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
                  <span className="text-2xl flex-shrink-0">💬</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-foreground font-medium leading-relaxed text-sm">
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
        </div>
      )}

      {/* Disabled State */}
      {!enabled && (
        <div className="flex-1 flex items-center">
          <p className="text-muted-foreground text-sm">
            Enable to receive real-time coaching feedback during your practice session.
            The AI coach will give you brief, motivational tips at your chosen interval.
          </p>
        </div>
      )}

      {/* Not Running State */}
      {enabled && !isRunning && (
        <div className="flex-1 flex items-center justify-center">
          <div className="bg-card rounded-lg p-4 text-center w-full">
            <p className="text-muted-foreground">
              Start a session to receive live coaching feedback
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default LiveCoachFeedback;