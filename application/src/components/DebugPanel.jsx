import React from 'react';

const DebugPanel = ({ debugInfo, show }) => {
  if (!show || !debugInfo) return null;

  const noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
  const noteName = noteNames[debugInfo.pitch_class] || '-';

  return (
    <div className="bg-card/50 backdrop-blur-sm border border-border rounded-xl p-4 mt-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-foreground">Debug Info</h3>
        <span className="text-xs text-muted font-mono">Real-time Detection</span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        <div className="bg-card rounded-lg p-3">
          <div className="text-xs text-muted-foreground mb-1">Detected Frequency</div>
          <div className="text-lg font-mono text-primary">
            {debugInfo.detected_hz > 0 ? `${debugInfo.detected_hz.toFixed(2)} Hz` : '-'}
          </div>
        </div>

        <div className="bg-card rounded-lg p-3">
          <div className="text-xs text-muted-foreground mb-1">MIDI Note</div>
          <div className="text-lg font-mono text-secondary">
            {debugInfo.detected_midi > 0 ? debugInfo.detected_midi.toFixed(2) : '-'}
          </div>
        </div>

        <div className="bg-card rounded-lg p-3">
          <div className="text-xs text-muted-foreground mb-1">Pitch Class</div>
          <div className="text-lg font-mono text-accent">
            {debugInfo.pitch_class !== undefined ? `${debugInfo.pitch_class} (${noteName})` : '-'}
          </div>
        </div>

        <div className="bg-card rounded-lg p-3">
          <div className="text-xs text-muted-foreground mb-1">In Scale?</div>
          <div className={`text-lg font-bold ${debugInfo.in_scale ? 'text-accent' : 'text-destructive'}`}>
            {debugInfo.in_scale ? 'TRUE' : 'FALSE'}
          </div>
        </div>

        <div className="bg-card rounded-lg p-3">
          <div className="text-xs text-muted-foreground mb-1">Raw Pitch Score</div>
          <div className="text-lg font-mono text-primary">
            {(debugInfo.raw_pitch * 100).toFixed(1)}%
          </div>
        </div>

        <div className="bg-card rounded-lg p-3">
          <div className="text-xs text-muted-foreground mb-1">Raw Timing Score</div>
          <div className="text-lg font-mono text-secondary">
            {(debugInfo.raw_timing * 100).toFixed(1)}%
          </div>
        </div>
      </div>
    </div>
  );
};

export default DebugPanel;
