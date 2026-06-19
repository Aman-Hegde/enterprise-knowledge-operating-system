import { useEffect, useState } from 'react'
import AppShell from './components/AppShell'
import Dashboard from './pages/Dashboard'
import DocumentUpload from './pages/DocumentUpload'
import GraphRAGChat from './pages/GraphRAGChat'
import { getHealth } from './services/api'
import './styles/global.css'

const VALID_PAGES = ['dashboard', 'upload', 'chat']

function App() {
  const initialPage = window.location.hash.replace('#', '')
  const [activePage, setActivePage] = useState(
    VALID_PAGES.includes(initialPage) ? initialPage : 'dashboard',
  )
  const [backendStatus, setBackendStatus] = useState('checking')
  const [lastUpload, setLastUpload] = useState(() => {
    const savedUpload = sessionStorage.getItem('ekos-last-upload')
    return savedUpload ? JSON.parse(savedUpload) : null
  })

  useEffect(() => {
    // The dashboard checks the API once when the application opens.
    getHealth()
      .then(() => setBackendStatus('online'))
      .catch(() => setBackendStatus('offline'))
  }, [])

  useEffect(() => {
    function handleHashChange() {
      const nextPage = window.location.hash.replace('#', '')
      if (VALID_PAGES.includes(nextPage)) setActivePage(nextPage)
    }

    window.addEventListener('hashchange', handleHashChange)
    return () => window.removeEventListener('hashchange', handleHashChange)
  }, [])

  function navigate(page) {
    setActivePage(page)
    window.location.hash = page
  }

  function handleUploadComplete(upload) {
    setLastUpload(upload)
    sessionStorage.setItem('ekos-last-upload', JSON.stringify(upload))
  }

  const pages = {
    dashboard: (
      <Dashboard
        backendStatus={backendStatus}
        lastUpload={lastUpload}
        onNavigate={navigate}
      />
    ),
    upload: <DocumentUpload onUploadComplete={handleUploadComplete} />,
    chat: <GraphRAGChat hasDocument={Boolean(lastUpload)} />,
  }

  return (
    <AppShell
      activePage={activePage}
      backendStatus={backendStatus}
      onNavigate={navigate}
    >
      {pages[activePage]}
    </AppShell>
  )
}

export default App
