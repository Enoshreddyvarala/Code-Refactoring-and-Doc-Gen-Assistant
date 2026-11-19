import { Link } from 'react-router-dom';
import { Code2, ScanLine, Wand2, BookOpen, FileText, Check, Sparkles } from 'lucide-react';
const features = [
  { icon: ScanLine, title: 'Find the rough edges.', text: 'Spot Python code issues with AST analysis, quality checks, and a clear health score.', to: '/analysis', label: 'Explore analysis' },
  { icon: Wand2, title: 'Make every line better.', text: 'Refactor with Gemini, compare the changes, and review a cleaner version of your code.', to: '/refactoring', label: 'Explore refactoring' },
  { icon: BookOpen, title: 'Understand the why.', text: 'Turn unfamiliar code into approachable explanations, one step at a time.', to: '/explanation', label: 'Explore explanations' },
  { icon: FileText, title: 'Let your code speak.', text: 'Create README files and Python docstrings that make your work easier to share.', to: '/documentation', label: 'Explore documentation' },
];
export default function Dashboard() {
  return <div className="intro-page">
    <section className="intro-hero">
      <div className="hero-copy">
        <span className="eyebrow"><Sparkles size={15} /> YOUR PYTHON PROJECT, REIMAGINED</span>
        <h1>Good code.<br /><span>Even better</span><br />understood.</h1>
        <p>Meet CodeMate AI. Your companion for turning Python code into cleaner logic, clearer explanations, and documentation that makes sense.</p>
        <div className="hero-actions"><Link className="neo-button primary" to="/workspace"><Code2 size={18} />Open workspace</Link><a className="neo-button" href="#discover">Discover the project</a></div>
        <div className="hero-note"><span>Built for Python</span><span>Powered by Gemini</span></div>
      </div>
      <div className="hero-visual" aria-label="Illustrative example of code refactoring">
        <div className="preview-title"><span className="preview-icon"><Code2 size={21} /></span><div><strong>A little less clutter.</strong><span>A lot more clarity.</span></div><span className="example-tag">EXAMPLE</span></div>
        <div className="code-preview before"><div className="code-caption"><span>BEFORE</span><span>calculate.py</span></div><pre><code>{'def calc(x):\n    s=0\n    for i in x:\n        s=s+i\n    return s'}</code></pre></div>
        <div className="transform-label"><Wand2 size={16} /><span>A clearer way to write it</span></div>
        <div className="code-preview after"><div className="code-caption"><span>AFTER</span><Check size={15} /></div><pre><code><span className="code-purple">def </span><span className="code-blue">calculate_total</span>{'(values):\n'}<span className="code-comment">{'    """Return the sum of values."""\n'}</span><span className="code-purple">{'    return '}</span>{'sum(values)'}</code></pre></div>
        <div className="preview-footer"><Check size={15} /> Descriptive names <span>·</span> Readable logic <span>·</span> Useful docs</div>
      </div>
    </section>
    <section className="discover-section" id="discover">
      <div className="section-heading"><div><span className="eyebrow">FROM FIRST DRAFT TO CLEARER CODE</span><h2>One companion. A more thoughtful workflow.</h2></div><p>Spend less time untangling your code.<br />Spend more time understanding it.</p></div>
      <div className="feature-grid">{features.map(({ icon: Icon, title, text, to, label }) => <article className="feature-card card" key={to}><span className="feature-icon"><Icon size={23} /></span><h3>{title}</h3><p>{text}</p><Link to={to}>{label}</Link></article>)}</div>
    </section>
    <section className="workflow-section"><div><span className="eyebrow">SIMPLE BY DESIGN</span><h2>Bring your code.<br />Leave with clarity.</h2><Link className="neo-button" to="/workspace">Start with your Python code</Link></div><ol><li><strong>Add your Python code</strong><p>Paste a snippet, upload a .py file, or try a built-in sample.</p></li><li><strong>Explore and improve</strong><p>Analyze quality, review AI suggestions, and understand the changes.</p></li><li><strong>Document and take it with you</strong><p>Generate explanations and docs, then download the outputs you need.</p></li></ol></section>
    <footer className="intro-footer"><span>CodeMate AI</span><span>Built to make code a little more human.</span><Link to="/about">About the project</Link></footer>
  </div>;
}
