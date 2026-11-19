// Download button — creates a file and triggers browser download
import { Download } from 'lucide-react';

export default function DownloadButton({ content, filename, label = 'Download', disabled = false }) {
  const handleDownload = () => {
    if (!content) return;
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <button
      onClick={handleDownload}
      disabled={disabled || !content}
      className="inline-flex items-center gap-2 px-4 py-2 bg-blue-700 text-white text-sm font-medium rounded-lg shadow-md hover:bg-blue-800 disabled:bg-slate-300 disabled:text-slate-700 disabled:shadow-none disabled:cursor-not-allowed transition-colors"
    >
      <Download size={14} />
      {label}
    </button>
  );
}

