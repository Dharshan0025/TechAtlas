# 🔧 API Endpoint Corrections

## ❌ **Incorrect Endpoint in Postman Collection**

The Postman collection had an incorrect endpoint. Here's the fix:

### **Search Decisions**

**❌ WRONG (in Postman collection)**:
```
POST /decisions/search
```

**✅ CORRECT**:
```
POST /search-decisions
```

---

## ✅ **Corrected Postman Request**

### **Search Decisions - CORRECTED**

**Request**:
```http
POST http://localhost:5000/search-decisions
Content-Type: application/json

{
  "keyword": "database",
  "status": "Open",
  "limit": 20
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "results": [
    {
      "decision_id": "dec_1762838928599",
      "title": "Migrate to PostgreSQL",
      "owner": "dev@example.com",
      "status": "Open",
      "risk_score": 5,
      "created_at": "2025-11-11T05:28:49.270000+00:00"
    }
  ],
  "total": 1
}
```

---

## 📋 **All Correct Decision Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/decisions` | List all decisions |
| GET | `/decisions/:id` | Get decision by ID |
| POST | `/decisions` | Create new decision |
| PUT | `/decisions/:id` | Update decision |
| DELETE | `/decisions/:id` | Delete decision |
| PATCH | `/decisions/:id/status` | Update status only |
| GET | `/decisions/:id/history` | Get decision history |
| GET | `/decisions/:id/related` | Get related decisions |
| **POST** | **`/search-decisions`** | **Search with filters** ⭐ |

---

## 🔍 **Quick Test**

```bash
# Test the correct endpoint
curl -X POST http://localhost:5000/search-decisions \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "database",
    "status": "Open",
    "limit": 20
  }'
```

---

## 📝 **Updated Postman Request Body**

For `/search-decisions`:

```json
{
  "keyword": "database",
  "owner": "dev@example.com",
  "status": "Open",
  "channel_id": "tech-team",
  "min_risk_score": 5,
  "max_risk_score": 10,
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "limit": 20,
  "offset": 0
}
```

**All fields are optional** - you can search with any combination.

---

## ✅ **Working Now!**

The endpoint is `/search-decisions` (not `/decisions/search`).

Update your Postman collection and try again! 🚀
