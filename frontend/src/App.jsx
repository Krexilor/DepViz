// LIBRARIES ---------------------------------------------------------------------------------------------------------------------------------------|
import { useState } from 'react'

// COMPONENTS --------------------------------------------------------------------------------------------------------------------------------------|
import Graph from './components/Graph/Graph.jsx'
import DropZone from './components/DropZone/DropZone.jsx'
import StatsBar from './components/StatsBar/StatsBar.jsx'
import SidePanel from './components/SidePanel/SidePanel.jsx'

// APPPLICATION ------------------------------------------------------------------------------------------------------------------------------------|
export default function App() {
    const [graphData, setGraphData] = useState(null)
    const [selectedNode, setSelectedNode] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    async function handleFileUpload(file) {
        setLoading(true)
        setError(null)
        setGraphData(null)
        setSelectedNode(null)

        const formData = new FormData()
        formData.append('file', file)

        try {
            const res = await fetch('/analyze', {
                method: 'POST',
                body: formData,
            })

            if (!res.ok) {
                const err = await res.json()
                throw new Error(err.detail || 'Analysis failed.')
            }

            const data = await res.json()
            setGraphData(data)

        }
        
        catch (err) {
            setError(err.message)
        }
        
        finally {
            setLoading(false)
        }
    }

    function handleReset() {
        setGraphData(null)
        setSelectedNode(null)
        setError(null)
    }

    return (
        <div className = "app">

            {/* Navigation */}
            <nav className = "app-nav">
                <span className = "app-logo" onClick = {handleReset}>
                    dep<em>viz</em>
                </span>
                <div className = "app-nav-links">
                    <a href = "https://osv.dev" target = "_blank" rel = "noreferrer">osv.dev</a>
                    <a href = "https://github.com/Krexilor/DepViz" target = "_blank" rel = "noreferrer">github</a>
                </div>
            </nav>

            {/* Upload Screen */}
            {!graphData && !loading && (
                <div className  = "app-upload-screen">
                    <div className = "app-hero">
                        <p className = "tag">dependency graph visualizer</p>
                        <h1 className = "app-title">
                            See what's <span>inside</span><br />your project
                        </h1>
                        <p className = "app-subtitle">
                            Upload a dependency file. Get an interactive graph with<br />
                            transitive dependencies and live CVE warnings.
                        </p>
                    </div>
                    <DropZone onUpload = {handleFileUpload} />
                    {error && <p className = "app-error">{error}</p>}
                </div>
            )}

            {/* Loading State */}
            {loading && (
                <div className = "app-loading">
                    <div className = "app-spinner" />
                    <p className = "mono">resolving dependencies...</p>
                </div>
            )}

            {/* Result Screen */}
            {graphData && (
                <div className = "app-results">
                    <StatsBar data = {graphData} onReset = {handleReset} />
                    <div className = "app-graph-layout">
                        <Graph
                            data = {graphData}
                            onSelectNode = {setSelectedNode}
                            selectedNode = {selectedNode}
                        />
                        <SidePanel node = {selectedNode} />
                    </div>
                </div>
            )}

        </div>
    )
}
