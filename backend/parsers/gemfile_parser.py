# LIBRARIES ----------------------------------------------------------------------------------------------------------------------------------------|
import re

# ENTRY POINT --------------------------------------------------------------------------------------------------------------------------------------|
def parse(content: str) -> dict[str, str]:
    deps = {}

    for line in content.splitlines():
        line = line.strip()

        if not line or line.startswith("#") or line.startswith("source") or line.startswith("ruby"):
            continue

        if line.startswith("group") or line == "end":
            continue

        match = re.match(r'^gem\s+["\']([^"\']+)["\'](?:\s*,\s*["\']([^"\']+)["\'])?', line)
        if match:
            name = match.group(1).strip()
            version = _clean(match.group(2)) if match.group(2) else "latest"
            deps[name] = version

    return deps

# HELPER FUNCTIONS --------------------------------------------------------------------------------------------------------------------------------|

# (1) Strips Ruby version constraint operators
def _clean(version: str) -> str:
    cleaned = re.sub(r"^[~><=\s]+", "", version.strip())
    return cleaned or "latest"
