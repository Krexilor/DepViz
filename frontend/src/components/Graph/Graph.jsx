// LIBRARIES ---------------------------------------------------------------------------------------------------------------------------------------|
import * as d3 from 'd3'
import { useEffect, useRef } from 'react'

// STYLES ------------------------------------------------------------------------------------------------------------------------------------------|
import styles from './Graph.module.css'

// COLOR MAP ---------------------------------------------------------------------------------------------------------------------------------------|
const RISK_FILL = {
    high: 'rgba(255, 95, 95, 0.18)',
    medium: 'rgba(245, 166, 35, 0.18)',
    low: 'rgba(78, 203, 113, 0.18)',
    none: 'rgba(108, 99, 255, 0.12)',
}

const RISK_STROKE = {
    high: '#ff5f5f',
    medium: '#f5a623',
    low: '#4ecb71',
    none: '#6c63ff',
}

// GRAPH COMPONENT ---------------------------------------------------------------------------------------------------------------------------------|
export default function Graph({ data, onSelectNode, selectedNode }) {
    const svgRef = useRef(null)
    const containerRef = useRef(null)

    useEffect(() => {
        if (!data || !svgRef.current || !containerRef.current) return

        d3.select(svgRef.current).selectAll('*').remove()

        const { width, height } = containerRef.current.getBoundingClientRect()

        const svg = d3.select(svgRef.current)
            .attr('width', width)
            .attr('height', height)

        svg.append('defs').append('marker')
            .attr('id', 'arrow')
            .attr('viewBox', '0 -4 8 8')
            .attr('refX', 8)
            .attr('refY', 0)
            .attr('markerWidth', 5)
            .attr('markerHeight', 5)
            .attr('orient', 'auto')
            .append('path')
            .attr('d', 'M0,-4L8,0L0,4')
            .attr('fill', '#3a3a5c')

        const nodes = data.nodes.map(n => ({ ...n }))
        const edges = data.edges.map(e => ({ ...e }))

        const simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(edges)
                .id(d => d.id)
                .distance(d => d.source.is_direct || d.target.is_direct ? 80 : 55)
                .strength(0.8)
            )
            .force('charge', d3.forceManyBody()
                .strength(d => d.is_direct ? -180 : -120)
            )
            .force('center', d3.forceCenter(width / 2, height / 2).strength(0.08))
            .force('collision', d3.forceCollide().radius(d => {
                const nameLen = d.id.length
                const base = d.is_direct ? 10 : 8
                return Math.max(base, nameLen * (d.is_direct ? 4.2 : 3.8)) + 8
            }).strength(0.9))
            .force('x', d3.forceX(width / 2).strength(0.04))
            .force('y', d3.forceY(height / 2).strength(0.04))

        const g = svg.append('g')

        svg.call(
            d3.zoom()
                .scaleExtent([0.15, 4])
                .on('zoom', e => g.attr('transform', e.transform))
        )

        const link = g.append('g')
            .selectAll('line')
            .data(edges)
            .join('line')
            .attr('stroke', '#2a2a42')
            .attr('stroke-width', 1)
            .attr('marker-end', 'url(#arrow)')

        const node = g.append('g')
            .selectAll('g')
            .data(nodes)
            .join('g')
            .attr('cursor', 'pointer')
            .on('click', (_, d) => onSelectNode(d))
            .call(
                d3.drag()
                    .on('start', (e, d) => {
                        if (!e.active) simulation.alphaTarget(0.3).restart()
                        d.fx = d.x
                        d.fy = d.y
                    })
                    .on('drag', (e, d) => {
                        d.fx = e.x
                        d.fy = e.y
                    })
                    .on('end', (e, d) => {
                        if (!e.active) simulation.alphaTarget(0)
                        d.fx = null
                        d.fy = null
                    })
            )

        node.append('rect')
            .attr('rx', 6)
            .attr('ry', 6)
            .attr('fill', d => RISK_FILL[d.risk])
            .attr('stroke', d => RISK_STROKE[d.risk])
            .attr('stroke-width', d => d.is_direct ? 1.5 : 1)

        node.append('text')
            .text(d => d.id)
            .attr('text-anchor', 'middle')
            .attr('dominant-baseline', 'middle')
            .attr('fill', '#e8e6f0')
            .attr('font-family', 'IBM Plex Mono, monospace')
            .attr('font-size', d => d.is_direct ? 11 : 10)
            .attr('font-weight', d => d.is_direct ? '500' : '400')
            .attr('pointer-events', 'none')

        node.each(function(d) {
            const textEl = d3.select(this).select('text').node()
            const bbox = textEl.getBBox()
            const padX = 10
            const padY = 6
            d._w = bbox.width + padX * 2
            d._h = bbox.height + padY * 2
            d3.select(this).select('rect')
                .attr('width', d._w)
                .attr('height', d._h)
                .attr('x', -d._w / 2)
                .attr('y', -d._h / 2)
        })

        simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y)

            node.attr('transform', d => `translate(${d.x},${d.y})`)
        })

        return () => simulation.stop()

    }, [data])

    useEffect(() => {
        if (!svgRef.current) return

        d3.select(svgRef.current)
            .selectAll('rect')
            .attr('stroke-width', d =>
                selectedNode && d.id === selectedNode.id ? 2.5 : d.is_direct ? 1.5 : 1
            )
            .attr('stroke', d =>
                selectedNode && d.id === selectedNode.id ? '#ffffff' : RISK_STROKE[d.risk]
            )
    }, [selectedNode])

    return (
        <div ref = {containerRef} className = {styles.container}>

            {!data && (
                <p className = {styles.empty}>Upload a file to see the graph</p>
            )}

            <svg ref = {svgRef} className = {styles.svg} />

            {data && (
                <div className = {styles.legend}>
                    {[
                        { label: 'high CVE', color: '#ff5f5f' },
                        { label: 'medium', color: '#f5a623' },
                        { label: 'low', color: '#4ecb71' },
                        { label: 'clean', color: '#6c63ff' },
                        { label: 'direct dep', color: '#e8e6f0', thick: true },
                    ].map(({ label, color, thick }) => (
                        <div key = {label} className = {styles.legendItem}>
                            <span
                                className = {styles.legendDot}
                                style = {{
                                    background: thick ? 'transparent' : color,
                                    border: thick ? `2px solid ${color}` : 'none',
                                }}
                            />
                            <span>{label}</span>
                        </div>
                    ))}
                </div>
            )}

        </div>
    )
}
