# Day 8: RAG System Deep Dive

## 📖 Reading List
1. **rag/rag_system.py** - Complete file (all methods)
2. **docs/CODE_REVIEW_FIXES.md** - RAG section
3. **docs/TECHNICAL_REPORT.md** - RAG implementation details

## 🎯 Learning Objectives
- Master the complete RAG classification flow
- Understand priority cascade (Vector → LLM → Rule-based)
- Know how context is formatted for LLM
- Understand similarity weighting

## ✅ Tasks
1. Trace through `classify_patient()` completely
2. Study all classification methods
3. Test different scenarios (with/without vector DB, with/without LLM)
4. Understand fallback mechanisms

## 🔑 Key Points
- Vector DB retrieval happens FIRST
- LLM uses retrieved context when available
- Rule-based is intelligent fallback
- Similarity weighting improves accuracy

---

**Time:** 2 hours | **Difficulty:** ⭐⭐⭐


