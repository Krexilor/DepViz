# LIBRARIES ----------------------------------------------------------------------------------------------------------------------------------------|
import httpx
import asyncio

# MODELS & CONFIG ----------------------------------------------------------------------------------------------------------------------------------|
from config import OSV_API_URL, REQUEST_TIMEOUT
from models import GraphResponse, CVE, RiskLevel, EcosystemType

# ECOSYSTEM MAP ------------------------------------------------------------------------------------------------------------------------------------|
OSV_ECOSYSTEM_MAP = {
    EcosystemType.PIP: "PyPI",
    EcosystemType.NPM: "npm",
    EcosystemType.CARGO: "crates.io",
    EcosystemType.GO: "Go",
    EcosystemType.GEM: "RubyGems"
}

# ENTRY POINT --------------------------------------------------------------------------------------------------------------------------------------|
async def scan(graph: GraphResponse, ecosystem: str) -> GraphResponse:
    osv_ecosystem = OSV_ECOSYSTEM_MAP.get(ecosystem, "PyPI")

    async with httpx.AsyncClient(timeout = REQUEST_TIMEOUT) as client:
        results = await asyncio.gather(*[
            _query_osv(client, node.id, node.version, osv_ecosystem)
            for node in graph.nodes
        ])

    for node, cves in zip(graph.nodes, results):
        if cves:
            node.cves = cves
            node.risk = _compute_risk(cves)

    return graph

# OSV QUERY ----------------------------------------------------------------------------------------------------------------------------------------|
async def _query_osv(
    client: httpx.AsyncClient,
    package: str,
    version: str,
    ecosystem: str,
) -> list[CVE]:
    payload = {
        "package": {
            "name": package,
            "ecosystem": ecosystem,
        }
    }

    if version and version != "latest":
        payload["version"] = version

    try:
        response = await client.post(OSV_API_URL, json = payload)
        if response.status_code != 200:
            return []
        data = response.json()
        return _parse_vulns(data.get("vulns", []))

    except Exception:
        return []

# PARSER -------------------------------------------------------------------------------------------------------------------------------------------|
def _parse_vulns(vulns: list[dict]) -> list[CVE]:
    cves = []

    for vuln in vulns:
        vuln_id = vuln.get("id", "UNKNOWN")
        summary = vuln.get("summary", "No description available.")

        cvss_score = None
        for severity in vuln.get("severity", []):
            if severity.get("type") == "CVSS_V3":
                try:
                    cvss_score = float(severity.get("score", 0) or 0)

                except (ValueError, TypeError):
                    cvss_score = None

        severity_label = _cvss_to_label(cvss_score)
        fixed_version = _extract_fixed_version(vuln)

        cves.append(CVE(
            id = vuln_id,
            description = summary,
            severity = severity_label,
            cvss = cvss_score,
            fixed_version = fixed_version,
        ))

    return cves

# HELPER FUNCTIONS ---------------------------------------------------------------------------------------------------------------------------------|

# (1) Picks the highest risk level across all CVEs for a node
def _compute_risk(cves: list[CVE]) -> RiskLevel:
    if any(c.severity in ("high", "critical") for c in cves):
        return RiskLevel.HIGH
    
    if any(c.severity == "medium" for c in cves):
        return RiskLevel.MEDIUM
    
    if cves:
        return RiskLevel.LOW
    
    return RiskLevel.NONE

# (2) Maps a CVSS score to a human-readable severity label
def _cvss_to_label(score: float | None) -> str:
    if score is None:
        return "unknown"
    
    if score >= 9.0:
        return "critical"
    
    if score >= 7.0:
        return "high"
    
    if score >= 4.0:
        return "medium"
    
    return "low"

# (3) Extracts the earliest fixed version from OSV affected ranges
def _extract_fixed_version(vuln: dict) -> str | None:
    for affected in vuln.get("affected", []):
        for r in affected.get("ranges", []):
            for event in r.get("events", []):
                fixed = event.get("fixed")

                if fixed:
                    return fixed
    return None
