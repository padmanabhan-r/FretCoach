import React from 'react';

const StatusPanel = ({ isRunning, currentNote, targetScale }) => {
  return (
    <div className="bg-card/50 backdrop-blur-sm border border-border rounded-xl p-6">
      <h2 className="text-xl font-semibold mb-4 text-foreground">Status</h2>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-muted-foreground">Engine</span>
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isRunning ? 'bg-accent animate-pulse' : 'bg-muted'}`} />
            <span className={`font-medium ${isRunning ? 'text-accent' : 'text-muted'}`}>
              {isRunning ? 'Running' : 'Stopped'}
            </span>
          </div>
        </div>

        <div className="h-px bg-border" />

        <div>
          <div className="text-muted-foreground text-sm mb-2">Current Note</div>
          <div className="text-3xl font-bold text-center py-4 bg-card rounded-lg text-glow text-primary">
            {currentNote}
          </div>
        </div>

        <div>
          <div className="text-muted-foreground text-sm mb-2">Target Scale</div>
          <div className="text-lg font-medium text-center py-2 bg-card rounded-lg text-secondary">
            {targetScale}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StatusPanel;
