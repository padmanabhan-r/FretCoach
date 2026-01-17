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
import ModeToggle from './components/ModeToggle';
import AIRecommendation from './components/AIRecommendation';
import { api } from './api';

function App() {
  const [setupStep, setSetupStep] = useState('checking'); // checking, audio, scale, mode, ai-recommendation, ready
  const [practiceMode, setPracticeMode] = useState('manual'); // 'manual' or 'ai'
  const [aiRecommendation, setAiRecommendation] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [currentPracticeId, setCurrentPracticeId] = useState(null);
  const [sessionId, setSessionId] = useState(null);
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
        setSetupStep('mode'); // Go to mode selection
      } else {
        setSetupStep('audio');
      }
    } catch (error) {
      console.error('Failed to check config:', error);
      setSetupStep('audio');
    }
  };

  const handleAudioSetupComplete = () => {
    setSetupStep('mode'); // Go to mode selection instead of scale
  };

  const handleModeChange = async (mode) => {
    setPracticeMode(mode);
    
    if (mode === 'manual') {
      setSetupStep('scale');
    } else if (mode === 'ai') {
      setSetupStep('ai-recommendation');
      await fetchAIRecommendation();
    }
  };

  const fetchAIRecommendation = async () => {
    setAiLoading(true);
    try {
      const result = await api.startAISession();
      if (result.success) {
        setAiRecommendation(result);
        setCurrentPracticeId(result.practice_id);
      } else {
        alert('Failed to get AI recommendation');
        setSetupStep('mode');
      }
    } catch (error) {
      console.error('Error getting AI recommendation:', error);
      alert(`Failed to get AI recommendation: ${error.message}`);
      setSetupStep('mode');
    } finally {
      setAiLoading(false);
    }
  };

  const handleAcceptAIRecommendation = async (ambientLighting = true) => {
    try {
      // Get current config to preserve device settings
      const currentConfig = await api.getConfig();

      // Merge AI recommendation with existing device config
      const config = {
        ...currentConfig,  // Preserve input_device, output_device, channels
        scale_name: aiRecommendation.config.scale_name,
        scale_type: aiRecommendation.config.scale_type,
        strictness: aiRecommendation.config.strictness,
        sensitivity: aiRecommendation.config.sensitivity,
        ambient_lighting: ambientLighting,
      };

      console.log('Applying AI recommendation config:', config);

      const result = await api.saveConfig(config);
      console.log('Config saved successfully:', result);
      setState(prev => ({
        ...prev,
        targetScale: `${config.scale_name} ${config.scale_type}`
      }));
      setSetupStep('ready');
    } catch (error) {
      console.error('Error applying AI config:', error);
      alert('Failed to apply AI recommendation');
    }
  };

  const handleRejectAIRecommendation = () => {
    setAiRecommendation(null);
    setCurrentPracticeId(null);
    setSetupStep('mode');
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
        setSessionId(result.session_id);

        // If this is an AI mode session, link it to the practice plan
        if (practiceMode === 'ai' && currentPracticeId && result.session_id) {
          try {
            await api.markPlanExecuted(currentPracticeId, result.session_id);
            console.log('Linked session to AI practice plan');
          } catch (error) {
            console.error('Failed to link session to practice plan:', error);
          }
        }
        
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
    
    setSessionId(null);
  };

  const handleReconfigure = () => {
    if (state.isRunning) {
      handleStop();
    }
    setAiRecommendation(null);
    setCurrentPracticeId(null);
    setPracticeMode('manual');
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

        {setupStep === 'mode' && (
          <div className="mt-12 max-w-2xl mx-auto">
            <ModeToggle 
              mode={practiceMode} 
              onModeChange={handleModeChange}
              disabled={state.isRunning}
            />
          </div>
        )}

        {setupStep === 'ai-recommendation' && (
          <div className="mt-12 max-w-3xl mx-auto">
            <AIRecommendation
              recommendation={aiRecommendation}
              onAccept={handleAcceptAIRecommendation}
              onReject={handleRejectAIRecommendation}
              loading={aiLoading}
            />
          </div>
        )}

        {setupStep === 'scale' && (
          <div className="mt-12 max-w-4xl mx-auto">
            <ScaleSelection onComplete={handleScaleSelectionComplete} />
          </div>
        )}

        {setupStep === 'ready' && (
          <>
            {practiceMode === 'ai' && aiRecommendation && (
              <div className="mt-6 max-w-5xl mx-auto">
                <div className="bg-purple-900/20 border border-purple-500/50 rounded-lg p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl">🤖</span>
                      <div>
                        <h3 className="text-purple-300 font-semibold">AI Coach Mode Active</h3>
                        <p className="text-slate-400 text-sm">
                          Focus: {aiRecommendation.focus_area} | {aiRecommendation.reasoning}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
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
