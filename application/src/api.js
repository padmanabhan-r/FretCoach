const API_BASE_URL = 'http://127.0.0.1:8000';

export const api = {
  // Audio device endpoints
  async getAudioDevices() {
    const response = await fetch(`${API_BASE_URL}/audio/devices`);
    return response.json();
  },

  async testAudioDevice(deviceIndex, channel = 0) {
    const response = await fetch(`${API_BASE_URL}/audio/test/${deviceIndex}?channel=${channel}`, {
      method: 'POST',
    });
    return response.json();
  },

  // Scale endpoints
  async getScales() {
    const response = await fetch(`${API_BASE_URL}/scales`);
    return response.json();
  },

  // Config endpoints
  async saveConfig(config) {
    const response = await fetch(`${API_BASE_URL}/config`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    });
    return response.json();
  },

  async getConfig() {
    const response = await fetch(`${API_BASE_URL}/config`);
    return response.json();
  },

  // Session endpoints
  async startSession() {
    const response = await fetch(`${API_BASE_URL}/session/start`, {
      method: 'POST',
    });
    return response.json();
  },

  async stopSession() {
    const response = await fetch(`${API_BASE_URL}/session/stop`, {
      method: 'POST',
    });
    return response.json();
  },

  async getMetrics() {
    const response = await fetch(`${API_BASE_URL}/session/metrics`);
    return response.json();
  },

  // WebSocket for real-time metrics
  connectWebSocket(onMessage) {
    const ws = new WebSocket(`ws://127.0.0.1:8000/ws/metrics`);
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return ws;
  },
};
