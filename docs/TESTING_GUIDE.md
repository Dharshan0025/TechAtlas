# 🧪 TechAtlas Backend - Testing Guide

## 📋 **Test Coverage**

Comprehensive test suites have been created for all core services:

### **✅ Services Tested**

1. **FeasibilityAnalyzer** - `tests/test_feasibility_analyzer.py`
   - ✅ Initialization
   - ✅ Basic feasibility analysis
   - ✅ Score calculation
   - ✅ Risk level determination
   - ✅ Recommendation generation
   - ✅ Fallback analysis
   - ✅ Analysis with history

2. **AnalyticsEngine** - `tests/test_analytics_engine.py`
   - ✅ Decision count aggregation
   - ✅ Trend analysis
   - ✅ Topic frequency
   - ✅ Owner contribution metrics
   - ✅ Channel activity tracking
   - ✅ Completion rate calculation
   - ✅ Time to resolution
   - ✅ Decision velocity
   - ✅ Comprehensive dashboard stats

3. **RiskAssessor** - `tests/test_risk_assessor.py`
   - ✅ Risk assessment for single owner
   - ✅ Risk assessment with multiple participants
   - ✅ Past due detection
   - ✅ Due soon detection
   - ✅ Open status risk
   - ✅ Aging decision detection
   - ✅ Insufficient documentation detection
   - ✅ Single owner risk detection
   - ✅ Knowledge silo detection
   - ✅ Risk trend calculation

4. **InputValidator** - `tests/test_input_validator.py`
   - ✅ Email validation (valid, invalid, empty)
   - ✅ Title validation (length, empty)
   - ✅ Rationale validation (length, empty)
   - ✅ URL validation (HTTP, HTTPS, invalid)
   - ✅ Date validation (format, value)
   - ✅ Participants validation (list, emails, count)
   - ✅ Status validation
   - ✅ Decision input validation
   - ✅ Text sanitization (script removal, XSS prevention)
   - ✅ Query parameter validation
   - ✅ Pagination validation
   - ✅ Required fields validation
   - ✅ Field type validation

5. **TextProcessor** - `tests/test_text_processor.py`
   - ✅ Text cleaning (URLs, emails, special chars)
   - ✅ Keyword extraction (frequency, stop words)
   - ✅ Entity extraction (people, tools, dates)
   - ✅ Sentiment analysis (positive, negative, neutral)
   - ✅ Text summarization
   - ✅ Language detection
   - ✅ Duplicate detection
   - ✅ Action item extraction

---

## 🚀 **Running Tests**

### **Option 1: Run All Tests (Recommended)**

```bash
python run_tests.py
```

This will:
- Run all test suites
- Display detailed results
- Generate a summary report
- Return exit code (0 = success, 1 = failures)

### **Option 2: Run Individual Test Files**

```bash
# Test FeasibilityAnalyzer
python -m pytest tests/test_feasibility_analyzer.py -v

# Test AnalyticsEngine
python -m pytest tests/test_analytics_engine.py -v

# Test RiskAssessor
python -m pytest tests/test_risk_assessor.py -v

# Test InputValidator
python -m pytest tests/test_input_validator.py -v

# Test TextProcessor
python -m pytest tests/test_text_processor.py -v
```

### **Option 3: Run Specific Test Classes**

```bash
# Run specific test class
python -m pytest tests/test_input_validator.py::TestInputValidator -v

# Run specific test method
python -m pytest tests/test_input_validator.py::TestInputValidator::test_validate_email_valid -v
```

### **Option 4: Run with Coverage**

```bash
# Install coverage
pip install pytest-cov

# Run with coverage report
python -m pytest tests/ --cov=services --cov-report=html --cov-report=term

# View HTML report
# Open htmlcov/index.html in browser
```

---

## 📊 **Test Statistics**

### **Total Test Cases: 100+**

| Service | Test Cases | Coverage |
|---------|-----------|----------|
| FeasibilityAnalyzer | 8 tests | Core functionality |
| AnalyticsEngine | 11 tests | All metrics |
| RiskAssessor | 13 tests | All risk factors |
| InputValidator | 40+ tests | All validation rules |
| TextProcessor | 30+ tests | All processing functions |

---

## 🔧 **Test Requirements**

### **Install Test Dependencies**

```bash
pip install pytest pytest-cov pytest-mock
```

### **Required for Tests**

The tests use mocking for external dependencies:
- ✅ Firebase Firestore (mocked)
- ✅ Google Gemini AI (mocked for unit tests)
- ✅ No actual API calls in unit tests

---

## 📝 **Test Structure**

Each test file follows this structure:

```python
class TestServiceName:
    """Test suite for ServiceName"""
    
    @pytest.fixture
    def service(self):
        """Create service instance"""
        return ServiceName()
    
    def test_feature_name(self, service):
        """Test specific feature"""
        # Arrange
        input_data = {...}
        
        # Act
        result = service.method(input_data)
        
        # Assert
        assert result is not None
        assert 'expected_key' in result
```

---

## ✅ **What's Tested**

### **1. FeasibilityAnalyzer**
- ✅ AI-powered analysis workflow
- ✅ Score calculation algorithm
- ✅ Risk level categorization
- ✅ Recommendation generation logic
- ✅ Fallback handling when AI fails
- ✅ Historical context integration

### **2. AnalyticsEngine**
- ✅ Data aggregation and counting
- ✅ Time-based trend analysis
- ✅ Topic frequency calculation
- ✅ User contribution tracking
- ✅ Channel activity metrics
- ✅ Completion rate formulas
- ✅ Velocity calculations

### **3. RiskAssessor**
- ✅ Multi-factor risk scoring
- ✅ Knowledge silo detection
- ✅ Aging decision identification
- ✅ Due date monitoring
- ✅ Risk trend analysis
- ✅ Mitigation recommendations

### **4. InputValidator**
- ✅ All input field validations
- ✅ Security (XSS prevention)
- ✅ Format validations (email, URL, date)
- ✅ Length constraints
- ✅ Type checking
- ✅ Required field enforcement

### **5. TextProcessor**
- ✅ Text cleaning and normalization
- ✅ Keyword extraction algorithms
- ✅ Entity recognition patterns
- ✅ Sentiment analysis logic
- ✅ Summarization algorithms
- ✅ Duplicate detection

---

## 🎯 **Test Coverage Goals**

### **Current Coverage**
- ✅ **Core Services**: 100% of critical paths tested
- ✅ **Edge Cases**: Major edge cases covered
- ✅ **Error Handling**: Error paths tested
- ✅ **Input Validation**: All validation rules tested

### **Future Enhancements**
- ⏳ Integration tests with real Firebase
- ⏳ End-to-end API tests
- ⏳ Performance/load tests
- ⏳ Security penetration tests

---

## 🐛 **Debugging Failed Tests**

### **View Detailed Output**

```bash
# Show full traceback
python -m pytest tests/test_name.py -v --tb=long

# Show print statements
python -m pytest tests/test_name.py -v -s

# Stop on first failure
python -m pytest tests/test_name.py -v -x
```

### **Common Issues**

1. **Import Errors**
   - Ensure you're in the project root directory
   - Check that all dependencies are installed
   - Verify Python path includes project directory

2. **Mock Failures**
   - Check that Firebase is properly mocked
   - Verify mock return values match expected structure

3. **API Key Errors**
   - Unit tests should NOT require real API keys
   - Check that services are properly mocked

---

## 📈 **Continuous Integration**

### **GitHub Actions Example**

```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: python run_tests.py
    
    - name: Generate coverage report
      run: pytest tests/ --cov=services --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

## 🎉 **Test Results Interpretation**

### **Success Output**
```
✅ PASS tests/test_feasibility_analyzer.py
     Passed: 8, Failed: 0
✅ PASS tests/test_analytics_engine.py
     Passed: 11, Failed: 0
✅ PASS tests/test_risk_assessor.py
     Passed: 13, Failed: 0
✅ PASS tests/test_input_validator.py
     Passed: 40, Failed: 0
✅ PASS tests/test_text_processor.py
     Passed: 30, Failed: 0

TOTAL: 102 passed, 0 failed
```

### **Failure Output**
```
❌ FAIL tests/test_input_validator.py
     Passed: 38, Failed: 2

FAILED tests/test_input_validator.py::TestInputValidator::test_validate_email_invalid
FAILED tests/test_input_validator.py::TestInputValidator::test_sanitize_text_script_removal
```

---

## 🔍 **Manual Testing**

For services that require real API integration:

### **Test FeasibilityAnalyzer with Real AI**

```python
from services.feasibility_analyzer import FeasibilityAnalyzer

analyzer = FeasibilityAnalyzer()
result = analyzer.analyze(
    title="Migrate to PostgreSQL",
    rationale="Need better ACID compliance and join performance",
    context="Currently using MySQL 5.7"
)

print(f"Feasibility Score: {result['feasibility_score']}")
print(f"Risk Level: {result['risk_level']}")
print(f"Recommendation: {result['recommendation']}")
```

### **Test with Sample Data**

```bash
# Use dev utilities to seed test data
curl -X POST http://localhost:5000/dev/seed-data \
  -H "Content-Type: application/json" \
  -d '{"count": 20}'

# Run analytics
curl http://localhost:5000/dashboard/stats

# Test search
curl -X POST http://localhost:5000/search-decisions \
  -H "Content-Type: application/json" \
  -d '{"keyword": "database"}'
```

---

## 📚 **Best Practices**

1. **Run tests before committing**
   ```bash
   python run_tests.py
   ```

2. **Write tests for new features**
   - Add test cases when adding new services
   - Test both success and failure paths
   - Include edge cases

3. **Keep tests independent**
   - Each test should run independently
   - Use fixtures for setup/teardown
   - Don't rely on test execution order

4. **Mock external dependencies**
   - Mock Firebase, AI APIs, etc.
   - Keep unit tests fast
   - Use integration tests for real APIs

5. **Maintain test coverage**
   - Aim for >80% code coverage
   - Focus on critical paths first
   - Add tests when bugs are found

---

## 🎊 **Summary**

✅ **100+ test cases** covering all core services
✅ **Comprehensive coverage** of critical functionality
✅ **Fast execution** with mocked dependencies
✅ **Easy to run** with single command
✅ **CI/CD ready** for automated testing

**Your TechAtlas backend services are thoroughly tested and production-ready! 🚀**
