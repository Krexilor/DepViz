# LIBRARIES ----------------------------------------------------------------------------------------------------------------------------------------|
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, HTTPException

# MODELS & CONFIG ----------------------------------------------------------------------------------------------------------------------------------|
from config import SUPPORTED_FILES
from models import GraphResponse, EcosystemType

# PARSERS ------------------------------------------------------------------------------------------------------------------------------------------|
from parsers.pip_parser import parse as parse_pip
from parsers.npm_parser import parse as parse_npm

# RESOLVERS ----------------------------------------------------------------------------------------------------------------------------------------|
from resolver.npm import resolve as resolve_npm
from resolver.pypi import resolve as resolve_pip

# SCANNER ------------------------------------------------------------------------------------------------------------------------------------------|
from scanner.osv import scan

# APP ----------------------------------------------------------------------------------------------------------------------------------------------|
app = FastAPI(title = "depviz API", version = "0.1.0")

# CORS ---------------------------------------------------------------------------------------------------------------------------------------------|
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:5173"],
    allow_methods = ["*"],
    allow_headers = ["*"]
)

# ENDPOINTS ----------------------------------------------------------------------------------------------------------------------------------------|

# (1) Health check
@app.get("/health")
async def health():
    return {"status": "ok"}

# (2) Analyze dependencies
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

    else:
        direct_deps = parse_npm(content)
        graph = await resolve_npm(direct_deps)

    graph = await scan(graph, ecosystem)

    graph.total = len(graph.nodes)
    graph.high_cve_count = sum(1 for n in graph.nodes if n.risk == "high")
    graph.medium_cve_count = sum(1 for n in graph.nodes if n.risk == "medium")
    graph.clean_count = sum(1 for n in graph.nodes if n.risk == "none")

    return graph
