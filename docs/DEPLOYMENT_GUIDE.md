# Deployment Guide - AI Triage Assistant

## Quick Start

### Using Docker (Recommended)

1. **Build and start:**
   ```bash
   docker-compose up -d
   ```

2. **Check status:**
   ```bash
   docker-compose ps
   curl http://localhost:8000/health
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f api
   ```

### Manual Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your settings
   ```

3. **Run setup:**
   ```bash
   python scripts/setup.py
   ```

4. **Start server:**
   ```bash
   python scripts/start.py api
   ```

## Adding MIMIC CSV Data

When you have your CSV files, place them in `data/mimic_iv_ed/`:
- `triage.csv`
- `edstays.csv`
- `vitalsign.csv`
- `diagnosis.csv`
- `medrecon.csv`
- `pyxis.csv`

Then restart the system - it will automatically process them on next startup.

**Note:** Without MIMIC data, the system will automatically generate 100 synthetic cases for RAG functionality.

## Authentication

### Enable Authentication

Set in `.env`:
```bash
ENABLE_AUTH=true
SECRET_KEY=your-very-secret-key-here-change-in-production
```

### Default Users (Change immediately!)

- **Admin:** username=`admin`, password=`admin123`
- **Nurse:** username=`nurse`, password=`nurse123`

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

Use the returned token:
```bash
curl http://localhost:8000/dashboard \
  -H "Authorization: Bearer <token>"
```

## Performance Features

- **Model Caching:** Model loads once and stays in memory
- **Request Caching:** Classification results cached for 5 minutes
- **Redis Support:** Optional Redis for distributed caching
- **Connection Pooling:** Thread-safe database connections

## Monitoring

- Health check: `GET /health`
- API docs: `http://localhost:8000/docs`
- Logs: `./logs/app.log`

## Troubleshooting

### Model won't load
- Check available RAM (needs 8GB+)
- Set `MODEL_DEVICE=cpu` in `.env` if GPU issues
- Check `./data/models/` directory

### Vector DB empty
- Place CSV files in `data/mimic_iv_ed/`
- System will auto-generate synthetic data if none found
- Check logs for processing status

### Authentication fails
- Verify `ENABLE_AUTH=true` in `.env`
- Check `SECRET_KEY` is set
- Verify user exists in `data/users.json`
