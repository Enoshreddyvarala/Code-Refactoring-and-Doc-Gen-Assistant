// Loading spinner with optional message
export default function LoadingSpinner({ message = 'Processing…' }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 gap-3 text-muted">
      <div className="spinner" />
      <div className="text-sm">{message}</div>
    </div>
  );
}
