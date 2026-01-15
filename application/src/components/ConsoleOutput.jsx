import React, { useRef, useEffect } from 'react';

const ConsoleOutput = ({ logs }) => {
  const consoleRef = useRef(null);

  useEffect(() => {
    if (consoleRef.current) {
      consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="bg-slate-900/50 backdrop-blur-sm border border-slate-800 rounded-xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold text-slate-200">Console Output</h2>
        <button
          className="text-sm text-slate-400 hover:text-slate-300 transition-colors"
          onClick={() => {}}
        >
          Clear
        </button>
      </div>
      
      <div
        ref={consoleRef}
        className="bg-slate-950 rounded-lg p-4 h-48 overflow-y-auto font-mono text-xs text-slate-300 space-y-1"
      >
        {logs.length === 0 ? (
          <div className="text-slate-500 italic">No output yet...</div>
        ) : (
          logs.map((log, index) => (
            <div
              key={index}
              className={`${log.startsWith('ERROR') ? 'text-red-400' : 'text-slate-400'}`}
            >
              {log}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ConsoleOutput;
