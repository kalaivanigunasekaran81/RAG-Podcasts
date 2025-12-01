# LLM Model Setup Guide

This guide explains how to configure and use the multi-model LLM system.

## Supported Models

| Purpose       | Model        | Default Config |
| ------------- | ------------ | -------------- |
| Main LLM      | Phi-3 Mini   | Primary model  |
| Fast fallback | TinyLlama    | Fallback model |
| Bigger option | Llama-3.1-8B | Optional       |

## Model Selection Strategy

1. **Primary Model (Phi-3 Mini)**: Used by default for all queries
2. **Fallback Model (TinyLlama)**: Automatically used if primary model fails or is unavailable
3. **Bigger Model (Llama-3.1-8B)**: Used for long contexts (>4000 chars) when enabled

## Downloading Models

### Phi-3 Mini
```bash
# Download from Hugging Face (example)
# Visit: https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf
# Download a quantized version (Q4_K_M recommended)
```

### TinyLlama
```bash
# Download from Hugging Face
# Visit: https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF
# Download Q4_K_M or Q5_K_M version
```

### Llama-3.1-8B
```bash
# Download from Hugging Face
# Visit: https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct
# Download a quantized GGUF version
```

## Configuration

### Basic Setup (Phi-3 Mini only)

Add to your `.env` file:

```bash
# Primary model
PRIMARY_MODEL=phi3_mini
PHI3_MODEL_PATH=/path/to/phi-3-mini.gguf

# Fallback model (optional but recommended)
FALLBACK_MODEL=tinyllama
TINYLLAMA_MODEL_PATH=/path/to/tinyllama.gguf
```

### Full Setup (All Models)

```bash
# Model selection
PRIMARY_MODEL=phi3_mini
FALLBACK_MODEL=tinyllama
USE_BIGGER_MODEL=true

# Phi-3 Mini (Main)
PHI3_MODEL_PATH=/path/to/phi-3-mini.gguf
PHI3_TEMPERATURE=0.2
PHI3_N_CTX=4096

# TinyLlama (Fallback)
TINYLLAMA_MODEL_PATH=/path/to/tinyllama.gguf
TINYLLAMA_TEMPERATURE=0.2
TINYLLAMA_N_CTX=2048

# Llama-3.1-8B (Bigger)
LLAMA3_8B_MODEL_PATH=/path/to/llama-3.1-8b.gguf
LLAMA3_8B_TEMPERATURE=0.2
LLAMA3_8B_N_CTX=8192

# Global settings (optional overrides)
LLAMA_N_THREADS=6
LLAMA_N_GPU_LAYERS=35
```

## Model Behavior

### Automatic Fallback

The system automatically falls back to TinyLlama if:
- Primary model fails to load
- Primary model encounters an error during generation
- Context window is exceeded

### Long Context Handling

When `USE_BIGGER_MODEL=true` and prompt length > 4000 characters:
- System automatically uses Llama-3.1-8B for better context handling
- Falls back to primary/fallback if bigger model unavailable

### Error Handling

1. **Model not found**: Falls back to next available model
2. **Context window exceeded**: Reduces max_tokens and retries
3. **Generation error**: Tries fallback model
4. **All models fail**: Returns error message

## Performance Considerations

### Model Sizes (approximate)

- **TinyLlama**: ~700MB (Q4_K_M)
- **Phi-3 Mini**: ~2.4GB (Q4_K_M)
- **Llama-3.1-8B**: ~4.6GB (Q4_K_M)

### Speed Comparison

- **TinyLlama**: Fastest (~100-200ms per token)
- **Phi-3 Mini**: Medium (~200-400ms per token)
- **Llama-3.1-8B**: Slowest (~400-800ms per token)

### Memory Requirements

- **TinyLlama**: ~2GB RAM
- **Phi-3 Mini**: ~4GB RAM
- **Llama-3.1-8B**: ~8GB RAM

## Usage Examples

### Using Specific Model

```python
from llm import generate_answer

# Use Phi-3 Mini
answer = generate_answer(prompt, model_preference="phi3_mini")

# Use TinyLlama
answer = generate_answer(prompt, model_preference="tinyllama")

# Use Llama-3.1-8B
answer = generate_answer(prompt, model_preference="llama3_8b")
```

### Automatic Model Selection

```python
from llm import generate_answer

# System automatically selects best model
answer = generate_answer(prompt)

# For long contexts, enable bigger model
answer = generate_answer(prompt, use_bigger_for_long_context=True)
```

## Troubleshooting

### Model Not Loading

1. Check model path is correct
2. Verify model file exists and is readable
3. Check file format (must be .gguf)
4. Verify llama-cpp-python is installed: `pip install llama-cpp-python`

### Out of Memory

1. Use smaller quantized models (Q4_K_M or Q3_K_M)
2. Reduce `LLAMA_N_GPU_LAYERS` if using GPU
3. Close other applications
4. Use TinyLlama as primary for lower memory usage

### Slow Performance

1. Use TinyLlama for faster responses
2. Reduce `LLAMA_MAX_TOKENS`
3. Enable GPU acceleration (set `LLAMA_N_GPU_LAYERS` > 0)
4. Use smaller context windows

## Recommended Configurations

### Development (Fast)
```bash
PRIMARY_MODEL=tinyllama
TINYLLAMA_MODEL_PATH=/path/to/tinyllama.gguf
```

### Production (Balanced)
```bash
PRIMARY_MODEL=phi3_mini
PHI3_MODEL_PATH=/path/to/phi-3-mini.gguf
FALLBACK_MODEL=tinyllama
TINYLLAMA_MODEL_PATH=/path/to/tinyllama.gguf
```

### High Quality (Slower)
```bash
PRIMARY_MODEL=llama3_8b
LLAMA3_8B_MODEL_PATH=/path/to/llama-3.1-8b.gguf
FALLBACK_MODEL=phi3_mini
PHI3_MODEL_PATH=/path/to/phi-3-mini.gguf
USE_BIGGER_MODEL=true
```

