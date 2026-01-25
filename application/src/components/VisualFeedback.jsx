import React, { useState, useEffect } from 'react';

const VisualFeedback = ({ pitchAccuracy, scaleConformity, timingStability, isRunning, isPaused = false }) => {
  const [sessionSeconds, setSessionSeconds] = useState(0);
  const WARMUP_SECONDS = 10; // Wait 10 seconds before showing performance

  // Timer for warmup period - pauses when isPaused
  useEffect(() => {
    let timer = null;
    if (isRunning && !isPaused) {
      timer = setInterval(() => {
        setSessionSeconds(prev => prev + 1);
      }, 1000);
    } else if (!isRunning) {
      setSessionSeconds(0);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [isRunning, isPaused]);

  const overallScore = Math.round((pitchAccuracy + scaleConformity + timingStability) / 3);
  const isWarmingUp = isRunning && sessionSeconds < WARMUP_SECONDS;

  // Get performance label based on score
  const getPerformanceLabel = (score) => {
    if (score >= 70) return 'Excellent';
    if (score >= 50) return 'Good';
    if (score >= 30) return 'Average';
    return 'Needs Work';
  };

  // Get color based on performance level - Red → Yellow → Green palette
  const getColor = (score) => {
    if (score >= 70) return 'hsl(142, 76%, 45%)'; // Green - Excellent
    if (score >= 50) return 'hsl(85, 70%, 45%)'; // Yellow-green - Good
    if (score >= 30) return 'hsl(45, 90%, 50%)'; // Yellow - Average
    return 'hsl(0, 84%, 60%)'; // Red - Needs Work
  };

  // Pre-session state
  if (!isRunning) {
    return (
      <div className="bg-card/50 backdrop-blur-sm border border-border rounded-xl p-6 h-full">
        <h2 className="text-xl font-semibold mb-4 text-foreground">Overall Session Performance</h2>

        <div className="flex items-center justify-center">
          <div className="relative">
            <div
              className="absolute inset-0 rounded-full blur-2xl opacity-30"
              style={{ backgroundColor: 'hsl(0, 0%, 40%)' }}
            />

            <div
              className="relative w-48 h-48 rounded-full flex items-center justify-center border-4 transition-all duration-500"
              style={{
                backgroundColor: 'hsl(0, 0%, 20%)',
                borderColor: 'hsl(0, 0%, 30%)',
                boxShadow: '0 0 40px hsla(0, 0%, 30%, 0.3)'
              }}
            >
              <div className="text-center px-4">
                <div className="text-lg font-medium text-muted-foreground mb-1">
                  Press Start
                </div>
                <div className="text-muted-foreground text-xs uppercase tracking-wider">
                  to begin
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 text-center text-muted-foreground text-sm">
          Waiting for session to start...
        </div>
      </div>
    );
  }

  const label = getPerformanceLabel(overallScore);
  const color = getColor(overallScore);

  // Warmup state - show "Keep playing..." message
  if (isWarmingUp) {
    const warmupColor = 'hsl(200, 70%, 50%)'; // Blue for warmup
    return (
      <div className="bg-card/50 backdrop-blur-sm border border-border rounded-xl p-6 h-full">
        <h2 className="text-xl font-semibold mb-4 text-foreground flex items-center gap-2">
          Overall Session Performance
          <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
        </h2>

        <div className="flex items-center justify-center">
          <div className="relative">
            <div
              className="absolute inset-0 rounded-full blur-2xl opacity-40 animate-pulse"
              style={{ backgroundColor: warmupColor }}
            />

            <div
              className="relative w-48 h-48 rounded-full flex items-center justify-center border-4 transition-all duration-500"
              style={{
                backgroundColor: `${warmupColor}15`,
                borderColor: warmupColor,
                boxShadow: `0 0 40px ${warmupColor}30`
              }}
            >
              <div className="text-center px-4">
                <div className="text-2xl font-bold mb-1" style={{ color: warmupColor }}>
                  Keep Playing
                </div>
                <div className="text-muted-foreground text-sm mt-2">
                  Analyzing in {WARMUP_SECONDS - sessionSeconds}s
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 text-center text-muted-foreground text-sm">
          Play some notes to calibrate...
        </div>
      </div>
    );
  }

  // Paused state
  if (isPaused) {
    const pausedColor = 'hsl(45, 90%, 50%)'; // Yellow for paused
    return (
      <div className="bg-card/50 backdrop-blur-sm border border-border rounded-xl p-6 h-full">
        <h2 className="text-xl font-semibold mb-4 text-foreground flex items-center gap-2">
          Overall Session Performance
          <span className="w-2 h-2 rounded-full bg-yellow-500"></span>
        </h2>

        <div className="flex items-center justify-center">
          <div className="relative">
            <div
              className="absolute inset-0 rounded-full blur-2xl opacity-30"
              style={{ backgroundColor: pausedColor }}
            />

            <div
              className="relative w-48 h-48 rounded-full flex items-center justify-center border-4 transition-all duration-500"
              style={{
                backgroundColor: `${pausedColor}15`,
                borderColor: pausedColor,
                boxShadow: `0 0 40px ${pausedColor}30`
              }}
            >
              <div className="text-center px-4">
                <div className="text-2xl font-bold mb-1" style={{ color: pausedColor }}>
                  Paused
                </div>
                <div className="text-muted-foreground text-sm mt-2">
                  Press Resume to continue
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 text-center text-muted-foreground text-sm">
          Session paused
        </div>
      </div>
    );
  }

  return (
    <div className="bg-card/50 backdrop-blur-sm border border-border rounded-xl p-6 h-full">
      <h2 className="text-xl font-semibold mb-4 text-foreground flex items-center gap-2">
        Overall Session Performance
        <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
      </h2>

      <div className="flex items-center justify-center">
        <div className="relative">
          <div
            className="absolute inset-0 rounded-full blur-2xl opacity-50 animate-pulse-slow"
            style={{ backgroundColor: color }}
          />

          <div
            className="relative w-48 h-48 rounded-full flex items-center justify-center border-4 transition-all duration-500"
            style={{
              backgroundColor: `${color}20`,
              borderColor: color,
              boxShadow: `0 0 60px ${color}40`
            }}
          >
            <div className="text-center">
              <div className="text-3xl font-bold" style={{ color }}>
                {label}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 text-center text-muted-foreground text-sm">
        Average of all metrics
      </div>
    </div>
  );
};

export default VisualFeedback;
