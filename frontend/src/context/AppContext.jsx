// AppContext.jsx — Global persistent state for CodeMate AI
// Keeps code, analysis, refactored code, explanations, and documentation
// intact across tab switches and page reloads.

import { createContext, useContext, useState } from 'react';

const AppContext = createContext(null);

export function AppProvider({ children }) {
  // 1. Python source code
  const [code, setCodeState] = useState(() => {
    return localStorage.getItem('cm_code') || localStorage.getItem('codemate_code') || '';
  });
  const setCode = (val) => {
    const next = val ?? '';
    setCodeState(next);
    localStorage.setItem('cm_code', next);
    localStorage.setItem('codemate_code', next);
  };

  // 2. AI Refactoring result (original code, refactored code, diff, explanation, delta)
  const [refactorResult, setRefactorResultState] = useState(() => {
    try {
      const saved = localStorage.getItem('cm_refactor_result');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const setRefactorResult = (val) => {
    setRefactorResultState(val);
    if (val) localStorage.setItem('cm_refactor_result', JSON.stringify(val));
    else localStorage.removeItem('cm_refactor_result');
  };

  // 3. Code Analysis result (health score, syntax, issues, metrics, black)
  const [analysisResult, setAnalysisResultState] = useState(() => {
    try {
      const saved = localStorage.getItem('cm_analysis_result');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const setAnalysisResult = (val) => {
    setAnalysisResultState(val);
    if (val) localStorage.setItem('cm_analysis_result', JSON.stringify(val));
    else localStorage.removeItem('cm_analysis_result');
  };

  // 4. Code Explanation result (markdown breakdown, analogy, execution flow)
  const [explanationResult, setExplanationResultState] = useState(() => {
    try {
      const saved = localStorage.getItem('cm_explanation_result');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const setExplanationResult = (val) => {
    setExplanationResultState(val);
    if (val) localStorage.setItem('cm_explanation_result', JSON.stringify(val));
    else localStorage.removeItem('cm_explanation_result');
  };

  // 5. Documentation results: README
  const [readmeResult, setReadmeResultState] = useState(() => {
    try {
      const saved = localStorage.getItem('cm_readme_result');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const setReadmeResult = (val) => {
    setReadmeResultState(val);
    if (val) localStorage.setItem('cm_readme_result', JSON.stringify(val));
    else localStorage.removeItem('cm_readme_result');
  };

  // Documentation results: Docstrings
  const [docstringResult, setDocstringResultState] = useState(() => {
    try {
      const saved = localStorage.getItem('cm_docstring_result');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const setDocstringResult = (val) => {
    setDocstringResultState(val);
    if (val) localStorage.setItem('cm_docstring_result', JSON.stringify(val));
    else localStorage.removeItem('cm_docstring_result');
  };

  // 6. User API Key override
  const [apiKey, setApiKeyState] = useState(() => {
    return localStorage.getItem('codemate_apikey') || '';
  });
  const setApiKey = (k) => {
    setApiKeyState(k);
    localStorage.setItem('codemate_apikey', k || '');
  };

  // 7. User Model override
  const [model, setModelState] = useState(() => {
    return localStorage.getItem('codemate_model') || '';
  });
  const setModel = (m) => {
    setModelState(m);
    localStorage.setItem('codemate_model', m || '');
  };

  // Helper to clear everything
  const clearAllResults = () => {
    setRefactorResult(null);
    setAnalysisResult(null);
    setExplanationResult(null);
    setReadmeResult(null);
    setDocstringResult(null);
  };

  return (
    <AppContext.Provider
      value={{
        code,
        setCode,
        refactorResult,
        setRefactorResult,
        analysisResult,
        setAnalysisResult,
        explanationResult,
        setExplanationResult,
        readmeResult,
        setReadmeResult,
        docstringResult,
        setDocstringResult,
        apiKey,
        setApiKey,
        model,
        setModel,
        clearAllResults,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return ctx;
}
