// Code Workspace — central hub for entering code, uploading files, selecting samples
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Code2, Upload, ChevronDown, CheckCircle, AlertCircle } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import CodeEditor from '../components/CodeEditor';
import ErrorMessage from '../components/ErrorMessage';
import LoadingSpinner from '../components/LoadingSpinner';
import { fetchSamples, fetchSampleCode, uploadFile, validateCode } from '../services/api';
import { useApp } from '../context/AppContext';

// Legacy helpers kept for compatibility
export const getSharedCode = () => localStorage.getItem('cm_code') || localStorage.getItem('codemate_code') || '';
export const setSharedCode = (code) => {
  localStorage.setItem('cm_code', code || '');
  localStorage.setItem('codemate_code', code || '');
};

export default function Workspace() {
  const navigate = useNavigate();
  const { code, setCode } = useApp();
  const [samples, setSamples] = useState([]);
  const [selectedSample, setSelectedSample] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [validateResult, setValidateResult] = useState(null);
  const [formatResult, setFormatResult] = useState(null);

  // Load sample names on mount
  useEffect(() => {
    fetchSamples()
      .then((data) => setSamples(data || []))
      .catch(() => setSamples([]));
  }, []);

  const handleCodeChange = (val) => {
    setCode(val || '');
  };

  // Load a sample program
  const handleLoadSample = async (name) => {
    if (!name) return;
    setLoading(true);
    setError('');
    try {
      const data = await fetchSampleCode(name);
      handleCodeChange(data.code || '');
      setSelectedSample(name);
    } catch (e) {
      setError(`Could not load sample: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Handle .py file upload
  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (!file.name.endsWith('.py')) {
      setError('Please upload a .py Python file.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const data = await uploadFile(file);
      handleCodeChange(data.code || '');
    } catch (err) {
      setError(`Upload failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Validate syntax
  const handleValidate = async () => {
    if (!code.trim()) { setError('Please enter code first.'); return; }
    setLoading(true);
    setError('');
    setValidateResult(null);
    try {
      const result = await validateCode(code, 'validate');
      setValidateResult(result);
    } catch (e) {
      setError(`Validation failed: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Format with Black
  const handleFormatBlack = async () => {
    if (!code.trim()) { setError('Please enter code first.'); return; }
    setLoading(true);
    setError('');
    setFormatResult(null);
    try {
      const result = await validateCode(code, 'format_black');
      setFormatResult(result);
      if (result.formatted_code) handleCodeChange(result.formatted_code);
    } catch (e) {
      setError(`Format failed: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <PageHeader
        title="Code Workspace"
        description="Paste Python code, upload a .py file, or choose a sample program"
        icon={Code2}
      />

      {/* Controls bar */}
      <div className="flex flex-wrap items-center gap-3 mb-4">
        {/* Sample selector */}
        <div className="relative">
          <select
            value={selectedSample}
            onChange={(e) => handleLoadSample(e.target.value)}
            className="appearance-none pl-3 pr-8 py-2 text-sm border border-border rounded-lg bg-white text-textPrimary focus:outline-none focus:ring-2 focus:ring-accent/30"
          >
            <option value="">— Load Sample —</option>
            {samples.map((s) => (
              <option key={s.name} value={s.name}>{s.name}</option>
            ))}
          </select>
          <ChevronDown size={14} className="absolute right-2 top-1/2 -translate-y-1/2 text-muted pointer-events-none" />
        </div>

        {/* File upload */}
        <label className="inline-flex items-center gap-2 px-3 py-2 text-sm border border-border rounded-lg bg-white text-textPrimary cursor-pointer hover:bg-gray-50 transition-colors">
          <Upload size={14} />
          Upload .py
          <input type="file" accept=".py" onChange={handleFileUpload} className="hidden" />
        </label>

        {/* Validate */}
        <button
          onClick={handleValidate}
          disabled={loading}
          className="workspace-tool"
        >
          Validate Syntax
        </button>

        {/* Format with Black */}
        <button
          onClick={handleFormatBlack}
          disabled={loading}
          className="workspace-tool workspace-tool-format"
        >
          Format with Black
        </button>

        {/* Clear */}
        <button
          onClick={() => { handleCodeChange(''); setValidateResult(null); setFormatResult(null); }}
          className="workspace-tool workspace-tool-clear"
        >
          Clear
        </button>
      </div>

      <ErrorMessage message={error} onDismiss={() => setError('')} />

      {loading && <LoadingSpinner message="Loading…" />}

      {/* Validation result */}
      {validateResult && !loading && (
        <div className={`flex items-center gap-2 text-sm px-3 py-2 rounded-lg border mb-3 ${validateResult.syntax_valid ? 'bg-green-50 border-green-200 text-green-700' : 'bg-red-50 border-red-200 text-red-700'}`}>
          {validateResult.syntax_valid
            ? <><CheckCircle size={14} /> Syntax is valid</>
            : <><AlertCircle size={14} /> {validateResult.error || 'Syntax error detected'}</>}
        </div>
      )}

      {/* Format result */}
      {formatResult && !loading && (
        <div className={`flex items-center gap-2 text-sm px-3 py-2 rounded-lg border mb-3 ${formatResult.formatted_code ? 'bg-green-50 border-green-200 text-green-700' : 'bg-amber-50 border-amber-200 text-amber-700'}`}>
          {formatResult.formatted_code
            ? <><CheckCircle size={14} /> Code formatted with Black</>
            : <><AlertCircle size={14} /> {formatResult.black_message || 'Black formatting failed'}</>}
        </div>
      )}

      {/* Monaco Editor */}
      <CodeEditor value={code} onChange={handleCodeChange} height="450px" label="Python Code" />

      {code.trim() && (
        <div className="mt-2 text-xs text-muted text-right">
          {code.split('\n').length} lines · {code.length} characters
        </div>
      )}

      {/* Navigate to other pages */}
      {code.trim() && (
        <div className="mt-5 flex flex-wrap gap-3">
          <button onClick={() => navigate('/analysis')} className="workspace-action workspace-action-blue">
            → Run Analysis
          </button>
          <button onClick={() => navigate('/refactoring')} className="workspace-action workspace-action-purple">
            → AI Refactor
          </button>
          <button onClick={() => navigate('/explanation')} className="workspace-action workspace-action-green">
            → Explain Code
          </button>
          <button onClick={() => navigate('/documentation')} className="workspace-action workspace-action-amber">
            → Generate Docs
          </button>
        </div>
      )}
    </div>
  );
}


