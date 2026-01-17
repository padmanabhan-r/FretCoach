import React from 'react';

const Header = ({ minimal = false }) => {
  if (minimal) {
    return (
      <header className="pb-2">
        <div className="flex items-center gap-3">
          <span className="text-lg font-bold text-foreground">FretCoach</span>
          <span className="text-xs text-muted-foreground font-mono">v0.1.0</span>
          <span className="text-xs px-1.5 py-0.5 bg-secondary/20 text-secondary rounded">Early Beta</span>
        </div>
      </header>
    );
  }

  return (
    <header className="border-b border-border pb-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold gradient-text mb-2">
            FretCoach
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
        </div>
      </div>
    </header>
  );
};

export default Header;
