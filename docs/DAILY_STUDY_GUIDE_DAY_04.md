# Day 4: Vector Databases & RAG Fundamentals

## 📖 Reading List

1. **rag/rag_system.py** - First half (RAGSystem class, vector retrieval)
2. **docs/TECHNICAL_REPORT.md** - RAG section
3. ChromaDB documentation: https://docs.trychroma.com/

## 🎯 Learning Objectives

- Understand what vector databases are
- Learn how similarity search works
- Understand embeddings and semantic similarity
- See how RAG retrieves relevant context

## 🔍 Key Concepts

### Vector Databases
- **Purpose:** Store high-dimensional vectors (embeddings)
- **Why:** Fast similarity search
- **How:** ChromaDB uses cosine similarity

### RAG (Retrieval-Augmented Generation)
1. **Retrieve:** Find similar cases from vector DB
2. **Augment:** Use retrieved cases as context
3. **Generate:** LLM creates response with context

## ✅ Hands-On Tasks

1. Study `search_similar_cases()` method
2. Understand similarity threshold filtering
3. Test vector search with different queries
4. See how retrieved cases are formatted

## 📝 Questions
1. How does cosine similarity work?
2. What's the difference between distance and similarity?
3. Why filter by similarity threshold?
4. How many cases should be retrieved?

---

**Time:** 2 hours | **Difficulty:** ⭐⭐


