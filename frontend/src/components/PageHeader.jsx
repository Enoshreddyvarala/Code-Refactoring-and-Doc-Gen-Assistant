// Page header with title and description
export default function PageHeader({ title, description, icon: Icon }) {
  return (
    <div className="mb-6">
      <div className="flex items-center gap-3 mb-1">
        {Icon && (
          <div className="w-8 h-8 bg-primary-50 rounded-lg flex items-center justify-center">
            <Icon size={18} className="text-accent" />
          </div>
        )}
        <h1 className="text-xl font-bold text-textPrimary">{title}</h1>
      </div>
      {description && (
        <p className="text-sm text-muted ml-11">{description}</p>
      )}
    </div>
  );
}
