# Week 1 Exercises - Foundation & Architecture

## Exercise 1: Project Exploration (30 minutes)

**Task:** Create a visual diagram of the system architecture

**Requirements:**
- Show all main components
- Indicate data flow between components
- Label the technologies used
- Include the three main layers (Client, API, Data)

**Deliverable:** Diagram (hand-drawn or digital)

---

## Exercise 2: Configuration Mastery (20 minutes)

**Task:** Create a custom configuration file

**Requirements:**
1. Copy `.env` to `.env.custom`
2. Change these settings:
   - API port to 9000
   - Enable authentication
   - Set RAG_TOP_K to 10
   - Change similarity threshold to 0.8
3. Test that changes are loaded correctly

**Deliverable:** Working `.env.custom` file

---

## Exercise 3: Data Processing (30 minutes)

**Task:** Process sample data manually

**Requirements:**
1. Create a simple CSV file with 3 patient cases
2. Place it in `data/mimic_iv_ed/test_triage.csv`
3. Modify `mimic_processor.py` to load your test file
4. Process and create embeddings
5. Verify vector database has your cases

**Deliverable:** Working test with your data

---

## Exercise 4: Vector Search (20 minutes)

**Task:** Test similarity search

**Requirements:**
1. Generate 5 synthetic cases
2. Create vector database
3. Search for similar cases with different queries
4. Analyze why certain cases match

**Deliverable:** Search results analysis

---

## Exercise 5: Code Review (30 minutes)

**Task:** Read and understand RAG flow

**Requirements:**
1. Trace through `classify_patient()` method
2. Document the decision flow (vector → LLM → rule-based)
3. Identify all fallback scenarios
4. Explain why each fallback is needed

**Deliverable:** Flowchart or written explanation

---

## Exercise 6: Agent Understanding (25 minutes)

**Task:** Understand tool execution

**Requirements:**
1. Find all tools in `triage_agent.py`
2. For each tool, identify:
   - What it does
   - When it's called
   - What it returns
3. Trace one complete patient processing flow

**Deliverable:** Tool documentation

---

## Exercise 7: Week 1 Summary (20 minutes)

**Task:** Write your own summary

**Requirements:**
1. Create a document explaining:
   - What the system does (in your own words)
   - How the main components work together
   - What you found most interesting
   - What's still unclear

**Deliverable:** Personal summary document

---

## Bonus Exercises

### Bonus 1: Add a New Configuration Option
Add a new setting to `config.py` and use it somewhere in the code.

### Bonus 2: Modify Synthetic Data Generator
Add a new chief complaint type with its own symptom patterns.

### Bonus 3: Create a Simple Test
Write a unit test for one of the configuration methods.

---

## Self-Assessment

Before moving to Week 2, make sure you can:

- [ ] Explain what RAG is and why it's used
- [ ] Navigate the codebase confidently
- [ ] Understand the configuration system
- [ ] Explain how vector databases work
- [ ] Describe the agent workflow
- [ ] Trace data flow from input to output

If you can't check all boxes, review the relevant days again!


