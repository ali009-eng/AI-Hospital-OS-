# Day 1: Project Overview & Setup

## 📖 Reading List

1. **README.md** (Project root) - Complete overview
2. **docs/TECHNICAL_REPORT.md** - Sections 1-3 (Executive Summary, Architecture, Core Functionality)
3. **docs/ARCHITECTURE.md** - System architecture deep dive
4. **docs/DEVELOPMENT_LOG.md** - Understanding the project's history

## 🎯 Learning Objectives

By the end of today, you should:
- Understand what the AI Triage Assistant does
- Know the main components and how they connect
- Have your development environment set up
- Be able to navigate the project structure confidently

## 🔍 Key Concepts to Understand

### What is this system?
An AI-powered emergency department triage system that:
- Classifies patients using ESI (Emergency Severity Index) levels 1-5
- Uses AI/ML to make intelligent decisions
- Provides real-time dashboard for healthcare workers
- Detects potential disease outbreaks

### Main Components
1. **RAG System** - Retrieves similar cases and uses AI for classification
2. **Triage Agent** - Orchestrates the entire workflow
3. **API Server** - REST API and WebSocket endpoints
4. **Dashboard** - Real-time web interface
5. **Surveillance** - Detects patterns and outbreaks

## ✅ Hands-On Tasks

### Task 1: Environment Setup (30 minutes)
```bash
# 1. Verify Python version (3.8+)
python --version

# 2. Create virtual environment (optional but recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation
python -c "import fastapi, langchain, transformers; print('Dependencies OK')"
```

### Task 2: Explore Project Structure (20 minutes)
```bash
# Navigate and explore
cd traige-deploy-cursor

# Key directories to explore:
# - api/          # API server
# - rag/          # RAG system
# - langchain_integration/  # Agents
# - data_processing/  # Data handling
# - surveillance/  # Outbreak detection
```

### Task 3: Configuration Setup (15 minutes)
```bash
# 1. Copy example environment file
cp env.example .env

# 2. Open .env and review all settings
# 3. Understand what each variable does
# 4. Note: You can use defaults for now
```

### Task 4: First Run (20 minutes)
```bash
# Try to start the server (may fail, that's OK)
python scripts/start.py api

# Or try directly:
python -c "from config import Config; print(f'API Port: {Config.API_PORT}')"
```

## 📝 Questions to Answer

1. What are the 5 ESI triage levels and what do they mean?
2. What is RAG and why is it used here?
3. What is the difference between the RAG system and the Triage Agent?
4. What programming languages/frameworks are used?
5. Where would you add new features?

## 🎓 Key Takeaways

- **ESI Levels:** 1 (Immediate) to 5 (Minor) - Lower number = Higher priority
- **RAG:** Retrieval-Augmented Generation - Uses vector DB to find similar cases before AI classification
- **LangChain:** Framework for building AI agent systems
- **Architecture:** Modular design with clear separation of concerns

## 🔗 Related Files to Study Tomorrow

- `config.py` - Configuration management
- `env.example` - Environment variables
- `requirements.txt` - Dependencies

## 💡 Tips

- Don't worry if things don't run perfectly yet - we'll fix that as we learn
- Take notes in your own words
- Draw diagrams of how components connect
- Ask yourself: "How would I explain this to someone else?"

## ⏭️ Tomorrow's Preview: Configuration & Environment

You'll dive deep into how the system is configured and understand all the settings that control behavior.

---

**Time Estimate:** 2-3 hours  
**Difficulty:** ⭐⭐ (Beginner-friendly)

