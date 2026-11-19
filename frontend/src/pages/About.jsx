// About Project page — static info on architecture, tech stack, security
import { Info, Code2, Shield, Zap, BookOpen, FileText } from 'lucide-react';
import PageHeader from '../components/PageHeader';

const TECH_STACK = [
  { layer: 'Frontend',  techs: ['React.js 18', 'Vite', 'Tailwind CSS', 'React Router', 'Monaco Editor', 'Lucide React', 'React Markdown'] },
  { layer: 'Backend',   techs: ['Python 3.11+', 'FastAPI', 'Uvicorn', 'Pydantic', 'python-dotenv'] },
  { layer: 'AI / ML',   techs: ['Google Gemini API', 'google-genai SDK', 'Configurable model (env var)'] },
  { layer: 'Analysis',  techs: ['Python AST', 'Black', 'difflib'] },
  { layer: 'Testing',   techs: ['Pytest', 'FastAPI TestClient'] },
];

const FEATURES = [
  { icon: Code2,    title: 'Code Analysis',         desc: 'AST-based quality analysis with health scoring, issue detection, and Black formatting checks.' },
  { icon: Zap,      title: 'AI Refactoring',         desc: 'Google Gemini rewrites your code to follow PEP 8 while preserving original functionality.' },
  { icon: BookOpen, title: 'Code Explanation',       desc: 'Beginner-friendly breakdowns with real-world analogies, step-by-step execution guides, and function explanations.' },
  { icon: FileText, title: 'Documentation',          desc: 'Auto-generate README.md and PEP 257 docstrings for any Python code.' },
  { icon: Shield,   title: 'Security',               desc: 'Gemini API keys stay on the backend only. User code is never executed directly in the server process.' },
];

export default function About() {
  return (
    <div className="p-8 max-w-4xl mx-auto">
      <PageHeader
        title="About CodeMate AI"
        description="An AI-powered Python code refactoring and documentation assistant built as a learning project"
        icon={Info}
      />

      {/* Overview card */}
      <div className="card p-6 mb-5">
        <h2 className="text-base font-bold text-primary mb-2">Project Overview</h2>
        <p className="text-sm text-textSecondary leading-relaxed">
          <strong>CodeMate AI</strong> is a full-stack AI developer productivity tool designed for beginner Python developers.
          Upload or paste Python code and instantly analyze quality, refactor it with Google Gemini,
          get a plain-English explanation, and auto-generate documentation — all in a clean, modern interface.
        </p>
        <p className="text-sm text-textSecondary mt-3 leading-relaxed">
          Originally built with Streamlit, CodeMate AI was migrated to a <strong>React.js + FastAPI</strong> architecture
          to provide a more professional user experience, cleaner separation of concerns, and better extensibility.
          The original Streamlit app is preserved in the <code className="bg-gray-100 px-1 rounded text-xs">legacy_streamlit/</code> folder.
        </p>
      </div>

      {/* Features */}
      <div className="card p-6 mb-5">
        <h2 className="text-base font-bold text-primary mb-4">Features</h2>
        <div className="space-y-4">
          {FEATURES.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="flex gap-3">
              <div className="w-8 h-8 bg-accent/10 rounded-lg flex items-center justify-center flex-shrink-0">
                <Icon size={15} className="text-accent" />
              </div>
              <div>
                <div className="text-sm font-semibold text-textPrimary">{title}</div>
                <div className="text-xs text-muted mt-0.5">{desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Tech stack */}
      <div className="card p-6 mb-5">
        <h2 className="text-base font-bold text-primary mb-4">Technology Stack</h2>
        <div className="space-y-3">
          {TECH_STACK.map(({ layer, techs }) => (
            <div key={layer} className="flex gap-3">
              <div className="w-24 flex-shrink-0 text-xs font-semibold text-muted uppercase tracking-wide pt-0.5">{layer}</div>
              <div className="flex flex-wrap gap-1.5">
                {techs.map((t) => (
                  <span key={t} className="text-xs bg-primary-50 text-primary px-2 py-0.5 rounded-full border border-primary/10">{t}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Architecture */}
      <div className="card p-6 mb-5">
        <h2 className="text-base font-bold text-primary mb-3">Architecture</h2>
        <pre className="text-xs font-mono bg-gray-50 border border-border rounded-lg p-4 overflow-auto">{`
codemate-ai/
├── frontend/               ← React.js (Vite + Tailwind)
│   └── src/
│       ├── components/     ← Reusable UI components
│       ├── pages/          ← 7 page views
│       └── services/api.js ← All backend API calls
│
├── backend/                ← FastAPI Python server
│   ├── main.py             ← App entry point + CORS
│   ├── routes/             ← 7 API route modules
│   ├── services/           ← Business logic (AI, analysis)
│   ├── prompts/            ← Gemini prompt templates
│   ├── schemas/            ← Pydantic models
│   └── utils/              ← Helpers (file, samples)
│
└── legacy_streamlit/       ← Original Streamlit app (preserved)
`.trim()}</pre>
      </div>

      {/* Security note */}
      <div className="card p-5 border-l-4 border-l-amber-400 bg-amber-50">
        <div className="flex gap-2">
          <Shield size={16} className="text-amber-600 flex-shrink-0 mt-0.5" />
          <div>
            <div className="text-sm font-semibold text-amber-800 mb-1">Security Note</div>
            <ul className="text-xs text-amber-700 space-y-1 list-disc pl-4">
              <li>Gemini API keys are <strong>never sent to the React frontend</strong> or included in bundled JavaScript.</li>
              <li>User-uploaded code is <strong>never executed directly</strong> in the server process — only parsed by AST and Black.</li>
              <li>Test execution runs in an isolated subprocess with a strict timeout.</li>
              <li>No user data is stored or logged beyond the current session.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
