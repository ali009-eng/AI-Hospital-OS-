# Quick Start Guide

Get up and running in 15 minutes!

## 🚀 Fastest Path to Running

### Step 1: Install (5 minutes)
```bash
pip install -r requirements.txt
```

### Step 2: Configure (2 minutes)
```bash
cp env.example .env
# Edit .env if needed (defaults work for testing)
```

### Step 3: Run (5 minutes)
```bash
# Option 1: Docker (Recommended)
docker-compose up -d

# Option 2: Manual
python scripts/start.py api
```

### Step 4: Test (3 minutes)
```bash
# Check health
curl http://localhost:8000/health

# Test classification
curl -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "TEST001",
    "age": 45,
    "chief_complaint": "Chest pain",
    "heart_rate": 110,
    "oxygen_saturation": 92
  }'
```

## ✅ Success Indicators

You're ready when:
- ✅ Health endpoint returns `{"status": "healthy"}`
- ✅ Classification endpoint returns triage level
- ✅ Dashboard loads at http://localhost:8000/dashboard
- ✅ No critical errors in logs

## 🎓 Next Steps

After quick start:
1. Read **README.md** for learning roadmap
2. Follow **docs/DAILY_STUDY_GUIDE_DAY_01.md**
3. Complete exercises in **docs/WEEK_01_EXERCISES.md**

## 🆘 Troubleshooting

**Server won't start?**
- Check Python version (3.8+)
- Verify dependencies installed
- Check port 8000 is available

**Model loading issues?**
- Normal on first run (downloads 8GB model)
- Check available RAM (needs 8GB+)
- Set `MODEL_DEVICE=cpu` in .env if GPU issues

**Vector DB empty?**
- System will generate synthetic data automatically
- Or add CSV files to `data/mimic_iv_ed/`

---

**Ready to learn? Start with README.md!**


