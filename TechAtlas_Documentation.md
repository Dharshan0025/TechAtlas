# TechAtlas Backend Documentation

## 1. Project Overview

**TechAtlas** is a Decision Intelligence Engine designed to combat "Decision Drift" in engineering teams. It captures, analyzes, and retrieves decisions from chat conversations using AI, acting as a centralized knowledge base for architectural and technical decisions.

### Core Philosophy
- **Capture**: Automatically detect and structure decisions from natural language conversations.
- **Analyze**: Evaluate decisions for feasibility, risks, and gaps using AI.
- **Retrieve**: Provide semantic search and Q&A capabilities to find past decisions instantly.
- **Insight**: Generate analytics on decision velocity, risks, and team expertise.

### Technology Stack
- **Framework**: Flask (Python)
- **Database**: Google Firebase Firestore (NoSQL)
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **AI/LLM**: Google Gemini Pro
- **Authentication**: Firebase Auth (implied via token verification)

---

## 2. Core Services

The application logic is encapsulated in modular services located in the `services/` directory.

### AI & NLP Services

#### `DecisionDetector` (`services/detector.py`)
- **Purpose**: Identifies if a chat message contains a team decision.
- **Mechanism**:
    1.  **Keyword Check**: Filters messages based on high-signal keywords (e.g., "decided", "agreed", "plan").
    2.  **AI Analysis**: Uses Gemini to analyze the context and extract a confidence score (0.0-1.0) and a concise title.
- **Key Methods**: `detect(message: str) -> tuple[bool, float, str]`

#### `FeasibilityAnalyzer` (`services/feasibility_analyzer.py`)
- **Purpose**: Evaluates the quality and viability of a proposed decision.
- **Mechanism**: Uses Gemini to analyze the decision's title, rationale, and context. It compares the decision against historical data (via RAG) to identify contradictions or patterns.
- **Outputs**: Strengths, Risks, Alternatives, Feasibility Score (0-100), Recommendation.
- **Key Methods**: `analyze(title, rationale, context)`, `analyze_with_history(title, rationale, context, past_decisions)`

#### `GeminiEmbedder` (`services/embedder.py`)
- **Purpose**: Converts text into vector embeddings for semantic search.
- **Mechanism**: Uses Google's `embedding-001` model to generate 768-dimensional vectors.
- **Key Methods**: `embed(text: str) -> List[float]`

#### `TextProcessor` (`services/text_processor.py`)
- **Purpose**: Utilities for text cleaning and analysis.
- **Features**: Keyword extraction, entity extraction (people, tools, dates), sentiment analysis (VADER-based), and text summarization.
- **Key Methods**: `clean_text()`, `extract_keywords()`, `analyze_sentiment()`, `summarize_text()`

### Search & Retrieval Services

#### `RAGEngine` (`services/rag_engine.py`)
- **Purpose**: Orchestrates Retrieval-Augmented Generation for answering user queries.
- **Pipeline**:
    1.  **Embed**: Convert user query to vector.
    2.  **Retrieve**: Search `VectorStore` for relevant past decisions.
    3.  **Generate**: Feed retrieved context + query to Gemini to generate a natural language answer.
- **Key Methods**: `query(user_query: str) -> dict`

#### `VectorStore` (`services/vector_store.py`)
- **Purpose**: Manages high-dimensional vector data for similarity search.
- **Implementation**: Uses FAISS (FlatIP index) for fast cosine similarity searches. Persists index to disk (`data/faiss_index.bin`).
- **Key Methods**: `upsert(id, embedding, metadata)`, `query(embedding, top_k)`

#### `SearchEngine` (`services/search_engine.py`)
- **Purpose**: Unified search interface supporting multiple modes.
- **Modes**:
    -   **Keyword**: Exact match in title/rationale.
    -   **Filter**: Structured search (status, owner, date, risk).
    -   **Semantic**: Concept-based search (currently falls back to keyword search if vector search isn't fully integrated).
    -   **Advanced**: Combines filters and text queries.

### Analytics & Management Services

#### `AnalyticsEngine` (`services/analytics_engine.py`)
- **Purpose**: Aggregates data for dashboards and reports.
- **Metrics**: Decision trends (weekly/monthly), topic frequency, decision velocity (time to complete), and owner stats.

#### `RiskAssessor` (`services/risk_assessor.py`)
- **Purpose**: Heuristic-based risk evaluation.
- **Risk Factors**:
    -   **Single Owner**: "Bus factor" risk.
    -   **Aging**: Decisions open > 90 days.
    -   **Due Date**: Past due or due soon.
    -   **Documentation**: Short/insufficient rationale.
- **Key Methods**: `assess_decision_risk()`, `detect_knowledge_silos()`

#### `ExpertiseMapper` (`services/expertise_mapper.py`)
- **Purpose**: Infers user expertise based on decision ownership and participation.
- **Features**: Identifies top contributors and maps users to specific topics (e.g., "Database", "UI").

#### `AuditLogger` (`services/audit_logger.py`)
- **Purpose**: Compliance and tracking.
- **Function**: Logs every create, update, delete, view, and search action to the `audit_logs` Firestore collection.

#### `NotificationManager` (`services/notification_manager.py`)
- **Purpose**: Handles system alerts.
- **Types**: Due date reminders, overdue alerts, high-risk warnings, assignment notifications.
- **Note**: Currently logs to console; email integration is mocked.

---

## 3. API Reference

### Core & System
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Service info and available endpoints. |
| `GET` | `/health` | Health check for Firebase, Vector Store, and AI services. |
| `GET` | `/version` | API version and build details. |
| `GET` | `/routes` | List all registered API routes (Dev/Debug). |

### Decision Management
| Method | Endpoint | Description | Input | Output |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/detect-decision` | Detect if text is a decision. | `{ "message": "..." }` | `{ "is_decision": bool, "confidence": float, "title": "..." }` |
| `POST` | `/analyze-decision` | AI feasibility analysis. | `{ "title": "...", "rationale": "...", "context": "..." }` | Analysis object (strengths, risks, score, etc.) |
| `POST` | `/save-decision` | Save and vectorise a decision. | `{ "title", "owner", "rationale", "due_date", "thread_link" }` | `{ "decision_id": "...", "status": "success" }` |
| `GET` | `/decisions` | List decisions with pagination/filters. | Query params: `page`, `limit`, `status`, `owner` | List of decisions |
| `GET` | `/decisions/<id>` | Get single decision details. | N/A | Decision object |
| `PUT` | `/decisions/<id>` | Update decision details. | JSON body with fields to update | Updated decision object |
| `PATCH` | `/decisions/<id>/status` | Update status only. | `{ "status": "In Progress" }` | Success message |
| `DELETE` | `/decisions/<id>` | Soft delete a decision. | N/A | Success message |

### Search & Intelligence
| Method | Endpoint | Description | Input | Output |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/query-decisions` | RAG-based Q&A. | `{ "query": "Why did we choose Postgres?" }` | `{ "answer": "...", "sources": [...] }` |
| `POST` | `/search-decisions` | Structured/Advanced search. | `{ "query": "...", "filters": {...} }` | List of matching decisions |
| `GET` | `/decisions/<id>/related` | Find semantically similar decisions. | N/A | List of related decisions with similarity scores |

### Analytics & Dashboard
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/dashboard/stats` | High-level stats (total, open, high-risk counts). |
| `GET` | `/analytics/trends` | Decision volume over time (period=week/month). |
| `GET` | `/analytics/topics` | Most frequent topics with sentiment analysis. |
| `GET` | `/analytics/velocity` | Avg days to complete decisions. |
| `GET` | `/decisions/high-risk` | List decisions with risk score >= 7. |
| `GET` | `/decisions/aging` | List decisions older than threshold (default 30 days). |

### Users & Expertise
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/users/<email>` | User profile, stats, and inferred expertise. |
| `GET` | `/users/top-contributors` | Leaderboard of most active decision makers. |
| `GET` | `/expertise` | Map of topics to experts. |
| `GET` | `/knowledge-gaps` | Identify "knowledge silos" (single-owner topics). |

### Risk & Audit
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/assess-risk/<id>` | Trigger risk assessment for a specific decision. |
| `POST` | `/decisions/reassess-all-risks` | Batch reassess risks for all decisions. |
| `GET` | `/audit-logs` | Retrieve system audit logs (filterable by user/action). |
| `GET` | `/export/decisions` | Export data as CSV or JSON. |

### Development Utilities (`/dev`)
*These endpoints are for testing and seeding data.*
- `POST /dev/seed-data`: Populate DB with sample decisions.
- `DELETE /dev/clear-data`: Wipe all decision data.
- `POST /dev/validate-embeddings`: Test embedding generation for a string.
- `GET /dev/stats`: DB statistics.

---

## 4. Data Models

### Firestore Collections
- **`decisions`**: Main storage. Documents contain:
    -   `title`, `rationale`, `owner`, `status`, `created_at`, `due_date`
    -   `participants` (list), `tags` (list)
    -   `risk_score`, `risk_level`, `risk_factors`
    -   `embedding_id` (reference to vector store)
- **`audit_logs`**: Immutable history of actions.
- **`users`**: (Optional) Extended user profiles.

### Vector Store (FAISS)
- Stores 768-dimensional vectors generated by Gemini.
- Metadata includes: `decision_id`, `title`, `owner`, `status`.
