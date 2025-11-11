# TechAtlas Backend - Complete API Routes Documentation

## 📋 **Route Summary**

**Total Routes Implemented**: 34+ endpoints across 10 blueprints

---

## 🏠 **Core System Routes** (`routes/core.py`)

### 1. **GET /** - Service Information
- **Description**: Root endpoint with service info and available endpoints list
- **Response**: Service metadata, version, endpoint list
- **Status**: ✅ Implemented

### 2. **GET /health** - Health Check
- **Description**: Health check with component status (Firebase, Vector Store, Gemini AI)
- **Response**: Service health status, component statuses
- **Status**: ✅ Implemented

### 3. **GET /routes** - List All Routes
- **Description**: List all registered routes (debug/development only)
- **Response**: Array of all API endpoints with methods
- **Status**: ✅ Implemented

### 4. **GET /version** - API Version
- **Description**: API version and build information
- **Response**: Version, build info, feature list
- **Status**: ✅ Implemented

---

## 🔍 **Decision Detection & Analysis** (`routes/detect.py`, `routes/analyze.py`)

### 5. **POST /detect-decision** - Decision Detection
- **Description**: Analyze text to detect if it contains a decision
- **Input**: `message`, `user`, `channel_id`
- **Output**: `is_decision`, `confidence`, `suggested_title`
- **Status**: ✅ Implemented

### 6. **POST /analyze-decision** - Feasibility Analysis ⭐ NEW
- **Description**: Perform AI-powered feasibility analysis
- **Input**: `title`, `rationale`, `context`
- **Output**: `strengths`, `risks`, `alternatives`, `past_decisions`, `recommendation`, `feasibility_score`
- **Status**: ✅ Implemented (placeholder for AI integration)

---

## 💾 **Decision Storage & Management** (`routes/save.py`, `routes/decisions.py`)

### 7. **POST /save-decision** - Save Decision
- **Description**: Save a new decision with embeddings
- **Input**: `title`, `owner`, `rationale`, `due_date`, `thread_link`, `participants`, `channel_id`
- **Output**: `decision_id`, success message
- **Status**: ✅ Implemented

### 8. **GET /decisions** - List Decisions
- **Description**: List all decisions with pagination and filters
- **Query Params**: `status`, `owner`, `channel_id`, `limit`, `offset`, `sort_by`
- **Output**: Array of decisions with pagination metadata
- **Status**: ✅ Implemented

### 9. **GET /decisions/{decision_id}** - Get Single Decision
- **Description**: Retrieve full decision details
- **Output**: Complete decision object
- **Status**: ✅ Implemented

### 10. **PUT /decisions/{decision_id}** - Update Decision
- **Description**: Update existing decision
- **Input**: Updated fields (`status`, `rationale`, `due_date`, etc.)
- **Output**: Updated decision object
- **Status**: ✅ Implemented

### 11. **DELETE /decisions/{decision_id}** - Delete Decision
- **Description**: Soft delete a decision (archives it)
- **Output**: Success message
- **Status**: ✅ Implemented

### 12. **PATCH /decisions/{decision_id}/status** - Change Status
- **Description**: Update decision status
- **Input**: `status` (Open/In Progress/Completed/Archived)
- **Output**: Updated status
- **Status**: ✅ Implemented

### 13. **GET /decisions/{decision_id}/history** - Decision History
- **Description**: Get change log for a decision
- **Output**: Array of changes (who, when, what changed)
- **Status**: ✅ Implemented (placeholder)

### 14. **GET /decisions/{decision_id}/related** - Related Decisions
- **Description**: Find semantically similar decisions
- **Output**: Array of related decisions with similarity scores
- **Status**: ✅ Implemented (placeholder for vector search)

---

## 🔎 **Search & Retrieval** (`routes/query.py`, `routes/decisions.py`)

### 15. **POST /query-decisions** - Semantic Query (RAG)
- **Description**: Natural language search with RAG
- **Input**: `query`, `user`
- **Output**: `answer`, `sources` (decisions with relevance scores)
- **Status**: ✅ Implemented

### 16. **POST /search-decisions** - Advanced Search
- **Description**: Structured search with filters
- **Input**: `keyword`, `owner`, `date_range`, `status`, `channel_id`
- **Output**: List of matching decisions
- **Status**: ✅ Implemented

---

## 📊 **Dashboard & Analytics** (`routes/dashboard.py`)

### 17. **GET /dashboard/stats** - Dashboard Statistics
- **Description**: Overview statistics
- **Output**: `total_decisions`, `open_decisions`, `high_risk_count`, `recent_count`
- **Status**: ✅ Implemented

### 18. **GET /decisions/high-risk** - High-Risk Decisions
- **Description**: Get decisions with risk_score >= 7
- **Output**: Array of high-risk decisions sorted by risk score
- **Status**: ✅ Implemented

### 19. **GET /decisions/recent** - Recent Decisions
- **Description**: Get decisions from last N days
- **Query Params**: `days` (default: 30)
- **Output**: Array of recent decisions
- **Status**: ✅ Implemented

### 20. **GET /decisions/by-owner/{owner_email}** - Decisions by Owner
- **Description**: Get all decisions owned by a specific person
- **Output**: Array of decisions with ownership stats
- **Status**: ✅ Implemented

### 21. **GET /decisions/by-channel/{channel_id}** - Decisions by Channel
- **Description**: Get all decisions from a specific channel
- **Output**: Array of decisions grouped by channel
- **Status**: ✅ Implemented

### 22. **GET /decisions/aging** - Aging Decisions
- **Description**: Get decisions past due date or unreviewed
- **Query Params**: `days_threshold`
- **Output**: Array of aging decisions needing review
- **Status**: ✅ Implemented

### 23. **GET /decisions/upcoming-due** - Upcoming Due Dates
- **Description**: Get decisions due soon
- **Query Params**: `days_ahead` (default: 7)
- **Output**: Array of decisions with approaching due dates
- **Status**: ✅ Implemented

---

## 👥 **User & Expertise Management** (`routes/users.py`)

### 24. **GET /users/{user_email}** - User Profile
- **Description**: Get user profile and decision stats
- **Output**: `name`, `decisions_owned`, `decisions_participated`, `expertise_areas`
- **Status**: ✅ Implemented

### 25. **GET /expertise** - Expertise Map
- **Description**: Get expertise distribution across topics
- **Output**: Array of topics with expert users
- **Status**: ✅ Implemented

### 26. **GET /users/top-contributors** - Top Contributors
- **Description**: Get most active decision makers
- **Query Params**: `limit` (default: 10)
- **Output**: Ranked list of users by contribution
- **Status**: ✅ Implemented

### 27. **GET /knowledge-gaps** - Knowledge Gaps
- **Description**: Identify single-owner decisions (knowledge silos)
- **Output**: Array of decisions with single participants
- **Status**: ✅ Implemented

---

## 📈 **Trends & Insights** (`routes/analytics.py`)

### 28. **GET /analytics/trends** - Decision Trends
- **Description**: Get decision-making trends over time
- **Query Params**: `period` (week/month/year)
- **Output**: Timeline data with decision counts
- **Status**: ✅ Implemented

### 29. **GET /analytics/topics** - Topic Analysis
- **Description**: Get most discussed decision topics
- **Output**: Array of topics with frequency and sentiment
- **Status**: ✅ Implemented

### 30. **GET /analytics/velocity** - Decision Velocity
- **Description**: Average time from decision to completion
- **Output**: `avg_completion_time`, `fastest`, `slowest`
- **Status**: ✅ Implemented

---

## ⚠️ **Risk & Monitoring** (`routes/risk.py`)

### 31. **POST /assess-risk/{decision_id}** - Risk Assessment
- **Description**: Re-calculate risk score for a decision
- **Output**: Updated `risk_score`, `risk_level`, `risk_factors`
- **Status**: ✅ Implemented

### 32. **POST /decisions/reassess-all-risks** - Reassess All Risks
- **Description**: Recalculate risk scores for all decisions
- **Output**: Count of updated decisions
- **Status**: ✅ Implemented

---

## 🗂️ **Audit & Compliance** (`routes/audit.py`)

### 33. **GET /audit-logs** - Audit Logs
- **Description**: Get system audit trail
- **Query Params**: `user`, `action_type`, `date_range`, `limit`
- **Output**: Array of audit log entries
- **Status**: ✅ Implemented (placeholder)

### 34. **GET /export/decisions** - Export Data
- **Description**: Export decisions as CSV/JSON
- **Query Params**: `format` (csv/json), filters
- **Output**: Downloadable file
- **Status**: ✅ Implemented

### 35. **POST /reminders/send** - Send Reminder
- **Description**: Trigger reminder for a decision
- **Input**: `decision_id`, `recipient_email`
- **Output**: Success, reminder_sent_at
- **Status**: ✅ Implemented (placeholder)

---

## 🧪 **Testing & Development** (`routes/dev.py`)

### 36. **POST /dev/seed-data** - Seed Sample Data
- **Description**: Populate database with sample decisions (dev only)
- **Input**: `count` (number of samples)
- **Output**: Success, created_count
- **Status**: ✅ Implemented

### 37. **DELETE /dev/clear-data** - Clear Test Data
- **Description**: Clear all test data (dev only)
- **Output**: Success, deleted_count
- **Status**: ✅ Implemented

### 38. **POST /dev/validate-embeddings** - Validate Embeddings
- **Description**: Test embedding generation (dev only)
- **Input**: `text`
- **Output**: `embedding_vector`, `dimension`
- **Status**: ✅ Implemented

### 39. **GET /dev/stats** - Development Stats
- **Description**: Get development environment statistics
- **Output**: Database stats, environment info
- **Status**: ✅ Implemented

---

## 🎯 **Implementation Priority**

### 🔴 **CRITICAL (MVP/Demo Ready)**
- ✅ POST /detect-decision
- ✅ POST /analyze-decision (NEW - differentiator)
- ✅ POST /save-decision
- ✅ POST /query-decisions
- ✅ GET /health
- ✅ GET /dashboard/stats
- ✅ GET /decisions

### 🟡 **IMPORTANT (Strong Demo)**
- ✅ GET /decisions/{decision_id}
- ✅ GET /decisions/high-risk
- ✅ PUT /decisions/{decision_id}
- ✅ GET /decisions/recent
- ✅ GET /decisions/by-owner/{owner_email}
- ✅ GET /expertise

### 🟢 **NICE-TO-HAVE (Future Enhancement)**
- ✅ GET /analytics/trends
- ✅ GET /decisions/aging
- ✅ POST /assess-risk/{decision_id}
- ⏳ GET /audit-logs (placeholder)
- ⏳ GET /decisions/{decision_id}/related (needs vector search)
- ✅ GET /users/top-contributors

### ⚪ **DEVELOPMENT ONLY**
- ✅ POST /dev/seed-data
- ✅ DELETE /dev/clear-data
- ✅ POST /dev/validate-embeddings
- ✅ GET /dev/stats

---

## 📂 **File Structure**

```
routes/
├── __init__.py
├── core.py          # GET /, /health, /routes, /version
├── detect.py        # POST /detect-decision
├── analyze.py       # POST /analyze-decision (NEW)
├── save.py          # POST /save-decision
├── query.py         # POST /query-decisions, POST /search-decisions
├── decisions.py     # GET/PUT/DELETE /decisions/{id}, GET /decisions
├── dashboard.py     # GET /dashboard/*, GET /decisions/high-risk, /recent
├── users.py         # GET /users/*, GET /expertise
├── analytics.py     # GET /analytics/*
├── risk.py          # POST /assess-risk, GET /knowledge-gaps
├── audit.py         # GET /audit-logs, GET /export/*
└── dev.py           # POST /dev/* (development routes)
```

---

## 🚀 **Next Steps for Refinement**

### **Phase 1: AI Integration**
- [ ] Implement actual Gemini AI analysis in `/analyze-decision`
- [ ] Add vector similarity search for `/decisions/{id}/related`
- [ ] Enhance topic extraction with NLP

### **Phase 2: Real-time Features**
- [ ] Implement actual audit logging system
- [ ] Add email/notification service for reminders
- [ ] WebSocket support for real-time updates

### **Phase 3: Advanced Analytics**
- [ ] Sentiment analysis for decisions
- [ ] Predictive risk modeling
- [ ] Decision impact analysis
- [ ] Knowledge graph visualization

### **Phase 4: Enterprise Features**
- [ ] Multi-tenant support
- [ ] Role-based access control
- [ ] Advanced export formats (PDF, Excel)
- [ ] Scheduled reports

---

## 🎉 **Summary**

**Total Routes**: 39 endpoints
**Status**: All basic implementations complete ✅
**Ready for**: Testing, iteration, and AI enhancement

The foundation is solid with comprehensive CRUD operations, analytics, user management, and development utilities. All routes return proper JSON responses with error handling and logging.
