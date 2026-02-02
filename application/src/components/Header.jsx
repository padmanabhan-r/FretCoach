import React from 'react';

const Header = ({ minimal = false, onQuit }) => {
  const QuitButton = () => (
    <button
      onClick={onQuit}
      className="flex items-center gap-1 px-2 py-1.5 rounded-lg bg-destructive/10 hover:bg-destructive/20 border border-destructive/30 text-destructive transition-colors text-sm font-medium"
      title="Quit Application"
    >
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  );

  if (minimal) {
    return (
      <header className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-lg font-bold text-foreground">FretCoach Studio</span>
            <span className="text-xs text-muted-foreground font-mono">v0.1.0</span>
            <span className="text-xs px-1.5 py-0.5 bg-secondary/20 text-secondary rounded">Early Beta</span>
          </div>
          {onQuit && <QuitButton />}
        </div>
      </header>
    );
  }

  return (
    <header className="border-b border-border pb-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold gradient-text mb-2">
            FretCoach Studio
          </h1>
          <p className="text-muted-foreground text-sm">
            Adaptive Guitar Learning Agent
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <div className="text-xs text-muted">Version</div>
            <div className="text-sm font-mono text-foreground/80">0.1.0</div>
          </div>
          <span className="text-xs px-2 py-1 bg-secondary/20 text-secondary rounded">Early Beta</span>
          {onQuit && <QuitButton />}
        </div>
      </div>
    </header>
  );
};

export default Header;
