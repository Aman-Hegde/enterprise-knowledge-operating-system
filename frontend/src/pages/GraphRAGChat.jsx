import {
  Bot,
  ChevronDown,
  ChevronUp,
  LoaderCircle,
  Network,
  Search,
  Send,
  Sparkles,
} from 'lucide-react'
import { useState } from 'react'
import KnowledgeGraph from '../components/KnowledgeGraph'
import PageHeader from '../components/PageHeader'
import { askGraphRAG } from '../services/api'

function GraphRAGChat({ hasDocument }) {
  const [question, setQuestion] = useState('')
  const [response, setResponse] = useState(null)
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [expanded, setExpanded] = useState({
    vector: true,
    graph: true,
  })

  async function handleSubmit(event) {
    event.preventDefault()
    const cleanQuestion = question.trim()
    if (!cleanQuestion) return

    setIsLoading(true)
    setError('')

    try {
      const answer = await askGraphRAG(cleanQuestion)
      setResponse(answer)
    } catch (requestError) {
      setError(requestError.message)
    } finally {
      setIsLoading(false)
    }
  }

  function toggleSection(section) {
    setExpanded((current) => ({
      ...current,
      [section]: !current[section],
    }))
  }

  return (
    <div className="page chat-page">
      <PageHeader
        eyebrow="Intelligence"
        title="GraphRAG Chat"
        description="Vector retrieval with Neo4j relationship context."
      />

      <section className="chat-workspace">
        <div className="chat-transcript">
          {!response && !isLoading && (
            <div className="chat-empty">
              <span className="chat-empty-icon">
                <Sparkles size={25} />
              </span>
              <strong>Knowledge query</strong>
              <span>
                {hasDocument
                  ? 'The current document index is ready.'
                  : 'Upload a PDF to initialize the document index.'}
              </span>
            </div>
          )}

          {response && (
            <>
              <div className="message message--user">
                <div className="message-avatar">
                  <span>Y</span>
                </div>
                <div>
                  <span className="message-label">You</span>
                  <p>{response.question}</p>
                </div>
              </div>

              <div className="message message--assistant">
                <div className="message-avatar">
                  <Bot size={18} />
                </div>
                <div>
                  <span className="message-label">EKOS</span>
                  <p>{response.answer}</p>
                </div>
              </div>

              <KnowledgeGraph />

              <div className="context-grid">
                <ContextSection
                  icon={Search}
                  title="Vector Context"
                  count={response.vector_context.length}
                  isExpanded={expanded.vector}
                  onToggle={() => toggleSection('vector')}
                >
                  {response.vector_context.map((context, index) => (
                    <article
                      className="context-item"
                      key={`${context.filename}-${context.chunk_index}-${index}`}
                    >
                      <span>
                        {context.filename} · Chunk {context.chunk_index + 1}
                      </span>
                      <p>{context.text}</p>
                    </article>
                  ))}
                </ContextSection>

                <ContextSection
                  icon={Network}
                  title="Graph Context"
                  isExpanded={expanded.graph}
                  onToggle={() => toggleSection('graph')}
                >
                  <pre className="graph-context">{response.graph_context}</pre>
                </ContextSection>
              </div>
            </>
          )}

          {isLoading && (
            <div className="loading-state">
              <LoaderCircle className="spin" size={21} />
              <span>Retrieving context</span>
            </div>
          )}
        </div>

        {error && <div className="alert alert--error chat-error">{error}</div>}

        <form className="chat-composer" onSubmit={handleSubmit}>
          <textarea
            value={question}
            rows="2"
            placeholder="Ask about people, skills, projects, or relationships"
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault()
                event.currentTarget.form?.requestSubmit()
              }
            }}
          />
          <button
            className="send-button"
            type="submit"
            aria-label="Ask GraphRAG"
            disabled={!question.trim() || isLoading}
          >
            {isLoading ? (
              <LoaderCircle className="spin" size={19} />
            ) : (
              <Send size={19} />
            )}
          </button>
        </form>
      </section>
    </div>
  )
}

function ContextSection({
  children,
  count,
  icon: Icon,
  isExpanded,
  onToggle,
  title,
}) {
  return (
    <section className="context-section">
      <button className="context-header" type="button" onClick={onToggle}>
        <span>
          <Icon size={17} />
          {title}
          {count !== undefined && <small>{count}</small>}
        </span>
        {isExpanded ? <ChevronUp size={17} /> : <ChevronDown size={17} />}
      </button>
      {isExpanded && <div className="context-body">{children}</div>}
    </section>
  )
}

export default GraphRAGChat
