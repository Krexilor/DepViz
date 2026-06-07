# DepViz — Dependency Graph Visualizer

Upload a dependency file and instantly get an interactive graph of your entire package tree — with live CVE vulnerability data from [OSV.dev](https://osv.dev).

- Main Page
![depviz preview](https://github.com/Krexilor/DepViz/blob/main/assets/MainPage.png?raw=true)

- Graph Tree
![depviz preview](https://github.com/Krexilor/DepViz/blob/main/assets/GraphTree.png?raw=true)

---

## Features

- **Interactive graph** — force-directed D3.js visualization with zoom, pan, and draggable nodes
- **CVE scanning** — live vulnerability data via OSV.dev (no API key required)
- **Risk color coding** — red (high), orange (medium), green (low), purple (clean)
- **Transitive resolution** — walks up to 2 levels deep into nested dependencies
- **Multi-ecosystem** — supports Python, Node.js, Rust, Go, and Ruby out of the box
- **Concurrent fetching** — all packages at each depth level are resolved in parallel for fast results

---

## Supported Files

| File | Ecosystem | Registry Used |
|------|-----------|---------------|
| `requirements.txt` | Python (pip) | PyPI |
| `pyproject.toml` | Python (Poetry / PEP 621) | PyPI |
| `package.json` | Node.js (npm) | npm registry |
| `Cargo.toml` | Rust | crates.io |
| `go.mod` | Go | proxy.golang.org |
| `Gemfile` | Ruby | rubygems.org |

---

## How It Works

1. You upload a dependency file via the drag-and-drop interface
2. The backend detects the ecosystem from the filename and parses direct dependencies
3. For each direct dependency, the resolver fetches transitive dependencies from the relevant registry (PyPI, npm, crates.io, etc.) — all requests run concurrently
4. Every resolved package is checked against the [OSV.dev](https://osv.dev) vulnerability database
5. The frontend renders a force-directed graph with nodes color-coded by CVE risk level
6. Click any node to see its version, CVEs, CVSS scores, and the suggested fix version

---

## Ecosystem Notes

**Python (pip / pyproject.toml)**
Resolves transitive dependencies from PyPI up to depth 2. Supports both PEP 621 `[project]` style and Poetry `[tool.poetry.dependencies]` style in `pyproject.toml`. Be aware that large Python projects (e.g. FastAPI) have deep dependency trees — even at depth 2 you may see 80–100+ nodes, which is accurate.

**Node.js (package.json)**
Reads `dependencies`, `devDependencies`, and `peerDependencies`. Resolves transitive deps from the npm registry. Semver range prefixes (`^`, `~`, `>=`) are stripped to get plain version numbers.

**Rust (Cargo.toml)**
Reads `[dependencies]`, `[dev-dependencies]`, `[build-dependencies]`, and `[workspace.dependencies]`. Resolves from the crates.io API. The crates.io API requires a `User-Agent` header — depviz sends one identifying itself per their policy.

**Go (go.mod)**
Parses direct `require` statements and skips lines marked `// indirect` since those are managed by Go's module system automatically. The Go module proxy (`proxy.golang.org`) does not expose a package's own dependency list, so transitive resolution is limited to depth 1 — you see your direct deps and their versions but not their full trees.

**Ruby (Gemfile)**
Parses `gem` declarations and skips `group` blocks, `source` lines, and Ruby version pins. Resolves runtime dependencies from rubygems.org. Development gems inside `group :development` blocks are excluded.

---

## Tech Stack

**Backend**
- | `Python 3.11+` | `FastAPI` | `uvicorn` | `httpx` | `pydantic` |
- | `OSV.dev API` | `PyPI` | `npm registry` | `crates.io` | `proxy.golang.org` | `rubygems.org` |

**Frontend**
- | `React 18` | `Vite` | `D3.js` |

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/Krexilor/depviz.git
cd depviz
```

### 2. Backend

```bash
cd backend

python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`  
API docs available at `http://localhost:8000/docs`

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

### 4. Upload a file

Open `http://localhost:5173`, drag and drop any supported dependency file, and the graph renders automatically.

---

## Project Structure

```
depviz/
├── backend/
│   ├── parsers/
│   │    ├── __init__.py
│   │    ├── pip_parser.py                       # requirements.txt + pyproject.toml
│   │    ├── npm_parser.py                       # package.json
│   │    ├── cargo_parser.py                     # Cargo.toml
│   │    ├── go_parser.py                        # go.mod
│   │    └── gemfile_parser.py                   # Gemfile
│   ├── resolver/
│   │    ├── __init__.py
│   │    ├── pypi.py                             # PyPI transitive resolution
│   │    ├── npm.py                              # npm registry resolution
│   │    ├── cargo.py                            # crates.io resolution
│   │    ├── go.py                               # Go module proxy resolution
│   │    └── gem.py                              # RubyGems resolution
│   ├── scanner/
│   │    ├── __init__.py
│   │    └── osv.py                              # OSV.dev CVE scanner
│   ├── __init__.py
│   ├── config.py                                # API URLs, supported files, constants
│   ├── main.py                                  # FastAPI app + /analyze endpoint
│   ├── models.py                                # Pydantic models
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── styles/
│   │   │    └── globals.css
│   │   └── components/
│   │        ├── DropZone/                       # file upload with drag-and-drop
│   │        │    ├── DropZone.jsx
│   │        │    └── DropZone.module.css
│   │        ├── Graph/                          # D3.js force-directed graph
│   │        │    ├── Graph.jsx
│   │        │    └── Graph.module.css
│   │        ├── SidePanel/                      # selected node CVE details
│   │        │    ├── SidePanel.jsx
│   │        │    └── SidePanel.module.css
│   │        └── StatsBar/                       # summary counts + reset button
│   │             ├── StatsBar.jsx
│   │             └── StatsBar.module.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── .gitignore
├── LICENSE
└── README.md
```

---

## License

MIT — free to use with credit. See [LICENSE](./LICENSE).
