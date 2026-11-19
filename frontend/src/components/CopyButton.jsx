// CopyButton.jsx — Interactive copy-to-clipboard button with visual feedback
import { useState } from 'react';
import { Copy, Check } from 'lucide-react';

export default function CopyButton({ text, label = 'Copy', className = '' }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async (e) => {
    e.stopPropagation();
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  return (
    <button
      onClick={handleCopy}
      disabled={!text}
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-md transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed ${
        copied
          ? 'bg-green-100 text-green-800 border border-green-300'
          : 'bg-white/80 hover:bg-white text-textSecondary hover:text-textPrimary border border-border shadow-xs hover:shadow-sm'
      } ${className}`}
      title="Copy to clipboard"
    >
      {copied ? (
        <>
          <Check size={12} className="text-green-600 animate-in fade-in zoom-in-50 duration-150" />
          <span className="text-green-700 font-semibold">Copied!</span>
        </>
      ) : (
        <>
          <Copy size={12} />
          <span>{label}</span>
        </>
      )}
    </button>
  );
}
