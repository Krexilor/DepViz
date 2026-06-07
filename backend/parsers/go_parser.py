# LIBRARIES ----------------------------------------------------------------------------------------------------------------------------------------|
import re

# ENTRY POINT --------------------------------------------------------------------------------------------------------------------------------------|
def parse(content: str) -> dict[str, str]:
    deps = {}

    for line in content.splitlines():
        line = line.strip()

        if not line or line.startswith("//") or line.startswith("module") or line.startswith("go "):
            continue

        single = re.match(r"^require\s+(\S+)\s+(v[\w\.\-]+)", line)
        if single:
            name = _short_name(single.group(1))
            version = _clean(single.group(2))
            deps[name] = version
            continue

        block = re.match(r"^(\S+)\s+(v[\w\.\-]+)", line)
        if block and "/" in block.group(1):
            name = _short_name(block.group(1))
            version = _clean(block.group(2))
            if "// indirect" not in line:
                deps[name] = version

    return deps

# HELPER FUNCTIONS ---------------------------------------------------------------------------------------------------------------------------------|

# (1) Extracts a short readable name from a Go module path
def _short_name(module_path: str) -> str:
    return module_path.rstrip("/").split("/")[-1]

# (2) Strips the leading "v" from Go version tags
def _clean(version: str) -> str:
    return version.lstrip("v") or "latest"
