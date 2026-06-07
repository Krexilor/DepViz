# LIBRARIES ----------------------------------------------------------------------------------------------------------------------------------------|
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, HTTPException

# MODELS & CONFIG ----------------------------------------------------------------------------------------------------------------------------------|
from config import SUPPORTED_FILES
from models import GraphResponse, EcosystemType

# PARSERS ------------------------------------------------------------------------------------------------------------------------------------------|
from parsers.go_parser import parse as parse_go
from parsers.pip_parser import parse as parse_pip
from parsers.npm_parser import parse as parse_npm
from parsers.gemfile_parser import parse as parse_gem
from parsers.cargo_parser import parse as parse_cargo

# RESOLVERS ----------------------------------------------------------------------------------------------------------------------------------------|
from resolver.go import resolve as resolve_go
from resolver.npm import resolve as resolve_npm
from resolver.gem import resolve as resolve_gem
from resolver.pypi import resolve as resolve_pip
from resolver.cargo import resolve as resolve_cargo

# SCANNER ------------------------------------------------------------------------------------------------------------------------------------------|
from scanner.osv import scan

# APP ----------------------------------------------------------------------------------------------------------------------------------------------|
app = FastAPI(title = "depviz API", version = "0.1.0")

# CORS ---------------------------------------------------------------------------------------------------------------------------------------------|
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:5173"],
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# ENDPOINTS ----------------------------------------------------------------------------------------------------------------------------------------|

# (1) Health check
@app.get("/health")
async def health():
    return {"status": "ok"}

# (2) Analyze
@app.post("/analyze", response_model = GraphResponse)
async def analyze(file: UploadFile):
    filename = file.filename

    if filename not in SUPPORTED_FILES:
        raise HTTPException(
            status_code = 400,
            detail = f"Unsupported file. Supported: {', '.join(SUPPORTED_FILES.keys())}"
        )

    ecosystem = SUPPORTED_FILES[filename]
    content = (await file.read()).decode("utf-8")

    if ecosystem == EcosystemType.PIP:
        direct_deps = parse_pip(content, filename)
        graph = await resolve_pip(direct_deps)

    elif ecosystem == EcosystemType.NPM:
        direct_deps = parse_npm(content)
        graph = await resolve_npm(direct_deps)

    elif ecosystem == EcosystemType.CARGO:
        direct_deps = parse_cargo(content)
        graph = await resolve_cargo(direct_deps)

    elif ecosystem == EcosystemType.GO:
        direct_deps = parse_go(content)
        graph = await resolve_go(direct_deps)

    elif ecosystem == EcosystemType.GEM:
        direct_deps = parse_gem(content)
        graph = await resolve_gem(direct_deps)

    else:
        raise HTTPException(status_code = 400, detail = "Unsupported ecosystem.")

    graph = await scan(graph, ecosystem)

    graph.total = len(graph.nodes)
    graph.high_cve_count = sum(1 for n in graph.nodes if n.risk == "high")
    graph.medium_cve_count = sum(1 for n in graph.nodes if n.risk == "medium")
    graph.clean_count = sum(1 for n in graph.nodes if n.risk == "none")

    return graph
