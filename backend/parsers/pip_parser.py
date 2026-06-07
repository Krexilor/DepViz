# LIBRARIES ----------------------------------------------------------------------------------------------------------------------------------------|
import re
import tomllib

# ENTRY POINT --------------------------------------------------------------------------------------------------------------------------------------| 
def parse(content: str, filename: str) -> dict[str, str]:
    if filename == "pyproject.toml":
        return _parse_pyproject(content)
    
    return _parse_requirements(content)

# PARSES PIP-STYLE DEPENDENCY LINES ----------------------------------------------------------------------------------------------------------------|
def _parse_requirements(content: str) -> dict[str, str]:
    deps = {}

    for line in content.splitlines():
        line = line.strip()
        
        if not line or line.startswith("#") or line.startswith("-"):
            continue

        line = line.split("#")[0].strip()
        match = re.match(r"^([A-Za-z0-9_\-\.]+)\s*([><=!~]+)\s*([\w\.\*]+)?", line)
        
        if match:
            name = match.group(1).lower().replace("_", "-")
            version = match.group(3) or "latest"
            deps[name] = version
        
        else:
            name = line.lower().replace("_", "-")
            deps[name] = "latest"

    return deps

# SUPPORTS BOTH 621 AND POETRY FORMATS -------------------------------------------------------------------------------------------------------------|
def _parse_pyproject(content: str) -> dict[str, str]:
    deps = {}
    data = tomllib.loads(content)

    project_deps = data.get("project", {}).get("dependencies", [])
    for dep in project_deps:
        name, version = _split_pep508(dep)
        deps[name] = version

    poetry_deps = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
    for name, spec in poetry_deps.items():
        if name.lower() == "python":
            continue
        
        if isinstance(spec, str):
            version = re.sub(r"[^0-9\.]", "", spec) or "latest"
        
        elif isinstance(spec, dict):
            raw = spec.get("version", "latest")
            version = re.sub(r"[^0-9\.]", "", raw) or "latest"
        
        else:
            version = "latest"

        deps[name.lower().replace("_", "-")] = version

    return deps

# HELPER FUNCTION ----------------------------------------------------------------------------------------------------------------------------------|
def _split_pep508(dep: str) -> tuple[str, str]:
    match = re.match(r"^([A-Za-z0-9_\-\.]+)\s*([><=!~]+)\s*([\w\.\*]+)?", dep)
    if match:
        name = match.group(1).lower().replace("_", "-")
        version = match.group(3) or "latest"
        return name, version
    
    return dep.lower().replace("_", "-"), "latest"
