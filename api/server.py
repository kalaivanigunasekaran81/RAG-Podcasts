"""
Flask web application for querying podcast transcripts
Optimized for modular RAG + local LLM on M2 Mac
"""

import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load .env file automatically
load_dotenv()

from rag import (
    ask_podcast_question,
    embed_text,
    search_transcripts
)
from index import get_opensearch_client
from index.vector import PODCAST_INDEX

app = Flask(__name__, template_folder='../templates')

# -----------------------------
# Initialize OpenSearch client
# -----------------------------
try:
    client = get_opensearch_client()
    print("✅ Connected to OpenSearch")
except Exception as e:
    print(f"❌ OpenSearch connection failed: {e}")
    client = None


@app.route('/')
def index():
    """Render main UI"""
    return render_template('index.html')


@app.route('/api/search', methods=['POST'])
def search():
    """
    API endpoint for querying podcast transcripts via RAG
    """
    try:
        if not client:
            return jsonify({"error": "OpenSearch not available"}), 503

        data = request.get_json(force=True)
        query = data.get("query", "").strip()
        podcast_name = data.get("podcast_name")
        top_k = int(data.get("top_k", 5))

        if not query:
            return jsonify({"error": "Query is required"}), 400

        # Answer via LLM
        answer = ask_podcast_question(
            client,
            user_query=query,
            podcast_name=podcast_name or None,
            top_k=top_k,
        )

        # Retrieve hits for citations
        query_emb = embed_text(query)
        hits = search_transcripts(
            client,
            user_query=query,
            query_embedding=query_emb,
            size=top_k,
            podcast_name=podcast_name or None,
        )

        # Build citation sources
        sources = []
        for hit in hits:
            src = hit.get("_source", {})
            snippet = src.get("chunk_text", "")
            snippet = snippet[:350] + "..." if len(snippet) > 350 else snippet

            sources.append(
                {
                    "episode_title": src.get("title", "Unknown"),
                    "podcast_name": src.get("podcast_name", "Unknown"),
                    "guest": src.get("guest") or "Unknown",
                    "date": src.get("date", ""),
                    "timestamp": src.get("timestamp", ""),
                    "chunk_text": snippet,
                    "url": src.get("url", ""),
                    "score": round(hit.get("_score", 0), 3),
                }
            )

        # Determine which model was used
        primary_model = os.getenv("PRIMARY_MODEL", "phi3_mini")
        model_info = f"{primary_model} (primary)"
        if os.getenv("PHI3_MODEL_PATH"):
            model_info = f"Phi-3 Mini ({os.getenv('PHI3_MODEL_PATH', 'configured')})"
        elif os.getenv("TINYLLAMA_MODEL_PATH"):
            model_info = f"TinyLlama ({os.getenv('TINYLLAMA_MODEL_PATH', 'configured')})"
        elif os.getenv("LLAMA3_8B_MODEL_PATH"):
            model_info = f"Llama-3.1-8B ({os.getenv('LLAMA3_8B_MODEL_PATH', 'configured')})"
        
        return jsonify(
            {
                "query": query,
                "answer": answer,
                "sources": sources,
                "model": model_info,
            }
        )

    except Exception as e:
        print(f"🔥 Search error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def stats():
    """
    Index statistics endpoint
    """
    try:
        if not client:
            return jsonify({"error": "OpenSearch not available"}), 503

        # Total chunk count
        count_result = client.count(index=PODCAST_INDEX)
        total_chunks = count_result.get("count", 0)

        # Unique episode + podcast counts
        agg_query = {
            "size": 0,
            "aggs": {
                "unique_episodes": {"cardinality": {"field": "episode_id"}},
                "unique_podcasts": {"cardinality": {"field": "podcast_name"}},
            },
        }

        agg_result = client.search(index=PODCAST_INDEX, body=agg_query)

        return jsonify(
            {
                "total_chunks": total_chunks,
                "unique_episodes": agg_result["aggregations"]["unique_episodes"]["value"],
                "unique_podcasts": agg_result["aggregations"]["unique_podcasts"]["value"],
            }
        )

    except Exception as e:
        print(f"🔥 Stats error: {e}")
        return jsonify({"error": str(e)}), 500


# -----------------------------
# Startup
# -----------------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    print("\n🚀 Podcast RAG Web UI Running")
    print(f"🌐 Open in browser: http://localhost:{port}\n")

    app.run(host="0.0.0.0", port=port, debug=True)

