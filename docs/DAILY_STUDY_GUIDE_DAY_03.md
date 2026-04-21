# Day 3: Data Processing Pipeline

## 📖 Reading List

1. **data_processing/mimic_processor.py** - Complete file
2. **data_processing/synthetic_data_generator.py** - Synthetic data creation
3. **docs/TECHNICAL_REPORT.md** - Section 2.1 (Patient Triage Classification)

## 🎯 Learning Objectives

Understand:
- How CSV files are loaded and processed
- How vector embeddings are created
- How vector database is populated
- How synthetic data generation works
- The data flow from CSV → Vector DB

## 🔍 Key Concepts

### Data Processing Steps
1. **Load CSV files** - Read MIMIC-IV-ED data
2. **Merge tables** - Combine triage, vitals, diagnoses
3. **Create case text** - Convert to searchable text
4. **Generate embeddings** - Convert text to vectors
5. **Store in vector DB** - ChromaDB collection

### Vector Embeddings
- **What:** Numerical representation of text
- **Why:** Enables similarity search
- **How:** Sentence transformers model
- **Result:** Similar cases can be found quickly

## ✅ Hands-On Tasks

### Task 1: Study MIMICProcessor Class (30 minutes)
```python
# Open mimic_processor.py
# Trace through each method:
# - load_data()
# - process_data()
# - create_vector_db()
# - search_similar_cases()

# Try importing:
from data_processing.mimic_processor import MIMICProcessor
processor = MIMICProcessor()
```

### Task 2: Understand Data Flow (20 minutes)
```python
# Create a test script: test_data_flow.py
from data_processing.mimic_processor import MIMICProcessor

processor = MIMICProcessor()

# 1. Load data
data = processor.load_data()
print(f"Loaded {len(data)} tables")

# 2. Process data
processed = processor.process_data()
print(f"Processed {len(processed)} cases")

# 3. Create vector DB
collection = processor.create_vector_db()
print(f"Vector DB has {collection.count()} documents")
```

### Task 3: Test Synthetic Data (20 minutes)
```python
# Test synthetic data generation
from data_processing.synthetic_data_generator import SyntheticDataGenerator

# Generate a single case
case = SyntheticDataGenerator.generate_case(
    patient_id="TEST001",
    complaint="Chest pain"
)
print(case)

# Generate multiple
cases = SyntheticDataGenerator.generate_cases(count=10)
print(f"Generated {len(cases)} cases")
```

### Task 4: Understand Vector Search (15 minutes)
```python
# Test similarity search
from data_processing.mimic_processor import MIMICProcessor

processor = MIMICProcessor()
processor.create_vector_db()

# Search for similar cases
query = "Chest pain, heart rate 110, oxygen 92"
results = processor.search_similar_cases(query, top_k=3)

for i, result in enumerate(results, 1):
    print(f"Result {i}:")
    print(f"  Distance: {result['distance']}")
    print(f"  Document: {result['document'][:100]}...")
```

## 📝 Questions to Answer

1. What format does MIMIC data need to be in?
2. How are multiple CSV files combined?
3. What is an embedding and why is it used?
4. How does similarity search work?
5. When is synthetic data used vs real data?

## 🎓 Key Takeaways

- **Data Loading:** Pandas reads CSV files into DataFrames
- **Data Merging:** Tables joined on common keys (subject_id)
- **Text Creation:** Patient info converted to searchable text strings
- **Embeddings:** Text → vectors using sentence-transformers
- **Vector DB:** ChromaDB stores and searches embeddings

## 🔗 Related Files for Tomorrow

- `rag/rag_system.py` - Uses the processor for retrieval
- `config.py` - RAG configuration (TOP_K, similarity threshold)

## 💡 Tips

- Data processing is CPU/memory intensive
- Vector DB creation takes time (minutes for large datasets)
- Synthetic data is useful for testing without real data
- Embeddings capture semantic meaning, not just keywords

## ⏭️ Tomorrow's Preview: Vector Databases & RAG Fundamentals

You'll learn how RAG uses vector databases to retrieve relevant context for AI classification.

---

**Time Estimate:** 2 hours  
**Difficulty:** ⭐⭐ (Intermediate)


