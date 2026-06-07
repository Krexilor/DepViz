# LIBRARIES ----------------------------------------------------------------------------------------------------------------------------------------|
import re
import httpx
import asyncio

# MODELS & CONFIG ----------------------------------------------------------------------------------------------------------------------------------|
from config import MAX_DEPTH, REQUEST_TIMEOUT
from models import Node, Edge, GraphResponse, RiskLevel, EcosystemType

CRATES_API_URL = "https://crates.io/api/v1/crates/{package}"
CRATES_HEADERS = {"User-Agent": "depviz/0.1.0 (github.com/Krexilor/depviz)"}

# ENTRY POINT --------------------------------------------------------------------------------------------------------------------------------------|
async def resolve(direct_deps: dict[str, str]) -> GraphResponse:
    nodes: dict[str, Node] = {}
    edges: list[Edge] = []

    async with httpx.AsyncClient(timeout = REQUEST_TIMEOUT, headers = CRATES_HEADERS) as client:
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
        _fetch_crate(client, name) for name in new_deps
    ])

    next_level: list[tuple[str, dict[str, str]]] = []

    for name, meta in zip(new_deps.keys(), results):
        if not meta:
            continue

        resolved_version = meta.get("version", new_deps[name])

        nodes[name] = Node(
            id = name,
            version = resolved_version,
            ecosystem = EcosystemType.CARGO,
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

# CRATES.IO FETCH ----------------------------------------------------------------------------------------------------------------------------------|
async def _fetch_crate(client: httpx.AsyncClient, package: str) -> dict | None:
    try:
        url = CRATES_API_URL.format(package = package)
        response = await client.get(url)
        if response.status_code != 200:
            return None

        data = response.json()
        crate = data.get("crate", {})

        newest_version = crate.get("newest_version", "latest")

        versions = data.get("versions", [])
        deps = {}
        if versions:
            latest = versions[0]
            for dep in latest.get("dependencies") or []:
                if dep.get("kind") == "normal":
                    dep_name = dep.get("crate_id", dep.get("name", ""))
                    dep_version = re.sub(r"^[\^~>=<]+", "", dep.get("req", "latest")).strip()

                    if dep_name:
                        deps[dep_name] = dep_version or "latest"

        return {"version": newest_version, "deps": deps}

    except Exception:
        return None
    