"""
Check which LLM models are configured and available locally.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Model configuration mapping
MODELS = {
    "Phi-3 Mini (Main)": {
        "env_var": "PHI3_MODEL_PATH",
        "default": None,
    },
    "TinyLlama (Fallback)": {
        "env_var": "TINYLLAMA_MODEL_PATH",
        "default": None,
    },
    "Llama-3.1-8B (Bigger)": {
        "env_var": "LLAMA3_8B_MODEL_PATH",
        "default": None,
    },
}

# Legacy support
LEGACY_MODEL_PATH = os.getenv("LLAMA_MODEL_PATH")


def check_model_file(path: str) -> tuple[bool, str]:
    """
    Check if a model file exists and is readable.
    
    Returns:
        (exists, message)
    """
    if not path:
        return False, "Path not set"
    
    model_path = Path(path)
    
    if not model_path.exists():
        return False, f"File not found: {path}"
    
    if not model_path.is_file():
        return False, f"Path is not a file: {path}"
    
    if not model_path.suffix.lower() == ".gguf":
        return False, f"File is not a .gguf file: {path}"
    
    # Check file size
    size_mb = model_path.stat().st_size / (1024 * 1024)
    
    # Check if readable
    if not os.access(model_path, os.R_OK):
        return False, f"File is not readable: {path}"
    
    return True, f"✅ Available ({size_mb:.1f} MB)"


def check_llama_cpp() -> bool:
    """Check if llama-cpp-python is installed."""
    try:
        import llama_cpp
        return True
    except ImportError:
        return False


def main():
    """Check model availability and print status."""
    print("🔍 Checking LLM Model Availability\n")
    print("=" * 60)
    
    # Check llama-cpp-python
    print("\n📦 Dependencies:")
    if check_llama_cpp():
        print("  ✅ llama-cpp-python is installed")
    else:
        print("  ❌ llama-cpp-python is NOT installed")
        print("     Install with: pip install llama-cpp-python")
        return
    
    # Check model configuration
    print("\n🤖 Model Configuration:")
    print("-" * 60)
    
    primary_model = os.getenv("PRIMARY_MODEL", "phi3_mini").lower()
    fallback_model = os.getenv("FALLBACK_MODEL", "tinyllama").lower()
    use_bigger = os.getenv("USE_BIGGER_MODEL", "false").lower() == "true"
    
    print(f"Primary Model: {primary_model}")
    print(f"Fallback Model: {fallback_model}")
    print(f"Use Bigger Model: {use_bigger}")
    print()
    
    # Check each model
    available_models = []
    unavailable_models = []
    
    for model_name, config in MODELS.items():
        env_var = config["env_var"]
        model_path = os.getenv(env_var)
        
        print(f"{model_name}:")
        print(f"  Env Var: {env_var}")
        
        if model_path:
            exists, message = check_model_file(model_path)
            print(f"  Path: {model_path}")
            print(f"  Status: {message}")
            
            if exists:
                available_models.append(model_name)
            else:
                unavailable_models.append((model_name, message))
        else:
            print(f"  Status: ❌ Not configured (env var not set)")
            unavailable_models.append((model_name, "Not configured"))
        
        print()
    
    # Check legacy model path
    if LEGACY_MODEL_PATH:
        print("📜 Legacy Configuration:")
        print(f"  LLAMA_MODEL_PATH: {LEGACY_MODEL_PATH}")
        exists, message = check_model_file(LEGACY_MODEL_PATH)
        print(f"  Status: {message}")
        if exists:
            print("  ⚠️  Note: This is the old configuration format.")
            print("     Consider migrating to the new multi-model setup.")
        print()
    
    # Summary
    print("=" * 60)
    print("\n📊 Summary:")
    print(f"  ✅ Available Models: {len(available_models)}")
    for model in available_models:
        print(f"     - {model}")
    
    print(f"\n  ❌ Unavailable Models: {len(unavailable_models)}")
    for model, reason in unavailable_models:
        print(f"     - {model}: {reason}")
    
    # Recommendations
    print("\n💡 Recommendations:")
    if len(available_models) == 0:
        print("  ⚠️  No models are configured!")
        print("     Set at least one model path in your .env file:")
        print("     - PHI3_MODEL_PATH=/path/to/phi-3-mini.gguf")
        print("     - TINYLLAMA_MODEL_PATH=/path/to/tinyllama.gguf")
        print("     - LLAMA3_8B_MODEL_PATH=/path/to/llama-3.1-8b.gguf")
    elif len(available_models) == 1:
        print("  ⚠️  Only one model is available.")
        print("     Consider adding a fallback model for better reliability.")
    else:
        print("  ✅ Multiple models available - fallback will work!")
    
    # Check if primary model is available
    primary_available = False
    if primary_model == "phi3_mini":
        primary_available = "Phi-3 Mini (Main)" in available_models
    elif primary_model == "tinyllama":
        primary_available = "TinyLlama (Fallback)" in available_models
    elif primary_model in ["llama3_8b", "llama3", "llama-3.1-8b"]:
        primary_available = "Llama-3.1-8B (Bigger)" in available_models
    
    if not primary_available:
        print(f"\n  ⚠️  Primary model ({primary_model}) is not available!")
        print("     The system will fall back to the first available model.")
    
    print()


if __name__ == "__main__":
    main()

