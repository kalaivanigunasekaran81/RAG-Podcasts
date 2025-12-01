#!/bin/bash
# Main run script for Podcast RAG system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Podcast RAG System${NC}"
echo "=================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating template...${NC}"
    cat > .env << EOF
# OpenSearch Configuration
OPENSEARCH_HOST=http://localhost:9200
OPENSEARCH_USER=admin
OPENSEARCH_PASS=admin
PODCAST_INDEX=podcast-transcripts

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# LLM Configuration (llama.cpp) - Multi-Model Support
# Model Selection
PRIMARY_MODEL=phi3_mini
FALLBACK_MODEL=tinyllama
USE_BIGGER_MODEL=false

# Phi-3 Mini (Main LLM)
PHI3_MODEL_PATH=
PHI3_TEMPERATURE=0.2
PHI3_N_CTX=4096

# TinyLlama (Fast Fallback)
TINYLLAMA_MODEL_PATH=
TINYLLAMA_TEMPERATURE=0.2
TINYLLAMA_N_CTX=2048

# Llama-3.1-8B (Bigger Option)
LLAMA3_8B_MODEL_PATH=
LLAMA3_8B_TEMPERATURE=0.2
LLAMA3_8B_N_CTX=8192

# Global LLM Settings (optional overrides)
LLAMA_TEMPERATURE=0.2
LLAMA_MAX_TOKENS=250
LLAMA_N_THREADS=6
LLAMA_N_GPU_LAYERS=35

# Data Configuration
TRANSCRIPTS_DIR=data/transcripts
PODCAST_NAME=Local Transcripts

# API Configuration
PORT=8080
EOF
    echo -e "${GREEN}✅ Created .env file. Please configure it.${NC}"
    echo ""
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies if needed
if [ ! -f ".venv/.deps_installed" ]; then
    echo -e "${YELLOW}📦 Installing dependencies...${NC}"
    pip install -r requirements.txt
    touch .venv/.deps_installed
    echo -e "${GREEN}✅ Dependencies installed${NC}"
fi

# Check command line argument
COMMAND=${1:-server}

case $COMMAND in
    server|api)
        echo -e "${GREEN}🌐 Starting API server...${NC}"
        python3 -m api.server
        ;;
    ingest|index)
        echo -e "${GREEN}📚 Starting ingestion...${NC}"
        python3 -m scripts.ingest
        ;;
    benchmark)
        echo -e "${GREEN}📊 Running benchmark...${NC}"
        bash scripts/benchmark.sh
        ;;
    check-models|models)
        echo -e "${GREEN}🔍 Checking model availability...${NC}"
        python3 scripts/check_models.py
        ;;
    migrate-models)
        echo -e "${GREEN}🔄 Migrating legacy model configuration...${NC}"
        python3 scripts/migrate_models.py
        ;;
    *)
        echo "Usage: ./run.sh [server|ingest|benchmark|check-models|migrate-models]"
        echo ""
        echo "Commands:"
        echo "  server        - Start the Flask API server (default)"
        echo "  ingest        - Index transcripts from data/transcripts/"
        echo "  benchmark     - Run benchmark queries"
        echo "  check-models   - Check which models are available"
        echo "  migrate-models - Migrate from legacy LLAMA_MODEL_PATH"
        exit 1
        ;;
esac

