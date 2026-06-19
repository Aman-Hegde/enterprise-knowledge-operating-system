import { Menu } from 'lucide-react'
import { useState } from 'react'
import Sidebar from './Sidebar'

function AppShell({ activePage, backendStatus, children, onNavigate }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  function navigate(page) {
    onNavigate(page)
    setSidebarOpen(false)
  }

  return (
    <div className="app-shell">
      <Sidebar
        activePage={activePage}
        backendStatus={backendStatus}
        isOpen={sidebarOpen}
        onNavigate={navigate}
      />

      {sidebarOpen && (
        <button
          className="sidebar-backdrop"
          type="button"
          aria-label="Close navigation"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <main className="main-content">
        <div className="mobile-bar">
          <button
            className="icon-button"
            type="button"
            aria-label="Open navigation"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu size={20} />
          </button>
          <span>EKOS</span>
        </div>
        {children}
      </main>
    </div>
  )
}

export default AppShell
