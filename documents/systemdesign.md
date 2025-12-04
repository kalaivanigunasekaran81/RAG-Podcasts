
# Podcast RAG System — Architecture & Design

## Overview

The Podcast RAG system is a local, production-grade Retrieval-Augmented Generation platform for searching and answering questions over podcast transcripts. The entire pipeline runs on local infrastructure and does not depend on third‑party LLM APIs. It is designed to offer semantic search, citation‑aware answers, and multi‑model resilience.

The system is divided into three primary layers:

1. Ingestion & Indexing — builds the knowledge base
2. Retrieval & Ranking — finds the most relevant content
3. Answer Generation — produces grounded natural‑language responses

Each layer is independent and replaceable, allowing the system to evolve without architectural rewrites.

---

## Architecture

Refer Rag_Podcasts_architecture.png

### High‑Level Flow

At a high level:

1. Podcast transcripts are cleaned and chunked.
2. Chunks are vectorized using embedding models.
3. The chunk data is indexed into OpenSearch.
4. User queries are embedded and matched through hybrid retrieval.
5. Relevant segments are assembled into a context window.
6. A local LLM generates the final response.

---

### User & API Layer

The system exposes functionality through both:

• A web interface  
• A REST API  

The user submits a question through the interface. The API accepts the request, validates input, and hands off execution to the RAG orchestrator.

Example request:

```
POST /api/search
{
  "query": "What did the guest say about AI in healthcare?",
  "top_k": 5,
  "podcast_name": "AI Today"
}
```

---

### RAG Orchestration Layer

The `rag.py` module acts as the system controller and coordinates:

• Query embedding  
• Hybrid retrieval  
• Optional reranking  
• Context assembly  
• Prompt creation  
• Model selection  
• Final response formatting

This layer contains minimal business logic and focuses on orchestration rather than processing.

---

### Search & Retrieval Layer

The retrieval engine uses two strategies in parallel:

**BM25 keyword search** — captures exact and phrase‑based matches  
**Vector kNN search** — finds semantically similar segments  

Final relevance is computed using weighted scoring:

```
score = 0.5 × BM25 + 0.5 × Vector Similarity
```

An optional cross‑encoder can be enabled to re‑rank high‑confidence matches.

---

### OpenSearch Index

OpenSearch serves as the system’s knowledge store.

It manages:

• Transcript data  
• Metadata  
• Vector embeddings  
• Faceted filters  
• Search statistics

Vector fields are indexed using kNN for efficient nearest‑neighbor search.

---

### LLM Generation Layer

Answer generation runs on `llama.cpp` locally.

Supported models:

• Phi‑3 Mini (Primary)
• TinyLlama (Fast fallback)
• Llama‑3.1‑8B (Extended context)

The fallback engine automatically escalates models on failure or context overflow.

Prompts are strictly controlled. The model is required to respond with "I don’t know" when context does not contain the answer.

---

### Ingestion Pipeline

Transcript processing is fully offline and batch‑driven.

**Flow:**

1. Clean — normalize text and remove artifacts
2. Chunk — speaker‑aware semantic segmentation
3. Embed — convert text to vectors
4. Index — store vectors + metadata

---

### Data Flow Summary

```
Transcript → Cleaning → Chunking → Embedding → Indexing → OpenSearch
```

---

### Query Flow Summary

```
User → Query Embedding → Hybrid Search → Rerank → Context → Prompt → LLM → Answer
```

---

## Performance

Typical latency on consumer hardware:

| Stage | Time |
|-------|------|
| Embeddings | ~50ms |
| Retrieval | ~100ms |
| LLM | 2–4s |

---

## Design Principles

✔ Fully local inference  
✔ Modular architecture  
✔ Transparent relevance scoring  
✔ Zero vendor lock‑in  
✔ Deterministic behavior

---

## Future Enhancements

• GPU inference  
• Conversational memory  
• Index federation  
• Relevance feedback  
• Streaming ingestion
