// Documentation Generator page — README and Docstrings generation
// Persisted across tab switches via AppContext.
import { useState } from 'react';
import { FileText, Play } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import PageHeader from '../components/PageHeader';
import CodeEditor from '../components/CodeEditor';
import ErrorMessage from '../components/ErrorMessage';
import LoadingSpinner from '../components/LoadingSpinner';
import DownloadButton from '../components/DownloadButton';
import CopyButton from '../components/CopyButton';
import { documentCode } from '../services/api';
import { useApp } from '../context/AppContext';

export default function Documentation() {
  const {
    code,
    setCode,
    readmeResult,
    setReadmeResult,
    docstringResult,
    setDocstringResult,
    apiKey,
    setApiKey,
    model,
    setModel,
  } = useApp();

  const [loading, setLoading] = useState(false);
  const [loadingType, setLoadingType] = useState('');
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('readme');

  const handleGenerate = async (type) => {
    if (!code.trim()) { setError('Please enter Python code first.'); return; }
    setLoading(true);
    setLoadingType(type);
    setError('');
    try {
      const data = await documentCode(code, type, apiKey, model);
      if (type === 'readme') setReadmeResult(data);
      else setDocstringResult(data);
      if (!data.success) setError(data.error || 'Generation failed.');
      else setActiveTab(type);
    } catch (e) {
      setError(`Documentation generation failed: ${e.message}`);
    } finally {
      setLoading(false);
      setLoadingType('');
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <PageHeader
        title="Documentation Generator"
        description="Auto-generate README.md and PEP 257 docstrings for your Python code using Gemini"
        icon={FileText}
      />

      {/* Code input */}
      <div className="card p-5 mb-5">
        <CodeEditor value={code} onChange={setCode} height="220px" label="Python Code" />

        <div className="mt-4 flex flex-wrap gap-3 items-end">
          <div className="flex-1 min-w-48">
            <label className="block text-xs font-semibold text-muted uppercase tracking-wide mb-1">
              Gemini API Key (optional — uses server key if blank)
            </label>
            <input
              type="password"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="AIza…"
              className="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-accent/30"
            />
          </div>
          <div className="w-52">
            <label className="block text-xs font-semibold text-muted uppercase tracking-wide mb-1">Model</label>
            <input
              type="text"
              value={model}
              onChange={(e) => setModel(e.target.value)}
              placeholder="gemini-3.5-flash-lite"
              className="w-full px-3 py-2 text-sm border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-accent/30"
            />
          </div>
          <button
            onClick={() => handleGenerate('readme')}
            disabled={loading || !code.trim()}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-amber-600 text-white text-sm font-medium rounded-lg hover:bg-amber-700 disabled:opacity-50 transition-colors"
          >
            <Play size={14} />
            Generate README
          </button>
          <button
            onClick={() => handleGenerate('docstrings')}
            disabled={loading || !code.trim()}
            className="inline-flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            <FileText size={14} />
            Add Docstrings
          </button>
        </div>
      </div>

      <ErrorMessage message={error} onDismiss={() => setError('')} />
      {loading && <LoadingSpinner message={`Generating ${loadingType === 'readme' ? 'README' : 'docstrings'}…`} />}

      {/* Results (persisted across tabs) */}
      {(readmeResult?.success || docstringResult?.success) && !loading && (
        <div>
          {/* Tabs */}
          <div className="flex gap-1 mb-4 p-1 bg-gray-100 rounded-lg w-fit">
            {readmeResult?.success && (
              <button onClick={() => setActiveTab('readme')} className={`tab-btn ${activeTab === 'readme' ? 'active' : ''}`}>README.md</button>
            )}
            {docstringResult?.success && (
              <button onClick={() => setActiveTab('docstrings')} className={`tab-btn ${activeTab === 'docstrings' ? 'active' : ''}`}>Docstrings</button>
            )}
          </div>

          {/* README tab */}
          {activeTab === 'readme' && readmeResult?.success && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <CopyButton text={readmeResult.readme_markdown} label="Copy Markdown" />
                <DownloadButton content={readmeResult.readme_markdown} filename="README.md" label="Download README.md" />
              </div>
              <div className="card p-6 markdown-body">
                <ReactMarkdown>{readmeResult.readme_markdown || ''}</ReactMarkdown>
              </div>
            </div>
          )}

          {/* Docstrings tab */}
          {activeTab === 'docstrings' && docstringResult?.success && (
            <div>
              <div className="flex items-center gap-2 mb-3">
                <CopyButton text={docstringResult.documented_code} label="Copy Code" />
                <DownloadButton content={docstringResult.documented_code} filename="documented_code.py" label="Download Documented .py" />
              </div>
              <CodeEditor value={docstringResult.documented_code || ''} height="500px" readOnly label="Code with Docstrings" />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
