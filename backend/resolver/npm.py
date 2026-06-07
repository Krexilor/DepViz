# LIBRARIES ----------------------------------------------------------------------------------------------------------------------------------------|
import re
import httpx
import asyncio

# MODELS & CONFIG ----------------------------------------------------------------------------------------------------------------------------------|
from config import NPM_API_URL, MAX_DEPTH, REQUEST_TIMEOUT
from models import Node, Edge, GraphResponse, RiskLevel, EcosystemType

# ENTRY POINT --------------------------------------------------------------------------------------------------------------------------------------|
async def resolve(direct_deps: dict[str, str], ecosystem: str = EcosystemType.NPM) -> GraphResponse:
    nodes: dict[str, Node] = {}
    edges: list[Edge] = []

    async with httpx.AsyncClient(timeout = REQUEST_TIMEOUT) as client:
        await _resolve_concurrent(direct_deps, is_direct = True, depth = 0, client = client, nodes = nodes, edges = edges)

    return GraphResponse(
        nodes = list(nodes.values()),
        edges = edges,
        total = 0,
        high_cve_count = 0,
        medium_cve_count = 0,
        clean_count = 0,
    )

# CONCURRENT RESOLVER ------------------------------------------------------------------------------------------------------------------------------|
async def _resolve_concurrent(
    deps: dict[str, str],
    is_direct: bool,
    depth: int,
    client: httpx.AsyncClient,
    nodes: dict[str, Node],
    edges: list[Edge],
    parent: str | None = None,
) -> None:
    if depth > MAX_DEPTH:
        return

    new_deps = {}
    for name, version in deps.items():
        if parent:
            edge = Edge(source = parent, target = name)
            if edge not in edges:
                edges.append(edge)
        if name not in nodes:
            new_deps[name] = version

    if not new_deps:
        return

    results = await asyncio.gather(*[
        _fetch_npm(client, name) for name in new_deps
    ])

    next_level: list[tuple[str, dict[str, str]]] = []

    for name, meta in zip(new_deps.keys(), results):
        if not meta:
            continue

        resolved_version = meta.get("version", new_deps[name])

        nodes[name] = Node(
            id = name,
            version = resolved_version,
            ecosystem = EcosystemType.NPM,
            risk = RiskLevel.NONE,
            is_direct = is_direct,
        )

        transitive = _extract_deps(meta)
        if transitive:
            next_level.append((name, transitive))

    if next_level:
        await asyncio.gather(*[
            _resolve_concurrent(
                deps = transitive,
                is_direct = False,
                depth = depth + 1,
                client = client,
                nodes = nodes,
                edges = edges,
                parent = parent_name,
            )
            for parent_name, transitive in next_level
        ])

# NPM FETCH ----------------------------------------------------------------------------------------------------------------------------------------|
async def _fetch_npm(client: httpx.AsyncClient, package: str) -> dict | None:
    try:
        encoded = package.replace("/", "%2F")
        url = NPM_API_URL.format(package = encoded)
        response = await client.get(url)

        if response.status_code != 200:
            return None

        return response.json()

    except Exception:
        return None

# EXTRACTOR ----------------------------------------------------------------------------------------------------------------------------------------|
def _extract_deps(meta: dict) -> dict[str, str]:
    deps = {}

    raw = meta.get("dependencies", {})

    for name, version_spec in raw.items():
        deps[name.lower()] = _clean_version(version_spec)

    return deps

# HELPER FUNCTION ----------------------------------------------------------------------------------------------------------------------------------|

# (1) Strips version specifiers from version strings
def _clean_version(spec: str) -> str:
    if not spec or spec in ("*", "latest", "x"):
        return "latest"

    cleaned = re.sub(r"^[\^~>=<]+", "", spec).strip()

    if " - " in cleaned:
        cleaned = cleaned.split(" - ")[0].strip()

    if "||" in cleaned:
        cleaned = cleaned.split("||")[0].strip()
        cleaned = re.sub(r"^[\^~>=<]+", "", cleaned).strip()

    return cleaned or "latest"
