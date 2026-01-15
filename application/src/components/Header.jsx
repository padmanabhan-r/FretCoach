import React from 'react';

const Header = () => {
  return (
    <header className="border-b border-slate-800 pb-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold gradient-text mb-2">
            FretCoach
          </h1>
          <p className="text-slate-400 text-sm">
            Adaptive Guitar Learning Agent
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <div className="text-xs text-slate-500">Version</div>
            <div className="text-sm font-mono text-slate-300">0.1.0</div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
