import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import StatusPanel from './components/StatusPanel';
import VisualFeedback from './components/VisualFeedback';
import MetricsDisplay from './components/MetricsDisplay';
import ControlPanel from './components/ControlPanel';
import ConsoleOutput from './components/ConsoleOutput';
import AudioSetup from './components/AudioSetup';
import ScaleSelection from './components/ScaleSelection';
import DebugPanel from './components/DebugPanel';
import { api } from './api';

function App() {
  const [setupStep, setSetupStep] = useState('checking'); // checking, audio, scale, ready
  const [state, setState] = useState({
    isRunning: false,
    pitchAccuracy: 0,
    scaleConformity: 0,
    timingStability: 0,
    currentNote: '-',
    targetScale: 'Not Set',
    logs: [],
    debugInfo: null,
  });
  const [showDebug, setShowDebug] = useState(false);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    // Check if configuration exists
    checkConfig();

    // Set up Python backend output listeners
    if (window.electronAPI) {
      window.electronAPI.onPythonOutput((data) => {
        setState(prev => ({
          ...prev,
          logs: [...prev.logs, data].slice(-100),
        }));
      });

      window.electronAPI.onPythonError((data) => {
        setState(prev => ({
          ...prev,
          logs: [...prev.logs, `ERROR: ${data}`].slice(-100),
        }));
      });
    }
  }, []);

  const checkConfig = async () => {
    try {
      const config = await api.getConfig();
      if (config && config.scale_name) {
        setState(prev => ({ ...prev, targetScale: config.scale_name }));
        setSetupStep('ready');
      } else {
        setSetupStep('audio');
      }
    } catch (error) {
      console.error('Failed to check config:', error);
      setSetupStep('audio');
    }
  };

  const handleAudioSetupComplete = () => {
    setSetupStep('scale');
  };

  const handleScaleSelectionComplete = (scaleName) => {
    setState(prev => ({ ...prev, targetScale: scaleName }));
    setSetupStep('ready');
  };

  const handleStart = async () => {
    if (window.electronAPI) {
      const result = await window.electronAPI.startBackend();
      if (!result.success) {
        alert(`Failed to start backend: ${result.error}`);
        return;
      }
    }

    // Wait a bit for backend to start
    await new Promise(resolve => setTimeout(resolve, 2000));

    try {
      const result = await api.startSession();
      if (result.success) {
        setState(prev => ({ ...prev, isRunning: true }));
        
        // Connect WebSocket for real-time metrics
        const websocket = api.connectWebSocket((data) => {
          setState(prev => ({
            ...prev,
            currentNote: data.current_note || '-',
            pitchAccuracy: Math.round(data.pitch_accuracy * 100),
            scaleConformity: Math.round(data.scale_conformity * 100),
            timingStability: Math.round(data.timing_stability * 100),
            debugInfo: data.debug_info || null,
          }));
        });
        setWs(websocket);
      } else {
        alert(`Failed to start session: ${result.error}`);
      }
    } catch (error) {
      alert(`Error starting session: ${error.message}`);
    }
  };

  const handleStop = async () => {
    if (ws) {
      ws.close();
      setWs(null);
    }

    try {
      await api.stopSession();
    } catch (error) {
      console.error('Error stopping session:', error);
    }

    if (window.electronAPI) {
      await window.electronAPI.stopBackend();
    }

    setState(prev => ({ 
      ...prev, 
      isRunning: false,
      currentNote: '-',
      pitchAccuracy: 0,
      scaleConformity: 0,
      timingStability: 0,
    }));
  };

  const handleReconfigure = () => {
    if (state.isRunning) {
      handleStop();
    }
    setSetupStep('audio');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <div className="container mx-auto px-6 py-4">
        <Header />
        
        {setupStep === 'checking' && (
          <div className="mt-12 text-center">
            <div className="text-slate-400">Loading...</div>
          </div>
        )}

        {setupStep === 'audio' && (
          <div className="mt-12 max-w-2xl mx-auto">
            <AudioSetup onComplete={handleAudioSetupComplete} />
          </div>
        )}

        {setupStep === 'scale' && (
          <div className="mt-12 max-w-4xl mx-auto">
            <ScaleSelection onComplete={handleScaleSelectionComplete} />
          </div>
        )}

        {setupStep === 'ready' && (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
              <div className="space-y-6">
                <StatusPanel 
                  isRunning={state.isRunning}
                  currentNote={state.currentNote}
                  targetScale={state.targetScale}
                />
                <ControlPanel
                  isRunning={state.isRunning}
                  onStart={handleStart}
                  onStop={handleStop}
                  onReconfigure={handleReconfigure}
                />
                
                {state.isRunning && (
                  <button
                    onClick={() => setShowDebug(!showDebug)}
                    className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 py-2 px-4 rounded-lg transition-all text-sm font-medium"
                  >
                    {showDebug ? '🐛 Hide Debug Info' : '🐛 Show Debug Info'}
                  </button>
                )}
              </div>

              <div className="lg:col-span-2 space-y-6">
                <VisualFeedback
                  pitchAccuracy={state.pitchAccuracy}
                  scaleConformity={state.scaleConformity}
                  timingStability={state.timingStability}
                />
                <MetricsDisplay
                  pitchAccuracy={state.pitchAccuracy}
                  scaleConformity={state.scaleConformity}
                  timingStability={state.timingStability}
                />
                
                <DebugPanel debugInfo={state.debugInfo} show={showDebug && state.isRunning} />
              </div>
            </div>

            <div className="mt-6">
              <ConsoleOutput logs={state.logs} />
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default App;
