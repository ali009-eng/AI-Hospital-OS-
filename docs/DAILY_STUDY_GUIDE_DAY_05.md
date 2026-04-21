# Day 5: LLM Integration

## 📖 Reading List

1. **rag/rag_system.py** - TriageLLM class
2. Hugging Face Transformers docs
3. **docs/CODE_REVIEW_FIXES.md** - Model caching section

## 🎯 Learning Objectives

- Understand how models are loaded
- Learn about model caching
- See how prompts are constructed
- Understand token generation

## 🔍 Key Concepts

### Model Loading
- **Lazy Loading:** Model loads on first use
- **Caching:** Model stays in memory
- **Device Management:** GPU vs CPU

### Prompt Engineering
- **Context Injection:** Similar cases in prompt
- **Format:** Structured prompts for JSON output
- **Temperature:** Controls randomness (0 = deterministic)

## ✅ Hands-On Tasks

1. Study `_load_model()` and `_load_model_cached()`
2. Understand prompt construction in `_llm_classify()`
3. See how JSON is extracted from model output
4. Test model loading (if available)

## 📝 Questions
1. Why cache the model?
2. What happens if model loading fails?
3. How are prompts structured?
4. What's the difference between temperature 0 and >0?

---

**Time:** 2-3 hours | **Difficulty:** ⭐⭐⭐


