# RAG-Based Podcast Search System - Architecture Design

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          RAG PODCAST SEARCH SYSTEM                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  Web Browser (http://localhost:8080)                                       │
│  ┌─────────────────────────────────────────────────────────────┐          │
│  │  • Search Input Field                                        │          │
│  │  • Results Display (Answer + Sources)                        │          │
│  │  • Stats Dashboard (Episodes, Chunks, Podcasts)              │          │
│  │  • Timestamp & Guest Information                             │          │
│  └─────────────────────────────────────────────────────────────┘          │
│                              ↓ HTTP (REST API)                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         APPLICATION LAYER (Flask)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  app.py - Flask Web Server (Port 8080)                                     │
│  ┌─────────────────────────────────────────────────────────────┐          │
│  │  Endpoints:                                                  │          │
│  │  • GET  /           → Serve HTML UI                          │          │
│  │  • POST /api/search → Process search queries                 │          │
│  │  • GET  /api/stats  → Get indexing statistics                │          │
│  └─────────────────────────────────────────────────────────────┘          │
│                              ↓                                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           RAG PROCESSING PIPELINE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  podcast_rag.py - Core RAG Logic                                           │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────┐             │
│  │ 1. Query Processing                                       │             │
│  │    ├─ User query input                                    │             │
│  │    ├─ Generate query embedding (sentence-transformers)    │             │
│  │    └─ Extract filters (podcast, topics)                   │             │
│  └──────────────────────────────────────────────────────────┘             │
│                              ↓                                               │
│  ┌──────────────────────────────────────────────────────────┐             │
│  │ 2. Hybrid Search (OpenSearch)                             │             │
│  │    ├─ BM25 Text Search (keyword matching)                 │             │
│  │    ├─ kNN Vector Search (semantic similarity)             │             │
│  │    └─ Combined ranking & scoring                          │             │
│  └──────────────────────────────────────────────────────────┘             │
│                              ↓                                               │
│  ┌──────────────────────────────────────────────────────────┐             │
│  │ 3. Context Building                                       │             │
│  │    ├─ Retrieve top-k chunks                               │             │
│  │    ├─ Format with metadata (title, guest, timestamp)      │             │
│  │    └─ Build RAG prompt                                    │             │
│  └──────────────────────────────────────────────────────────┘             │
│                              ↓                                               │
│  ┌──────────────────────────────────────────────────────────┐             │
│  │ 4. Answer Generation (Ollama LLM)                         │             │
│  │    ├─ Send prompt to llama3.2                             │             │
│  │    ├─ Generate contextual answer                          │             │
│  │    └─ Return answer + sources                             │             │
│  └──────────────────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         INDEXING PIPELINE                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  index_transcripts.py - Transcript Ingestion                                │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────┐             │
│  │ 1. Data Loading                                           │             │
│  │    ├─ Read .txt files from transcripts/ directory         │             │
│  │    └─ Extract episode metadata from filename              │             │
│  └──────────────────────────────────────────────────────────┘             │
│                              ↓                                               │
│  ┌──────────────────────────────────────────────────────────┐             │
│  │ 2. Preprocessing                                          │             │
│  │    ├─ Extract guest name from title                       │             │
│  │    │  (Patterns: "with X", "ft. X", "X on Y")            │             │
│  │    └─ Chunk by paragraphs                                 │             │
│  │       ├─ Split on double newlines                         │             │
│  │       ├─ Extract timestamps [HH:MM:SS]                    │             │
│  │       └─ Preserve paragraph structure                     │             │
│  └──────────────────────────────────────────────────────────┘             │
│                              ↓                                               │
│  ┌──────────────────────────────────────────────────────────┐             │
│  │ 3. Embedding Generation                                   │             │
│  │    ├─ For each paragraph chunk:                           │             │
│  │    │  └─ Generate 384-dim vector (all-MiniLM-L6-v2)      │             │
│  │    └─ Local embedding model (no API calls)                │             │
│  └──────────────────────────────────────────────────────────┘             │
│                              ↓                                               │
│  ┌──────────────────────────────────────────────────────────┐             │
│  │ 4. Index Storage (OpenSearch)                             │             │
│  │    ├─ Store chunk_text, embedding, metadata               │             │
│  │    ├─ Create vector index (HNSW)                          │             │
│  │    └─ Enable hybrid search                                │             │
│  └──────────────────────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA STORAGE LAYER                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────┐  ┌──────────────────────────────────┐ │
│  │   OpenSearch (Port 9200)       │  │  Local File System               │ │
│  ├────────────────────────────────┤  ├──────────────────────────────────┤ │
│  │ Index: podcast-transcripts     │  │  transcripts/                    │ │
│  │                                 │  │  ├─ episode1.txt                 │ │
│  │ Document Schema:                │  │  ├─ episode2.txt                 │ │
│  │ ├─ chunk_id (keyword)           │  │  ├─ episode3.txt                 │ │
│  │ ├─ episode_id (keyword)         │  │  └─ ...                          │ │
│  │ ├─ title (text)                 │  └──────────────────────────────────┘ │
│  │ ├─ podcast_name (keyword)       │                                       │
│  │ ├─ host (text)                  │                                       │
│  │ ├─ guest (text) [extracted]     │                                       │
│  │ ├─ date (date)                  │                                       │
│  │ ├─ chunk_text (text)            │                                       │
│  │ ├─ chunk_index (integer)        │                                       │
│  │ ├─ timestamp (keyword) [parsed] │                                       │
│  │ ├─ topics (keyword[])           │                                       │
│  │ ├─ url (keyword)                │                                       │
│  │ └─ embedding (knn_vector[384])  │                                       │
│  │                                  │                                       │
│  │ Indices:                         │                                       │
│  │ ├─ Text index (BM25)             │                                       │
│  │ └─ Vector index (HNSW)           │                                       │
│  └──────────────────────────────────┘                                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           AI/ML SERVICES LAYER                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────┐  ┌──────────────────────────────────┐ │
│  │  Ollama (Port 11434)           │  │  Sentence Transformers           │ │
│  ├────────────────────────────────┤  ├──────────────────────────────────┤ │
│  │  Model: llama3.2               │  │  Model: all-MiniLM-L6-v2         │ │
│  │  Task: Text Generation         │  │  Task: Text Embedding            │ │
│  │  Use: Answer generation        │  │  Use: Query & document vectors   │ │
│  │  Input: RAG prompt + context   │  │  Output: 384-dim vectors         │ │
│  │  Output: Natural language ans. │  │  Runtime: Local (CPU/GPU)        │ │
│  │  Runtime: Local (CPU/GPU)      │  │  No API keys required            │ │
│  │  No API keys required          │  └──────────────────────────────────┘ │
│  └────────────────────────────────┘                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA FLOW DIAGRAM                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  USER QUERY FLOW:                                                           │
│  ┌──────┐      ┌──────┐      ┌──────────┐      ┌──────┐      ┌──────┐    │
│  │User  │──1──→│Flask │──2──→│Embedding │──3──→│Open  │──4──→│Ollama│    │
│  │      │←─8───│      │←─7───│Model     │      │Search│←─5───│      │    │
│  └──────┘      └──────┘      └──────────┘      └──────┘      └──────┘    │
│                   │                                  ↑                       │
│                   └────────────6─────────────────────┘                       │
│                                                                              │
│  Steps:                                                                     │
│  1. User submits query via web UI                                          │
│  2. Flask receives query, sends to embedding model                         │
│  3. Generate query vector (384-dim)                                        │
│  4. OpenSearch performs hybrid search (BM25 + kNN)                         │
│  5. Returns top-k relevant chunks with scores                              │
│  6. Build context prompt from chunks                                       │
│  7. Ollama generates answer based on context                               │
│  8. Return answer + sources to user                                        │
│                                                                              │
│  INDEXING FLOW:                                                             │
│  ┌──────┐      ┌──────┐      ┌──────────┐      ┌──────┐                  │
│  │.txt  │──1──→│Index │──2──→│Embedding │──3──→│Open  │                  │
│  │Files │      │Script│      │Model     │      │Search│                  │
│  └──────┘      └──────┘      └──────────┘      └──────┘                  │
│                                                                              │
│  Steps:                                                                     │
│  1. Read transcript files from disk                                        │
│  2. Parse & chunk by paragraphs, extract metadata                          │
│  3. Generate embeddings for each chunk                                     │
│  4. Store in OpenSearch with vector index                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          TECHNOLOGY STACK                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Frontend:                                                                  │
│  └─ HTML5, CSS3, JavaScript (Vanilla)                                      │
│                                                                              │
│  Backend:                                                                   │
│  ├─ Python 3.13                                                             │
│  ├─ Flask (Web Framework)                                                   │
│  └─ opensearch-py (Client Library)                                         │
│                                                                              │
│  Search Engine:                                                             │
│  ├─ OpenSearch 2.14.0                                                       │
│  ├─ Lucene Vector Search (HNSW)                                             │
│  └─ BM25 Text Search                                                        │
│                                                                              │
│  AI/ML:                                                                     │
│  ├─ Ollama (LLM Runtime)                                                    │
│  │  └─ Model: llama3.2 (2B parameters)                                     │
│  └─ Sentence Transformers                                                   │
│     └─ Model: all-MiniLM-L6-v2 (384 dimensions)                            │
│                                                                              │
│  Infrastructure:                                                            │
│  ├─ Docker (OpenSearch containerization)                                    │
│  ├─ Python Virtual Environment                                              │
│  └─ macOS (Development environment)                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                        KEY FEATURES & CAPABILITIES                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ✓ Hybrid Search (BM25 + Vector Similarity)                                │
│  ✓ Paragraph-based Chunking (Natural boundaries)                           │
│  ✓ Timestamp Extraction & Preservation                                     │
│  ✓ Guest Name Auto-extraction from Titles                                  │
│  ✓ Free & Local LLM (No API costs)                                         │
│  ✓ Free Local Embeddings (No API costs)                                    │
│  ✓ Real-time Search Results                                                │
│  ✓ Source Attribution with Scores                                          │
│  ✓ Metadata Filtering (Podcast, Topics)                                    │
│  ✓ Responsive Web UI                                                        │
│  ✓ RESTful API                                                              │
│  ✓ Scalable Architecture                                                    │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         DEPLOYMENT ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Current (Development):                                                     │
│  ┌────────────────────────────────────────────────────────┐               │
│  │  macOS Host                                             │               │
│  │  ├─ Flask App (Port 8080)                               │               │
│  │  ├─ Ollama Server (Port 11434)                          │               │
│  │  ├─ OpenSearch Docker (Port 9200, 9600)                 │               │
│  │  └─ Python Virtual Environment                          │               │
│  └────────────────────────────────────────────────────────┘               │
│                                                                              │
│  Production (Recommended):                                                  │
│  ┌────────────────────────────────────────────────────────┐               │
│  │  Load Balancer (nginx)                                  │               │
│  │         ↓                                                │               │
│  │  Flask App Cluster (Gunicorn/uWSGI)                     │               │
│  │         ↓                                                │               │
│  │  OpenSearch Cluster (3+ nodes)                          │               │
│  │         ↓                                                │               │
│  │  Ollama Service (GPU-enabled)                           │               │
│  └────────────────────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          PERFORMANCE METRICS                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Current Statistics:                                                        │
│  ├─ Indexed Episodes: 5                                                     │
│  ├─ Total Chunks: 1,302 paragraphs                                         │
│  ├─ Average Query Time: ~2-5 seconds                                       │
│  │  ├─ Embedding: ~50ms                                                     │
│  │  ├─ OpenSearch: ~100ms                                                   │
│  │  └─ LLM Generation: 2-4s                                                 │
│  ├─ Index Size: ~50-100MB                                                   │
│  └─ No API costs (100% local)                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

## File Structure

```
Rag-Ecommerce/
├── app.py                          # Flask web application
├── podcast_rag.py                  # Core RAG logic
├── index_transcripts.py            # Transcript indexing script
├── test_paragraph_chunking.py      # Testing script
├── scrape_podscribe.py             # Web scraping utility
├── rag_example.py                  # Original e-commerce RAG example
├── templates/
│   └── index.html                  # Web UI
├── transcripts/                    # Transcript text files
│   ├── episode1.txt
│   ├── episode2.txt
│   └── ...
├── docker/
│   └── docker-compose.yml          # OpenSearch configuration
└── .venv/                          # Python virtual environment
```

---

_Generated: November 22, 2025_
