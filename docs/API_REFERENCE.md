# API Reference

Complete API documentation for AI Triage Assistant.

## Base URL
```
http://localhost:8000
```

## Authentication

Most endpoints require JWT authentication (unless `ENABLE_AUTH=false`).

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

Response:
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

### Using Tokens
```http
Authorization: Bearer <token>
```

---

## Endpoints

### Health Check
```http
GET /health

Response:
{
  "status": "healthy",
  "timestamp": "2024-12-XX...",
  "agent_available": true
}
```

### Classify Patient
```http
POST /triage
Authorization: Bearer <token>
Content-Type: application/json

{
  "patient_id": "P001",
  "age": 45,
  "gender": "M",
  "chief_complaint": "Chest pain",
  "heart_rate": 110,
  "respiratory_rate": 24,
  "oxygen_saturation": 92,
  "temperature": 37.2,
  "blood_pressure": "140/90",
  "pain_level": 7
}

Response:
{
  "patient_id": "P001",
  "triage_level": 2,
  "esi_level": "High Risk - Urgent",
  "reasoning": "...",
  "risk_factors": [...],
  "recommendations": [...],
  "confidence": 0.85,
  "retrieved_cases": 5,
  "classification_method": "rag_with_context"
}
```

### Get Dashboard Data
```http
GET /dashboard
Authorization: Bearer <token>

Response:
{
  "total_patients": 10,
  "high_priority_patients": 3,
  "queue": [...],
  "triage_distribution": {...}
}
```

### Get Surveillance Data
```http
GET /surveillance
Authorization: Bearer <token>

Response:
{
  "alerts": [...],
  "trends": [...],
  "clusters_detected": 2,
  "active_alerts_count": 1
}
```

### WebSocket Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle updates
};
```

---

See `/docs` endpoint for interactive API documentation.


