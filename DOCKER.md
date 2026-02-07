# FusionChat Docker Setup

This document provides instructions for running FusionChat using Docker.

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key

## Setup

1. **Create environment file**
   ```bash
   cp .env.example .env
   ```

2. **Add your OpenAI API key**
   Edit the `.env` file and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

## Running with Docker

### Start all services

```bash
docker-compose up -d
```

This will start:
- **Neo4j** (Graph Database) - `http://localhost:7474`
- **Qdrant** (Vector Database) - `http://localhost:6333`
- **PostgreSQL** (Relational Database) - `localhost:5432`
- **Backend** (FastAPI) - `http://localhost:8000`
- **Frontend** (React + Vite) - `http://localhost:5173`

### View logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Stop services

```bash
docker-compose down
```

### Stop services and remove volumes (clean slate)

```bash
docker-compose down -v
```

## Development

The Docker setup includes volume mounts for hot-reload:
- Backend code changes will automatically reload the FastAPI server
- Frontend code changes will trigger Vite's HMR (Hot Module Replacement)

## Accessing Services

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474 (username: `neo4j`, password: `password`)
- **Qdrant Dashboard**: http://localhost:6333/dashboard

## Troubleshooting

### Rebuild containers after dependency changes

```bash
docker-compose up -d --build
```

### Reset databases

```bash
docker-compose down -v
docker-compose up -d
```

### Check service health

```bash
docker-compose ps
```

### Access container shell

```bash
# Backend
docker exec -it fusionchat-backend bash

# Frontend
docker exec -it fusionchat-frontend sh
```
