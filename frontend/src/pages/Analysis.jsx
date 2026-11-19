// Code Analysis page — AST + Black analysis with health score and issues
// Persisted across tab switches via AppContext.
import { useState } from 'react';
import { BarChart3, Play, TrendingUp, AlertTriangle, CheckCircle, Info } from 'lucide-react';
import PageHeader from '../components/PageHeader';
import MetricCard from '../components/MetricCard';
import IssueCard from '../components/IssueCard';
import ErrorMessage from '../components/ErrorMessage';
import LoadingSpinner from '../components/LoadingSpinner';
import DownloadButton from '../components/DownloadButton';
import CodeEditor from '../components/CodeEditor';
import { analyzeCode } from '../services/api';
import { useApp } from '../context/AppContext';

export default function Analysis() {
  const { code, setCode, analysisResult, setAnalysisResult } = useApp();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    if (!code.trim()) { setError('Please enter Python code to analyze.'); return; }
    setLoading(true);
    setError('');
    try {
      const data = await analyzeCode(code);
      setAnalysisResult(data);
    } catch (e) {
      setError(`Analysis failed: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Build downloadable report text
  const buildReport = () => {
    if (!analysisResult) return '';
    const lines = [
      '# CodeMate AI — Code Analysis Report',
      `Generated: ${new Date().toLocaleString()}`,
      '',
      `## Health Score: ${analysisResult.health_score}/100`,
      `Syntax Valid: ${analysisResult.syntax_valid ? 'Yes' : 'No'}`,
      `Black Compliant: ${analysisResult.black_compliant ? 'Yes' : 'No'}`,
      analysisResult.black_message ? `Black: ${analysisResult.black_message}` : '',
      '',
      '## Metrics',
      ...Object.entries(analysisResult.metrics || {}).map(([k, v]) => `- ${k}: ${v}`),
      '',
      '## Issues Found',
      ...(analysisResult.issues || []).map((i) =>
        `- [${i.severity}] ${i.category}: ${i.message}${i.line ? ` (line ${i.line})` : ''}${i.suggestion ? ` — ${i.suggestion}` : ''}`
      ),
      analysisResult.disclaimer ? `\n## Note\n${analysisResult.disclaimer}` : '',
    ];
    return lines.join('\n');
  };

  const scoreColor = (s) => s >= 80 ? 'green' : s >= 50 ? 'amber' : 'red';

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <PageHeader
        title="Code Analysis"
        description="Analyze Python code quality using AST parsing and Black formatting checks"
        icon={BarChart3}
      />

      {/* Code editor */}
      <div className="card p-5 mb-5">
        <CodeEditor value={code} onChange={setCode} height="300px" label="Python Code to Analyze" />
        <div className="mt-3 flex gap-3">
          <button
            onClick={handleAnalyze}
            disabled={loading || !code.trim()}
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-accent text-white text-sm font-medium rounded-lg hover:bg-accent-dark disabled:opacity-50 transition-colors"
          >
            <Play size={14} />
            Run Analysis
          </button>
          {analysisResult && (
            <DownloadButton content={buildReport()} filename="analysis_report.md" label="Download Report" />
          )}
        </div>
      </div>

      <ErrorMessage message={error} onDismiss={() => setError('')} />
      {loading && <LoadingSpinner message="Analyzing code…" />}

      {/* Results (persisted across tab switches) */}
      {analysisResult && !loading && (
        <div>
          {/* Score cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-5">
            <MetricCard title="Health Score" value={`${analysisResult.health_score}/100`} icon={TrendingUp} color={scoreColor(analysisResult.health_score)} />
            <MetricCard title="Syntax" value={analysisResult.syntax_valid ? 'Valid' : 'Error'} icon={analysisResult.syntax_valid ? CheckCircle : AlertTriangle} color={analysisResult.syntax_valid ? 'green' : 'red'} />
            <MetricCard title="Black" value={analysisResult.black_compliant ? 'Compliant' : 'Needs Fix'} icon={Info} color={analysisResult.black_compliant ? 'green' : 'amber'} />
            <MetricCard title="Issues" value={(analysisResult.issues || []).length} icon={AlertTriangle} color={(analysisResult.issues || []).length === 0 ? 'green' : 'amber'} />
          </div>

          {/* Metrics */}
          {analysisResult.metrics && Object.keys(analysisResult.metrics).length > 0 && (
            <div className="card p-5 mb-5">
              <h3 className="text-sm font-semibold text-muted uppercase tracking-wide mb-3">Code Metrics</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {Object.entries(analysisResult.metrics).map(([k, v]) => (
                  <div key={k} className="bg-gray-50 rounded-lg p-3">
                    <div className="text-xs text-muted capitalize">{k.replace(/_/g, ' ')}</div>
                    <div className="text-lg font-bold text-textPrimary">{String(v)}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Issues list */}
          <div className="card p-5">
            <h3 className="text-sm font-semibold text-muted uppercase tracking-wide mb-3">
              Issues Found ({(analysisResult.issues || []).length})
            </h3>
            {(analysisResult.issues || []).length === 0 ? (
              <div className="flex items-center gap-2 text-sm text-green-700">
                <CheckCircle size={16} /> No issues detected — great code!
              </div>
            ) : (
              <div>
                {(analysisResult.issues || []).map((issue, i) => (
                  <IssueCard key={i} issue={issue} />
                ))}
              </div>
            )}
            {analysisResult.disclaimer && (
              <div className="mt-3 text-xs text-muted italic border-t border-border pt-2">{analysisResult.disclaimer}</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
