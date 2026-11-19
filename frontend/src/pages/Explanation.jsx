// Code Explanation page — renders Gemini's markdown explanation
// Persisted across tab switches via AppContext.
import { useState } from 'react';
import { BookOpen, Play, AlertTriangle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import PageHeader from '../components/PageHeader';
import CodeEditor from '../components/CodeEditor';
import ErrorMessage from '../components/ErrorMessage';
import LoadingSpinner from '../components/LoadingSpinner';
import DownloadButton from '../components/DownloadButton';
import CopyButton from '../components/CopyButton';
import { explainCode } from '../services/api';
import { useApp } from '../context/AppContext';

export default function Explanation() {
  const {
    code,
    setCode,
    explanationResult,
    setExplanationResult,
    apiKey,
    setApiKey,
    model,
    setModel,
  } = useApp();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showCode, setShowCode] = useState(true);

  const handleExplain = async () => {
    if (!code.trim()) { setError('Please enter Python code to explain.'); return; }
    setLoading(true);
    setError('');
    try {
      const data = await explainCode(code, apiKey, model);
      setExplanationResult(data);
      if (!data.success) setError(data.error || 'Explanation failed.');
    } catch (e) {
      setError(`Explanation failed: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const buildDownload = () => {
    if (!explanationResult) return '';
    return [
      '# CodeMate AI — Code Explanation',
      `Generated: ${new Date().toLocaleString()}`,
      '',
      '## Original Code',
      '```python',
      code,
      '```',
      '',
      '---',
      '',
      explanationResult.explanation || '',
    ].join('\n');
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <PageHeader
        title="Code Explanation"
        description="Understand your code with beginner-friendly explanations, real-world analogies, and step-by-step guides"
        icon={BookOpen}
      />

      {/* Input section */}
      <div className="card p-5 mb-5">
        <div className="flex items-center justify-between mb-3">
          <span className="text-xs font-semibold text-muted uppercase tracking-wide">Python Code</span>
          <button
            onClick={() => setShowCode(!showCode)}
            className="text-xs text-accent hover:text-accent-dark"
          >
            {showCode ? 'Hide editor' : 'Show editor'}
          </button>
        </div>

        {showCode && (
          <CodeEditor value={code} onChange={setCode} height="220px" />
        )}

        {!showCode && code.trim() && (
          <div className="text-xs text-muted px-2 py-1 bg-gray-50 rounded border border-border">
            {code.split('\n').length} lines of code loaded
          </div>
        )}

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
            onClick={handleExplain}
            disabled={loading || !code.trim()}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
          >
            <Play size={14} />
            Explain Code
          </button>
        </div>
      </div>

      <ErrorMessage message={error} onDismiss={() => setError('')} />
      {loading && <LoadingSpinner message="Gemini is generating a beginner-friendly explanation…" />}

      {/* Results (persisted across tabs) */}
      {explanationResult && explanationResult.success && !loading && (
        <div>
          {explanationResult.has_syntax_warning && (
            <div className="flex items-center gap-2 text-sm px-3 py-2 bg-amber-50 border border-amber-200 text-amber-700 rounded-lg mb-3">
              <AlertTriangle size={14} />
              Note: Code has a syntax issue — {explanationResult.syntax_warning_message}. Explanation may be incomplete.
            </div>
          )}

          <div className="flex items-center gap-2 mb-3">
            <CopyButton text={explanationResult.explanation} label="Copy Explanation" />
            <DownloadButton content={buildDownload()} filename="code_explanation.md" label="Download Explanation (.md)" />
          </div>

          <div className="card p-6 markdown-body">
            <ReactMarkdown>{explanationResult.explanation || 'No explanation generated.'}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}
