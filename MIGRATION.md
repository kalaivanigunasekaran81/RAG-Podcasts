# Migration Guide: Old Structure → New Production Structure

## Overview

The project has been restructured from a monolithic structure to a production-ready modular architecture.

## Directory Structure Changes

### Old Structure
```
podcasts-rag/
├── app.py
├── podcast_rag.py
├── chunking.py
├── index_transcripts.py
├── transcripts/
└── templates/
```

### New Structure
```
podcasts-rag/
├── data/
│   └── transcripts/          # Moved from transcripts/
├── ingest/
│   ├── clean.py             # New: Text cleaning
│   ├── chunk.py              # From chunking.py
│   └── embed.py              # Extracted from podcast_rag.py
├── index/
│   ├── bm25.py               # New: BM25 search
│   ├── vector.py             # Extracted from podcast_rag.py
│   └── hybrid.py             # Extracted from podcast_rag.py
├── rerank/
│   └── cross_encoder.py      # New: Reranking support
├── api/
│   ├── server.py             # From app.py
│   └── templates/           # Moved from templates/
├── llm/
│   └── prompt.py             # Extracted from podcast_rag.py
├── scripts/
│   ├── ingest.py             # From index_transcripts.py
│   └── benchmark.sh         # New: Benchmarking
├── rag.py                    # New: Main RAG orchestration
└── run.sh                    # New: Entry point
```

## Code Migration

### Import Changes

**Old:**
```python
from podcast_rag import (
    get_opensearch_client,
    ask_podcast_question,
    embed_text
)
from chunking import chunk_by_semantic_windows
```

**New:**
```python
from rag import ask_podcast_question, embed_text
from index import get_opensearch_client
from ingest import chunk_by_semantic_windows
```

### Running the Application

**Old:**
```bash
python app.py
```

**New:**
```bash
./run.sh server
# or
python -m api.server
```

### Ingesting Transcripts

**Old:**
```bash
python index_transcripts.py
```

**New:**
```bash
./run.sh ingest
# or
python -m scripts.ingest
```

## Backward Compatibility

The old files (`app.py`, `podcast_rag.py`, `chunking.py`, `index_transcripts.py`) are still present for reference but are deprecated. They will be removed in a future version.

## Benefits of New Structure

1. **Modularity**: Each component has a clear responsibility
2. **Testability**: Modules can be tested independently
3. **Scalability**: Easy to add new search strategies, rerankers, etc.
4. **Maintainability**: Clear separation of concerns
5. **Production-ready**: Follows best practices for Python projects

## Migration Checklist

- [x] Create new directory structure
- [x] Move transcripts to data/transcripts/
- [x] Refactor chunking logic
- [x] Split podcast_rag.py into modules
- [x] Create API server module
- [x] Create ingestion script
- [x] Create benchmark script
- [x] Update all imports
- [x] Create README
- [ ] Update existing scripts that import old modules
- [ ] Test all functionality
- [ ] Remove old files (optional)

