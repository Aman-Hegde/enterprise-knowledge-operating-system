import {
  ArrowRight,
  Database,
  FileText,
  Network,
  Server,
} from 'lucide-react'
import PageHeader from '../components/PageHeader'
import StatusBadge from '../components/StatusBadge'

function Dashboard({ backendStatus, lastUpload, onNavigate }) {
  const services = [
    {
      name: 'FastAPI',
      detail: 'Application API',
      icon: Server,
      status: backendStatus,
    },
    {
      name: 'Qdrant',
      detail: 'In-memory vectors',
      icon: Database,
      status: lastUpload ? 'online' : 'idle',
    },
    {
      name: 'Neo4j',
      detail: 'Knowledge graph',
      icon: Network,
      status: 'online',
    },
  ]

  return (
    <div className="page">
      <PageHeader
        eyebrow="Overview"
        title="Knowledge Workspace"
        description="System status and indexed document activity."
      />

      <section className="metric-grid" aria-label="Workspace summary">
        <article className="metric-card">
          <span>Documents indexed</span>
          <strong>{lastUpload ? '1' : '0'}</strong>
          <small>Current memory session</small>
        </article>
        <article className="metric-card">
          <span>Vector chunks</span>
          <strong>{lastUpload?.total_chunks ?? '0'}</strong>
          <small>Qdrant collection</small>
        </article>
        <article className="metric-card metric-card--accent">
          <span>Retrieval mode</span>
          <strong>GraphRAG</strong>
          <small>Vector + graph context</small>
        </article>
      </section>

      <div className="dashboard-grid">
        <section className="panel">
          <div className="panel-heading">
            <div>
              <span className="section-label">Services</span>
              <h2>Runtime status</h2>
            </div>
          </div>
          <div className="service-list">
            {services.map(({ name, detail, icon: Icon, status }) => (
              <div className="service-row" key={name}>
                <div className="service-icon">
                  <Icon size={18} />
                </div>
                <div className="service-copy">
                  <strong>{name}</strong>
                  <span>{detail}</span>
                </div>
                <StatusBadge status={status} />
              </div>
            ))}
          </div>
        </section>

        <section className="panel latest-document">
          <div className="panel-heading">
            <div>
              <span className="section-label">Index</span>
              <h2>Latest document</h2>
            </div>
            <FileText size={19} />
          </div>

          {lastUpload ? (
            <div className="document-summary">
              <strong>{lastUpload.filename}</strong>
              <dl>
                <div>
                  <dt>Characters</dt>
                  <dd>{lastUpload.total_characters.toLocaleString()}</dd>
                </div>
                <div>
                  <dt>Chunks</dt>
                  <dd>{lastUpload.total_chunks}</dd>
                </div>
              </dl>
              <button
                className="text-button"
                type="button"
                onClick={() => onNavigate('chat')}
              >
                Open GraphRAG
                <ArrowRight size={16} />
              </button>
            </div>
          ) : (
            <div className="empty-state">
              <FileText size={25} />
              <strong>No document indexed</strong>
              <button
                className="text-button"
                type="button"
                onClick={() => onNavigate('upload')}
              >
                Upload PDF
                <ArrowRight size={16} />
              </button>
            </div>
          )}
        </section>
      </div>
    </div>
  )
}

export default Dashboard
