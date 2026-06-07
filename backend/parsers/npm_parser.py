# LIBRARIES ----------------------------------------------------------------------------------------------------------------------------------------|
import re
import json

# 
def parse(content: str) -> dict[str, str]:
    data = json.loads(content)
    deps = {}

    for section in ("dependencies", "devDependencies", "peerDependencies"):
        for name, version_spec in data.get(section, {}).items():
            deps[name.lower()] = _clean_version(version_spec)

    return deps

# 
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
