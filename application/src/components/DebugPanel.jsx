import React from 'react';

const DebugPanel = ({ debugInfo, show }) => {
  if (!show || !debugInfo) return null;

  const noteNames = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
  const noteName = noteNames[debugInfo.pitch_class] || '-';

  return (
    <div className="bg-card/50 backdrop-blur-sm border border-border rounded-lg px-4 py-2 mt-4">
      <div className="flex items-center gap-6 text-xs font-mono flex-wrap">
        <span className="text-muted-foreground">Debug:</span>
        <span>
          <span className="text-muted-foreground">Freq: </span>
          <span className="text-primary">{debugInfo.detected_hz > 0 ? `${debugInfo.detected_hz.toFixed(1)}Hz` : '-'}</span>
        </span>
        <span>
          <span className="text-muted-foreground">MIDI: </span>
          <span className="text-secondary">{debugInfo.detected_midi > 0 ? debugInfo.detected_midi.toFixed(1) : '-'}</span>
        </span>
        <span>
          <span className="text-muted-foreground">Pitch: </span>
          <span className="text-accent">{debugInfo.pitch_class !== undefined ? `${debugInfo.pitch_class} (${noteName})` : '-'}</span>
        </span>
        <span>
          <span className="text-muted-foreground">In Scale: </span>
          <span className={debugInfo.in_scale ? 'text-accent' : 'text-destructive'}>{debugInfo.in_scale ? 'YES' : 'NO'}</span>
        </span>
        <span>
          <span className="text-muted-foreground">Pitch Score: </span>
          <span className="text-primary">{(debugInfo.raw_pitch * 100).toFixed(0)}%</span>
        </span>
        <span>
          <span className="text-muted-foreground">Timing: </span>
          <span className="text-secondary">{(debugInfo.raw_timing * 100).toFixed(0)}%</span>
        </span>
      </div>
    </div>
  );
};

export default DebugPanel;
