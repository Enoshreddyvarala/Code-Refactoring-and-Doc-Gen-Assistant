// Error message display
import { AlertCircle } from 'lucide-react';

export default function ErrorMessage({ message, onDismiss }) {
  if (!message) return null;
  return (
    <div className="flex items-start gap-3 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700 mb-4">
      <AlertCircle size={16} className="flex-shrink-0 mt-0.5" />
      <span className="flex-1">{message}</span>
      {onDismiss && (
        <button onClick={onDismiss} className="text-red-400 hover:text-red-600 ml-auto text-xs font-medium">
          Dismiss
        </button>
      )}
    </div>
  );
}
