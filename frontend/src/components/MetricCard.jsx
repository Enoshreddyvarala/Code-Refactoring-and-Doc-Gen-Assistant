// Metric stat card component
export default function MetricCard({ title, value, subtitle, color = 'accent', icon: Icon }) {
  const colorMap = {
    accent: 'text-accent bg-blue-50',
    green:  'text-green-600 bg-green-50',
    amber:  'text-amber-600 bg-amber-50',
    red:    'text-red-600 bg-red-50',
    primary:'text-primary bg-primary-50',
  };
  return (
    <div className="card p-5">
      <div className="flex items-start justify-between">
        <div>
          <div className="text-xs font-semibold text-muted uppercase tracking-wide mb-1">{title}</div>
          <div className="text-2xl font-bold text-textPrimary">{value}</div>
          {subtitle && <div className="text-xs text-muted mt-0.5">{subtitle}</div>}
        </div>
        {Icon && (
          <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${colorMap[color] || colorMap.accent}`}>
            <Icon size={18} />
          </div>
        )}
      </div>
    </div>
  );
}
