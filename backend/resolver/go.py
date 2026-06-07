# LIBRARIES ----------------------------------------------------------------------------------------------------------------------------------------|
import httpx
import asyncio

# MODELS & CONFIG ----------------------------------------------------------------------------------------------------------------------------------|
from config import MAX_DEPTH, REQUEST_TIMEOUT
from models import Node, Edge, GraphResponse, RiskLevel, EcosystemType

GO_PROXY_URL = "https://proxy.golang.org/{module}/@latest"

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
        _fetch_go_module(client, name) for name in new_deps
    ])

    next_level: list[tuple[str, dict[str, str]]] = []

    for name, meta in zip(new_deps.keys(), results):
        if not meta:
            continue

        nodes[name] = Node(
            id = name,
            version = meta.get("version", new_deps[name]),
            ecosystem = EcosystemType.GO,
            risk = RiskLevel.NONE,
            is_direct = is_direct,
        )

        if is_direct and meta.get("deps"):
            next_level.append((name, meta["deps"]))

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

# GO PROXY FETCH -----------------------------------------------------------------------------------------------------------------------------------|
async def _fetch_go_module(client: httpx.AsyncClient, module: str) -> dict | None:
    try:
        url = GO_PROXY_URL.format(module = module)
        response = await client.get(url)
        if response.status_code != 200:
            return None

        data = response.json()
        version = data.get("Version", "latest").lstrip("v")
        return {"version": version, "deps": {}}

    except Exception:
        return None
    