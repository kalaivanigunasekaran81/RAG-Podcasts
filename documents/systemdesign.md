```markdown
# System Design Document
## Podcast RAG System

### Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Technology Stack](#technology-stack)
6. [Design Decisions](#design-decisions)
7. [Performance Characteristics](#performance-characteristics)
8. [Scalability Considerations](#scalability-considerations)

---

## System Overview

The Podcast RAG (Retrieval-Augmented Generation) system is a production-ready application that enables semantic search and question-answering over podcast transcripts. The system combines hybrid search (BM25 + vector similarity), local LLM inference, and a web-based interface to provide an end-to-end solution for querying podcast content.

### Key Features
- **Hybrid Search**: Combines keyword-based (BM25) and semantic (vector) search
- **Local Processing**: All embeddings and LLM inference run locally (no API costs)
- **Multi-Model Support**: Supports Phi-3 Mini, TinyLlama, and Llama-3.1-8B with automatic fallback
- **Semantic Chunking**: Speaker-aware chunking with overlap for context preservation
- **Reranking**: Optional cross-encoder reranking for improved relevance
- **Web UI**: Interactive interface for querying and exploring transcripts

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                    (Web UI / REST API)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RAG Orchestration Layer                    │
│                         (rag.py)                                │
│  • Query Processing                                             │
│  • Context Building                                             │
│  • Answer Generation                                            │
└────────────┬───────────────────────────┬───────────────────────┘
             │                           │
             ▼                           ▼
┌──────────────────────┐    ┌──────────────────────────────┐
│   Search Layer       │    │      LLM Layer                │
│  (index/)            │    │      (llm/)                   │
│  • Hybrid Search     │    │  • Prompt Building            │
│  • BM25 Search       │    │  • Multi-Model Support        │
│  • Vector Search     │    │  • Answer Generation          │
│  • Reranking         │    │  • Fallback Logic             │
└──────────┬───────────┘    └──────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OpenSearch Backend                           │
│  • Document Storage                                              │
│  • Vector Index (kNN)                                            │
│  • BM25 Index                                                    │
│  • Metadata Filtering                                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    Ingestion Pipeline                           │
│  • Text Cleaning (clean.py)                                      │
│  • Semantic Chunking (chunk.py)                                 │
│  • Embedding Generation (embed.py)                              │
│  • Indexing (vector.py)                                          │
└─────────────────────────────────────────────────────────────────┘
```

### Component Architecture

```
podcasts-rag/
├── api/                    # Web API Layer
│   ├── server.py          # Flask REST API
│   └── templates/         # HTML UI templates
│
├── ingest/                 # Data Ingestion
│   ├── clean.py           # Text normalization
│   ├── chunk.py           # Semantic chunking
│   └── embed.py           # Embedding generation
│
├── index/                  # Search & Indexing
│   ├── vector.py          # Vector search & index management
│   ├── bm25.py            # BM25 keyword search
│   └── hybrid.py          # Hybrid search orchestration
│
├── rerank/                 # Result Reranking
│   └── cross_encoder.py   # Cross-encoder reranking
│
├── llm/                    # LLM Integration
│   └── prompt.py          # Prompt building & generation
│
├── rag.py                  # Main RAG orchestration
└── scripts/                # Utility scripts
```

---

## Core Components

### 1. Ingestion Pipeline (`ingest/`)

#### Text Cleaning (`clean.py`)
- Normalizes transcript text
- Removes artifacts and formatting issues
- Prepares text for chunking

#### Semantic Chunking (`chunk.py`)
**Strategy**: Overlapping semantic windows with speaker awareness

**Key Features**:
- **Speaker-aware splitting**: Detects and preserves speaker boundaries (Host, Guest, etc.)
- **Fallback to paragraphs**: Uses paragraph boundaries if speaker format not detected
- **Overlapping windows**: 40-token overlap (16.7% of 240-token chunks) for context preservation
- **Token estimation**: Uses `words * 1.3` for token counting (no tokenizer dependency)

**Parameters**:
- `max_tokens`: 240 (default)
- `overlap`: 40 tokens (default)

**Output Format**:
```python
{
    "text": "chunk content...",
    "timestamp": None,  # Reserved for future timestamp extraction
    "paragraph_index": 0
}
```

#### Embedding Generation (`embed.py`)
- Uses Sentence Transformers (default: `all-MiniLM-L6-v2`)
- Generates 384-dimensional vectors
- Batch processing support
- Local inference (no API calls)

### 2. Search Layer (`index/`)

#### Vector Search (`vector.py`)
- **kNN Search**: Uses OpenSearch's native kNN capabilities
- **Index Management**: Creates and manages vector indices
- **Metadata Storage**: Stores embeddings alongside text and metadata

**Index Schema**:
```json
{
  "chunk_id": "keyword",
  "episode_id": "keyword",
  "chunk_text": "text",
  "embedding": "knn_vector (384 dim)",
  "title": "text",
  "podcast_name": "keyword",
  "host": "keyword",
  "guest": "keyword",
  "date": "date",
  "topics": "keyword",
  "url": "keyword",
  "chunk_index": "integer"
}
```

#### BM25 Search (`bm25.py`)
- Traditional keyword-based search
- Good for exact matches and named entities
- Fast and efficient

#### Hybrid Search (`hybrid.py`)
- **Combines BM25 + Vector Search**
- Uses OpenSearch's `bool` query with `must` (BM25) and `should` (kNN)
- Configurable weights (default: 0.5 each)
- Supports filtering by podcast name and topics

**Query Structure**:
```json
{
  "query": {
    "bool": {
      "must": [{"match": {"chunk_text": "query"}}],  // BM25
      "should": [{"knn": {"embedding": {...}}}],     // Vector
      "filter": [...]                                 // Metadata filters
    }
  }
}
```

### 3. Reranking (`rerank/`)

#### Cross-Encoder Reranking (`cross_encoder.py`)
- Optional reranking step for improved relevance
- Uses cross-encoder models for query-document scoring
- Re-scores top-k results from hybrid search

### 4. LLM Layer (`llm/`)

#### Multi-Model Support (`prompt.py`)

**Supported Models**:
1. **Phi-3 Mini** (Primary)
   - Context: 4096 tokens
   - Max output: 500 tokens
   - Temperature: 0.2

2. **TinyLlama** (Fast Fallback)
   - Context: 2048 tokens
   - Max output: 250 tokens
   - Temperature: 0.2

3. **Llama-3.1-8B** (Bigger Option)
   - Context: 8192 tokens
   - Max output: 1000 tokens
   - Temperature: 0.2

**Fallback Strategy**:
1. Try primary model (Phi-3 Mini)
2. Fall back to TinyLlama if primary fails
3. Optionally use Llama-3.1-8B for long contexts (>4000 chars)

**Prompt Structure**:
```
You are an assistant that answers questions using ONLY the CONTEXT below.
If the answer is not in the context, respond: 'I don't know.'
When answering, mention the episode title and podcast name, include relevant quotes,
and cite the episode URL if citing specifics. Do not invent information.

CONTEXT:
[Retrieved chunks with metadata]

USER QUESTION:
[User query]

Answer:
```

**Context Building**:
- Formats retrieved chunks with episode metadata
- Truncates long chunks (default: 800 chars) to fit context window
- Includes episode title, podcast name, host, guest, date, URL

### 5. API Layer (`api/`)

#### REST API (`server.py`)
**Endpoints**:
- `GET /`: Web UI
- `POST /api/search`: Query endpoint
  - Input: `{query, top_k, podcast_name}`
  - Output: `{answer, sources, model}`
- `GET /api/stats`: Index statistics
  - Output: `{total_chunks, unique_episodes, unique_podcasts}`

**Features**:
- Error handling and validation
- Source citations with snippets
- Model information in responses

---

## Data Flow

### Ingestion Flow

```
1. Transcript File (data/transcripts/*.txt)
   │
   ▼
2. Text Cleaning (clean.py)
   │
   ▼
3. Semantic Chunking (chunk.py)
   │  • Speaker-aware splitting
   │  • Overlapping windows
   │  • Token estimation
   │
   ▼
4. Embedding Generation (embed.py)
   │  • Sentence Transformer
   │  • 384-dim vectors
   │
   ▼
5. Indexing (vector.py)
   │  • Store in OpenSearch
   │  • Embedding + metadata
   │
   ▼
6. Indexed Chunks (Ready for Search)
```

### Query Flow

```
1. User Query (Web UI / API)
   │
   ▼
2. Query Embedding (embed.py)
   │  • Generate query vector
   │
   ▼
3. Hybrid Search (hybrid.py)
   │  • BM25 + Vector search
   │  • Metadata filtering
   │  • Top-k retrieval
   │
   ▼
4. Optional Reranking (cross_encoder.py)
   │  • Re-score results
   │
   ▼
5. Context Building (prompt.py)
   │  • Format chunks with metadata
   │  • Truncate if needed
   │
   ▼
6. Prompt Construction (prompt.py)
   │  • System instructions
   │  • Context + Query
   │
   ▼
7. LLM Generation (prompt.py)
   │  • Multi-model with fallback
   │  • Answer generation
   │
   ▼
8. Response (API)
   │  • Answer + Sources + Citations
```

---

## Technology Stack

### Core Technologies
- **Python 3.8+**: Main programming language
- **OpenSearch**: Search engine and vector database
- **Sentence Transformers**: Embedding generation
- **llama.cpp**: Local LLM inference
- **Flask**: Web framework

### Key Libraries
- `opensearch-py`: OpenSearch client
- `sentence-transformers`: Embedding models
- `llama-cpp-python`: LLM inference
- `flask`: Web server
- `python-dotenv`: Environment configuration

### Infrastructure
- **Docker**: OpenSearch deployment
- **Local Processing**: All ML inference runs locally

---

## Design Decisions

### 1. Hybrid Search Strategy
**Decision**: Combine BM25 + Vector Search
**Rationale**:
- BM25 excels at exact matches and keywords
- Vector search captures semantic similarity
- Hybrid approach provides best of both worlds

### 2. Overlapping Chunks
**Decision**: 40-token overlap (16.7% of chunk size)
**Rationale**:
- Prevents information loss at boundaries
- Maintains context continuity
- Improves retrieval quality for boundary-spanning queries

### 3. Speaker-Aware Chunking
**Decision**: Prioritize speaker boundaries over fixed-size chunks
**Rationale**:
- Podcasts are conversational
- Speaker turns are natural semantic boundaries
- Preserves dialogue context

### 4. Local Processing
**Decision**: Run all ML inference locally
**Rationale**:
- No API costs
- Data privacy
- Predictable performance
- Offline capability

### 5. Multi-Model Support with Fallback
**Decision**: Support multiple LLMs with automatic fallback
**Rationale**:
- Flexibility for different use cases
- Resilience to model failures
- Performance optimization (fast vs. quality)

### 6. Token Estimation vs. Tokenizer
**Decision**: Use `words * 1.3` instead of tokenizer
**Rationale**:
- No external dependencies
- Fast and lightweight
- Sufficient accuracy for chunking

### 7. Context Truncation
**Decision**: Truncate chunks to 800 chars in prompts
**Rationale**:
- Prevents context window overflow
- Maintains essential information
- Works with smaller models

---

## Performance Characteristics

### Latency Breakdown (Typical Query)
- **Query Embedding**: ~50ms
- **OpenSearch Search**: ~100ms
- **LLM Generation**: 2-4s (depends on model)
- **Total**: ~2-5 seconds

### Throughput
- **Embedding Generation**: ~20 embeddings/second
- **Indexing**: ~10-15 chunks/second
- **Search**: ~10 queries/second

### Resource Usage
- **Memory**: 
  - Embedding model: ~200MB
  - LLM models: 2-8GB (depending on model)
  - OpenSearch: ~500MB-2GB
- **CPU**: Moderate (6 threads default)
- **GPU**: Optional (35 layers default)

### Scalability Limits
- **Current Design**: Single-node, local processing
- **Chunk Limit**: ~100K chunks (tested)
- **Concurrent Queries**: Limited by LLM inference (typically 1-2)

---

## Scalability Considerations

### Current Limitations
1. **Single-Node Processing**: All inference runs on one machine
2. **Sequential LLM Inference**: One query at a time per model
3. **Local Storage**: OpenSearch runs locally (Docker)

### Potential Improvements

#### Horizontal Scaling
- **Distributed OpenSearch**: Multi-node cluster
- **Load Balancing**: Multiple API instances
- **Model Serving**: Dedicated LLM serving layer (vLLM, TensorRT-LLM)

#### Vertical Scaling
- **GPU Acceleration**: More GPU layers for faster inference
- **Larger Models**: Better quality with more capable models
- **Batch Processing**: Batch embedding generation

#### Optimization Strategies
- **Caching**: Cache frequent queries and embeddings
- **Async Processing**: Async LLM inference
- **Model Quantization**: Smaller, faster models
- **Index Optimization**: Tune OpenSearch for better performance

### Production Considerations
- **Monitoring**: Add logging and metrics
- **Error Handling**: Robust error recovery
- **Rate Limiting**: Protect against overload
- **Security**: Authentication and authorization
- **Backup**: Regular index backups

---

## Future Enhancements

1. **Timestamp Extraction**: Extract and preserve timestamps from transcripts
2. **Multi-Modal Support**: Add support for audio/video transcripts
3. **Advanced Reranking**: Implement more sophisticated reranking strategies
4. **Query Expansion**: Automatic query expansion for better retrieval
5. **Conversation History**: Support multi-turn conversations
6. **Analytics**: Query analytics and insights dashboard

---

## Conclusion

The Podcast RAG system is designed as a modular, extensible platform for semantic search over podcast transcripts. The architecture prioritizes local processing, flexibility, and production-readiness while maintaining simplicity and ease of deployment.

The system's hybrid search approach, semantic chunking strategy, and multi-model LLM support provide a robust foundation for querying conversational content with high accuracy and relevance.
```
