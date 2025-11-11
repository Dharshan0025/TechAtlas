# 📮 TechAtlas Backend - Postman API Collection

Complete API reference with request/response examples for testing with Postman.

**Base URL**: `http://localhost:5000`

---

## 📋 Table of Contents

1. [Core Routes](#core-routes) (4 endpoints)
2. [Decision Detection & Analysis](#decision-detection--analysis) (2 endpoints)
3. [Decision Management](#decision-management) (3 endpoints)
4. [Decision CRUD](#decision-crud) (8 endpoints)
5. [Dashboard & Analytics](#dashboard--analytics) (10 endpoints)
6. [User & Expertise](#user--expertise) (4 endpoints)
7. [Risk Assessment](#risk-assessment) (2 endpoints)
8. [Audit & Export](#audit--export) (3 endpoints)
9. [Development Utilities](#development-utilities) (4 endpoints)

**Total: 40 Endpoints**

---

## 🔷 Core Routes

### 1. GET / - Service Info
**Description**: Get service information

**Request**:
```http
GET http://localhost:5000/
```

**Response** (200 OK):
```json
{
  "service": "TechAtlas Backend",
  "version": "2.0.0",
  "description": "AI-powered decision intelligence platform",
  "status": "operational"
}
```

---

### 2. GET /health - Health Check
**Description**: Check service health

**Request**:
```http
GET http://localhost:5000/health
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "TechAtlas Backend",
  "version": "2.0.0",
  "timestamp": "2025-11-11T10:30:00Z",
  "services": {
    "firebase": true,
    "vector_store": true,
    "gemini_ai": true
  }
}
```

---

### 3. GET /routes - List All Routes
**Description**: Get all registered API routes

**Request**:
```http
GET http://localhost:5000/routes
```

**Response** (200 OK):
```json
{
  "success": true,
  "total_routes": 40,
  "routes": [
    {
      "endpoint": "/",
      "methods": ["GET"],
      "description": "Service information"
    },
    {
      "endpoint": "/health",
      "methods": ["GET"],
      "description": "Health check"
    }
  ]
}
```

---

### 4. GET /version - API Version
**Description**: Get API version information

**Request**:
```http
GET http://localhost:5000/version
```

**Response** (200 OK):
```json
{
  "version": "2.0.0",
  "api_version": "v2",
  "release_date": "2025-11-11"
}
```

---

## 🤖 Decision Detection & Analysis

### 5. POST /detect-decision - Detect Decision
**Description**: Detect if a message contains a decision

**Request**:
```http
POST http://localhost:5000/detect-decision
Content-Type: application/json

{
  "message": "We decided to migrate to PostgreSQL for better performance and ACID compliance",
  "user": "dev@example.com",
  "channel_id": "tech-team"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "is_decision": true,
  "confidence": 0.95,
  "suggested_title": "Migration to PostgreSQL",
  "reasoning": "Message contains decision keywords and clear action",
  "timestamp": "2025-11-11T10:30:00Z"
}
```

---

### 6. POST /analyze-decision - Feasibility Analysis
**Description**: Perform AI-powered feasibility analysis

**Request**:
```http
POST http://localhost:5000/analyze-decision
Content-Type: application/json

{
  "title": "Migrate to PostgreSQL",
  "rationale": "Need better join performance, ACID compliance, and advanced features",
  "context": "Currently using MySQL with 100GB database"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "analysis": {
    "strengths": [
      "Better join performance",
      "Full ACID compliance",
      "Advanced indexing options"
    ],
    "risks": [
      "Migration complexity",
      "Potential downtime",
      "Team learning curve"
    ],
    "alternatives": [
      "Optimize current MySQL setup",
      "Consider MariaDB",
      "Evaluate cloud-managed solutions"
    ],
    "recommendation": "Proceed with migration in phases",
    "feasibility_score": 75,
    "risk_level": "Medium",
    "confidence": 0.88
  }
}
```

---

## 💾 Decision Management

### 7. POST /save-decision - Save Decision
**Description**: Save a new decision with embeddings

**Request**:
```http
POST http://localhost:5000/save-decision
Content-Type: application/json

{
  "title": "Migrate to PostgreSQL",
  "owner": "dev@example.com",
  "rationale": "Better performance and ACID compliance needed for our growing dataset",
  "due_date": "2024-12-31",
  "thread_link": "https://slack.com/archives/C123/p1234567890",
  "participants": ["dev@example.com", "dba@example.com", "lead@example.com"],
  "channel_id": "tech-team",
  "status": "Open"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "decision_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Decision saved successfully",
  "embedding_generated": true,
  "risk_score": 5,
  "timestamp": "2025-11-11T10:30:00Z"
}
```

---

### 8. POST /query-decisions - Query Decisions (RAG)
**Description**: Semantic search using RAG

**Request**:
```http
POST http://localhost:5000/query-decisions
Content-Type: application/json

{
  "query": "What decisions were made about database migrations?",
  "user": "user@example.com",
  "limit": 5
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "answer": "Three database migration decisions were made: PostgreSQL migration for better performance, MongoDB for analytics data, and Redis for caching layer.",
  "sources": [
    {
      "decision_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Migrate to PostgreSQL",
      "similarity": 0.92,
      "owner": "dev@example.com",
      "created_at": "2025-11-01T10:00:00Z"
    }
  ],
  "query_time_ms": 245
}
```

---

### 9. POST /search-decisions - Search Decisions
**Description**: Advanced search with filters

**Request**:
```http
POST http://localhost:5000/search-decisions
Content-Type: application/json

{
  "keyword": "database",
  "owner": "dev@example.com",
  "status": "Open",
  "channel_id": "tech-team",
  "min_risk_score": 5,
  "limit": 20
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "results": [
    {
      "decision_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Migrate to PostgreSQL",
      "owner": "dev@example.com",
      "status": "Open",
      "risk_score": 5,
      "created_at": "2025-11-01T10:00:00Z"
    }
  ],
  "total": 1,
  "page": 1
}
```

---

## 📝 Decision CRUD

### 10. GET /decisions - List All Decisions
**Description**: Get paginated list of decisions

**Request**:
```http
GET http://localhost:5000/decisions?limit=20&offset=0&status=Open
```

**Response** (200 OK):
```json
{
  "success": true,
  "decisions": [
    {
      "decision_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Migrate to PostgreSQL",
      "owner": "dev@example.com",
      "status": "Open",
      "risk_score": 5,
      "created_at": "2025-11-01T10:00:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

---

### 11. GET /decisions/:id - Get Decision by ID
**Description**: Get specific decision details

**Request**:
```http
GET http://localhost:5000/decisions/550e8400-e29b-41d4-a716-446655440000
```

**Response** (200 OK):
```json
{
  "success": true,
  "decision": {
    "decision_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Migrate to PostgreSQL",
    "owner": "dev@example.com",
    "rationale": "Better performance and ACID compliance",
    "due_date": "2024-12-31",
    "status": "Open",
    "risk_score": 5,
    "participants": ["dev@example.com", "dba@example.com"],
    "channel_id": "tech-team",
    "created_at": "2025-11-01T10:00:00Z",
    "updated_at": "2025-11-01T10:00:00Z"
  }
}
```

---

### 12. PUT /decisions/:id - Update Decision
**Description**: Update decision details

**Request**:
```http
PUT http://localhost:5000/decisions/550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{
  "status": "In Progress",
  "rationale": "Updated rationale with more details",
  "participants": ["dev@example.com", "dba@example.com", "pm@example.com"]
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Decision updated successfully",
  "decision_id": "550e8400-e29b-41d4-a716-446655440000",
  "updated_fields": ["status", "rationale", "participants"]
}
```

---

### 13. DELETE /decisions/:id - Delete Decision
**Description**: Delete a decision

**Request**:
```http
DELETE http://localhost:5000/decisions/550e8400-e29b-41d4-a716-446655440000
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Decision deleted successfully",
  "decision_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### 14. PATCH /decisions/:id/status - Update Status
**Description**: Update decision status only

**Request**:
```http
PATCH http://localhost:5000/decisions/550e8400-e29b-41d4-a716-446655440000/status
Content-Type: application/json

{
  "status": "Completed",
  "user": "dev@example.com"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Status updated to Completed",
  "decision_id": "550e8400-e29b-41d4-a716-446655440000",
  "old_status": "In Progress",
  "new_status": "Completed"
}
```

---

### 15. GET /decisions/:id/history - Get Decision History
**Description**: Get change history for a decision

**Request**:
```http
GET http://localhost:5000/decisions/550e8400-e29b-41d4-a716-446655440000/history
```

**Response** (200 OK):
```json
{
  "success": true,
  "decision_id": "550e8400-e29b-41d4-a716-446655440000",
  "history": [
    {
      "timestamp": "2025-11-01T10:00:00Z",
      "action": "created",
      "user": "dev@example.com",
      "changes": {}
    },
    {
      "timestamp": "2025-11-05T14:30:00Z",
      "action": "status_changed",
      "user": "dev@example.com",
      "changes": {
        "status": {"from": "Open", "to": "In Progress"}
      }
    }
  ]
}
```

---

### 16. GET /decisions/:id/related - Get Related Decisions
**Description**: Find semantically related decisions

**Request**:
```http
GET http://localhost:5000/decisions/550e8400-e29b-41d4-a716-446655440000/related?limit=5
```

**Response** (200 OK):
```json
{
  "success": true,
  "decision_id": "550e8400-e29b-41d4-a716-446655440000",
  "related_decisions": [
    {
      "decision_id": "660e8400-e29b-41d4-a716-446655440001",
      "title": "Implement database connection pooling",
      "similarity": 0.85,
      "owner": "dba@example.com"
    }
  ],
  "total": 1
}
```

---

### 17. POST /decisions/bulk - Bulk Create Decisions
**Description**: Create multiple decisions at once

**Request**:
```http
POST http://localhost:5000/decisions/bulk
Content-Type: application/json

{
  "decisions": [
    {
      "title": "Decision 1",
      "owner": "user1@example.com",
      "rationale": "Rationale 1"
    },
    {
      "title": "Decision 2",
      "owner": "user2@example.com",
      "rationale": "Rationale 2"
    }
  ]
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "created": 2,
  "decision_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "660e8400-e29b-41d4-a716-446655440001"
  ]
}
```

---

## 📊 Dashboard & Analytics

### 18. GET /dashboard/stats - Dashboard Statistics
**Description**: Get overall dashboard statistics

**Request**:
```http
GET http://localhost:5000/dashboard/stats
```

**Response** (200 OK):
```json
{
  "success": true,
  "stats": {
    "total_decisions": 150,
    "open_decisions": 45,
    "in_progress": 30,
    "completed": 75,
    "high_risk_count": 12,
    "recent_count": 28,
    "completion_rate": 50.0,
    "avg_risk_score": 4.5
  },
  "timestamp": "2025-11-11T10:30:00Z"
}
```

---

### 19. GET /decisions/high-risk - High Risk Decisions
**Description**: Get decisions with high risk scores

**Request**:
```http
GET http://localhost:5000/decisions/high-risk?threshold=7&limit=20
```

**Response** (200 OK):
```json
{
  "success": true,
  "high_risk_decisions": [
    {
      "decision_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Migrate to PostgreSQL",
      "risk_score": 8,
      "risk_factors": [
        "Single Owner",
        "Past Due"
      ],
      "owner": "dev@example.com"
    }
  ],
  "total": 1,
  "threshold": 7
}
```

---

### 20. GET /dashboard/recent - Recent Decisions
**Description**: Get recently created decisions

**Request**:
```http
GET http://localhost:5000/dashboard/recent?days=30&limit=10
```

**Response** (200 OK):
```json
{
  "success": true,
  "recent_decisions": [
    {
      "decision_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Migrate to PostgreSQL",
      "owner": "dev@example.com",
      "created_at": "2025-11-01T10:00:00Z",
      "status": "Open"
    }
  ],
  "total": 1,
  "period_days": 30
}
```

---

### 21. GET /dashboard/by-owner - Decisions by Owner
**Description**: Get decisions grouped by owner

**Request**:
```http
GET http://localhost:5000/dashboard/by-owner?limit=10
```

**Response** (200 OK):
```json
{
  "success": true,
  "by_owner": [
    {
      "owner": "dev@example.com",
      "total_decisions": 25,
      "open": 10,
      "in_progress": 8,
      "completed": 7
    }
  ]
}
```

---

### 22. GET /dashboard/by-channel - Decisions by Channel
**Description**: Get decisions grouped by channel

**Request**:
```http
GET http://localhost:5000/dashboard/by-channel?limit=10
```

**Response** (200 OK):
```json
{
  "success": true,
  "by_channel": [
    {
      "channel_id": "tech-team",
      "total_decisions": 45,
      "open": 15,
      "in_progress": 12,
      "completed": 18
    }
  ]
}
```

---

### 23. GET /dashboard/aging - Aging Decisions
**Description**: Get decisions that are aging (old and open)

**Request**:
```http
GET http://localhost:5000/dashboard/aging?threshold_days=60&limit=20
```

**Response** (200 OK):
```json
{
  "success": true,
  "aging_decisions": [
    {
      "decision_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Migrate to PostgreSQL",
      "age_days": 75,
      "status": "Open",
      "owner": "dev@example.com"
    }
  ],
  "total": 1,
  "threshold_days": 60
}
```

---

### 24. GET /dashboard/upcoming-due - Upcoming Due Decisions
**Description**: Get decisions due soon

**Request**:
```http
GET http://localhost:5000/dashboard/upcoming-due?days=7&limit=20
```

**Response** (200 OK):
```json
{
  "success": true,
  "upcoming_due": [
    {
      "decision_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Migrate to PostgreSQL",
      "due_date": "2024-12-31",
      "days_until_due": 5,
      "status": "In Progress",
      "owner": "dev@example.com"
    }
  ],
  "total": 1
}
```

---

### 25. GET /analytics/trends - Decision Trends
**Description**: Get decision trends over time

**Request**:
```http
GET http://localhost:5000/analytics/trends?period=month&months=6
```

**Response** (200 OK):
```json
{
  "success": true,
  "period": "month",
  "trends": [
    {
      "period": "2025-11",
      "total": 28,
      "open": 10,
      "completed": 15,
      "in_progress": 3
    },
    {
      "period": "2025-10",
      "total": 32,
      "open": 8,
      "completed": 20,
      "in_progress": 4
    }
  ]
}
```

---

### 26. GET /analytics/topics - Topic Analysis
**Description**: Analyze decision topics

**Request**:
```http
GET http://localhost:5000/analytics/topics?limit=10
```

**Response** (200 OK):
```json
{
  "success": true,
  "topics": [
    {
      "topic": "database",
      "count": 15,
      "percentage": 10.0
    },
    {
      "topic": "migration",
      "count": 12,
      "percentage": 8.0
    }
  ],
  "total_topics": 2
}
```

---

### 27. GET /analytics/velocity - Decision Velocity
**Description**: Calculate decision completion velocity

**Request**:
```http
GET http://localhost:5000/analytics/velocity?period=month
```

**Response** (200 OK):
```json
{
  "success": true,
  "velocity": {
    "period": "month",
    "decisions_per_period": 25.5,
    "avg_time_to_complete_days": 15.3,
    "completion_rate": 65.0
  }
}
```

---

## 👥 User & Expertise

### 28. GET /users/profile/:email - User Profile
**Description**: Get user profile and statistics

**Request**:
```http
GET http://localhost:5000/users/profile/dev@example.com
```

**Response** (200 OK):
```json
{
  "success": true,
  "user": {
    "email": "dev@example.com",
    "total_decisions": 25,
    "decisions_owned": 20,
    "decisions_participated": 5,
    "completion_rate": 70.0,
    "avg_risk_score": 4.2,
    "expertise_areas": ["database", "backend", "api"]
  }
}
```

---

### 29. GET /users/expertise/:email - User Expertise
**Description**: Get detailed expertise mapping

**Request**:
```http
GET http://localhost:5000/users/expertise/dev@example.com
```

**Response** (200 OK):
```json
{
  "success": true,
  "email": "dev@example.com",
  "expertise": [
    {
      "topic": "database",
      "decision_count": 15,
      "expertise_score": 0.85
    },
    {
      "topic": "backend",
      "decision_count": 12,
      "expertise_score": 0.78
    }
  ]
}
```

---

### 30. GET /users/top-contributors - Top Contributors
**Description**: Get top decision contributors

**Request**:
```http
GET http://localhost:5000/users/top-contributors?limit=10
```

**Response** (200 OK):
```json
{
  "success": true,
  "contributors": [
    {
      "email": "dev@example.com",
      "total_decisions": 25,
      "completed": 18,
      "completion_rate": 72.0
    }
  ],
  "total": 1
}
```

---

### 31. GET /users/knowledge-gaps - Knowledge Gaps
**Description**: Identify expertise gaps

**Request**:
```http
GET http://localhost:5000/users/knowledge-gaps
```

**Response** (200 OK):
```json
{
  "success": true,
  "knowledge_gaps": [
    {
      "topic": "security",
      "decision_count": 8,
      "expert_count": 1,
      "risk_level": "High"
    }
  ]
}
```

---

## ⚠️ Risk Assessment

### 32. POST /assess-risk - Assess Decision Risk
**Description**: Perform risk assessment on a decision

**Request**:
```http
POST http://localhost:5000/assess-risk
Content-Type: application/json

{
  "decision_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "decision_id": "550e8400-e29b-41d4-a716-446655440000",
  "risk_assessment": {
    "risk_score": 8,
    "risk_level": "High",
    "risk_factors": [
      {
        "factor": "Single Owner",
        "severity": "High",
        "description": "Knowledge silo - only one person owns this decision"
      },
      {
        "factor": "Past Due",
        "severity": "Medium",
        "description": "Decision is overdue by 5 days"
      }
    ],
    "recommendations": [
      "Add more participants",
      "Update due date or complete decision"
    ]
  }
}
```

---

### 33. POST /assess-risk/reassess - Reassess All Risks
**Description**: Reassess risk for all open decisions

**Request**:
```http
POST http://localhost:5000/assess-risk/reassess
Content-Type: application/json

{
  "status": "Open"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "reassessed_count": 45,
  "high_risk_count": 12,
  "medium_risk_count": 20,
  "low_risk_count": 13
}
```

---

## 📋 Audit & Export

### 34. GET /audit-logs - Get Audit Logs
**Description**: Retrieve audit logs

**Request**:
```http
GET http://localhost:5000/audit-logs?limit=50&offset=0&action=create
```

**Response** (200 OK):
```json
{
  "success": true,
  "logs": [
    {
      "log_id": "log-123",
      "timestamp": "2025-11-11T10:30:00Z",
      "action": "create",
      "user": "dev@example.com",
      "resource_type": "decision",
      "resource_id": "550e8400-e29b-41d4-a716-446655440000",
      "details": {}
    }
  ],
  "total": 1
}
```

---

### 35. POST /export/decisions - Export Decisions
**Description**: Export decisions to CSV/JSON

**Request**:
```http
POST http://localhost:5000/export/decisions
Content-Type: application/json

{
  "format": "csv",
  "filters": {
    "status": "Completed",
    "start_date": "2025-01-01",
    "end_date": "2025-12-31"
  }
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "export_id": "export-123",
  "format": "csv",
  "record_count": 75,
  "download_url": "/export/download/export-123",
  "expires_at": "2025-11-12T10:30:00Z"
}
```

---

### 36. POST /reminders/send - Send Reminders
**Description**: Send reminders for due decisions

**Request**:
```http
POST http://localhost:5000/reminders/send
Content-Type: application/json

{
  "days_before_due": 7
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "reminders_sent": 12,
  "recipients": [
    "dev@example.com",
    "pm@example.com"
  ]
}
```

---

## 🛠️ Development Utilities

### 37. POST /dev/seed-data - Seed Sample Data
**Description**: Create sample decisions for testing

**Request**:
```http
POST http://localhost:5000/dev/seed-data
Content-Type: application/json

{
  "count": 20
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "message": "20 sample decisions created",
  "decision_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "660e8400-e29b-41d4-a716-446655440001"
  ]
}
```

---

### 38. DELETE /dev/clear-data - Clear All Data
**Description**: Delete all decisions (development only)

**Request**:
```http
DELETE http://localhost:5000/dev/clear-data
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "All data cleared",
  "deleted_count": 150
}
```

---

### 39. GET /dev/validate-embeddings - Validate Embeddings
**Description**: Check embedding consistency

**Request**:
```http
GET http://localhost:5000/dev/validate-embeddings
```

**Response** (200 OK):
```json
{
  "success": true,
  "total_decisions": 150,
  "with_embeddings": 145,
  "missing_embeddings": 5,
  "validation_status": "OK"
}
```

---

### 40. POST /dev/reindex - Reindex Vector Store
**Description**: Rebuild FAISS index

**Request**:
```http
POST http://localhost:5000/dev/reindex
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Vector store reindexed",
  "indexed_count": 145
}
```

---

## 🔑 Common Response Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid input |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error |

---

## 📝 Common Error Response

```json
{
  "success": false,
  "error": "Error message here",
  "status": 400,
  "timestamp": "2025-11-11T10:30:00Z"
}
```

---

## 🚀 Quick Test Sequence

1. **Check Health**: `GET /health`
2. **Seed Data**: `POST /dev/seed-data` with `{"count": 20}`
3. **Get Stats**: `GET /dashboard/stats`
4. **List Decisions**: `GET /decisions?limit=10`
5. **Detect Decision**: `POST /detect-decision`
6. **Save Decision**: `POST /save-decision`
7. **Query Decisions**: `POST /query-decisions`
8. **Get Analytics**: `GET /analytics/trends`

---

**Total Endpoints: 40**  
**Base URL**: `http://localhost:5000`  
**Authentication**: None (add as needed)

**Ready to import into Postman! 📮**
