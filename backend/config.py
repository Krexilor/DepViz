SUPPORTED_FILES = {
    "requirements.txt": "pip",
    "pyproject.toml": "pip",
    "package.json": "npm",
    "Cargo.toml": "cargo",
    "go.mod": "go",
    "Gemfile": "gem"
}

OSV_API_URL = "https://api.osv.dev/v1/query"
PYPI_API_URL = "https://pypi.org/pypi/{package}/json"
NPM_API_URL = "https://registry.npmjs.org/{package}/latest"
CRATES_API_URL = "https://crates.io/api/v1/crates/{package}"
GO_PROXY_URL = "https://proxy.golang.org/{module}/@latest"
RUBYGEMS_API_URL = "https://rubygems.org/api/v1/gems/{package}.json"

MAX_DEPTH = 2
REQUEST_TIMEOUT = 10
