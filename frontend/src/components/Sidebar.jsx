import { useState } from 'react';
import { NavLink, Link } from 'react-router-dom';
import { Home, Code2, BarChart3, Wand2, BookOpen, FileText, Info, Settings, X } from 'lucide-react';
import { useApp } from '../context/AppContext';

const items = [
  ['/', 'Intro', Home], ['/workspace', 'Workspace', Code2],
  ['/analysis', 'Analysis', BarChart3], ['/refactoring', 'Refactor', Wand2],
  ['/explanation', 'Explain', BookOpen], ['/documentation', 'Docs', FileText], ['/about', 'About', Info],
];
const models = ['gemini-3.5-flash-lite', 'gemini-3.1-flash-lite', 'gemini-3.8-flash', 'gemini-3.5-flash'];

export default function Sidebar() {
  const { code, setCode, apiKey, setApiKey, model, setModel, clearAllResults, analysisResult, refactorResult, readmeResult, docstringResult } = useApp();
  const [open, setOpen] = useState(false);
  const [key, setKey] = useState(apiKey);
  const [selection, setSelection] = useState(model);
  const [saved, setSaved] = useState(false);
  const availableModels = [...new Set([...models, model].filter(Boolean))];
  return (
    <header className="top-header">
      <div className="brand-row">
        <Link to="/" className="brand"><span className="brand-mark"><Code2 size={23} /></span><span>CodeMate <strong>AI</strong></span></Link>
        <span className="brand-caption">A little clarity for every line.</span>
        <button className="settings-toggle" aria-label="Project settings" aria-expanded={open} aria-controls="project-settings" onClick={() => { setOpen(!open); setKey(apiKey); setSelection(model); setSaved(false); }}><Settings size={18} /><span>Settings</span></button>
      </div>
      <nav className="top-nav" aria-label="Main navigation">
        {items.map(([to, label, Icon]) => {
          const badge = to === '/analysis' && analysisResult ? `${analysisResult.health_score}%` : ((to === '/refactoring' && refactorResult?.success) || (to === '/documentation' && (readmeResult?.success || docstringResult?.success))) ? '✓' : null;
          return <NavLink key={to} to={to} end={to === '/'} className={({ isActive }) => `top-nav-link${isActive ? ' active' : ''}`}><Icon size={17} /><span>{label}</span>{badge && <small>{badge}</small>}</NavLink>;
        })}
      </nav>
      {open && <section className="settings-panel card" id="project-settings" aria-label="Project settings" onKeyDown={e => { if (e.key === 'Escape') setOpen(false); }}>
        <div className="settings-heading"><h2>Project settings</h2><button aria-label="Close settings" onClick={() => setOpen(false)}><X size={20} /></button></div>
        <form onSubmit={e => { e.preventDefault(); setApiKey(key); setModel(selection); setSaved(true); }}>
          <label htmlFor="ai-model">Active model</label><select id="ai-model" value={selection} onChange={e => { setSelection(e.target.value); setSaved(false); }}>{availableModels.map(m => <option key={m}>{m}</option>)}</select>
          <label htmlFor="api-key">Gemini API key</label><input id="api-key" type="password" value={key} onChange={e => { setKey(e.target.value); setSaved(false); }} placeholder="Uses server key if empty" />
          <button className="neo-button primary" type="submit">Apply settings</button><span role="status">{saved ? ' Settings saved' : ''}</span>
        </form>
        <div className="session-controls"><span>{code.trim() ? code.split('\n').length : 0} lines in workspace</span><button onClick={() => setCode('')}>Clear code</button><button onClick={clearAllResults}>Reset results</button></div>
      </section>}
    </header>
  );
}
