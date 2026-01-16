import React, { useState, useEffect } from 'react';
import { api } from '../api';

const ScaleSelection = ({ onComplete }) => {
  const [scales, setScales] = useState({ major: [], minor: [] });
  const [selectedScale, setSelectedScale] = useState('');
  const [scaleType, setScaleType] = useState('diatonic');
  const [ambientLighting, setAmbientLighting] = useState(true);
  const [strictness, setStrictness] = useState(0.5);
  const [sensitivity, setSensitivity] = useState(0.5);
  const [step, setStep] = useState(1); // 1: scale, 2: type, 3: settings
  const [filter, setFilter] = useState('');

  useEffect(() => {
    loadScales();
  }, []);

  const loadScales = async () => {
    try {
      const scaleList = await api.getScales();
      setScales(scaleList);
    } catch (error) {
      console.error('Failed to load scales:', error);
    }
  };

  const handleScaleSelect = (scale) => {
    setSelectedScale(scale);
    setStep(2);
  };

  const handleTypeSelect = (type) => {
    setScaleType(type);
    setStep(3);
  };

  const handleComplete = async () => {
    const config = await api.getConfig();
    config.scale_name = selectedScale;
    config.scale_type = scaleType;
    config.ambient_lighting = ambientLighting;
    config.strictness = strictness;
    config.sensitivity = sensitivity;
    await api.saveConfig(config);
    onComplete(`${selectedScale} (${scaleType === 'diatonic' ? 'Diatonic' : 'Pentatonic'})`);
  };

  const filteredMajor = scales.major.filter(s => 
    s.toLowerCase().includes(filter.toLowerCase())
  );
  const filteredMinor = scales.minor.filter(s => 
    s.toLowerCase().includes(filter.toLowerCase())
  );

  // Step 1: Scale Selection
  if (step === 1) {
    return (
      <div className="bg-slate-900/50 backdrop-blur-sm border border-slate-800 rounded-xl p-8">
        <h2 className="text-2xl font-bold mb-6 gradient-text">Step 1: Select Scale</h2>

        <div className="mb-6">
          <input
            type="text"
            placeholder="Search scales..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-slate-200 focus:outline-none focus:border-green-500"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-semibold text-blue-400 mb-3">Major Scales</h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {filteredMajor.map(scale => (
                <button
                  key={scale}
                  onClick={() => handleScaleSelect(scale)}
                  className="w-full text-left px-4 py-2 rounded-lg transition-all bg-slate-800 text-slate-300 hover:bg-blue-600 hover:text-white"
                >
                  {scale}
                </button>
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-purple-400 mb-3">Minor Scales</h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {filteredMinor.map(scale => (
                <button
                  key={scale}
                  onClick={() => handleScaleSelect(scale)}
                  className="w-full text-left px-4 py-2 rounded-lg transition-all bg-slate-800 text-slate-300 hover:bg-purple-600 hover:text-white"
                >
                  {scale}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Step 2: Scale Type Selection
  if (step === 2) {
    return (
      <div className="bg-slate-900/50 backdrop-blur-sm border border-slate-800 rounded-xl p-8">
        <h2 className="text-2xl font-bold mb-6 gradient-text">Step 2: Select Scale Type</h2>
        
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 mb-6">
          <div className="text-slate-400 text-sm mb-1">Selected Scale</div>
          <div className="text-xl font-semibold text-green-400">{selectedScale}</div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <button
            onClick={() => handleTypeSelect('diatonic')}
            className="bg-slate-800 hover:bg-blue-600 border-2 border-slate-700 hover:border-blue-500 rounded-xl p-6 text-left transition-all group"
          >
            <div className="text-xl font-bold text-slate-200 group-hover:text-white mb-2">Diatonic</div>
            <div className="text-slate-400 group-hover:text-slate-200 text-sm mb-2">7 notes - Complete scale</div>
            <div className="text-slate-500 group-hover:text-slate-300 text-xs">Full scale for comprehensive practice</div>
          </button>

          <button
            onClick={() => handleTypeSelect('pentatonic')}
            className="bg-slate-800 hover:bg-purple-600 border-2 border-slate-700 hover:border-purple-500 rounded-xl p-6 text-left transition-all group"
          >
            <div className="text-xl font-bold text-slate-200 group-hover:text-white mb-2">Pentatonic</div>
            <div className="text-slate-400 group-hover:text-slate-200 text-sm mb-2">5 notes - Simplified scale</div>
            <div className="text-slate-500 group-hover:text-slate-300 text-xs">Perfect for blues, rock & easier improvisation</div>
          </button>
        </div>

        <button
          onClick={() => setStep(1)}
          className="text-slate-400 hover:text-slate-200 text-sm"
        >
          ← Back to scale selection
        </button>
      </div>
    );
  }

  // Step 3: Settings
  return (
    <div className="bg-slate-900/50 backdrop-blur-sm border border-slate-800 rounded-xl p-8">
      <h2 className="text-2xl font-bold mb-6 gradient-text">Step 3: Practice Settings</h2>
      
      <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 mb-6">
        <div className="text-slate-400 text-sm mb-1">Selected Scale</div>
        <div className="text-xl font-semibold text-green-400">
          {selectedScale} ({scaleType === 'diatonic' ? 'Diatonic' : 'Pentatonic'})
        </div>
      </div>

      {/* Ambient Lighting */}
      <div className="mb-6">
        <label className="flex items-center justify-between p-4 bg-slate-800 rounded-lg hover:bg-slate-700 cursor-pointer transition-all">
          <div>
            <div className="text-slate-200 font-semibold">Ambient Lighting</div>
            <div className="text-slate-400 text-sm">Enable smart bulb visual feedback</div>
          </div>
          <input
            type="checkbox"
            checked={ambientLighting}
            onChange={(e) => setAmbientLighting(e.target.checked)}
            className="w-6 h-6 text-green-600 bg-slate-700 border-slate-600 rounded focus:ring-green-500 focus:ring-2"
          />
        </label>
      </div>

      {/* Strictness */}
      <div className="mb-6">
        <label className="block mb-2">
          <div className="flex justify-between items-center mb-2">
            <span className="text-slate-200 font-semibold">Strictness</span>
            <span className="text-green-400 font-mono">{strictness.toFixed(2)}</span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={strictness}
            onChange={(e) => setStrictness(parseFloat(e.target.value))}
            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-green-500"
          />
          <div className="flex justify-between text-xs text-slate-400 mt-1">
            <span>0.0 - Forgiving</span>
            <span>0.5 - Balanced</span>
            <span>1.0 - Strict</span>
          </div>
        </label>
        <p className="text-slate-500 text-sm mt-2">
          {strictness < 0.4 ? '🟢 Practice mode - mistakes are forgiven' :
           strictness < 0.7 ? '🟡 Balanced - moderate penalties' :
           '🔴 Performance mode - harsh on mistakes'}
        </p>
      </div>

      {/* Sensitivity */}
      <div className="mb-6">
        <label className="block mb-2">
          <div className="flex justify-between items-center mb-2">
            <span className="text-slate-200 font-semibold">Sensitivity</span>
            <span className="text-green-400 font-mono">{sensitivity.toFixed(2)}</span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={sensitivity}
            onChange={(e) => setSensitivity(parseFloat(e.target.value))}
            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-green-500"
          />
          <div className="flex justify-between text-xs text-slate-400 mt-1">
            <span>0.0 - Soft</span>
            <span>0.5 - Normal</span>
            <span>1.0 - Loud</span>
          </div>
        </label>
        <p className="text-slate-500 text-sm mt-2">
          {sensitivity < 0.4 ? '🎵 Picks up soft playing' :
           sensitivity < 0.7 ? '🎸 Normal volume required' :
           '🔊 Only registers loud playing'}
        </p>
      </div>

      <div className="flex gap-3">
        <button
          onClick={() => setStep(2)}
          className="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg transition-all"
        >
          ← Back
        </button>
        <button
          onClick={handleComplete}
          className="flex-1 bg-gradient-to-r from-green-600 to-green-500 hover:from-green-500 hover:to-green-400 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200"
        >
          Start Training →
        </button>
      </div>
    </div>
  );
};

export default ScaleSelection;
