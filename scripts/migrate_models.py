"""
Helper script to migrate from legacy LLAMA_MODEL_PATH to new multi-model setup.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def main():
    """Migrate legacy model configuration to new format."""
    legacy_path = os.getenv("LLAMA_MODEL_PATH")
    
    if not legacy_path:
        print("❌ No legacy LLAMA_MODEL_PATH found. Nothing to migrate.")
        return
    
    print(f"📦 Found legacy model: {legacy_path}")
    
    # Check if file exists
    if not Path(legacy_path).exists():
        print(f"⚠️  Model file not found: {legacy_path}")
        return
    
    # Detect model type from filename
    path_lower = legacy_path.lower()
    
    model_type = None
    env_var = None
    
    if "llama" in path_lower and ("8b" in path_lower or "3.1" in path_lower or "3-1" in path_lower):
        model_type = "Llama-3.1-8B"
        env_var = "LLAMA3_8B_MODEL_PATH"
    elif "phi" in path_lower or "phi3" in path_lower or "phi-3" in path_lower:
        model_type = "Phi-3 Mini"
        env_var = "PHI3_MODEL_PATH"
    elif "tiny" in path_lower:
        model_type = "TinyLlama"
        env_var = "TINYLLAMA_MODEL_PATH"
    else:
        # Default to Llama-3.1-8B if unsure (most common)
        model_type = "Llama-3.1-8B"
        env_var = "LLAMA3_8B_MODEL_PATH"
        print("⚠️  Could not detect model type from filename, defaulting to Llama-3.1-8B")
    
    print(f"\n✅ Detected model type: {model_type}")
    print(f"   Recommended env var: {env_var}")
    print(f"   Model path: {legacy_path}")
    
    # Check current .env
    env_file = Path(".env")
    if env_file.exists():
        content = env_file.read_text()
        
        # Check if already migrated
        if env_var in content:
            print(f"\n✅ {env_var} already exists in .env file")
            return
        
        # Add new configuration
        print(f"\n📝 Adding to .env file...")
        
        # Find where to add (after LLM Configuration section)
        lines = content.split("\n")
        new_lines = []
        added = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # Add after LLM Configuration comment
            if "LLM Configuration" in line and not added:
                # Find the right place to insert
                j = i + 1
                while j < len(lines) and (lines[j].startswith("#") or lines[j].strip() == ""):
                    j += 1
                
                # Insert new config
                if j < len(lines):
                    new_lines.append(f"{env_var}={legacy_path}")
                    new_lines.append(f"# Set PRIMARY_MODEL=llama3_8b to use this as primary")
                    added = True
        
        if not added:
            # Append at end
            new_lines.append(f"\n# Migrated from legacy LLAMA_MODEL_PATH")
            new_lines.append(f"{env_var}={legacy_path}")
            new_lines.append(f"PRIMARY_MODEL=llama3_8b")
        
        env_file.write_text("\n".join(new_lines))
        print(f"✅ Added {env_var} to .env file")
        print(f"\n💡 Next steps:")
        print(f"   1. Review the .env file")
        print(f"   2. Set PRIMARY_MODEL=llama3_8b (or phi3_mini/tinyllama)")
        print(f"   3. Optionally add other model paths for fallback")
        print(f"   4. Run: python3 scripts/check_models.py to verify")
    else:
        print(f"\n📝 .env file not found. Create it with:")
        print(f"   {env_var}={legacy_path}")
        print(f"   PRIMARY_MODEL=llama3_8b")


if __name__ == "__main__":
    main()

