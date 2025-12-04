# Podcast RAG

Podcast RAG is a local Retrieval‑Augmented Generation system that enables semantic search and question answering over podcast transcripts.

## Features

✅ Hybrid search (BM25 + Vector search)  
✅ Local LLM inference  
✅ Multi‑model fallback  
✅ Speaker‑aware chunking  
✅ Explainable answers  
✅ Offline indexing

---

## Project Structure

```
podcasts-rag/
├── api/        # Web UI and REST API
├── ingest/     # Transcript ingestion
├── index/      # Search layer
├── llm/        # Prompt & generation
├── rerank/     # Optional reranking
├── rag.py      # Orchestrator
```

---

## Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run ingestion

```bash
python ingest/run.py
```

### 3. Start server

```bash
python api/server.py
```

Open: http://localhost:5000

---

## Example Query

"What did the guest say about AI regulation?"

---

## Tech Stack

• Python  
• Flask  
• OpenSearch  
• Sentence Transformers  
• llama.cpp
