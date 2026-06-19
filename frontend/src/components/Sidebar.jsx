import {
  Activity,
  FileUp,
  LayoutDashboard,
  MessageSquareText,
  Network,
} from 'lucide-react'

const navigation = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'upload', label: 'Document Upload', icon: FileUp },
  { id: 'chat', label: 'GraphRAG Chat', icon: MessageSquareText },
]

function Sidebar({ activePage, backendStatus, isOpen, onNavigate }) {
  return (
    <aside className={`sidebar ${isOpen ? 'sidebar--open' : ''}`}>
      <div className="brand">
        <div className="brand-mark" aria-hidden="true">
          <Network size={20} />
        </div>
        <div>
          <strong>EKOS</strong>
          <span>Knowledge OS</span>
        </div>
      </div>

      <nav className="sidebar-nav" aria-label="Primary navigation">
        <span className="nav-label">Workspace</span>
        {navigation.map(({ id, label, icon: Icon }) => (
          <button
            className={`nav-item ${activePage === id ? 'nav-item--active' : ''}`}
            type="button"
            key={id}
            onClick={() => onNavigate(id)}
          >
            <Icon size={18} />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-status">
        <Activity size={17} />
        <div>
          <span>FastAPI</span>
          <strong className={`status-text status-text--${backendStatus}`}>
            {backendStatus === 'checking' ? 'Checking' : backendStatus}
          </strong>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
