# Day 6: LangChain Agents

## 📖 Reading List

1. **langchain_integration/triage_agent.py** - Complete file
2. LangChain ReAct agent documentation
3. **docs/ARCHITECTURE.md** - Agent section

## 🎯 Learning Objectives

- Understand ReAct agent pattern
- Learn how tools work
- See agent orchestration
- Understand tool execution flow

## 🔍 Key Concepts

### ReAct Pattern
- **Reasoning:** Agent thinks about what to do
- **Acting:** Agent calls tools
- **Observing:** Agent sees tool results
- **Iterating:** Repeats until done

### Tools
- **TriageTool:** Classify patients
- **DashboardUpdateTool:** Update dashboard
- **SurveillanceTool:** Analyze for outbreaks

## ✅ Hands-On Tasks

1. Study `_create_agent()` method
2. Understand tool definitions
3. Trace `process_patient()` execution
4. See how agent decides which tool to use

## 📝 Questions
1. What is the ReAct pattern?
2. How does the agent choose tools?
3. What happens if a tool fails?
4. Why use agents vs direct function calls?

---

**Time:** 2 hours | **Difficulty:** ⭐⭐⭐


