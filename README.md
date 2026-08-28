# OpenBayanNext

**OpenBayanNext** is a modern, high-throughput Information Retrieval (IR) and thematic synthesis platform tailored for classical Arabic scholarly corpora. It features an Astro web frontend, a FastAPI backend with embedded libSQL/Turso storage, Tantivy BM25 full-text indexing, vector search, and MinHash bitset clustering.

---

## 🏗️ Architecture & Monorepo Layout

The repository is organized as a polyglot monorepo managed with **Turborepo** and **pnpm workspaces**:

```
OpenBayanNext/
├── apps/
│   ├── api/                      # FastAPI Backend & Search Engine
│   │   ├── main.py               # FastAPI entry point & API routes
│   │   ├── requirements.txt      # Python dependencies
│   │   ├── Dockerfile            # Python 3.12 production container
│   │   └── package.json          # Workspace runner for Turborepo
│   └── web/                      # Astro Web Frontend
│       ├── src/                  # Astro components, layouts, & pages
│       ├── astro.config.mjs      # Astro configuration
│       ├── Dockerfile            # Multi-stage production container
│       └── package.json          # @openbayan/web package definition
├── compose.yml                   # Docker Compose & Portainer Stack configuration
├── package.json                  # Workspace scripts & tooling
├── pnpm-workspace.yaml           # pnpm workspace packages & permissions
├── turbo.json                    # Turborepo task pipeline configuration
└── README.md
```

---

## ⚡ Prerequisites

- **Node.js**: `>= 22.12.0`
- **pnpm**: `>= 10.0.0` (v11 recommended)
- **Python**: `>= 3.12`
- **Docker & Docker Compose** (for containerized execution or Portainer)

---

## 🚀 Getting Started

### 1. Install Workspace Dependencies
```bash
pnpm install
```

### 2. Set Up Python Backend Environment (Optional for local non-docker API runs)
```bash
pnpm setup:api
```
This creates a Python virtual environment (`apps/api/.venv`) and installs the dependencies listed in `requirements.txt`.

### 3. Run Development Servers
Start both the **Astro Frontend** and **FastAPI Backend** in parallel with unified log streams:
```bash
pnpm dev
```
- **Web App**: [http://localhost:4321](http://localhost:4321)
- **API Server**: [http://localhost:8000](http://localhost:8000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Build for Production
```bash
pnpm build
```

---

## 🐳 Docker & Portainer Deployment

### Local Docker Compose
To build and run all services locally:
```bash
# Start frontend and backend
docker compose up --build

# Or include data pipeline services (Prefect & Ingestion worker)
docker compose --profile pipeline up --build
```

### Deploying via Portainer
1. Open your **Portainer** dashboard.
2. Go to **Stacks** > **Add stack**.
3. Select **Repository** method.
4. Set the **Repository URL** to your Git repository and set **Compose path** to `compose.yml`.
5. Configure any custom environment variables (e.g., `API_URL`, `DB_PATH`).
6. Click **Deploy the stack**.

---

## 📜 Scripts Reference

| Command | Description |
| :--- | :--- |
| `pnpm dev` | Starts all applications in dev mode with hot reload |
| `pnpm build` | Builds all applications via Turborepo pipelines |
| `pnpm lint` | Runs lint checks across the workspace |
| `pnpm setup:api` | Installs Python virtualenv and requirements in `apps/api` |
