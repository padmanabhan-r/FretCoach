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
    if (inputDevice === null) return;
    
    setTesting(true);
    setTestResult(null);
    
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
    <div className="bg-slate-900/50 backdrop-blur-sm border border-slate-800 rounded-xl p-8">
      <h2 className="text-2xl font-bold mb-6 gradient-text">Audio Setup</h2>

      {step === 'loading' && (
        <div className="text-center py-12">
          <div className="text-slate-400">Loading audio devices...</div>
        </div>
      )}

      {step === 'devices' && (
        <div className="space-y-6">
          <div>
            <label className="block text-slate-300 mb-2">Input Device (Guitar)</label>
            <select
              value={inputDevice !== null ? inputDevice : ''}
              onChange={(e) => setInputDevice(e.target.value === '' ? null : parseInt(e.target.value))}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-slate-200 focus:outline-none focus:border-green-500"
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
              <label className="block text-slate-300 mb-2">Guitar Channel</label>
              <input
                type="number"
                min="0"
                value={guitarChannel}
                onChange={(e) => setGuitarChannel(parseInt(e.target.value))}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-slate-200 focus:outline-none focus:border-green-500"
              />
            </div>
          )}

          <div>
            <label className="block text-slate-300 mb-2">Output Device (Optional)</label>
            <select
              value={outputDevice !== null ? outputDevice : ''}
              onChange={(e) => setOutputDevice(e.target.value === '' ? null : parseInt(e.target.value))}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-slate-200 focus:outline-none focus:border-green-500"
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
            className="w-full bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 disabled:from-slate-700 disabled:to-slate-700 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200"
          >
            {testing ? 'Testing... Play your guitar!' : 'Test Audio'}
          </button>

          {testResult && (
            <div className={`p-4 rounded-lg ${testResult.has_signal ? 'bg-green-500/20 border border-green-500' : 'bg-red-500/20 border border-red-500'}`}>
              {testResult.has_signal ? (
                <div className="text-green-400">
                  ✓ Signal detected! (Level: {(testResult.rms_level * 100).toFixed(2)}%)
                </div>
              ) : (
                <div className="text-red-400">
                  No signal detected. Try playing your guitar or check connections.
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {step === 'done' && (
        <div className="text-center py-8">
          <div className="text-6xl mb-4">✓</div>
          <div className="text-xl text-green-400 mb-6">Audio setup complete!</div>
          <button
            onClick={handleComplete}
            className="bg-gradient-to-r from-green-600 to-green-500 hover:from-green-500 hover:to-green-400 text-white font-semibold py-3 px-8 rounded-lg transition-all duration-200"
          >
            Continue to Scale Selection
          </button>
        </div>
      )}
    </div>
  );
};

export default AudioSetup;
