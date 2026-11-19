// Severity badge for code issues
export default function IssueBadge({ severity }) {
  const map = {
    Critical: 'badge badge-critical',
    Warning:  'badge badge-warning',
    Info:     'badge badge-info',
    Success:  'badge badge-success',
  };
  return <span className={map[severity] || 'badge badge-info'}>{severity}</span>;
}
