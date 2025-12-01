#!/bin/bash
# Script to download LLM models to /Users/kalaivanigunasekaran/models

set -e

MODELS_DIR="/Users/kalaivanigunasekaran/models"
mkdir -p "$MODELS_DIR"

echo "📦 Downloading LLM Models to $MODELS_DIR"
echo "=========================================="
echo ""

# Check if huggingface-cli is available
if ! command -v huggingface-cli &> /dev/null && ! command -v hf &> /dev/null; then
    echo "❌ huggingface-cli not found. Install with: pip install huggingface-hub"
    exit 1
fi

# Use hf if available, otherwise huggingface-cli
HF_CMD="hf"
if ! command -v hf &> /dev/null; then
    HF_CMD="huggingface-cli"
fi

cd "$MODELS_DIR"

# Function to download a model
download_model() {
    local repo=$1
    local filename=$2
    local description=$3
    
    echo "📥 Downloading $description..."
    echo "   Repository: $repo"
    echo "   File: $filename"
    
    if [ -f "$filename" ]; then
        echo "   ✅ File already exists: $filename"
        return 0
    fi
    
    $HF_CMD download "$repo" "$filename" --local-dir . --local-dir-use-symlinks False
    
    if [ -f "$filename" ]; then
        size=$(ls -lh "$filename" | awk '{print $5}')
        echo "   ✅ Downloaded: $filename ($size)"
    else
        echo "   ❌ Download failed: $filename"
        return 1
    fi
    echo ""
}

# TinyLlama (Fast Fallback)
download_model \
    "TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF" \
    "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf" \
    "TinyLlama (Fast Fallback)"

# Phi-3 Mini (Main LLM) - Optional
read -p "Download Phi-3 Mini? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    download_model \
        "microsoft/Phi-3-mini-4k-instruct-gguf" \
        "Phi-3-mini-4k-instruct-q4.gguf" \
        "Phi-3 Mini (Main LLM)"
fi

# Llama-3.1-8B - Optional (user already has this)
read -p "Download Llama-3.1-8B? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    download_model \
        "bartowski/Meta-Llama-3.1-8B-Instruct-GGUF" \
        "Meta-Llama-3.1-8B-Instruct.Q4_K_M.gguf" \
        "Llama-3.1-8B (Bigger Option)"
fi

echo "=========================================="
echo "✅ Download complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Update your .env file with model paths:"
echo "      TINYLLAMA_MODEL_PATH=$MODELS_DIR/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
echo ""
echo "   2. Run: ./run.sh check-models"
echo "      to verify model configuration"

