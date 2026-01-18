import React, { useRef, useEffect } from 'react';

const ConsoleOutput = ({ logs, onClear }) => {
  const consoleRef = useRef(null);

  useEffect(() => {
    if (consoleRef.current) {
      consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="bg-card/50 backdrop-blur-sm border border-border rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-foreground">Console Output</h2>
        <button
          className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          onClick={onClear}
        >
          Clear
        </button>
      </div>

      <div
        ref={consoleRef}
        className="bg-background rounded-lg p-4 h-48 overflow-y-auto font-mono text-xs text-foreground/80 space-y-1"
      >
        {logs.length === 0 ? (
          <div className="text-muted italic">No output yet...</div>
        ) : (
          logs.map((log, index) => {
            // Detect actual errors (ERROR: prefix or error keywords)
            const isError = log.includes('ERROR:') || log.includes('Error:') ||
                           log.includes('Traceback') || log.includes('Exception');
            const isWarning = log.includes('WARNING:') || log.includes('Warning:');
            return (
              <div
                key={index}
                className={
                  isError ? 'text-destructive' :
                  isWarning ? 'text-yellow-500' :
                  'text-muted-foreground'
                }
              >
                {log}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default ConsoleOutput;
