import React, { useState, useEffect } from 'react';
import { api } from '../api';

const ScaleSelection = ({ onComplete }) => {
  const [scales, setScales] = useState([]);
  const [selectedScale, setSelectedScale] = useState('');
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

  const handleComplete = async () => {
    const config = await api.getConfig();
    config.scale_name = selectedScale;
    await api.saveConfig(config);
    onComplete(selectedScale);
  };

  const filteredScales = scales.filter(scale => 
    scale.toLowerCase().includes(filter.toLowerCase())
  );

  const majorScales = filteredScales.filter(s => s.includes('Major'));
  const minorScales = filteredScales.filter(s => s.includes('Minor'));

  return (
    <div className="bg-slate-900/50 backdrop-blur-sm border border-slate-800 rounded-xl p-8">
      <h2 className="text-2xl font-bold mb-6 gradient-text">Select Scale</h2>

      <div className="mb-6">
        <input
          type="text"
          placeholder="Search scales..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-slate-200 focus:outline-none focus:border-green-500"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div>
          <h3 className="text-lg font-semibold text-blue-400 mb-3">Major Scales</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {majorScales.map(scale => (
              <button
                key={scale}
                onClick={() => setSelectedScale(scale)}
                className={`w-full text-left px-4 py-2 rounded-lg transition-all ${
                  selectedScale === scale
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                {scale}
              </button>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-purple-400 mb-3">Minor Scales</h3>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {minorScales.map(scale => (
              <button
                key={scale}
                onClick={() => setSelectedScale(scale)}
                className={`w-full text-left px-4 py-2 rounded-lg transition-all ${
                  selectedScale === scale
                    ? 'bg-purple-600 text-white'
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                {scale}
              </button>
            ))}
          </div>
        </div>
      </div>

      {selectedScale && (
        <div className="bg-slate-800/50 border border-slate-700 rounded-lg p-4 mb-6">
          <div className="text-slate-400 text-sm mb-1">Selected Scale</div>
          <div className="text-xl font-semibold text-green-400">{selectedScale}</div>
        </div>
      )}

      <button
        onClick={handleComplete}
        disabled={!selectedScale}
        className="w-full bg-gradient-to-r from-green-600 to-green-500 hover:from-green-500 hover:to-green-400 disabled:from-slate-700 disabled:to-slate-700 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200"
      >
        Start Practice Session
      </button>
    </div>
  );
};

export default ScaleSelection;
