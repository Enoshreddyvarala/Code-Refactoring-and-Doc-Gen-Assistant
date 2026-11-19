// API service layer — all calls to FastAPI backend
// API base URL from environment variable (set in .env)
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Generic fetch wrapper with error handling
async function apiFetch(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `Request failed: ${response.status}`);
  }
  return response.json();
}

// Check backend health
export const checkHealth = () => apiFetch('/api/health');

// Analyze Python code (AST + Black)
export const analyzeCode = (code) =>
  apiFetch('/api/analyze', {
    method: 'POST',
    body: JSON.stringify({ code }),
  });

// AI refactor code (Gemini)
export const refactorCode = (code, apiKey = '', model = '') =>
  apiFetch('/api/refactor', {
    method: 'POST',
    body: JSON.stringify({ code, api_key: apiKey || undefined, model: model || undefined }),
  });

// AI explain code (Gemini)
export const explainCode = (code, apiKey = '', model = '') =>
  apiFetch('/api/explain', {
    method: 'POST',
    body: JSON.stringify({ code, api_key: apiKey || undefined, model: model || undefined }),
  });

// AI generate documentation (Gemini)
export const documentCode = (code, docType = 'readme', apiKey = '', model = '') =>
  apiFetch('/api/document', {
    method: 'POST',
    body: JSON.stringify({ code, doc_type: docType, api_key: apiKey || undefined, model: model || undefined }),
  });

// Validate / format with Black / run tests
export const validateCode = (code, action = 'validate', testCode = '') =>
  apiFetch('/api/validate', {
    method: 'POST',
    body: JSON.stringify({ code, action, test_code: testCode || undefined }),
  });

// Get list of sample programs
export const fetchSamples = () => apiFetch('/api/samples');

// Get a specific sample by name
export const fetchSampleCode = (name) => apiFetch(`/api/samples/${encodeURIComponent(name)}`);

// Upload a .py file
export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(`${BASE_URL}/api/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `Upload failed: ${response.status}`);
  }
  return response.json();
};
