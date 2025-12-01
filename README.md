# Podcast RAG System

A production-ready Retrieval-Augmented Generation (RAG) system for searching and querying podcast transcripts using OpenSearch, sentence transformers, and local LLMs.

## Architecture

```
podcasts-rag/
├── data/
│   └── transcripts/          # Transcript text files
├── ingest/                   # Data ingestion pipeline
│   ├── clean.py             # Text cleaning utilities
│   ├── chunk.py              # Text chunking strategies
│   └── embed.py              # Embedding generation
├── index/                    # Search indexing
│   ├── bm25.py               # BM25 keyword search
│   ├── vector.py             # Vector search & index management
│   └── hybrid.py             # Hybrid BM25 + vector search
├── rerank/                   # Result reranking
│   └── cross_encoder.py      # Cross-encoder reranking
├── api/                      # Web API
│   ├── server.py             # Flask web server
│   └── templates/            # HTML templates
├── llm/                      # LLM integration
│   └── prompt.py             # Prompt building & generation
├── scripts/                   # Utility scripts
│   ├── ingest.py             # Transcript ingestion script
│   └── benchmark.sh          # Benchmarking script
├── rag.py                    # Main RAG orchestration
├── run.sh                    # Main entry point
└── requirements.txt          # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenSearch (via Docker)
- Local LLM model (optional, for answer generation)

### Installation

1. **Clone and setup:**
   ```bash
   git clone <repo-url>
   cd podcasts-rag
   ./run.sh  # This will create venv and install dependencies
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env  # Edit .env with your settings
   ```

3. **Start OpenSearch:**
   ```bash
   docker-compose -f docker/docker-compose.yml up -d
   ```

4. **Ingest transcripts:**
   ```bash
   ./run.sh ingest
   ```

5. **Start API server:**
   ```bash
   ./run.sh server
   ```

6. **Access the web UI:**
   Open http://localhost:8080 in your browser

## 📚 Usage

### Ingesting Transcripts

Place transcript files in `data/transcripts/` as `.txt` files, then run:

```bash
./run.sh ingest
```

Or use the Python script directly:

```bash
python -m scripts.ingest
```

### Querying via API

```bash
curl -X POST http://localhost:8080/api/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is machine learning?",
    "top_k": 5
  }'
```

### Programmatic Usage

```python
from rag import get_opensearch_client, ask_podcast_question
from index import get_opensearch_client

client = get_opensearch_client()
answer = ask_podcast_question(
    client,
    user_query="What did they say about AI?",
    top_k=5
)
print(answer)
```

## 🔧 Configuration

Environment variables (set in `.env`):

### OpenSearch
- `OPENSEARCH_HOST`: OpenSearch host (default: http://localhost:9200)
- `OPENSEARCH_USER`: Username (default: admin)
- `OPENSEARCH_PASS`: Password (default: admin)
- `PODCAST_INDEX`: Index name (default: podcast-transcripts)

### Embeddings
- `EMBEDDING_MODEL`: Sentence transformer model (default: sentence-transformers/all-MiniLM-L6-v2)

### LLM (llama.cpp) - Multi-Model Support

The system supports three models with automatic fallback:

**Model Configuration:**
- `PRIMARY_MODEL`: Primary model to use (default: `phi3_mini`)
  - Options: `phi3_mini`, `tinyllama`, `llama3_8b`
- `FALLBACK_MODEL`: Fallback model if primary fails (default: `tinyllama`)
- `USE_BIGGER_MODEL`: Enable bigger model for long contexts (default: `false`)

**Phi-3 Mini (Main LLM):**
- `PHI3_MODEL_PATH`: Path to Phi-3 Mini .gguf model file
- `PHI3_TEMPERATURE`: Temperature (default: 0.2)
- `PHI3_N_CTX`: Context window (default: 4096)
- Default max tokens: 500

**TinyLlama (Fast Fallback):**
- `TINYLLAMA_MODEL_PATH`: Path to TinyLlama .gguf model file
- `TINYLLAMA_TEMPERATURE`: Temperature (default: 0.2)
- `TINYLLAMA_N_CTX`: Context window (default: 2048)
- Default max tokens: 250

**Llama-3.1-8B (Bigger Option):**
- `LLAMA3_8B_MODEL_PATH`: Path to Llama-3.1-8B .gguf model file
- `LLAMA3_8B_TEMPERATURE`: Temperature (default: 0.2)
- `LLAMA3_8B_N_CTX`: Context window (default: 8192)
- Default max tokens: 1000

**Global LLM Settings:**
- `LLAMA_TEMPERATURE`: Override temperature for all models (optional)
- `LLAMA_MAX_TOKENS`: Override max tokens for all models (optional)
- `LLAMA_N_THREADS`: Threads (default: 6)
- `LLAMA_N_GPU_LAYERS`: GPU layers (default: 35)

### Data
- `TRANSCRIPTS_DIR`: Transcript directory (default: data/transcripts)
- `PODCAST_NAME`: Default podcast name (default: Local Transcripts)

### API
- `PORT`: Server port (default: 8080)

## 🧪 Testing

Run benchmarks:

```bash
./run.sh benchmark
```

Or use the test script:

```bash
python test_paragraph_chunking.py
```

## 📦 Modules

### Ingest Module
- **clean.py**: Text cleaning and normalization
- **chunk.py**: Semantic chunking with overlap
- **embed.py**: Embedding generation using sentence transformers

### Index Module
- **bm25.py**: BM25 keyword search
- **vector.py**: Vector similarity search and index management
- **hybrid.py**: Combined BM25 + vector search

### Rerank Module
- **cross_encoder.py**: Cross-encoder reranking for improved relevance

### LLM Module
- **prompt.py**: RAG prompt construction and answer generation

### API Module
- **server.py**: Flask REST API with web UI

## 🎯 Features

- ✅ Hybrid search (BM25 + Vector similarity)
- ✅ Paragraph-based chunking with overlap
- ✅ Guest name extraction from titles
- ✅ Timestamp preservation
- ✅ Local LLM support (no API costs)
- ✅ Local embeddings (no API costs)
- ✅ Reranking support
- ✅ RESTful API
- ✅ Web UI
- ✅ Production-ready structure

## 🔍 Search Strategies

The system supports three search strategies:

1. **BM25**: Keyword-based search (fast, good for exact matches)
2. **Vector**: Semantic similarity search (good for conceptual queries)
3. **Hybrid**: Combines both for best results (default)

## 📊 Performance

- Query latency: ~2-5 seconds (depending on LLM)
- Embedding generation: ~50ms
- OpenSearch search: ~100ms
- LLM generation: 2-4s

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

[Your License Here]

## Acknowledgments

- OpenSearch for search infrastructure
- Sentence Transformers for embeddings
- llama.cpp for local LLM inference

