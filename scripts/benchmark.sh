#!/bin/bash
# Benchmark script for podcast RAG system

set -e

echo "🚀 Starting Podcast RAG Benchmark"
echo "=================================="
echo ""

# Check if OpenSearch is running
echo "📊 Checking OpenSearch connection..."
python3 -c "from index import get_opensearch_client; get_opensearch_client()" || {
    echo "❌ OpenSearch is not running. Please start it first."
    exit 1
}

echo "✅ OpenSearch is running"
echo ""

# Test queries
QUERIES=(
    "What is machine learning?"
    "How does AI work?"
    "What are the benefits of exercise?"
    "Tell me about nutrition"
    "What is the future of technology?"
)

echo "🔍 Running benchmark queries..."
echo ""

for query in "${QUERIES[@]}"; do
    echo "Query: $query"
    start_time=$(date +%s.%N)
    
    python3 -c "
from rag import get_opensearch_client, ask_podcast_question
client = get_opensearch_client()
answer = ask_podcast_question(client, '$query', top_k=5)
print('Answer:', answer[:100] + '...' if len(answer) > 100 else answer)
" || echo "❌ Query failed"
    
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc)
    echo "⏱️  Time: ${duration}s"
    echo ""
done

echo "✅ Benchmark complete"

