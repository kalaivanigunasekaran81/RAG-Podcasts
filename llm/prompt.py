"""
Prompt building and LLM answer generation with multi-model support.
Supports Phi-3 Mini (main), TinyLlama (fast fallback), and Llama-3.1-8B (bigger option).
"""

import os
from typing import List, Dict, Any, Optional, Literal
from enum import Enum

try:
    from llama_cpp import Llama
except ImportError:
    Llama = None


class ModelType(str, Enum):
    """Supported model types."""
    PHI3_MINI = "phi3_mini"      # Main LLM
    TINYLLAMA = "tinyllama"      # Fast fallback
    LLAMA3_8B = "llama3_8b"      # Bigger option


# Model configuration
MODEL_CONFIGS = {
    ModelType.PHI3_MINI: {
        "path_env": "PHI3_MODEL_PATH",
        "default_max_tokens": 500,
        "default_n_ctx": 4096,
        "default_temperature": 0.2,
        "description": "Phi-3 Mini (Main LLM)",
    },
    ModelType.TINYLLAMA: {
        "path_env": "TINYLLAMA_MODEL_PATH",
        "default_max_tokens": 250,
        "default_n_ctx": 2048,
        "default_temperature": 0.2,
        "description": "TinyLlama (Fast Fallback)",
    },
    ModelType.LLAMA3_8B: {
        "path_env": "LLAMA3_8B_MODEL_PATH",
        "default_max_tokens": 1000,
        "default_n_ctx": 8192,
        "default_temperature": 0.2,
        "description": "Llama-3.1-8B (Bigger Option)",
    },
}

# Model selection and fallback configuration
PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "phi3_mini").lower()
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "tinyllama").lower()
USE_BIGGER_MODEL = os.getenv("USE_BIGGER_MODEL", "false").lower() == "true"

# Global model instances
_loaded_models: Dict[ModelType, Optional[Llama]] = {
    ModelType.PHI3_MINI: None,
    ModelType.TINYLLAMA: None,
    ModelType.LLAMA3_8B: None,
}

LLAMA_N_THREADS = int(os.getenv("LLAMA_N_THREADS", "6"))
LLAMA_N_GPU_LAYERS = int(os.getenv("LLAMA_N_GPU_LAYERS", "35"))

# Maximum characters to keep per retrieved chunk when building the prompt.
CONTEXT_CHUNK_MAX_CHARS = int(os.getenv("CONTEXT_CHUNK_MAX_CHARS", "800"))


def _get_model_path(model_type: ModelType) -> Optional[str]:
    """
    Get the model path for a given model type.
    Also checks legacy LLAMA_MODEL_PATH for backward compatibility.
    """
    config = MODEL_CONFIGS[model_type]
    path = os.getenv(config["path_env"])
    
    # Legacy support: if no path set, check legacy LLAMA_MODEL_PATH
    # This helps with migration from old single-model setup
    if not path:
        legacy_path = os.getenv("LLAMA_MODEL_PATH")
        if legacy_path:
            # Map legacy path to appropriate model based on filename
            legacy_lower = legacy_path.lower()
            if model_type == ModelType.LLAMA3_8B and ("llama" in legacy_lower or "8b" in legacy_lower):
                print(f"⚠️  Using legacy LLAMA_MODEL_PATH for {model_type.value}")
                return legacy_path
            elif model_type == ModelType.PHI3_MINI and "phi" in legacy_lower:
                print(f"⚠️  Using legacy LLAMA_MODEL_PATH for {model_type.value}")
                return legacy_path
            elif model_type == ModelType.TINYLLAMA and "tiny" in legacy_lower:
                print(f"⚠️  Using legacy LLAMA_MODEL_PATH for {model_type.value}")
                return legacy_path
    
    return path


def _load_model(model_type: ModelType) -> Llama:
    """
    Load a specific model type.
    
    Args:
        model_type: Type of model to load
    
    Returns:
        Loaded Llama model instance
    
    Raises:
        RuntimeError: If llama-cpp-python is not installed or model path is not set
    """
    if Llama is None:
        raise RuntimeError(
            "`llama-cpp-python` is required. Install it with: `pip install llama-cpp-python`."
        )
    
    # Check if already loaded
    if _loaded_models[model_type] is not None:
        return _loaded_models[model_type]
    
    # Get model path
    model_path = _get_model_path(model_type)
    if not model_path:
        raise RuntimeError(
            f"Model path not set for {model_type.value}. "
            f"Set {MODEL_CONFIGS[model_type]['path_env']} environment variable."
        )
    
    config = MODEL_CONFIGS[model_type]
    
    # Get model-specific config or use defaults
    n_ctx = int(os.getenv(f"{model_type.value.upper()}_N_CTX", config["default_n_ctx"]))
    temperature = float(os.getenv(f"{model_type.value.upper()}_TEMPERATURE", config["default_temperature"]))
    
    print(f"Loading {config['description']} from: {model_path}")
    print(
        f"Config -> n_ctx={n_ctx}, "
        f"n_threads={LLAMA_N_THREADS}, n_gpu_layers={LLAMA_N_GPU_LAYERS}, "
        f"temperature={temperature}"
    )
    
    model = Llama(
        model_path=model_path,
        temperature=temperature,
        n_ctx=n_ctx,
        n_threads=LLAMA_N_THREADS,
        n_gpu_layers=LLAMA_N_GPU_LAYERS,
    )
    
    _loaded_models[model_type] = model
    return model


def _get_model_type_from_string(model_str: str) -> ModelType:
    """Convert string to ModelType enum."""
    model_str = model_str.lower()
    if model_str in ["phi3", "phi3_mini", "phi-3-mini"]:
        return ModelType.PHI3_MINI
    elif model_str in ["tinyllama", "tiny-llama"]:
        return ModelType.TINYLLAMA
    elif model_str in ["llama3", "llama3_8b", "llama-3.1-8b", "llama-3-8b"]:
        return ModelType.LLAMA3_8B
    else:
        raise ValueError(f"Unknown model type: {model_str}")


def _get_primary_model() -> Llama:
    """Get the primary model (Phi-3 Mini by default)."""
    try:
        model_type = _get_model_type_from_string(PRIMARY_MODEL)
        return _load_model(model_type)
    except (ValueError, RuntimeError) as e:
        print(f"⚠️  Failed to load primary model ({PRIMARY_MODEL}): {e}")
        # Try fallback
        return _get_fallback_model()


def _get_fallback_model() -> Llama:
    """Get the fallback model (TinyLlama by default)."""
    try:
        model_type = _get_model_type_from_string(FALLBACK_MODEL)
        return _load_model(model_type)
    except (ValueError, RuntimeError) as e:
        raise RuntimeError(
            f"Failed to load fallback model ({FALLBACK_MODEL}): {e}. "
            "Please configure at least one model path."
        )


def _get_bigger_model() -> Optional[Llama]:
    """Get the bigger model (Llama-3.1-8B) if configured."""
    if not USE_BIGGER_MODEL:
        return None
    try:
        return _load_model(ModelType.LLAMA3_8B)
    except RuntimeError as e:
        print(f"⚠️  Bigger model not available: {e}")
        return None


def build_context(hits: List[Dict[str, Any]]) -> str:
    """
    Build context string from search hits.
    
    Args:
        hits: List of search hits with _source containing chunk data
    
    Returns:
        Formatted context string
    """
    chunks: List[str] = []
    for h in hits:
        src = h["_source"]
        guest_info = f" with {src['guest']}" if src.get("guest") else ""
        timestamp_info = f" [{src['timestamp']}]" if src.get("timestamp") else ""
        # Truncate long chunk text to reduce prompt size (short-term safety fix).
        chunk_text = src.get("chunk_text", "") or ""
        if CONTEXT_CHUNK_MAX_CHARS and len(chunk_text) > CONTEXT_CHUNK_MAX_CHARS:
            # Truncate at a word boundary and add an ellipsis marker.
            truncated = chunk_text[:CONTEXT_CHUNK_MAX_CHARS]
            if " " in truncated:
                truncated = truncated.rsplit(" ", 1)[0]
            chunk_text = truncated + "... [truncated]"

        chunks.append(
            f"EPISODE: {src['title']}\n"
            f"PODCAST: {src['podcast_name']} - Host: {src['host']}{guest_info}\n"
            f"DATE: {src['date']}{timestamp_info}\n"
            f"URL: {src['url']}\n"
            f"TRANSCRIPT:\n{chunk_text}\n"
            "---"
        )
    return "\n\n".join(chunks)


def build_podcast_prompt(user_query: str, context: str) -> str:
    """
    Build a RAG prompt for the LLM.
    
    Args:
        user_query: User's question
        context: Retrieved context from search
    
    Returns:
        Complete prompt string
    """
    # Shortened system instructions to reduce prompt size while keeping
    # essential constraints. This helps avoid small-model context-window errors.
    return (
        "You are an assistant that answers questions using ONLY the CONTEXT below. "
        "If the answer is not in the context, respond: 'I don't know.' "
        "When answering, mention the episode title and podcast name, include relevant quotes, "
        "and cite the episode URL if citing specifics. Do not invent information.\n\n"
        "CONTEXT:\n"
        f"{context}\n\n"
        "USER QUESTION:\n"
        f"{user_query}\n\n"
        "Answer:\n"
    )


def generate_answer(
    prompt: str,
    model_preference: Optional[Literal["phi3_mini", "tinyllama", "llama3_8b"]] = None,
    use_bigger_for_long_context: bool = False,
) -> str:
    """
    Generate an answer using available LLM models with fallback support.
    
    Args:
        prompt: Complete prompt string
        model_preference: Optional model preference (overrides default)
        use_bigger_for_long_context: If True and prompt is long, use bigger model
    
    Returns:
        Generated answer text
    """
    # Determine which model to use
    model = None
    model_name = "unknown"
    max_tokens = 250
    temperature = 0.2
    
    # Check if we should use bigger model for long contexts
    if use_bigger_for_long_context and len(prompt) > 4000:
        bigger_model = _get_bigger_model()
        if bigger_model:
            model = bigger_model
            model_name = "Llama-3.1-8B"
            max_tokens = MODEL_CONFIGS[ModelType.LLAMA3_8B]["default_max_tokens"]
            temperature = MODEL_CONFIGS[ModelType.LLAMA3_8B]["default_temperature"]
            print("📊 Using bigger model for long context")
    
    # Use model preference if specified
    if model is None and model_preference:
        try:
            model_type = _get_model_type_from_string(model_preference)
            model = _load_model(model_type)
            model_name = MODEL_CONFIGS[model_type]["description"]
            max_tokens = MODEL_CONFIGS[model_type]["default_max_tokens"]
            temperature = MODEL_CONFIGS[model_type]["default_temperature"]
        except (ValueError, RuntimeError) as e:
            print(f"⚠️  Failed to load preferred model ({model_preference}): {e}")
            model = None
    
    # Try primary model
    if model is None:
        try:
            model = _get_primary_model()
            primary_type = _get_model_type_from_string(PRIMARY_MODEL)
            model_name = MODEL_CONFIGS[primary_type]["description"]
            max_tokens = MODEL_CONFIGS[primary_type]["default_max_tokens"]
            temperature = MODEL_CONFIGS[primary_type]["default_temperature"]
        except RuntimeError as e:
            print(f"⚠️  Primary model failed: {e}")
            model = None
    
    # Fallback to TinyLlama if primary fails
    if model is None:
        try:
            model = _get_fallback_model()
            model_name = MODEL_CONFIGS[ModelType.TINYLLAMA]["description"]
            max_tokens = MODEL_CONFIGS[ModelType.TINYLLAMA]["default_max_tokens"]
            temperature = MODEL_CONFIGS[ModelType.TINYLLAMA]["default_temperature"]
            print("🔄 Falling back to TinyLlama")
        except RuntimeError as e:
            return f"Error: No models available. {str(e)}"
    
    # Override with environment variables if set
    max_tokens = int(os.getenv("LLAMA_MAX_TOKENS", max_tokens))
    temperature = float(os.getenv("LLAMA_TEMPERATURE", temperature))
    
    try:
        print(f"🤖 Generating answer with {model_name} (max_tokens={max_tokens})")
        response = model(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        parts = response.get("choices", [])
        if not parts:
            return f"{model_name} returned no output."
        return parts[0].get("text", "").strip()
    except RuntimeError as err:
        # Model-specific runtime errors (e.g. missing model path)
        return f"Error with {model_name}: {str(err)}"
    except Exception as e:
        # Handle context-window / token-limit errors by retrying with a smaller max_tokens
        msg = str(e)
        low_token_indicators = ["exceed context window", "Requested tokens", "context window"]
        if any(ind in msg for ind in low_token_indicators):
            # Try a conservative fallback and retry once
            fallback_max = min(256, max_tokens)
            try:
                print(f"⚠️  Retrying with reduced max_tokens={fallback_max}")
                response = model(
                    prompt,
                    max_tokens=fallback_max,
                    temperature=temperature,
                )
                parts = response.get("choices", [])
                if not parts:
                    return f"{model_name} returned no output after retrying with smaller token limit."
                return (
                    parts[0].get("text", "").strip()
                    + f"\n\n(Note: output was generated with a reduced max token limit due to {model_name}'s context window.)"
                )
            except Exception as e2:
                # If still failing, try fallback model if not already using it
                if model_name != MODEL_CONFIGS[ModelType.TINYLLAMA]["description"]:
                    try:
                        print("🔄 Trying fallback model due to context window issues")
                        fallback_model = _get_fallback_model()
                        fallback_config = MODEL_CONFIGS[ModelType.TINYLLAMA]
                        response = fallback_model(
                            prompt,
                            max_tokens=fallback_config["default_max_tokens"],
                            temperature=fallback_config["default_temperature"],
                        )
                        parts = response.get("choices", [])
                        if parts:
                            return parts[0].get("text", "").strip() + "\n\n(Note: Generated using fallback model due to context limitations.)"
                    except Exception:
                        pass
                return f"Error generating answer after reducing tokens: {str(e2)}"

        return f"Error generating answer with {model_name}: {msg}"
