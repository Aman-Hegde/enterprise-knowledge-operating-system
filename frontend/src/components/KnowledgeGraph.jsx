import { AlertCircle, LoaderCircle, Maximize2, RotateCcw } from 'lucide-react'
import { useEffect, useMemo, useRef, useState } from 'react'
import ForceGraph2D from 'react-force-graph-2d'

const GRAPH_API_URL = 'http://127.0.0.1:8001/graph/network'
const GRAPH_ERROR_MESSAGE =
  'Unable to load graph data. Make sure Neo4j and FastAPI are running.'

function KnowledgeGraph() {
  const containerRef = useRef(null)
  const graphRef = useRef(null)
  const [size, setSize] = useState({ width: 700, height: 360 })
  const [network, setNetwork] = useState({ nodes: [], links: [] })
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  // The graph library mutates node positions, so each component gets its own copy.
  const graphData = useMemo(
    () => ({
      nodes: network.nodes.map((node) => ({ ...node })),
      links: network.links.map((link) => ({ ...link })),
    }),
    [network],
  )

  useEffect(() => {
    const container = containerRef.current
    if (!container) return undefined

    // ResizeObserver keeps the canvas fitted to desktop and mobile panels.
    const resizeObserver = new ResizeObserver(([entry]) => {
      setSize({
        width: Math.max(entry.contentRect.width, 280),
        height: entry.contentRect.width < 560 ? 300 : 360,
      })
    })

    resizeObserver.observe(container)
    return () => resizeObserver.disconnect()
  }, [])

  useEffect(() => {
    let isMounted = true

    async function loadGraph() {
      try {
        const response = await fetch(GRAPH_API_URL)
        if (!response.ok) throw new Error('Graph API request failed')

        const data = await response.json()
        if (!isMounted) return

        setNetwork({
          nodes: Array.isArray(data.nodes) ? data.nodes : [],
          links: Array.isArray(data.links) ? data.links : [],
        })
      } catch {
        if (isMounted) setError(GRAPH_ERROR_MESSAGE)
      } finally {
        if (isMounted) setIsLoading(false)
      }
    }

    loadGraph()
    return () => {
      isMounted = false
    }
  }, [])

  function drawNode(node, context, globalScale) {
    const isPerson = node.type === 'Person'
    const radius = isPerson ? 8 : 6
    const fontSize = Math.max(11 / globalScale, 3)

    context.beginPath()
    context.arc(node.x, node.y, radius, 0, 2 * Math.PI)
    context.fillStyle = isPerson ? '#36c7a0' : '#67a9ff'
    context.fill()
    context.strokeStyle = isPerson ? '#86ead0' : '#a7cfff'
    context.lineWidth = 1.2 / globalScale
    context.stroke()

    context.font = `600 ${fontSize}px Inter, sans-serif`
    context.textAlign = 'center'
    context.textBaseline = 'top'
    context.fillStyle = '#e8edf3'
    context.fillText(node.id, node.x, node.y + radius + 3 / globalScale)
  }

  function drawLinkLabel(link, context, globalScale) {
    const source = link.source
    const target = link.target
    if (typeof source !== 'object' || typeof target !== 'object') return

    const fontSize = Math.max(9 / globalScale, 2.5)
    const x = (source.x + target.x) / 2
    const y = (source.y + target.y) / 2

    context.font = `600 ${fontSize}px Inter, sans-serif`
    context.textAlign = 'center'
    context.textBaseline = 'middle'
    context.fillStyle = '#83909e'
    context.fillText(link.label || '', x, y)
  }

  function fitGraph() {
    graphRef.current?.zoomToFit(450, 48)
  }

  function resetGraph() {
    graphRef.current?.d3ReheatSimulation()
    window.setTimeout(fitGraph, 250)
  }

  return (
    <section className="knowledge-graph-panel">
      <header className="knowledge-graph-header">
        <div>
          <span className="section-label">Relationship map</span>
          <h3>Knowledge Graph</h3>
        </div>
        <div className="graph-actions">
          <button
            className="icon-button"
            type="button"
            title="Reset graph"
            aria-label="Reset graph"
            onClick={resetGraph}
          >
            <RotateCcw size={16} />
          </button>
          <button
            className="icon-button"
            type="button"
            title="Fit graph to panel"
            aria-label="Fit graph to panel"
            onClick={fitGraph}
          >
            <Maximize2 size={16} />
          </button>
        </div>
      </header>

      <div className="knowledge-graph-canvas" ref={containerRef}>
        {isLoading && (
          <div className="graph-feedback">
            <LoaderCircle className="spin" size={20} />
            <span>Loading Neo4j network</span>
          </div>
        )}

        {error && (
          <div className="graph-feedback graph-feedback--error">
            <AlertCircle size={20} />
            <span>{error}</span>
          </div>
        )}

        {!isLoading && !error && graphData.nodes.length === 0 && (
          <div className="graph-feedback">
            <span>No graph relationships are available yet.</span>
          </div>
        )}

        {!isLoading && !error && graphData.nodes.length > 0 && (
          <ForceGraph2D
            ref={graphRef}
            width={size.width}
            height={size.height}
            graphData={graphData}
            backgroundColor="#0b1015"
            linkColor={() => '#3b4a58'}
            linkWidth={1.2}
            linkLabel="label"
            linkDirectionalArrowLength={4}
            linkDirectionalArrowRelPos={0.92}
            linkCanvasObjectMode={() => 'after'}
            linkCanvasObject={drawLinkLabel}
            nodeCanvasObject={drawNode}
            nodePointerAreaPaint={(node, color, context) => {
              context.fillStyle = color
              context.beginPath()
              context.arc(node.x, node.y, 12, 0, 2 * Math.PI)
              context.fill()
            }}
            cooldownTicks={80}
            onEngineStop={fitGraph}
          />
        )}
      </div>

      <footer className="knowledge-graph-legend">
        <span>
          <i className="legend-dot legend-dot--person" />
          Person
        </span>
        <span>
          <i className="legend-dot legend-dot--related" />
          Related entity
        </span>
      </footer>
    </section>
  )
}

export default KnowledgeGraph
