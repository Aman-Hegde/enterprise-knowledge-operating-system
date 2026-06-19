import { Maximize2, RotateCcw } from 'lucide-react'
import { useEffect, useMemo, useRef, useState } from 'react'
import ForceGraph2D from 'react-force-graph-2d'

const SAMPLE_GRAPH = {
  nodes: [
    { id: 'Aman Hegde' },
    { id: 'Python' },
    { id: 'FastAPI' },
    { id: 'React' },
    { id: 'NeuroSphere AI' },
    { id: 'Credit Card Fraud Detection' },
  ],
  links: [
    { source: 'Aman Hegde', target: 'Python' },
    { source: 'Aman Hegde', target: 'FastAPI' },
    { source: 'Aman Hegde', target: 'React' },
    { source: 'Aman Hegde', target: 'NeuroSphere AI' },
    { source: 'Aman Hegde', target: 'Credit Card Fraud Detection' },
  ],
}

function KnowledgeGraph() {
  const containerRef = useRef(null)
  const graphRef = useRef(null)
  const [size, setSize] = useState({ width: 700, height: 360 })

  // The graph library mutates node positions, so each component gets its own copy.
  const graphData = useMemo(
    () => ({
      nodes: SAMPLE_GRAPH.nodes.map((node) => ({ ...node })),
      links: SAMPLE_GRAPH.links.map((link) => ({ ...link })),
    }),
    [],
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

  function drawNode(node, context, globalScale) {
    const isMainEntity = node.id === 'Aman Hegde'
    const radius = isMainEntity ? 8 : 6
    const fontSize = Math.max(11 / globalScale, 3)

    context.beginPath()
    context.arc(node.x, node.y, radius, 0, 2 * Math.PI)
    context.fillStyle = isMainEntity ? '#36c7a0' : '#67a9ff'
    context.fill()
    context.strokeStyle = isMainEntity ? '#86ead0' : '#a7cfff'
    context.lineWidth = 1.2 / globalScale
    context.stroke()

    context.font = `600 ${fontSize}px Inter, sans-serif`
    context.textAlign = 'center'
    context.textBaseline = 'top'
    context.fillStyle = '#e8edf3'
    context.fillText(node.id, node.x, node.y + radius + 3 / globalScale)
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
        <ForceGraph2D
          ref={graphRef}
          width={size.width}
          height={size.height}
          graphData={graphData}
          backgroundColor="#0b1015"
          linkColor={() => '#3b4a58'}
          linkWidth={1.2}
          linkDirectionalArrowLength={4}
          linkDirectionalArrowRelPos={0.92}
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
