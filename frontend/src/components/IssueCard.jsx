// Individual code issue display card
import IssueBadge from './IssueBadge';

export default function IssueCard({ issue }) {
  // issue: { severity, category, message, line, suggestion }
  return (
    <div className="card p-3 mb-2">
      <div className="flex items-start gap-2 flex-wrap">
        <IssueBadge severity={issue.severity} />
        <span className="text-xs font-medium text-muted bg-gray-100 px-2 py-0.5 rounded">
          {issue.category}
        </span>
        {issue.line && (
          <span className="text-xs text-muted">Line {issue.line}</span>
        )}
      </div>
      <div className="text-sm text-textPrimary mt-1.5">{issue.message}</div>
      {issue.suggestion && (
        <div className="text-xs text-muted mt-1 italic">💡 {issue.suggestion}</div>
      )}
    </div>
  );
}
