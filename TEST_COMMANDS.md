# TechAtlas API Testing Commands

## Start the Server
```powershell
python app.py
```

Server will run on: `http://127.0.0.1:5000`

---

## Test 1: Health Check
```powershell
curl http://127.0.0.1:5000/health
```

**Expected Output:**
```json
{
  "status": "healthy",
  "service": "TechAtlas Backend"
}
```

---

## Test 2: Save Decision
```powershell
curl -X POST http://127.0.0.1:5000/save-decision `
  -H "Content-Type: application/json" `
  -d '{
    "title": "Database Migration to PostgreSQL",
    "owner": "Priya Kumar",
    "rationale": "Schema has stabilized and we need better support for complex joins",
    "due_date": "2025-12-31",
    "thread_link": "https://cliq.zoho.com/thread/12345",
    "participants": ["priya@company.com", "rahul@company.com"],
    "channel_id": "tech-team"
  }'
```

**Expected Output:**
```json
{
  "success": true,
  "decision_id": "dec_1762788278601",
  "message": "Decision saved and vectorized successfully"
}
```

---

## Test 3: Query Decisions (RAG)
```powershell
curl -X POST http://127.0.0.1:5000/query-decisions `
  -H "Content-Type: application/json" `
  -d '{
    "query": "Why did we switch to PostgreSQL?",
    "user": "newdev@company.com"
  }'
```

**Expected Output:**
```json
{
  "answer": "The team migrated to PostgreSQL because the schema had stabilized and PostgreSQL provides better support for complex joins. Priya Kumar led this decision.",
  "sources": [
    {
      "decision_id": "dec_1762788278601",
      "title": "Database Migration to PostgreSQL",
      "owner": "Priya Kumar",
      "thread_link": "https://cliq.zoho.com/thread/12345",
      "relevance_score": 0.92
    }
  ]
}
```

---

## Test 4: Detect Decision
```powershell
curl -X POST http://127.0.0.1:5000/detect-decision `
  -H "Content-Type: application/json" `
  -d '{
    "message": "We decided to migrate to PostgreSQL because the schema is stable",
    "user": "priya@company.com",
    "channel_id": "tech-team"
  }'
```

**Expected Output:**
```json
{
  "is_decision": true,
  "confidence": 0.85,
  "suggested_title": "Migrate to PostgreSQL due to schema stability"
}
```

---

## Python Test Script
```powershell
python test_simple.py
```

---

## Check FAISS Data
```powershell
ls data/
```

Should show:
- `faiss_index.bin` - Vector index
- `metadata.pkl` - Decision metadata

---

## Troubleshooting

### If you get rate limit errors:
- Wait 60 seconds between tests
- The free tier has limits on requests per minute

### If query fails:
- Check server logs in the terminal running `python app.py`
- Look for error messages

### If Firebase errors:
- Ensure `firebase-key.json` exists in project root
- Check Firestore is enabled in Firebase Console
