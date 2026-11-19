// API health status banner
import { Wifi, WifiOff, Loader } from 'lucide-react';

export default function HealthBanner({ status }) {
  // status: 'online' | 'offline' | 'checking'
  if (status === 'checking') {
    return (
      <div className="flex items-center gap-2 text-xs text-muted px-3 py-2 bg-gray-50 rounded-lg border border-border mb-4">
        <Loader size={12} className="animate-spin" />
        Connecting to backend…
      </div>
    );
  }
  if (status === 'online') {
    return (
      <div className="flex items-center gap-2 text-xs text-green-700 px-3 py-2 bg-green-50 rounded-lg border border-green-200 mb-4">
        <Wifi size={12} />
        Backend connected — API ready
      </div>
    );
  }
  return (
    <div className="flex items-center gap-2 text-xs text-red-700 px-3 py-2 bg-red-50 rounded-lg border border-red-200 mb-4">
      <WifiOff size={12} />
      Backend offline — start FastAPI server on port 8000
    </div>
  );
}
