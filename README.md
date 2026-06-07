# DepViz — Dependency Graph Visualizer

Upload a dependency file and instantly get an interactive graph of your entire package tree — with live CVE vulnerability data from [OSV.dev](https://osv.dev).

![depviz preview](https://raw.githubusercontent.com/Krexilor/depviz/main/preview.png)

## Features

- **Interactive graph** — force-directed D3.js visualization, zoom, pan, drag nodes
- **CVE scanning** — live vulnerability data via OSV.dev (no API key needed)
- **Risk color coding** — red (high), orange (medium), green (clean)
- **Transitive resolution** — resolves up to 3 levels of nested dependencies
- **Multi-ecosystem** — supports pip and npm out of the box

## Supported Files

| File | Ecosystem |
|------|-----------|
| `requirements.txt` | Python (pip) |
| `pyproject.toml` | Python (Poetry / PEP 621) |
| `package.json` | Node.js (npm) |

## Tech Stack

**Backend** — Python · FastAPI · httpx · OSV.dev API · PyPI API · npm registry  
**Frontend** — React · Vite · D3.js

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
.venv\Scripts\activate # Windows

pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

### 4. Upload a file

Open `http://localhost:5173`, drag and drop a `requirements.txt` or `package.json` and hit analyze.

## Project Structure

```
depviz/
├── backend/
│   ├── parsers/
│   │    ├── __init__.py
│   │    ├── npm_parser.py
│   │    └── pip_parser.py
│   ├── resolvers/
│   │    ├── __init__.py
│   │    ├── npm.py
│   │    └── pypi.py
│   ├── scanner/
│   │    ├── __init__.py
│   │    └── osv.py
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   ├── models.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── styles/
│   │   │    └── global.css
│   │   └── components/
│   │        ├── DropZone/
│   │        │    ├── DropZone.jsx
│   │        │    └── DropZone.module.css
│   │        ├── Graph/
│   │        │    ├── Graph.jsx
│   │        │    └── Graph.module.css
│   │        ├── SidePanel/
│   │        │    ├── SidePanel.jsx
│   │        │    └── SidePanel.module.css
│   │        └── StatsBar/
│   │             ├── StatsBar.jsx
│   │             └── StatsBar.module.css
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   └── vite.config.js
├── .gitignore
├── LICENSE
└── README.md
```

## License

MIT — free to use with credit. See [LICENSE](./LICENSE).
