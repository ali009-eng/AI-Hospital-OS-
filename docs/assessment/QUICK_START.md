# Quick Start Guide - Assessment Framework

Get started with the AI Hospital OS assessment framework in **15 minutes**.

## ⚡ Quick Setup

### 1. Navigate to Assessment Folder
```bash
cd docs/assessment
```

### 2. Initialize the Tracker
```bash
python assessment_tracker.py --init
```

This creates standard milestones (M1-M10) from the roadmap.

### 3. Check Status
```bash
python assessment_tracker.py --status
```

You'll see:
- Overall progress (0%)
- All 5 phases (not started)
- 10 milestones (pending)
- No tasks yet
- No risks yet

## 📚 Read the Assessments (10 minutes)

### Must-Read (5 min)
1. **README.md** - Overview of framework
2. **Executive summaries** - From each phase doc

### Important (5 min)
3. **02_gap_analysis.md** - Critical gaps identified
4. **05_roadmap.md** - Week-by-week execution plan

### Deep Dive (Later)
5. Full read of all 5 phase documents

## 🎯 Your First Actions

### Update Phase 1 Progress
```bash
# Mark Phase 1 as started
python assessment_tracker.py --update-phase 01_as_is_analysis in_progress 25
```

### Add Your First Tasks
```bash
# Critical first tasks from Week 1
python assessment_tracker.py --add-task "Create fresh virtual environment" 01_as_is_analysis high
python assessment_tracker.py --add-task "Install dependencies" 01_as_is_analysis high
python assessment_tracker.py --add-task "Run integration tests" 01_as_is_analysis high
python assessment_tracker.py --add-task "Fix import errors" 01_as_is_analysis high
```

### Add Critical Risks
```bash
# From gap analysis
python assessment_tracker.py --add-risk "Code may not run" critical "Start with small tests"
python assessment_tracker.py --add-risk "Model won't load" critical "Use smaller model first"
python assessment_tracker.py --add-risk "MIMIC approval delayed" high "Use synthetic data"
```

### Check Updated Status
```bash
python assessment_tracker.py --status
```

## 📊 Generate Your First Report

```bash
# Create weekly report
python assessment_tracker.py --report weekly_report_week1.md
```

## 🚀 Begin Execution

### Week 1 Tasks (from roadmap)

**Days 1-2: Environment Setup**
```bash
# Follow these steps
1. Create virtual environment
2. Install requirements
3. Pin working versions
4. Document setup

# Track progress
python assessment_tracker.py --update-phase 01_as_is_analysis in_progress 30
```

**Days 3-5: Testing**
```bash
# Run tests
python tests/integration_test.py

# Track results
python assessment_tracker.py --update-phase 01_as_is_analysis in_progress 60
```

## 📈 Daily Workflow

### Every Morning
```bash
# Check today's tasks
python assessment_tracker.py --status
```

### Every Evening
```bash
# Update progress
python assessment_tracker.py --update-phase [PHASE] in_progress [PERCENTAGE]

# Add tomorrow's tasks
python assessment_tracker.py --add-task "Task description" [PHASE] [PRIORITY]
```

### Every Friday
```bash
# Generate weekly report
python assessment_tracker.py --report weekly_report_week[N].md
```

## 🎯 Next Steps

1. ✅ Read this quick start guide
2. ✅ Initialize tracker
3. ✅ Add initial tasks and risks
4. ✅ Read Phase 1 and 2 assessments
5. 📅 **Start Week 1 execution** (from 05_roadmap.md)

## 💡 Pro Tips

- **Update progress daily** - Stay accountable
- **Be honest** - Accurate tracking helps planning
- **Address blockers immediately** - Don't let them pile up
- **Review milestones weekly** - Adjust if needed
- **Generate reports** - Share with stakeholders

## 🆘 Troubleshooting

### Tracker not working?
```bash
# Check Python version (need 3.7+)
python --version

# Run with verbose errors
python -v assessment_tracker.py --status
```

### Lost progress?
Progress is saved in `progress.json` - back it up regularly!

### Need help?
- Check `README.md` in this folder
- Review the phase documents
- Check solution design for approaches

---

**You're ready! Start with Week 1 from the [Roadmap](05_roadmap.md)** 🚀
