import React from 'react';

function ModeToggle({ mode, onModeChange, disabled }) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Manual Mode Card */}
        <button
          onClick={() => onModeChange('manual')}
          disabled={disabled}
          className={`group relative overflow-hidden rounded-xl border-2 p-6 text-left transition-all duration-300 ${
            disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:scale-[1.02]'
          } ${
            mode === 'manual'
              ? 'border-primary bg-primary/10'
              : 'border-border bg-card/50 hover:border-primary/50 hover:bg-card'
          }`}
        >
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-3">
              <span className="text-3xl">🎯</span>
              <h3 className="text-xl font-bold text-foreground">Manual Mode</h3>
            </div>
            <p className="text-muted-foreground text-sm leading-relaxed">
              You fully control the practice settings. Perfect for focused practice on specific areas.
            </p>
          </div>
          {mode === 'manual' && (
            <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-transparent" />
          )}
          <div
            className={`absolute top-3 right-3 w-4 h-4 rounded-full border-2 transition-all ${
              mode === 'manual'
                ? 'border-primary bg-primary'
                : 'border-muted-foreground'
            }`}
          >
            {mode === 'manual' && (
              <svg className="w-full h-full text-primary-foreground" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            )}
          </div>
        </button>

        {/* AI Coach Mode Card */}
        <button
          onClick={() => onModeChange('ai')}
          disabled={disabled}
          className={`group relative overflow-hidden rounded-xl border-2 p-6 text-left transition-all duration-300 ${
            disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer hover:scale-[1.02]'
          } ${
            mode === 'ai'
              ? 'border-accent bg-accent/10'
              : 'border-border bg-card/50 hover:border-accent/50 hover:bg-card'
          }`}
        >
          <div className="relative z-10">
            <div className="flex items-center gap-3 mb-3">
              <span className="text-3xl">🤖</span>
              <h3 className="text-xl font-bold text-foreground">AI Coach</h3>
            </div>
            <p className="text-muted-foreground text-sm leading-relaxed">
              AI analyzes your performance history and automatically selects the optimal scale and practice routine.
            </p>
          </div>
          {mode === 'ai' && (
            <div className="absolute inset-0 bg-gradient-to-br from-accent/20 to-transparent" />
          )}
          <div
            className={`absolute top-3 right-3 w-4 h-4 rounded-full border-2 transition-all ${
              mode === 'ai'
                ? 'border-accent bg-accent'
                : 'border-muted-foreground'
            }`}
          >
            {mode === 'ai' && (
              <svg className="w-full h-full text-accent-foreground" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            )}
          </div>
        </button>
      </div>
    </div>
  );
}

export default ModeToggle;
