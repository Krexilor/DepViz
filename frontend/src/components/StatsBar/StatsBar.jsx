// STYLES ------------------------------------------------------------------------------------------------------------------------------------------|
import styles from './StatsBar.module.css'

// STATSBAR COMPONENT ------------------------------------------------------------------------------------------------------------------------------|
export default function StatsBar({ data, onReset }) {
    return (
        <div className = {styles.bar}>

            {/* Stats */}
            <div className = {styles.stats}>

                <div className = {styles.stat}>
                    <span className = {styles.statVal}>{data.total}</span>
                    <span className = {styles.statLabel}>packages</span>
                </div>

                <div className = {styles.divider} />

                <div className = {styles.stat}>
                    <span className = {`${styles.statVal} ${styles.high}`}>
                        {data.high_cve_count}
                    </span>
                    <span className = {styles.statLabel}>high CVEs</span>
                </div>

                <div className = {styles.divider} />

                <div className = {styles.stat}>
                    <span className = {`${styles.statVal} ${styles.medium}`}>
                        {data.medium_cve_count}
                    </span>
                    <span className = {styles.statLabel}>medium CVEs</span>
                </div>

                <div className = {styles.divider} />

                <div className = {styles.stat}>
                    <span className = {`${styles.statVal} ${styles.clean}`}>
                        {data.clean_count}
                    </span>
                    <span className = {styles.statLabel}>clean</span>
                </div>

            </div>

            {/* Actions */}
            <div className = {styles.actions}>
                <span className = {`${styles.healthBadge} ${data.high_cve_count > 0 ? styles.unhealthy : styles.healthy}`}>
                    {data.high_cve_count > 0 ? '⚠ vulnerabilities found' : '✓ no critical issues'}
                </span>

                <button className = {styles.resetBtn} onClick = {onReset}>
                    ← new file
                </button>
            </div>

        </div>
    )
}
