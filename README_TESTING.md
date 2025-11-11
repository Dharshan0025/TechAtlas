# TechAtlas Backend v2.0 - Testing & Deployment Guide

## 📋 Overview

TechAtlas Backend is a production-ready Flask API for detecting, saving, and querying team decisions using AI-powered RAG (Retrieval-Augmented Generation).

## 🎯 Features

- **Decision Detection**: AI-powered detection of decisions in text
- **Decision Storage**: Vector embeddings + Firestore for efficient retrieval
- **RAG Querying**: Intelligent decision querying with context
- **Comprehensive Testing**: 42 test cases with 100% endpoint coverage
- **Production Ready**: Hardened error handling, logging, and monitoring

## 📁 Project Structure

```
TechAtlas/
├── app_v2.py                  # Main application (use this)
├── app_v2_production.py       # Enhanced production version
├── test_suite.py              # Comprehensive test suite (42 tests)
├── requirements.txt           # Python dependencies
├── config.py                  # Configuration management
├── .env                       # Environment variables
├── firebase-key.json          # Firebase credentials
├── services/                  # Service layer
│   ├── detector.py           # Decision detection service
│   ├── embedder.py           # Embedding generation
│   ├── vector_store.py       # FAISS vector store
│   └── rag_engine.py         # RAG implementation
├── models/                    # Data models
│   └── decision.py           # Decision model
└── routes/                    # Route handlers (legacy)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

Ensure `.env` file contains:
```env
GEMINI_API_KEY=your_api_key_here
FIREBASE_CREDENTIALS_PATH=./firebase-key.json
PORT=5000
DEBUG=True
```

### 3. Run the Application

```bash
python app_v2.py
```

Expected output:
```
============================================================
🚀 TechAtlas Backend v2.0 - Production
============================================================
✅ Firebase initialized successfully
📋 Configuration:
   - Port: 5000
   - Debug: True
============================================================
🌐 Server starting on http://0.0.0.0:5000
============================================================
```

## 🧪 Testing

### Run All Tests

```bash
# Run with verbose output
python -m pytest test_suite.py -v

# Run with coverage report
python -m pytest test_suite.py -v --cov=app_v2 --cov-report=html

# Run specific test class
python -m pytest test_suite.py::TestDetectDecisionEndpoint -v

# Run with output capture disabled (see print statements)
python -m pytest test_suite.py -v -s
```

### Test Coverage

The test suite includes **42 comprehensive tests** covering:

#### 1. Health Check (5 tests)
- ✅ Returns 200 status
- ✅ Returns JSON format
- ✅ Includes required fields
- ✅ Status is 'healthy'
- ✅ Service name validation

#### 2. Routes Listing (3 tests)
- ✅ Returns 200 status
- ✅ Returns list format
- ✅ Includes all endpoints

#### 3. Detect Decision (12 tests)
- ✅ Valid input returns 200
- ✅ Response includes expected fields
- ✅ Missing message returns 400
- ✅ Empty message returns 400
- ✅ No JSON returns 400
- ✅ Long message handling
- ✅ Special characters handling
- ✅ Unicode characters handling
- ✅ Optional fields support
- ✅ Confidence range validation
- ✅ Boolean type validation
- ✅ Error handling for failures

#### 4. Save Decision (12 tests)
- ✅ Valid input returns 200
- ✅ Returns decision_id
- ✅ Missing title returns 400
- ✅ Missing owner returns 400
- ✅ Missing rationale returns 400
- ✅ Missing due_date returns 400
- ✅ Missing thread_link returns 400
- ✅ No JSON returns 400
- ✅ Optional fields support
- ✅ Firestore failure handling
- ✅ Embedding failure handling
- ✅ Success response format

#### 5. Query Decisions (10 tests)
- ✅ Valid query returns 200
- ✅ Returns answer and sources
- ✅ Missing query returns 400
- ✅ Empty query returns 400
- ✅ No JSON returns 400
- ✅ Optional user field support
- ✅ Long query handling
- ✅ Special characters handling
- ✅ RAG engine failure handling
- ✅ Error response format

### Expected Test Results

```
============================================================
test_suite.py::TestHealthEndpoint::test_health_check_returns_200 PASSED
test_suite.py::TestHealthEndpoint::test_health_check_returns_json PASSED
test_suite.py::TestHealthEndpoint::test_health_check_has_required_fields PASSED
...
============================================================
42 passed in 2.50s
============================================================
✅ ALL TESTS PASSED - Backend is production ready!
```

## 📡 API Endpoints

### 1. GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "TechAtlas Backend",
  "version": "2.0"
}
```

### 2. POST /detect-decision

Detect if text contains a decision.

**Request:**
```json
{
  "message": "We decided to migrate to PostgreSQL",
  "user": "john@company.com",
  "channel_id": "tech-team"
}
```

**Response:**
```json
{
  "is_decision": true,
  "confidence": 0.95,
  "suggested_title": "Migrate to PostgreSQL"
}
```

### 3. POST /save-decision

Save a decision with embeddings.

**Request:**
```json
{
  "title": "Migrate to PostgreSQL",
  "owner": "john@company.com",
  "rationale": "Better performance and ACID compliance",
  "due_date": "2025-12-31",
  "thread_link": "https://slack.com/thread/123",
  "participants": ["john@company.com", "jane@company.com"],
  "channel_id": "tech-team"
}
```

**Response:**
```json
{
  "success": true,
  "decision_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Decision saved and vectorized successfully"
}
```

### 4. POST /query-decisions

Query decisions using RAG.

**Request:**
```json
{
  "query": "Why did we choose PostgreSQL?",
  "user": "newdev@company.com"
}
```

**Response:**
```json
{
  "answer": "We chose PostgreSQL because...",
  "sources": [
    {
      "title": "Migrate to PostgreSQL",
      "content": "Better performance...",
      "decision_id": "550e8400-e29b-41d4-a716-446655440000"
    }
  ]
}
```

### 5. GET /routes

List all registered routes (debug endpoint).

**Response:**
```json
[
  {
    "endpoint": "health_check",
    "methods": ["GET"],
    "url": "/health"
  },
  ...
]
```

## 🧪 Manual Testing with PowerShell

Use the included `test_api.ps1` script:

```powershell
.\test_api.ps1
```

Or test manually:

```powershell
# Test health check
Invoke-RestMethod -Uri "http://localhost:5000/health" -Method Get

# Test detect decision
$body = @{
    message = "We decided to migrate to PostgreSQL"
    user = "test@test.com"
    channel_id = "tech"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/detect-decision" -Method Post -Body $body -ContentType "application/json"
```

## 🔧 Troubleshooting

### Test Failures

**Issue**: `ModuleNotFoundError: No module named 'pytest'`
```bash
pip install pytest pytest-cov pytest-mock
```

**Issue**: `ModuleNotFoundError: No module named 'flask'`
```bash
# Make sure virtual environment is activated
.\venv\Scripts\activate
pip install -r requirements.txt
```

**Issue**: Firebase initialization fails
```
✅ Check firebase-key.json exists
✅ Check FIREBASE_CREDENTIALS_PATH in .env
✅ Verify Firebase credentials are valid
```

### Server Issues

**Issue**: Port 5000 already in use
```bash
# Change port in .env
PORT=5001
```

**Issue**: Gemini API errors
```
✅ Check GEMINI_API_KEY in .env
✅ Verify API key is active
✅ Check API quota limits
```

## 📊 Production Deployment

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app_v2:app
```

### Using Docker (recommended)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app_v2:app"]
```

## 📈 Monitoring

### Health Check Monitoring

Set up periodic health checks:
```bash
curl http://localhost:5000/health
```

Expected: 200 status with `"status": "healthy"`

### Logs

Application logs are written to:
- Console (stdout)
- `techatlas_backend.log` file

## ✅ Pre-Production Checklist

- [ ] All 42 tests pass
- [ ] Health check returns 200
- [ ] Firebase connection successful
- [ ] Gemini API key configured
- [ ] Environment variables set
- [ ] Logs directory writable
- [ ] Port 5000 available (or configured)
- [ ] Frontend integration tested

## 🎓 Code Quality

### Test Coverage Goal: 80%+

Run coverage report:
```bash
python -m pytest test_suite.py --cov=app_v2 --cov-report=term-missing
```

### Linting

```bash
# Install flake8
pip install flake8

# Run linter
flake8 app_v2.py services/ models/
```

## 🤝 Contributing

1. Write tests for new features
2. Ensure all tests pass
3. Update documentation
4. Follow existing code style

## 📝 License

Proprietary - TechAtlas Internal Use Only

## 🆘 Support

For issues or questions:
- Check logs: `techatlas_backend.log`
- Run health check: `GET /health`
- Review test failures: `pytest test_suite.py -v`

---

**Version**: 2.0  
**Last Updated**: November 2025  
**Status**: ✅ Production Ready
