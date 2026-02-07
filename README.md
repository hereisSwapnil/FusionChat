# FusionChat

An AI-powered chat application with advanced RAG (Retrieval-Augmented Generation) capabilities. Upload documents, build knowledge graphs, and have intelligent conversations powered by vector search and graph-based retrieval.

## 🚀 Features

- **Document Ingestion**: Upload PDFs, text files, and markdown documents for AI-powered analysis
- **Graph RAG**: Combines vector embeddings with knowledge graph relationships for enhanced retrieval
- **Multi-Database Architecture**: PostgreSQL for metadata, Qdrant for vectors, Neo4j for knowledge graphs
- **Real-Time Processing**: Live document processing status with visual feedback
- **Modern UI**: Clean, ChatGPT-inspired interface with smooth animations
- **Docker Support**: One-command deployment with full containerization

## Screenshots

[![Clean-Shot-2026-02-07-at-20-59-51-2x.png](https://i.postimg.cc/5tMQq2nT/Clean-Shot-2026-02-07-at-20-59-51-2x.png)](https://postimg.cc/HrBLTdG9)
[![Clean-Shot-2026-02-07-at-21-00-25-2x.png](https://i.postimg.cc/WbFdBkyC/Clean-Shot-2026-02-07-at-21-00-25-2x.png)](https://postimg.cc/9r2XTrCY)

## 🛠️ Tech Stack

### Backend
- **FastAPI**: High-performance async API framework
- **OpenAI GPT-4o-mini**: Language model for chat and embeddings
- **Qdrant**: Vector database for semantic search
- **Neo4j**: Graph database for entity relationships
- **PostgreSQL**: Relational database for chat and document metadata
- **SQLAlchemy**: Async ORM with PostgreSQL
- **NLTK**: Natural language processing for text chunking

### Frontend
- **React 19**: Modern UI library
- **Vite**: Fast build tool and dev server
- **Framer Motion**: Smooth animations and transitions
- **Axios**: HTTP client for API communication
- **Lucide React**: Beautiful icon library

## 📋 Prerequisites

Before installation, ensure you have the following:

- [Python 3.11+](https://www.python.org/)
- [Node.js 20+](https://nodejs.org/)
- [Docker & Docker Compose](https://docs.docker.com/get-docker/) (for Docker setup)
- [OpenAI API Key](https://platform.openai.com/)

## 🔧 Installation

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/hereisSwapnil/FusionChat.git
   cd FusionChat
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your OpenAI API key:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: [http://localhost:5173](http://localhost:5173)
   - Backend API: [http://localhost:8000](http://localhost:8000)
   - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Option 2: Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/hereisSwapnil/FusionChat.git
   cd FusionChat
   ```

2. **Start databases with Docker**
   ```bash
   docker-compose up -d neo4j qdrant postgres
   ```

3. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   
   # Download NLTK data
   python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"
   ```

4. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

5. **Environment Variables**
   
   Create `backend/.env`:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

6. **Run the application**
   
   Terminal 1 (Backend):
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```
   
   Terminal 2 (Frontend):
   ```bash
   cd frontend
   npm run dev
   ```


## 📁 Project Structure

```
FusionChat/
├── backend/
│   ├── app/
│   │   ├── api/endpoints/      # API route handlers
│   │   ├── core/               # Configuration and utilities
│   │   ├── db/                 # Database clients and queries
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   └── services/           # Business logic
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx            # Main application component
│   │   ├── App.css            # Application styles
│   │   └── index.css          # Global styles
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml          # Multi-container orchestration
├── DOCKER.md                   # Detailed Docker documentation
└── .env.example                # Environment template
```

## 🔄 How It Works

1. **Create Chat**: Start a new conversation or select an existing one
2. **Upload Documents**: Attach PDFs or text files to enrich the knowledge base
3. **Processing Pipeline**:
   - Text extraction from documents
   - Semantic chunking with NLTK
   - Embedding generation with OpenAI
   - Vector storage in Qdrant (per-chat collections)
   - Entity and relationship extraction
   - Knowledge graph construction in Neo4j
4. **Intelligent Retrieval**: 
   - Vector similarity search for relevant chunks
   - Graph traversal for related entities
   - Context fusion for comprehensive answers
5. **AI Response**: GPT-4o-mini generates responses using retrieved context


## 🔒 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `NEO4J_URI` | Neo4j connection URI | bolt://localhost:7687 |
| `NEO4J_USER` | Neo4j username | neo4j |
| `NEO4J_PASSWORD` | Neo4j password | password |
| `QDRANT_HOST` | Qdrant host | localhost |
| `QDRANT_PORT` | Qdrant port | 6333 |
| `POSTGRES_HOST` | PostgreSQL host | localhost |
| `POSTGRES_PORT` | PostgreSQL port | 5432 |
| `POSTGRES_DB` | PostgreSQL database | fusionchat |
| `POSTGRES_USER` | PostgreSQL username | postgres |
| `POSTGRES_PASSWORD` | PostgreSQL password | password |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.