# Unused Files in Podcasts-Rag Project

This document lists files that are no longer used after the project restructuring.

## 🔴 Deprecated Python Files (Replaced by New Structure)

These files have been replaced by the new modular structure and are **no longer used**:

### 1. `app.py`
- **Status**: ❌ Unused
- **Replaced by**: `api/server.py`
- **Reason**: Moved to `api/` directory as part of production-ready structure
- **Action**: Can be safely deleted

### 2. `podcast_rag.py`
- **Status**: ❌ Unused
- **Replaced by**: 
  - `rag.py` (main orchestration)
  - `ingest/embed.py` (embedding functions)
  - `index/vector.py` (vector search)
  - `llm/prompt.py` (LLM functions)
- **Reason**: Split into modular components
- **Action**: Can be safely deleted (kept for reference during migration)

### 3. `chunking.py`
- **Status**: ❌ Unused
- **Replaced by**: `ingest/chunk.py`
- **Reason**: Moved to `ingest/` module
- **Action**: Can be safely deleted

### 4. `index_transcripts.py`
- **Status**: ❌ Unused
- **Replaced by**: `scripts/ingest.py`
- **Reason**: Moved to `scripts/` directory
- **Action**: Can be safely deleted

## 🟡 Potentially Unused Files

### 5. `test_paragraph_chunking.py`
- **Status**: ⚠️ Test file
- **Purpose**: Appears to be a test script
- **Action**: Review if still needed for testing, otherwise can be deleted

### 6. `scrape_podscribe.py`
- **Status**: ⚠️ Utility script
- **Purpose**: Web scraping utility for Podscribe
- **Action**: Review if still needed, otherwise can be moved to `scripts/` or deleted

## 📁 Empty/Unused Directories

### 7. `transcripts/` (empty directory)
- **Status**: ❌ Empty
- **Reason**: Transcripts moved to `data/transcripts/`
- **Action**: Can be safely deleted

### 8. `templates/` (duplicate)
- **Status**: ⚠️ Duplicate
- **Reason**: Templates moved to `api/templates/`
- **Action**: Can be deleted (but verify `api/templates/` has the files)

## 📄 Documentation/Design Files (KEEP)

These files are documentation/design artifacts - **keep for reference**:

- ✅ `chatgpt.drawio` - Design diagram
- ✅ `podcast_rag.drawio` - Design diagram
- ✅ `Rag_Architecture.drawio` - Architecture diagram
- ✅ `Rag_Architecture.png` - Architecture image
- ✅ `SYSTEM_DESIGN.md` - System design documentation

## 📝 Miscellaneous Files (KEEP)

### 9. `notes.txt`
- **Status**: ✅ Keep
- **Action**: Personal notes - keep for reference

### 10. `Untitled 2.txt`
- **Status**: ✅ Keep
- **Action**: Keep for reference

### 11. `Untitled.rtf`
- **Status**: ✅ Keep
- **Action**: Keep for reference

### 12. `loandetails`
- **Status**: ✅ Keep
- **Action**: Keep for reference

### 13. `Podcasts-Rag.code-workspace`
- **Status**: ✅ Keep
- **Action**: VS Code workspace file - keep for development

## 🗑️ Safe to Delete

The following files can be **safely deleted** without affecting the application:

```bash
# Deprecated Python files (replaced by new structure)
rm app.py
rm podcast_rag.py
rm chunking.py
rm index_transcripts.py

# Empty directory
rmdir transcripts/

# Duplicate templates (after verifying api/templates/ has the files)
rm -rf templates/
```

## ⚠️ Review Before Deleting

These files should be reviewed before deletion:

```bash
# Test file - check if still needed
test_paragraph_chunking.py

# Utility script - check if still needed
scrape_podscribe.py
```

## ✅ Files to Keep

The following files should be **kept**:

```bash
# Documentation/Design files
*.drawio
*.png
SYSTEM_DESIGN.md
README.md
LLM_SETUP.md
MIGRATION.md
MODEL_STATUS.md

# Miscellaneous files
notes.txt
Untitled 2.txt
Untitled.rtf
loandetails
Podcasts-Rag.code-workspace
```

## 📊 Summary

- **Total unused files**: ~13 files
- **Safe to delete immediately**: 6 files (deprecated Python files + empty directories)
- **Review before deleting**: 2 files (test/utility scripts)
- **Keep for reference**: 5+ files (documentation, design, miscellaneous)

## 🔄 Migration Status

According to `MIGRATION.md`, the old files are kept for reference during migration but will be removed in a future version. The new structure is fully functional and these old files are not imported anywhere in the codebase.

