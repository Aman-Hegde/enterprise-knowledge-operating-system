function StatusBadge({ status }) {
  const label = status === 'checking' ? 'Checking' : status

  return (
    <span className={`status-badge status-badge--${status}`}>
      <span className="status-dot" />
      {label}
    </span>
  )
}

export default StatusBadge
