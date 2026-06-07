SUPPORTED_FILES = {
    "package.json": "npm",
    "pyproject.toml": "pip",
    "requirements.txt": "pip"    
}

OSV_API_URL = "https://api.osv.dev/v1/query"
PYPI_API_URL = "https://pypi.org/pypi/{package}/json"
NPM_API_URL = "https://registry.npmjs.org/{package}/latest"

MAX_DEPTH = 3
REQUEST_TIMEOUT = 10
