# LIBRARIES ----------------------------------------------------------------------------------------------------------------------------------------|
import httpx
import asyncio

# MODELS & CONFIG ----------------------------------------------------------------------------------------------------------------------------------|
from config import MAX_DEPTH, REQUEST_TIMEOUT
from models import Node, Edge, GraphResponse, RiskLevel, EcosystemType

RUBYGEMS_API_URL = "https://rubygems.org/api/v1/gems/{package}.json"
RUBYGEMS_DEPS_URL = "https://rubygems.org/api/v1/dependencies.json?gems={package}"

# ENTRY POINT --------------------------------------------------------------------------------------------------------------------------------------|
async def resolve(direct_deps: dict[str, str]) -> GraphResponse:
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
        _fetch_gem(client, name) for name in new_deps
    ])

    next_level: list[tuple[str, dict[str, str]]] = []

    for name, meta in zip(new_deps.keys(), results):
        if not meta:
            continue

        nodes[name] = Node(
            id = name,
            version = meta.get("version", new_deps[name]),
            ecosystem = EcosystemType.GEM,
            risk = RiskLevel.NONE,
            is_direct = is_direct,
        )

        transitive = meta.get("deps", {})
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

# RUBYGEMS FETCH -----------------------------------------------------------------------------------------------------------------------------------|
async def _fetch_gem(client: httpx.AsyncClient, package: str) -> dict | None:
    try:
        url = RUBYGEMS_API_URL.format(package = package)
        response = await client.get(url)
        if response.status_code != 200:
            return None

        data = response.json()
        version = data.get("version", "latest")

        deps = {}
        for dep in data.get("dependencies", {}).get("runtime", []):
            dep_name = dep.get("name", "")
            dep_version = dep.get("requirements", "latest")

            import re
            dep_version = re.sub(r"^[~><=\s,]+", "", dep_version).strip().split(",")[0].strip()

            if dep_name:
                deps[dep_name] = dep_version or "latest"

        return {"version": version, "deps": deps}

    except Exception:
        return None
    