// AI Refactoring page — side-by-side original vs refactored with diff and explanation
// Results are globally persisted in AppContext across tab switches.
import { useState } from 'react';
import { Wand2, Play, ArrowRightLeft, FileText, Check, ArrowRight } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import PageHeader from '../components/PageHeader';
import CodeEditor from '../components/CodeEditor';
import ErrorMessage from '../components/ErrorMessage';
import LoadingSpinner from '../components/LoadingSpinner';
import DownloadButton from '../components/DownloadButton';
import CopyButton from '../components/CopyButton';
import { refactorCode } from '../services/api';
import { useApp } from '../context/AppContext';

export default function Refactoring() {
  const {
    code,
    setCode,
    refactorResult,
    setRefactorResult,
    apiKey,
    setApiKey,
    model,
    setModel,
  } = useApp();

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('comparison'); // 'comparison' | 'diff' | 'explanation'
  const [adopted, setAdopted] = useState(false);

  const handleRefactor = async () => {
    if (!code.trim()) { setError('Please enter Python code to refactor.'); return; }
    setLoading(true);
    setError('');
    setAdopted(false);
    try {
      const data = await refactorCode(code, apiKey, model);
      setRefactorResult(data);
      if (!data.success) setError(data.error || 'Refactoring did not succeed.');
    } catch (e) {
      setError(`Refactoring failed: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleAdoptCode = () => {
    if (refactorResult?.refactored_code) {
      setCode(refactorResult.refactored_code);
      setAdopted(true);
      setTimeout(() => setAdopted(false), 3000);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <PageHeader
        title="AI Refactoring"
        description="Improve code quality with Google Gemini — preserves functionality while applying PEP 8 and best practices"
        icon={Wand2}
      />

      {/* Input + API config */}
      <div className="card p-5 mb-5">
        <CodeEditor value={code} onChange={setCode} height="260px" label="Original Python Code" />

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
            onClick={handleRefactor}
            disabled={loading || !code.trim()}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-purple-600 text-white text-sm font-medium rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors"
          >
            <Wand2 size={14} />
            Refactor with AI
          </button>
        </div>
      </div>

      <ErrorMessage message={error} onDismiss={() => setError('')} />
      {loading && <LoadingSpinner message="Gemini is refactoring your code…" />}

      {/* Results (persisted across tabs) */}
      {refactorResult && refactorResult.success && !loading && (
        <div>
          {/* Action toolbar */}
          <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
            {/* Tabs */}
            <div className="flex gap-1 p-1 bg-gray-100 rounded-lg">
              {['comparison', 'diff', 'explanation'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`tab-btn capitalize ${activeTab === tab ? 'active' : ''}`}
                >
                  {tab === 'comparison' ? (
                    <span className="flex items-center gap-1.5"><ArrowRightLeft size={12} />Side by Side</span>
                  ) : tab === 'diff' ? (
                    <span className="flex items-center gap-1.5"><Play size={12} />Diff</span>
                  ) : (
                    <span className="flex items-center gap-1.5"><FileText size={12} />Explanation</span>
                  )}
                </button>
              ))}
            </div>

            {/* Buttons */}
            <div className="flex items-center gap-2">
              <button
                onClick={handleAdoptCode}
                className={`inline-flex items-center gap-1.5 px-3 py-2 text-xs font-semibold rounded-lg border transition-all ${
                  adopted
                    ? 'bg-green-600 text-white border-green-600'
                    : 'bg-white text-primary border-border hover:bg-gray-50'
                }`}
                title="Make this refactored code the active code across all other tabs"
              >
                {adopted ? <><Check size={13} /> Active Code Updated!</> : <><ArrowRight size={13} /> Use Refactored Code Everywhere</>}
              </button>

              <CopyButton
                text={refactorResult.refactored_code}
                label="Copy Code"
              />

              <DownloadButton
                content={refactorResult.refactored_code}
                filename="refactored_code.py"
                label="Download Refactored .py"
              />
            </div>
          </div>

          {/* Health delta */}
          {refactorResult.health_score_delta !== undefined && (
            <div className={`text-sm px-3 py-2 rounded-lg border mb-4 ${refactorResult.health_score_delta >= 0 ? 'bg-green-50 border-green-200 text-green-700' : 'bg-amber-50 border-amber-200 text-amber-700'}`}>
              Health score change: {refactorResult.health_score_delta >= 0 ? '+' : ''}{refactorResult.health_score_delta} points
            </div>
          )}

          {/* Comparison tab */}
          {activeTab === 'comparison' && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <CodeEditor value={refactorResult.original_code || code} height="400px" readOnly label="Original Code" />
              <CodeEditor value={refactorResult.refactored_code || ''} height="400px" readOnly label="Refactored Code" />
            </div>
          )}

          {/* Diff tab */}
          {activeTab === 'diff' && (
            <div className="card p-5">
              <h3 className="text-sm font-semibold text-muted uppercase tracking-wide mb-3">Unified Diff</h3>
              {refactorResult.diff ? (
                <pre className="text-xs font-mono bg-gray-900 text-gray-200 p-4 rounded-lg overflow-auto max-h-96 whitespace-pre">
                  {refactorResult.diff}
                </pre>
              ) : (
                <div className="text-sm text-muted">No diff available.</div>
              )}
            </div>
          )}

          {/* Explanation tab */}
          {activeTab === 'explanation' && (
            <div className="card p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-muted uppercase tracking-wide">Refactoring Explanation</h3>
                {refactorResult.explanation && (
                  <CopyButton text={refactorResult.explanation} label="Copy Explanation" />
                )}
              </div>
              {refactorResult.explanation ? (
                <div className="markdown-body">
                  <ReactMarkdown>{refactorResult.explanation}</ReactMarkdown>
                </div>
              ) : (
                <div className="text-sm text-muted">No explanation provided.</div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
