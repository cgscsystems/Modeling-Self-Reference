# N-Link Analysis - Docker Deployment

Docker-based deployment for the N-Link Rule Analysis platform, providing a REST API and interactive visualization dashboards for exploring Wikipedia's link graph structure.

## Services

| Service | Port | Description |
|---------|------|-------------|
| **API** | 8000 | FastAPI REST API for N-link tracing, basin mapping, and data queries |
| **Basin Viewer** | 8055 | 3D/2D visualization of basin geometry and point clouds |
| **Multiplex Analyzer** | 8056 | Cross-N analysis, phase transitions, and layer connectivity |
| **Tunneling Explorer** | 8060 | Tunnel node analysis, basin flows, and path tracing |
| **Reports Gallery** | 8070 | Static HTML reports, interactive visualizations, and analysis figures |

## Prerequisites

### 1. Install Docker

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac)
- [Docker Engine](https://docs.docker.com/engine/install/) (Linux)

### 2. Download Data

The Wikipedia link graph data must be downloaded separately and placed in `./data/wikipedia/processed/`.

**Required files** (~8 GB minimum):

```
data/wikipedia/processed/
├── pages.parquet              # 940 MB - Page IDs and titles
├── nlink_sequences.parquet    # 687 MB - N-link sequences
├── redirects.parquet          # 181 MB - Page redirects
├── disambig_pages.parquet     # 1.8 MB - Disambiguation pages
└── multiplex/                 # 126 MB - Pre-computed analysis
    ├── multiplex_basin_assignments.parquet
    ├── basin_flows.tsv
    ├── tunnel_frequency_ranking.tsv
    └── ...
```

**Optional files** (for full functionality):

```
data/wikipedia/processed/
├── links.parquet              # 2.7 GB - Raw Wikipedia links
├── links_prose.parquet        # 1.7 GB - Prose-only links
├── links_resolved.parquet     # 1.4 GB - Resolved links
└── analysis/                  # 1.7 GB - Per-N analysis outputs
```

**Data sources:**
- HuggingFace: `mgmacleod/wikidata1` (coming soon)
- Direct download: Contact maintainer

## Quick Start

### Start All Services

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

Access the services:
- API: http://localhost:8000/api/v1/health
- API Docs: http://localhost:8000/docs
- Basin Viewer: http://localhost:8055
- Multiplex Analyzer: http://localhost:8056
- Tunneling Explorer: http://localhost:8060
- Reports Gallery: http://localhost:8070

### Start Individual Services

```bash
# API only
docker-compose up -d api

# API + specific dashboard
docker-compose up -d api tunneling

# All dashboards (API auto-starts as dependency)
docker-compose up -d basin-viewer multiplex tunneling

# Reports gallery (standalone, no API needed)
docker-compose up -d reports
```

### Stop Services

```bash
# Stop all
docker-compose down

# Stop specific service
docker-compose stop tunneling
```

## Building

### Build Image

```bash
# Build with docker-compose (recommended)
docker-compose build

# Or build directly
docker build -t nlink-analysis:latest .
```

### Run Without Compose

```bash
# Run API
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data:ro \
  --name nlink-api \
  nlink-analysis:latest api

# Run dashboard
docker run -d \
  -p 8056:8056 \
  -v $(pwd)/data:/app/data:ro \
  --name nlink-multiplex \
  nlink-analysis:latest multiplex
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATA_SOURCE` | `local` | Data source: `local` or `huggingface` |
| `LOCAL_DATA_DIR` | `/app/data/wikipedia/processed` | Path to local data |
| `MAX_WORKERS` | `4` | Background task thread pool size |
| `DEBUG` | `false` | Enable debug mode |
| `API_URL` | - | API URL for Tunneling Explorer API mode |

### Custom Configuration

Create a `.env` file:

```bash
# .env
DATA_SOURCE=local
MAX_WORKERS=8
DEBUG=true
```

Then:

```bash
docker-compose --env-file .env up -d
```

## Service Commands

The container supports multiple entry points via the entrypoint script:

```bash
# API server
docker run nlink-analysis:latest api

# Individual dashboards
docker run nlink-analysis:latest basin-viewer
docker run nlink-analysis:latest multiplex
docker run nlink-analysis:latest tunneling

# Reports gallery
docker run nlink-analysis:latest reports

# All services in one container
docker run nlink-analysis:latest all

# Interactive shell
docker run -it nlink-analysis:latest shell

# Run tests
docker run nlink-analysis:latest test
```

## Development

### Rebuild After Code Changes

```bash
docker-compose build --no-cache
docker-compose up -d
```

### View Container Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
```

### Execute Commands in Running Container

```bash
docker-compose exec api bash
docker-compose exec api python -c "from nlink_api.main import app; print('OK')"
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Network                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐    ┌──────────────┐    ┌─────────────────┐   │
│  │   API    │◄───│   Tunneling  │    │  Basin Viewer   │   │
│  │  :8000   │    │    :8060     │    │     :8055       │   │
│  └────┬─────┘    └──────────────┘    └─────────────────┘   │
│       │                                                     │
│       │          ┌──────────────┐    ┌─────────────────┐   │
│       │          │   Multiplex  │    │    Reports      │   │
│       │          │    :8056     │    │     :8070       │   │
│       │          └──────────────┘    └─────────────────┘   │
│       │                                                     │
├───────┼─────────────────────────────────────────────────────┤
│       │                                                     │
│       ▼                                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Mounted Volume: ./data                  │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │  wikipedia/processed/                        │    │   │
│  │  │  ├── pages.parquet                          │    │   │
│  │  │  ├── nlink_sequences.parquet                │    │   │
│  │  │  ├── multiplex/                             │    │   │
│  │  │  └── analysis/                              │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

Note: The Reports service serves static HTML files built into the Docker image and does not require the data volume.

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs api

# Verify data mount
docker-compose exec api ls -la /app/data/wikipedia/processed/
```

### API Health Check Fails

```bash
# Test manually
curl http://localhost:8000/api/v1/health

# Check if data is accessible
docker-compose exec api python -c "
from pathlib import Path
p = Path('/app/data/wikipedia/processed/pages.parquet')
print(f'pages.parquet exists: {p.exists()}')
print(f'Size: {p.stat().st_size / 1e6:.1f} MB' if p.exists() else 'Not found')
"
```

### Dashboard Shows No Data

Ensure the `multiplex/` directory contains pre-computed analysis files:

```bash
ls -la data/wikipedia/processed/multiplex/
```

Required files:
- `multiplex_basin_assignments.parquet`
- `basin_flows.tsv`
- `tunnel_frequency_ranking.tsv`

### Port Conflicts

If ports are in use, modify `docker-compose.yml`:

```yaml
ports:
  - "9000:8000"  # Map container 8000 to host 9000
```

## Resource Requirements

| Configuration | RAM | Disk | CPU |
|--------------|-----|------|-----|
| API only | 2 GB | 8 GB data | 1 core |
| All services | 4 GB | 8 GB data | 2 cores |
| Full dataset | 8 GB | 12 GB data | 4 cores |

## License

See repository LICENSE file.
