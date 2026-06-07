# LIBRARIES ----------------------------------------------------------------------------------------------------------------------------------------|
import re
import httpx
import asyncio

# MODELS & CONFIG ----------------------------------------------------------------------------------------------------------------------------------|
from config import PYPI_API_URL, MAX_DEPTH, REQUEST_TIMEOUT
from models import Node, Edge, GraphResponse, RiskLevel, EcosystemType

# ENTRY POINT --------------------------------------------------------------------------------------------------------------------------------------|
async def resolve(direct_deps: dict[str, str], ecosystem: str = EcosystemType.PIP) -> GraphResponse:
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
        _fetch_pypi(client, name) for name in new_deps
    ])

    next_level: list[tuple[str, dict[str, str]]] = []

    for name, meta in zip(new_deps.keys(), results):
        if not meta:
            continue

        resolved_version = meta.get("version", new_deps[name])

        nodes[name] = Node(
            id = name,
            version = resolved_version,
            ecosystem = EcosystemType.PIP,
            risk = RiskLevel.NONE,
            is_direct = is_direct,
        )

        transitive = _extract_requires(meta)
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

# PYPI FETCH ---------------------------------------------------------------------------------------------------------------------------------------|
async def _fetch_pypi(client: httpx.AsyncClient, package: str) -> dict | None:
    try:
        url = PYPI_API_URL.format(package = package)
        response = await client.get(url)
        if response.status_code != 200:
            return None

        data = response.json()
        return data.get("info", {})

    except Exception:
        return None

# EXTRACTOR ----------------------------------------------------------------------------------------------------------------------------------------|
def _extract_requires(info: dict) -> dict[str, str]:
    deps = {}
    requires = info.get("requires_dist") or []

    for req in requires:
        if ";" in req:
            req = req.split(";")[0].strip()
            if not req:
                continue

        match = re.match(r"^([A-Za-z0-9_\-\.]+)\s*[\(]?([><=!~,\s\d\.\*]*)?[\)]?", req)
        if match:
            name = match.group(1).lower().replace("_", "-")
            raw_version = match.group(2) or ""
            ver_match = re.search(r"[\d]+[\d\.]*", raw_version)
            version = ver_match.group(0) if ver_match else "latest"
            deps[name] = version

    return deps
