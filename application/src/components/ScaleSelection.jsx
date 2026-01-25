import React, { useState, useEffect } from 'react';
import { api } from '../api';

const ScaleSelection = ({ onComplete, onBack }) => {
  const [scales, setScales] = useState({ major: [], minor: [] });
  const [selectedScale, setSelectedScale] = useState('');
  const [scaleType, setScaleType] = useState('natural');
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
    onComplete(`${selectedScale} (${scaleType === 'natural' ? 'Natural' : 'Pentatonic'})`);
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
      <div className="bg-card/50 backdrop-blur-sm border border-border rounded-xl p-8">
        <h2 className="text-2xl font-bold mb-6 gradient-text">Step 1: Select Scale</h2>

        <div className="mb-6">
          <input
            type="text"
            placeholder="Search scales..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="w-full bg-card border border-border rounded-lg px-4 py-3 text-foreground focus:outline-none focus:border-primary"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-lg font-semibold text-primary mb-3">Major Scales</h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {filteredMajor.map(scale => (
                <button
                  key={scale}
                  onClick={() => handleScaleSelect(scale)}
                  className="w-full text-left px-4 py-2 rounded-lg transition-all bg-card text-foreground hover:bg-primary hover:text-primary-foreground"
                >
                  {scale}
                </button>
              ))}
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold text-accent mb-3">Minor Scales</h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {filteredMinor.map(scale => (
                <button
                  key={scale}
                  onClick={() => handleScaleSelect(scale)}
                  className="w-full text-left px-4 py-2 rounded-lg transition-all bg-card text-foreground hover:bg-accent hover:text-accent-foreground"
                >
                  {scale}
                </button>
              ))}
            </div>
          </div>
        </div>

        {onBack && (
          <button
            onClick={onBack}
            className="mt-6 px-6 py-3 bg-card hover:bg-card/80 text-foreground rounded-lg transition-all border border-border"
          >
            ← Back to mode selection
          </button>
        )}
      </div>
    );
  }

  // Step 2: Scale Type Selection
  if (step === 2) {
    return (
      <div className="bg-card/50 backdrop-blur-sm border border-border rounded-xl p-8">
        <h2 className="text-2xl font-bold mb-6 gradient-text">Step 2: Select Scale Type</h2>

        <div className="bg-card border border-border rounded-lg p-4 mb-6">
          <div className="text-muted-foreground text-sm mb-1">Selected Scale</div>
          <div className="text-xl font-semibold text-primary">{selectedScale}</div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <button
            onClick={() => handleTypeSelect('natural')}
            className="bg-card hover:bg-primary border-2 border-border hover:border-primary rounded-xl p-6 text-left transition-all group"
          >
            <div className="text-xl font-bold text-foreground group-hover:text-primary-foreground mb-2">Natural</div>
            <div className="text-muted-foreground group-hover:text-primary-foreground/80 text-sm mb-2">7 notes - Complete scale</div>
            <div className="text-muted group-hover:text-primary-foreground/60 text-xs">Full scale for comprehensive practice</div>
          </button>

          <button
            onClick={() => handleTypeSelect('pentatonic')}
            className="bg-card hover:bg-accent border-2 border-border hover:border-accent rounded-xl p-6 text-left transition-all group"
          >
            <div className="text-xl font-bold text-foreground group-hover:text-accent-foreground mb-2">Pentatonic</div>
            <div className="text-muted-foreground group-hover:text-accent-foreground/80 text-sm mb-2">5 notes - Simplified scale</div>
            <div className="text-muted group-hover:text-accent-foreground/60 text-xs">Perfect for blues, rock & easier improvisation</div>
          </button>
        </div>

        <button
          onClick={() => setStep(1)}
          className="px-6 py-3 bg-card hover:bg-card/80 text-foreground rounded-lg transition-all border border-border"
        >
          ← Back to scale selection
        </button>
      </div>
    );
  }

  // Step 3: Settings
  return (
    <div className="bg-card/50 backdrop-blur-sm border border-border rounded-xl p-8">
      <h2 className="text-2xl font-bold mb-6 gradient-text">Step 3: Practice Settings</h2>

      <div className="bg-card border border-border rounded-lg p-4 mb-6">
        <div className="text-muted-foreground text-sm mb-1">Selected Scale</div>
        <div className="text-xl font-semibold text-primary">
          {selectedScale} ({scaleType === 'natural' ? 'Natural' : 'Pentatonic'})
        </div>
      </div>

      {/* Ambient Lighting */}
      <div className="mb-6">
        <label className="flex items-center justify-between p-4 bg-card rounded-lg hover:bg-card/80 cursor-pointer transition-all border border-border">
          <div>
            <div className="text-foreground font-semibold">Ambient Lighting</div>
            <div className="text-muted-foreground text-sm">Enable smart bulb visual feedback</div>
          </div>
          <input
            type="checkbox"
            checked={ambientLighting}
            onChange={(e) => setAmbientLighting(e.target.checked)}
            className="w-6 h-6 text-primary bg-card border-border rounded focus:ring-primary focus:ring-2"
          />
        </label>
      </div>

      {/* Strictness */}
      <div className="mb-6">
        <label className="block mb-2">
          <div className="flex justify-between items-center mb-2">
            <span className="text-foreground font-semibold">Strictness</span>
            <span className="text-primary font-mono">{strictness.toFixed(2)}</span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={strictness}
            onChange={(e) => setStrictness(parseFloat(e.target.value))}
            className="w-full h-2 bg-card rounded-lg appearance-none cursor-pointer accent-primary"
          />
          <div className="flex justify-between text-xs text-muted-foreground mt-1">
            <span>0.0 - Forgiving</span>
            <span>0.5 - Balanced</span>
            <span>1.0 - Strict</span>
          </div>
        </label>
        <p className="text-muted text-sm mt-2">
          {strictness < 0.4 ? 'Practice mode - mistakes are forgiven' :
           strictness < 0.7 ? 'Balanced - moderate penalties' :
           'Performance mode - harsh on mistakes'}
        </p>
      </div>

      {/* Sensitivity */}
      <div className="mb-6">
        <label className="block mb-2">
          <div className="flex justify-between items-center mb-2">
            <span className="text-foreground font-semibold">Sensitivity</span>
            <span className="text-primary font-mono">{sensitivity.toFixed(2)}</span>
          </div>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={sensitivity}
            onChange={(e) => setSensitivity(parseFloat(e.target.value))}
            className="w-full h-2 bg-card rounded-lg appearance-none cursor-pointer accent-primary"
          />
          <div className="flex justify-between text-xs text-muted-foreground mt-1">
            <span>0.0 - Soft</span>
            <span>0.5 - Normal</span>
            <span>1.0 - Loud</span>
          </div>
        </label>
        <p className="text-muted text-sm mt-2">
          {sensitivity < 0.4 ? 'Picks up soft playing' :
           sensitivity < 0.7 ? 'Normal volume required' :
           'Only registers loud playing'}
        </p>
      </div>

      <div className="flex gap-3">
        <button
          onClick={() => setStep(2)}
          className="px-6 py-3 bg-card hover:bg-card/80 text-foreground rounded-lg transition-all border border-border"
        >
          ← Back
        </button>
        <button
          onClick={handleComplete}
          className="flex-1 bg-gradient-to-r from-primary to-secondary hover:from-secondary hover:to-accent text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200"
        >
          Start Training
        </button>
      </div>
    </div>
  );
};

export default ScaleSelection;
