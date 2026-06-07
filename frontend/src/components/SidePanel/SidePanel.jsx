// STYLES ------------------------------------------------------------------------------------------------------------------------------------------|
import styles from './SidePanel.module.css'

// RISK CONFIG -------------------------------------------------------------------------------------------------------------------------------------|
const RISK_META = {
    high: { label: 'High Risk', cls: 'high' },
    medium: { label: 'Medium Risk', cls: 'medium' },
    low: { label: 'Low Risk', cls: 'low' },
    none: { label: 'Clean', cls: 'clean' },
}

// SIDE PANEL COMPONENT ----------------------------------------------------------------------------------------------------------------------------|
export default function SidePanel({ node }) {
    if (!node) {
        return (
            <div className = {styles.panel}>
                <div className = {styles.empty}>
                    <span className = {styles.emptyIcon}>◎</span>
                    <p>Click a node to inspect it</p>
                </div>
            </div>
        )
    }

    const risk = RISK_META[node.risk] ?? RISK_META.none

    return (
        <div className = {styles.panel}>

            {/* Package Header */}
            <div className = {styles.header}>
                <p className = "tag">selected package</p>
                <h2 className = {styles.pkgName}>{node.id}</h2>
                <div className = {styles.meta}>
                    <span className = {styles.version}>v{node.version}</span>
                    <span className = {styles.ecosystem}>{node.ecosystem}</span>
                    {node.is_direct && (
                        <span className = {styles.directBadge}>direct</span>
                    )}
                </div>
                <span className = {`${styles.riskBadge} ${styles[risk.cls]}`}>
                    {risk.label}
                    {node.cves.length > 0 && ` · ${node.cves.length} CVE${node.cves.length > 1 ? 's' : ''}`}
                </span>
            </div>

            {/* CVE List */}
            {node.cves.length > 0 && (
                <div className = {styles.section}>
                    <p className = "tag">vulnerabilities</p>
                    <div className = {styles.cveList}>
                        {node.cves.map(cve => (
                            <div key = {cve.id} className = {styles.cveCard}>
                                <div className = {styles.cveTop}>
                                    <span className = {styles.cveId}>{cve.id}</span>
                                    {cve.cvss != null && (
                                        <span className = {`${styles.cvssScore} ${styles[severityClass(cve.cvss)]}`}>
                                            {cve.cvss.toFixed(1)}
                                        </span>
                                    )}
                                </div>
                                <p className = {styles.cveDesc}>{cve.description}</p>
                                {cve.fixed_version && (
                                    <p className = {styles.fixedVersion}>
                                        fix: <code>≥ {cve.fixed_version}</code>
                                    </p>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Clean State */}
            {node.cves.length === 0 && (
                <div className = {styles.section}>
                    <p className = {styles.cleanMsg}>✓ No known vulnerabilities</p>
                </div>
            )}

        </div>
    )
}

// HELPER FUNCTIONS --------------------------------------------------------------------------------------------------------------------------------|

// (1) Determine CVE severity class based on CVSS score
function severityClass(score) {
    if (score >= 9.0) return 'high'
    if (score >= 7.0) return 'high'
    if (score >= 4.0) return 'medium'
    return 'low'
}
