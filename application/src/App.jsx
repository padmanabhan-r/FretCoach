import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import StatusPanel from './components/StatusPanel';
import VisualFeedback from './components/VisualFeedback';
import MetricsDisplay from './components/MetricsDisplay';
import ConsoleOutput from './components/ConsoleOutput';
import AudioSetup from './components/AudioSetup';
import ScaleSelection from './components/ScaleSelection';
import DebugPanel from './components/DebugPanel';
import ModeToggle from './components/ModeToggle';
import AIRecommendation from './components/AIRecommendation';
import LiveCoachFeedback from './components/LiveCoachFeedback';
import { api } from './api';

function App() {
  const [setupStep, setSetupStep] = useState('launch'); // launch, checking, audio, scale, mode, ai-recommendation, ready
  const [practiceMode, setPracticeMode] = useState('manual'); // 'manual' or 'ai'
  const [aiRecommendation, setAiRecommendation] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState(null);
  const [lastAiRecommendation, setLastAiRecommendation] = useState(null); // Track last recommendation to avoid repeats
  const [currentPracticeId, setCurrentPracticeId] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  const [audioConfig, setAudioConfig] = useState(null);
  const [enabledMetrics, setEnabledMetrics] = useState({
    pitch_accuracy: true,
    scale_conformity: true,
    timing_stability: true
  });
  const [state, setState] = useState({
    isRunning: false,
    pitchAccuracy: 0,
    scaleConformity: 0,
    timingStability: 0,
    currentNote: '-',
    targetScale: 'Not Set',
    logs: [],
    debugInfo: null,
    totalNotesPlayed: 0,
    correctNotes: 0,
    wrongNotes: 0,
  });
  const [showDebug, setShowDebug] = useState(false);
  const [showConsole, setShowConsole] = useState(false);
  const [ws, setWs] = useState(null);
  const [sessionSummary, setSessionSummary] = useState(null); // Session end summary
  const [sessionStartTime, setSessionStartTime] = useState(null);
  const [sessionElapsedTime, setSessionElapsedTime] = useState(0); // Track elapsed time in seconds
  const [isPaused, setIsPaused] = useState(false); // Pause state
  const [pausedTime, setPausedTime] = useState(0); // Track total paused time
  const pauseStartRef = useRef(null); // When pause started

  // Launch animation effect
  useEffect(() => {
    if (setupStep === 'launch') {
      const timer = setTimeout(() => {
        setSetupStep('checking');
        // Only check config after the launch animation completes
        checkConfig();
      }, 4500); // 4.5 second animation
      return () => clearTimeout(timer);
    }
  }, [setupStep]);

  // Session timer effect
  useEffect(() => {
    let timer = null;
    if (state.isRunning && sessionStartTime && !isPaused) {
      timer = setInterval(() => {
        setSessionElapsedTime(Math.floor((Date.now() - sessionStartTime - pausedTime) / 1000));
      }, 1000);
    } else if (!state.isRunning) {
      setSessionElapsedTime(0);
      setPausedTime(0);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [state.isRunning, sessionStartTime, isPaused, pausedTime]);

  // Format elapsed time as MM:SS
  const formatElapsedTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  useEffect(() => {

    // Set up Python backend output listeners
    if (window.electronAPI) {
      window.electronAPI.onPythonOutput((data) => {
        setState(prev => ({
          ...prev,
          logs: [...prev.logs, data].slice(-100),
        }));
      });

      window.electronAPI.onPythonError((data) => {
        // Don't prefix with ERROR - uvicorn sends INFO logs to stderr
        // The data already contains the log level (INFO, WARNING, ERROR, etc.)
        setState(prev => ({
          ...prev,
          logs: [...prev.logs, data].slice(-100),
        }));
      });
    }
  }, []);

  const checkConfig = async () => {
    try {
      const config = await api.getConfig();

      // Load session config for enabled metrics
      const sessionConfig = await api.getSessionConfig();
      if (sessionConfig && sessionConfig.enabled_metrics) {
        setEnabledMetrics(sessionConfig.enabled_metrics);
      }

      if (config && config.scale_name) {
        setState(prev => ({ ...prev, targetScale: config.scale_name }));
        setAudioConfig(config); // Store config for settings panel
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

  const fetchAIRecommendation = async (forceNew = false) => {
    setAiLoading(true);
    setAiError(null);

    // Clear current recommendation when forcing new one
    if (forceNew) {
      setAiRecommendation(null);
    }

    try {
      // Pass request_new flag to backend to generate fresh recommendations
      const result = await api.startAISession('default_user', forceNew);

      if (result.success) {
        setAiRecommendation(result);
        setCurrentPracticeId(result.practice_id);
        setLastAiRecommendation(result);
      } else {
        setAiError('AI practice suggestions are temporarily unavailable. You can still continue in Manual Mode.');
      }
    } catch (error) {
      console.error('Error getting AI recommendation:', error);
      setAiError('AI practice suggestions are temporarily unavailable. You can still continue in Manual Mode.');
    } finally {
      setAiLoading(false);
    }
  };

  const handleTryAnotherAI = async () => {
    await fetchAIRecommendation(true);
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
    setAiError(null);
    setSetupStep('mode');
  };

  // Navigate back to home (mode selection)
  const handleGoHome = () => {
    if (state.isRunning) {
      handleStop();
    }
    setAiRecommendation(null);
    setCurrentPracticeId(null);
    setAiError(null);
    setSetupStep('mode');
  };

  const handleScaleSelectionComplete = (scaleName) => {
    setState(prev => ({ ...prev, targetScale: scaleName }));
    setSetupStep('ready');
  };

  const handleStart = async () => {
    // Backend is already started by Electron main process
    // Just verify it's still running
    const isHealthy = await api.healthCheck();
    if (!isHealthy) {
      // Try to restart backend if it's not responding
      if (window.electronAPI) {
        const result = await window.electronAPI.startBackend();
        if (!result.success) {
          alert(`Failed to start backend: ${result.error}`);
          return;
        }
      } else {
        alert('Backend is not responding. Please restart the application.');
        return;
      }
    }

    try {
      const result = await api.startSession();
      if (result.success) {
        setState(prev => ({ ...prev, isRunning: true }));
        setSessionId(result.session_id);
        setSessionStartTime(Date.now());

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
          const debugInfo = data.debug_info || {};
          setState(prev => ({
            ...prev,
            currentNote: data.current_note || '-',
            pitchAccuracy: Math.round(data.pitch_accuracy * 100),
            scaleConformity: Math.round(data.scale_conformity * 100),
            timingStability: Math.round(data.timing_stability * 100),
            debugInfo: debugInfo,
            totalNotesPlayed: debugInfo.notes_played_count || 0,
            correctNotes: debugInfo.correct_notes || 0,
            wrongNotes: debugInfo.wrong_notes || 0,
          }));
        });
        setWs(websocket);
      } else {
        // Check for audio-related errors
        const errorMsg = result.error?.toLowerCase() || '';
        if (errorMsg.includes('channel') || errorMsg.includes('device') || errorMsg.includes('audio') || errorMsg.includes('stream')) {
          alert('Audio device configuration changed. Please reconfigure audio settings.');
          setSetupStep('audio');
        } else {
          alert(`Failed to start session: ${result.error}`);
        }
      }
    } catch (error) {
      const errorMsg = error.message?.toLowerCase() || '';
      if (errorMsg.includes('channel') || errorMsg.includes('device') || errorMsg.includes('audio') || errorMsg.includes('stream')) {
        alert('Audio device configuration changed. Please reconfigure audio settings.');
        setSetupStep('audio');
      } else {
        alert(`Error starting session: ${error.message}`);
      }
    }
  };

  const handlePause = () => {
    if (isPaused) {
      // Resume - add the paused duration to total paused time
      if (pauseStartRef.current) {
        setPausedTime(prev => prev + (Date.now() - pauseStartRef.current));
        pauseStartRef.current = null;
      }
      setIsPaused(false);
    } else {
      // Pause - record when we started pausing
      pauseStartRef.current = Date.now();
      setIsPaused(true);
    }
  };

  const handleStop = async () => {
    if (ws) {
      ws.close();
      setWs(null);
    }

    // Reset pause state
    setIsPaused(false);
    setPausedTime(0);
    pauseStartRef.current = null;

    // Calculate session duration
    const duration = sessionStartTime ? Math.round((Date.now() - sessionStartTime) / 1000) : 0;
    const minutes = Math.floor(duration / 60);
    const seconds = duration % 60;

    // Create session summary before resetting state
    // Generate fresh feedback from final stats (not accumulated history)
    const summary = {
      duration: `${minutes}m ${seconds}s`,
      durationSeconds: duration,
      scale: state.targetScale,
      mode: practiceMode,
      finalMetrics: {
        pitchAccuracy: state.pitchAccuracy,
        scaleConformity: state.scaleConformity,
        timingStability: state.timingStability,
        overall: Math.round((state.pitchAccuracy + state.scaleConformity + state.timingStability) / 3)
      },
      aiRecommendation: practiceMode === 'ai' ? aiRecommendation : null
    };
    setSessionSummary(summary);

    try {
      await api.stopSession();
    } catch (error) {
      console.error('Error stopping session:', error);
    }

    // Note: We don't stop the backend here anymore.
    // Backend stays running while the app is open for faster session restarts.
    // It's stopped automatically when the Electron app closes.

    setState(prev => ({
      ...prev,
      isRunning: false,
      currentNote: '-',
      pitchAccuracy: 0,
      scaleConformity: 0,
      timingStability: 0,
    }));

    setSessionId(null);
    setSessionStartTime(null);
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

  // Handle changing practice without full reconfiguration
  const handleChangePractice = () => {
    if (state.isRunning) {
      handleStop();
    }
    setAiRecommendation(null);
    setCurrentPracticeId(null);
    // Go back to mode selection instead of full reconfigure
    setSetupStep('mode');
  };

  // Handle quitting the application
  const handleQuit = async () => {
    if (state.isRunning) {
      await handleStop();
    }
    if (window.electronAPI) {
      await window.electronAPI.quitApp();
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Launch Animation */}
      {setupStep === 'launch' && (
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center animate-fade-in">
            <div className="relative">
              <div className="absolute inset-0 blur-3xl opacity-50 animate-pulse" style={{ background: 'radial-gradient(circle, hsl(14, 98%, 55%) 0%, transparent 70%)' }} />
              <h1 className="relative text-6xl font-bold bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent animate-scale-in">
                FretCoach
              </h1>
            </div>
            <p className="mt-4 text-muted-foreground text-lg animate-fade-in-delayed">
              Your AI-powered guitar practice companion
            </p>
            <div className="mt-8 flex justify-center">
              <div className="w-12 h-1 bg-gradient-to-r from-primary to-accent rounded-full animate-loading-bar" />
            </div>
          </div>
        </div>
      )}

      {setupStep !== 'launch' && (
        <div className="container mx-auto px-6 py-4">
          {/* Show full header only for non-playing screens */}
          {setupStep !== 'ready' && <Header onQuit={handleQuit} />}

          {setupStep === 'checking' && (
            <div className="mt-12 text-center">
              <div className="text-muted-foreground">Loading...</div>
            </div>
          )}

          {setupStep === 'audio' && (
            <div className="mt-12 max-w-2xl mx-auto">
              <AudioSetup onComplete={handleAudioSetupComplete} />
            </div>
          )}

          {setupStep === 'mode' && (
            <div className="min-h-[calc(100vh-120px)] flex flex-col items-center justify-center">
              <div className="w-full max-w-2xl mx-auto px-4">
                {/* Welcome Message */}
                <div className="text-center mb-8">
                  <h2 className="text-3xl font-bold text-foreground mb-2">Welcome to FretCoach</h2>
                  <p className="text-muted-foreground">Choose how you want to practice today.</p>
                </div>

                {/* Mode Toggle with improved layout */}
                <ModeToggle
                  mode={practiceMode}
                  onModeChange={handleModeChange}
                  disabled={state.isRunning}
                />

                {/* Settings Button */}
                <div className="mt-6 flex justify-center">
                  <button
                    onClick={() => setShowSettings(!showSettings)}
                    className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors text-sm"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    Audio Settings
                  </button>
                </div>

                {/* Settings Panel */}
                {showSettings && audioConfig && (
                  <div className="mt-4 bg-card/50 backdrop-blur-sm border border-border rounded-xl p-4">
                    <h3 className="text-sm font-semibold text-foreground mb-3">Current Audio Configuration</h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Input Device:</span>
                        <span className="text-foreground">{audioConfig.input_device_name || `Device ${audioConfig.input_device}`}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Channels:</span>
                        <span className="text-foreground">{audioConfig.channels}</span>
                      </div>
                    </div>
                    <button
                      onClick={() => { setShowSettings(false); setSetupStep('audio'); }}
                      className="mt-4 w-full bg-card hover:bg-card/80 text-foreground text-sm py-2 px-4 rounded-lg transition-all border border-border"
                    >
                      Reconfigure Audio
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}

          {setupStep === 'ai-recommendation' && (
            <div className="mt-12 max-w-3xl mx-auto">
              <AIRecommendation
                recommendation={aiRecommendation}
                onAccept={handleAcceptAIRecommendation}
                onReject={handleRejectAIRecommendation}
                onTryAnother={handleTryAnotherAI}
                loading={aiLoading}
                error={aiError}
                enabledMetrics={enabledMetrics}
                onMetricsChange={setEnabledMetrics}
              />
            </div>
          )}

          {setupStep === 'scale' && (
            <div className="mt-12 max-w-4xl mx-auto">
              <ScaleSelection
                onComplete={handleScaleSelectionComplete}
                onBack={() => setSetupStep('mode')}
                enabledMetrics={enabledMetrics}
                onMetricsChange={setEnabledMetrics}
              />
            </div>
          )}

          {setupStep === 'ready' && (
            <div className="flex flex-col h-[calc(100vh-2rem)]">
              {/* Compact Header Bar for Playing Screen */}
              <div className="flex items-center justify-between mb-4 pb-3 border-b border-border flex-shrink-0">
                {/* Left: Logo and Version */}
                <div className="flex items-center gap-3">
                  <span className="text-lg font-bold text-foreground">FretCoach</span>
                  <span className="text-xs text-muted-foreground font-mono">v0.1.0</span>
                  <span className="text-xs px-1.5 py-0.5 bg-secondary/20 text-secondary rounded">Early Beta</span>
                </div>

                {/* Right: Navigation Buttons */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleGoHome}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg bg-card hover:bg-card/80 border border-border text-foreground transition-colors text-sm font-medium"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                    </svg>
                    Home
                  </button>
                  <button
                    onClick={handleReconfigure}
                    disabled={state.isRunning}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg bg-card hover:bg-card/80 border border-border text-foreground transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    Audio Setup
                  </button>
                  <button
                    onClick={handleQuit}
                    disabled={state.isRunning}
                    className="flex items-center gap-1 px-2 py-2 rounded-lg bg-destructive/10 hover:bg-destructive/20 border border-destructive/30 text-destructive transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                    title="Quit Application"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>

              {practiceMode === 'ai' && aiRecommendation && (
                <div className="mb-8 max-w-5xl mx-auto flex-shrink-0">
                  <div className="bg-accent/20 border border-accent/50 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <span className="text-2xl">🤖</span>
                        <div>
                          <h3 className="text-accent font-semibold">AI Coach Mode Active</h3>
                          <p className="text-muted-foreground text-sm">
                            Focus: {aiRecommendation.focus_area} | {aiRecommendation.reasoning}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {practiceMode === 'manual' && (
                <div className="mb-8 max-w-5xl mx-auto flex-shrink-0">
                  <div className="bg-primary/20 border border-primary/50 rounded-lg p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <span className="text-2xl">🎯</span>
                        <div>
                          <h3 className="text-primary font-semibold">Manual Practice Mode</h3>
                          <p className="text-muted-foreground text-sm">
                            Practice at your own pace | Live AI Coach available for real-time feedback
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Main Content Grid - Reorganized */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 flex-1 min-h-0">
                {/* Left Column - Controls and Status */}
                <div className="lg:col-span-4 space-y-4">
                  {/* Session Controls Card */}
                  <div className="bg-card/50 backdrop-blur-sm border border-border rounded-xl p-6">
                    <div className="text-center mb-4">
                      <div className="text-muted-foreground text-sm mb-1">Current Scale</div>
                      <div className="text-xl font-bold text-primary">{state.targetScale}</div>
                    </div>

                    {!state.isRunning ? (
                      <button
                        onClick={handleStart}
                        className="w-full bg-gradient-to-r from-primary to-secondary hover:from-secondary hover:to-accent text-white font-bold py-4 px-6 rounded-xl transition-all duration-300 shadow-lg text-lg flex items-center justify-center gap-3"
                        style={{ boxShadow: '0 0 30px hsl(14, 98%, 55%, 0.4)' }}
                      >
                        <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                        </svg>
                        Start Session
                      </button>
                    ) : (
                      <div className="space-y-2">
                        {/* Session Timer Bar */}
                        <div className="flex items-center justify-between bg-card/50 rounded-lg px-4 py-2 border border-border">
                          <div className="flex items-center gap-2">
                            <span className={`w-2 h-2 rounded-full ${isPaused ? 'bg-yellow-500' : 'bg-red-500 animate-pulse'}`}></span>
                            <span className="text-sm text-muted-foreground">{isPaused ? 'Paused' : 'Session Time'}</span>
                          </div>
                          <span className="text-lg font-mono font-bold text-foreground">{formatElapsedTime(sessionElapsedTime)}</span>
                        </div>
                        {/* Pause and Stop Buttons */}
                        <div className="flex gap-2">
                          <button
                            onClick={handlePause}
                            className={`flex-1 font-bold py-4 px-4 rounded-xl transition-all duration-300 shadow-lg text-lg flex items-center justify-center gap-2 ${
                              isPaused
                                ? 'bg-gradient-to-r from-green-600 to-green-500 hover:from-green-500 hover:to-green-400 text-white'
                                : 'bg-gradient-to-r from-yellow-600 to-yellow-500 hover:from-yellow-500 hover:to-yellow-400 text-white'
                            }`}
                            style={{ boxShadow: isPaused ? '0 0 30px hsl(142, 76%, 45%, 0.4)' : '0 0 30px hsl(45, 90%, 50%, 0.4)' }}
                          >
                            {isPaused ? (
                              <>
                                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                                </svg>
                                Resume
                              </>
                            ) : (
                              <>
                                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                                </svg>
                                Pause
                              </>
                            )}
                          </button>
                          <button
                            onClick={handleStop}
                            className="flex-1 bg-gradient-to-r from-destructive to-red-600 hover:from-red-600 hover:to-red-500 text-white font-bold py-4 px-4 rounded-xl transition-all duration-300 shadow-lg text-lg flex items-center justify-center gap-2"
                            style={{ boxShadow: '0 0 30px hsl(0, 84%, 60%, 0.4)' }}
                          >
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8 7a1 1 0 00-1 1v4a1 1 0 001 1h4a1 1 0 001-1V8a1 1 0 00-1-1H8z" clipRule="evenodd" />
                            </svg>
                            Stop
                          </button>
                        </div>
                      </div>
                    )}

                    {!state.isRunning && (
                      <button
                        onClick={handleChangePractice}
                        className="w-full mt-3 py-2 px-4 text-sm font-medium text-secondary border border-secondary/50 rounded-lg hover:bg-secondary/10 hover:border-secondary transition-all flex items-center justify-center gap-2"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        Change Practice
                      </button>
                    )}
                  </div>

                  <StatusPanel
                    isRunning={state.isRunning}
                    currentNote={state.currentNote}
                    targetScale={state.targetScale}
                  />
                </div>

                {/* Right Column - Visual Feedback and Metrics */}
                <div className="lg:col-span-8 space-y-4">
                  {/* Visual Feedback with Live Coach beside it */}
                  <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
                    <VisualFeedback
                      pitchAccuracy={state.pitchAccuracy}
                      scaleConformity={state.scaleConformity}
                      timingStability={state.timingStability}
                      isRunning={state.isRunning}
                      isPaused={isPaused}
                      enabledMetrics={enabledMetrics}
                    />

                    <LiveCoachFeedback
                      isRunning={state.isRunning}
                      isPaused={isPaused}
                      pitchAccuracy={state.pitchAccuracy}
                      scaleConformity={state.scaleConformity}
                      timingStability={state.timingStability}
                      scaleName={state.targetScale}
                      sessionId={sessionId}
                      totalNotesPlayed={state.totalNotesPlayed}
                      correctNotes={state.correctNotes}
                      wrongNotes={state.wrongNotes}
                    />
                  </div>

                  <MetricsDisplay
                    pitchAccuracy={state.pitchAccuracy}
                    scaleConformity={state.scaleConformity}
                    timingStability={state.timingStability}
                    isRunning={state.isRunning}
                    debugInfo={state.debugInfo}
                    totalNotesPlayed={state.totalNotesPlayed}
                    correctNotes={state.correctNotes}
                    wrongNotes={state.wrongNotes}
                    enabledMetrics={enabledMetrics}
                  />
                </div>
              </div>

              {/* Debug Panel - Below all cards */}
              {showDebug && state.isRunning && <DebugPanel debugInfo={state.debugInfo} show={true} />}
            </div>
          )}
        </div>
      )}

      {/* Session Summary Modal */}
      {sessionSummary && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-card border border-border rounded-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-foreground">Session Complete</h2>
                <button
                  onClick={() => setSessionSummary(null)}
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Session Stats */}
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-background rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-primary">{sessionSummary.duration}</div>
                    <div className="text-sm text-muted-foreground">Duration</div>
                  </div>
                  <div className="bg-background rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-foreground">{sessionSummary.scale}</div>
                    <div className="text-sm text-muted-foreground">Scale</div>
                  </div>
                </div>

                {/* Final Metrics */}
                <div className="bg-background rounded-lg p-4">
                  <h3 className="text-sm font-semibold text-foreground mb-3">Final Performance</h3>
                  <div className="grid grid-cols-3 gap-3 text-center">
                    <div>
                      <div className="text-xl font-bold text-primary">{sessionSummary.finalMetrics.pitchAccuracy}%</div>
                      <div className="text-xs text-muted-foreground">Pitch</div>
                    </div>
                    <div>
                      <div className="text-xl font-bold text-secondary">{sessionSummary.finalMetrics.scaleConformity}%</div>
                      <div className="text-xs text-muted-foreground">Scale</div>
                    </div>
                    <div>
                      <div className="text-xl font-bold text-accent">{sessionSummary.finalMetrics.timingStability}%</div>
                      <div className="text-xs text-muted-foreground">Timing</div>
                    </div>
                  </div>
                  <div className="mt-3 pt-3 border-t border-border text-center">
                    <div className={`text-2xl font-bold ${
                      sessionSummary.finalMetrics.overall >= 70 ? 'text-green-500' :
                      sessionSummary.finalMetrics.overall >= 50 ? 'text-yellow-500' :
                      sessionSummary.finalMetrics.overall >= 30 ? 'text-orange-500' :
                      'text-red-500'
                    }`}>
                      {sessionSummary.finalMetrics.overall >= 70 ? 'Excellent' :
                       sessionSummary.finalMetrics.overall >= 50 ? 'Good' :
                       sessionSummary.finalMetrics.overall >= 30 ? 'Average' : 'Needs Work'}
                    </div>
                    <div className="text-sm text-muted-foreground">Overall: {sessionSummary.finalMetrics.overall}%</div>
                  </div>
                </div>

                {/* AI Mode: Show AI Recommendation and Feedback */}
                {sessionSummary.mode === 'ai' && sessionSummary.aiRecommendation && (
                  <div className="bg-accent/10 border border-accent/30 rounded-lg p-4">
                    <h3 className="text-sm font-semibold text-accent mb-2 flex items-center gap-2">
                      <span>🤖</span> AI Coach Focus
                    </h3>
                    <p className="text-sm text-foreground">{sessionSummary.aiRecommendation.focus_area}</p>
                    <p className="text-xs text-muted-foreground mt-1">{sessionSummary.aiRecommendation.reasoning}</p>
                  </div>
                )}

                {/* Mode Badge */}
                <div className="text-center">
                  <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm ${
                    sessionSummary.mode === 'ai' ? 'bg-accent/20 text-accent' : 'bg-primary/20 text-primary'
                  }`}>
                    {sessionSummary.mode === 'ai' ? '🤖 AI Coach' : '🎯 Manual'} Mode
                  </span>
                </div>
              </div>

              {/* Close Button */}
              <button
                onClick={() => setSessionSummary(null)}
                className="w-full mt-6 bg-primary hover:bg-primary/90 text-primary-foreground font-semibold py-3 px-6 rounded-lg transition-all"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Bottom-right buttons - Debug and Console */}
      {setupStep !== 'launch' && (
        <div className="fixed bottom-4 right-4 z-40 flex items-center gap-2">
          {/* Debug Button - Only show when session is running */}
          {setupStep === 'ready' && state.isRunning && (
            <button
              onClick={() => setShowDebug(!showDebug)}
              className={`bg-card/80 backdrop-blur-sm border hover:bg-card hover:border-primary/50 text-muted-foreground hover:text-foreground p-2 rounded-lg shadow-lg transition-all ${showDebug ? 'border-primary/50 text-foreground' : 'border-border'}`}
              title="Toggle Debug Info"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
              </svg>
            </button>
          )}

          {/* Console Button */}
          <button
            onClick={() => setShowConsole(!showConsole)}
            className="relative bg-card/80 backdrop-blur-sm border border-border hover:bg-card hover:border-primary/50 text-muted-foreground hover:text-foreground p-2 rounded-lg shadow-lg transition-all"
            title="Toggle Console"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            {state.logs.length > 0 && (
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-primary text-primary-foreground text-[10px] font-medium rounded-full flex items-center justify-center">
                {state.logs.length > 99 ? '99' : state.logs.length}
              </span>
            )}
          </button>
        </div>
      )}

      {/* Console Overlay Panel */}
      {showConsole && (
        <div className="fixed bottom-16 right-4 z-40 w-[500px] max-w-[calc(100vw-2rem)] max-h-[400px] bg-card border border-border rounded-xl shadow-xl overflow-hidden">
          <div className="flex items-center justify-between px-4 py-2 border-b border-border bg-card/50">
            <span className="text-sm font-medium text-foreground flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              Console
            </span>
            <button
              onClick={() => setShowConsole(false)}
              className="text-muted-foreground hover:text-foreground transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div className="max-h-[350px] overflow-y-auto">
            <ConsoleOutput logs={state.logs} onClear={() => setState(prev => ({ ...prev, logs: [] }))} />
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
