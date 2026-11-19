// Application routes and shared state.

import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Workspace from './pages/Workspace';
import Analysis from './pages/Analysis';
import Refactoring from './pages/Refactoring';
import Explanation from './pages/Explanation';
import Documentation from './pages/Documentation';
import About from './pages/About';

export default function App() {


  return (
    <AppProvider>
      <BrowserRouter>
        <div className="app-layout">
          <Sidebar />
          <main className="main-content" id="main-content">
            <Routes>
              <Route path="/"               element={<Dashboard />}     />
              <Route path="/workspace"      element={<Workspace />}     />
              <Route path="/analysis"       element={<Analysis />}      />
              <Route path="/refactoring"    element={<Refactoring />}   />
              <Route path="/explanation"    element={<Explanation />}   />
              <Route path="/documentation"  element={<Documentation />} />
              <Route path="/about"          element={<About />}         />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </AppProvider>
  );
}

