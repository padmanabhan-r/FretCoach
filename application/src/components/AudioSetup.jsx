import React, { useState, useEffect } from 'react';
import { api } from '../api';

const AudioSetup = ({ onComplete }) => {
  const [step, setStep] = useState('loading'); // loading, devices, test, done
  const [devices, setDevices] = useState([]);
  const [inputDevice, setInputDevice] = useState(null);
  const [outputDevice, setOutputDevice] = useState(null);
  const [guitarChannel, setGuitarChannel] = useState(0);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);

  useEffect(() => {
    loadDevices();
  }, []);

  const loadDevices = async () => {
    try {
      const deviceList = await api.getAudioDevices();
      setDevices(deviceList);
      setStep('devices');
    } catch (error) {
      console.error('Failed to load devices:', error);
    }
  };

  const handleTest = async () => {
    if (inputDevice === null || testing) return;

    // Clear previous results and start fresh test
    setTestResult(null);
    setTesting(true);

    try {
      const result = await api.testAudioDevice(inputDevice, guitarChannel);
      setTestResult(result);

      if (result.has_signal) {
        setTimeout(() => setStep('done'), 1500);
      }
    } catch (error) {
      console.error('Test failed:', error);
      setTestResult({ success: false, error: error.message });
    } finally {
      setTesting(false);
    }
  };

  const handleComplete = async () => {
    const config = {
      input_device: inputDevice,
      output_device: outputDevice || inputDevice,
      guitar_channel: guitarChannel,
      channels: 2,
      scale_name: 'A Minor', // Default, will be changed in next step
    };

    await api.saveConfig(config);
    onComplete(config);
  };

  const inputDevices = devices.filter(d => d.max_input_channels > 0);
  const outputDevices = devices.filter(d => d.max_output_channels > 0);

  return (
    <div className="bg-card/50 backdrop-blur-sm border border-border rounded-xl p-8">
      <h2 className="text-2xl font-bold mb-6 gradient-text">Audio Setup</h2>

      {step === 'loading' && (
        <div className="text-center py-12">
          <div className="text-muted-foreground">Loading audio devices...</div>
        </div>
      )}

      {step === 'devices' && (
        <div className="space-y-6">
          <div>
            <label className="block text-foreground mb-2">Input Device (Guitar)</label>
            <select
              value={inputDevice !== null ? inputDevice : ''}
              onChange={(e) => setInputDevice(e.target.value === '' ? null : parseInt(e.target.value))}
              className="w-full bg-card border border-border rounded-lg px-4 py-3 text-foreground focus:outline-none focus:border-primary"
            >
              <option value="">Select input device...</option>
              {inputDevices.map(device => (
                <option key={device.index} value={device.index}>
                  [{device.index}] {device.name} ({device.max_input_channels} channels)
                </option>
              ))}
            </select>
          </div>

          {inputDevice !== null && (
            <div>
              <label className="block text-foreground mb-2">Guitar Channel</label>
              <input
                type="number"
                min="0"
                value={guitarChannel}
                onChange={(e) => setGuitarChannel(parseInt(e.target.value))}
                className="w-full bg-card border border-border rounded-lg px-4 py-3 text-foreground focus:outline-none focus:border-primary"
              />
            </div>
          )}

          <div>
            <label className="block text-foreground mb-2">Output Device (Optional)</label>
            <select
              value={outputDevice !== null ? outputDevice : ''}
              onChange={(e) => setOutputDevice(e.target.value === '' ? null : parseInt(e.target.value))}
              className="w-full bg-card border border-border rounded-lg px-4 py-3 text-foreground focus:outline-none focus:border-primary"
            >
              <option value="">Use same as input...</option>
              {outputDevices.map(device => (
                <option key={device.index} value={device.index}>
                  [{device.index}] {device.name}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleTest}
            disabled={inputDevice === null || testing}
            className="w-full bg-gradient-to-r from-secondary to-primary hover:from-primary hover:to-secondary disabled:from-muted disabled:to-muted text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200"
          >
            {testing ? 'Testing... Play your guitar!' : 'Test Audio'}
          </button>

          {testResult && (
            <div className={`p-4 rounded-lg ${testResult.has_signal ? 'bg-accent/20 border border-accent' : 'bg-destructive/20 border border-destructive'}`}>
              {testResult.has_signal ? (
                <div className="text-accent">
                  Signal detected! (Level: {(testResult.rms_level * 100).toFixed(2)}%)
                </div>
              ) : (
                <div className="text-destructive">
                  No signal detected. Try playing your guitar or check connections.
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {step === 'done' && (
        <div className="text-center py-8">
          <div className="text-6xl mb-4 text-accent">&#10003;</div>
          <div className="text-xl text-accent mb-6">Audio setup complete!</div>
          <button
            onClick={handleComplete}
            className="bg-gradient-to-r from-primary to-secondary hover:from-secondary hover:to-accent text-white font-semibold py-3 px-8 rounded-lg transition-all duration-200"
          >
            Continue to Mode Selection
          </button>
        </div>
      )}
    </div>
  );
};

export default AudioSetup;
