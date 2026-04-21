# Day 2: Configuration & Environment

## 📖 Reading List

1. **config.py** - Complete configuration file
2. **env.example** - Environment variable template
3. **docs/TECHNICAL_REPORT.md** - Section 10 (Dependencies)
4. **.env** - Your local configuration (create this)

## 🎯 Learning Objectives

By the end of today, you should:
- Understand all configuration options
- Know how environment variables work
- Be able to customize system behavior
- Understand the difference between config.py and .env

## 🔍 Key Concepts

### Configuration Layers
1. **Hardcoded Defaults** - In `config.py` (last resort)
2. **Environment Variables** - In `.env` file (recommended)
3. **Runtime Configuration** - Can be changed via API (future)

### Key Configuration Categories
- **Model Configuration** - AI model settings
- **Database Configuration** - Data storage
- **API Configuration** - Server settings
- **Security Configuration** - Auth and secrets
- **Performance Configuration** - Caching and optimization

## ✅ Hands-On Tasks

### Task 1: Explore Configuration File (30 minutes)
```python
# Open config.py and study each section

# Try these in Python:
from config import Config

# Model settings
print(f"Model: {Config.MODEL_NAME}")
print(f"Device: {Config.MODEL_DEVICE}")

# API settings
print(f"Host: {Config.API_HOST}")
print(f"Port: {Config.API_PORT}")

# RAG settings
print(f"Top K: {Config.RAG_TOP_K}")
print(f"Similarity Threshold: {Config.SIMILARITY_THRESHOLD}")
```

### Task 2: Create Your .env File (20 minutes)
```bash
# Copy example
cp env.example .env

# Edit .env and try different settings:
# - Change API_PORT to 8080
# - Enable authentication
# - Set your own SECRET_KEY
```

### Task 3: Test Configuration Loading (15 minutes)
```python
# Create test_config.py
from config import Config

print("=== Configuration Test ===")
print(f"Model Name: {Config.MODEL_NAME}")
print(f"Vector DB Path: {Config.VECTOR_DB_PATH}")
print(f"Auth Enabled: {Config.ENABLE_AUTH}")
print(f"Caching Enabled: {Config.ENABLE_CACHING}")
```

### Task 4: Understand Environment Variables (15 minutes)
```python
# See how environment variables override defaults
import os
os.environ['API_PORT'] = '9000'
# Now reload config and see if it changed
```

## 📝 Questions to Answer

1. What's the difference between `config.py` and `.env`?
2. Why use environment variables instead of hardcoding?
3. What happens if an environment variable is not set?
4. How would you change the model being used?
5. What configuration controls whether RAG is used?

## 🎓 Key Takeaways

- **Config.py:** Python class with defaults and environment variable reading
- **.env file:** User-specific settings (not committed to git)
- **Environment Variables:** Can override any setting
- **Best Practice:** Sensitive data (keys, passwords) in .env only

## 🔗 Related Files for Tomorrow

- `data_processing/mimic_processor.py` - Uses Config.MIMIC_DATA_PATH
- `rag/rag_system.py` - Uses Config.RAG_TOP_K

## 💡 Tips

- Always keep `.env` in `.gitignore` (don't commit secrets!)
- Use `env.example` as a template for others
- Document why you changed certain config values
- Test configuration changes before deploying

## ⏭️ Tomorrow's Preview: Data Processing Pipeline

You'll learn how MIMIC data flows from CSV files to vector database embeddings.

---

**Time Estimate:** 1.5-2 hours  
**Difficulty:** ⭐ (Very Easy)

