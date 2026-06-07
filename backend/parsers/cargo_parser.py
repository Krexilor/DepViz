# LIBRARIES ----------------------------------------------------------------------------------------------------------------------------------------|
import re
import tomllib

# ENTRY POINT --------------------------------------------------------------------------------------------------------------------------------------|
def parse(content: str) -> dict[str, str]:
    data = tomllib.loads(content)
    deps = {}

    for name, spec in data.get("dependencies", {}).items():
        deps[name] = _extract_version(spec)

    for name, spec in data.get("dev-dependencies", {}).items():
        deps[name] = _extract_version(spec)

    for name, spec in data.get("build-dependencies", {}).items():
        deps[name] = _extract_version(spec)

    for name, spec in data.get("workspace", {}).get("dependencies", {}).items():
        deps[name] = _extract_version(spec)

    return deps

# HELPER FUNCTIONS ---------------------------------------------------------------------------------------------------------------------------------|

# (1) Extracts a plain version string from various Cargo dependency formats
def _extract_version(spec) -> str:
    if isinstance(spec, str):
        return _clean(spec)

    if isinstance(spec, dict):
        version = spec.get("version", "latest")
        return _clean(str(version))

    return "latest"

# (2) Strips semver range prefixes from version strings
def _clean(version: str) -> str:
    cleaned = re.sub(r"^[\^~>=<]+", "", version.strip())
    return cleaned or "latest"
