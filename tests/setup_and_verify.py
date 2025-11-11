"""
TechAtlas Backend - Setup and Verification Script
Checks all dependencies, configurations, and system integration
"""

import os
import sys
from pathlib import Path
import importlib.util


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.RESET}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")


def print_info(text):
    """Print info message"""
    print(f"  {text}")


def check_python_version():
    """Check Python version"""
    print_header("1. Checking Python Version")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python version: {version_str} (OK)")
        return True
    else:
        print_error(f"Python version: {version_str} (Requires 3.8+)")
        return False


def check_dependencies():
    """Check required Python packages"""
    print_header("2. Checking Dependencies")
    
    required_packages = {
        'flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'firebase_admin': 'Firebase Admin SDK',
        'google.generativeai': 'Google Generative AI',
        'faiss': 'FAISS',
        'numpy': 'NumPy',
        'python-dotenv': 'python-dotenv',
        'pytest': 'pytest'
    }
    
    all_installed = True
    
    for package, name in required_packages.items():
        try:
            if package == 'python-dotenv':
                importlib.import_module('dotenv')
            else:
                importlib.import_module(package.replace('-', '_'))
            print_success(f"{name} installed")
        except ImportError:
            print_error(f"{name} NOT installed")
            all_installed = False
    
    if not all_installed:
        print_warning("\nInstall missing packages with:")
        print_info("pip install -r requirements.txt")
    
    return all_installed


def check_environment_variables():
    """Check environment variables"""
    print_header("3. Checking Environment Variables")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        'GEMINI_API_KEY': 'Google Gemini API Key',
        'FIREBASE_CREDENTIALS_PATH': 'Firebase Credentials Path'
    }
    
    optional_vars = {
        'PORT': 'Server Port',
        'DEBUG': 'Debug Mode',
        'LOG_LEVEL': 'Log Level'
    }
    
    all_present = True
    
    print("Required Variables:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'KEY' in var or 'SECRET' in var:
                masked = value[:8] + '...' if len(value) > 8 else '***'
                print_success(f"{description}: {masked}")
            else:
                print_success(f"{description}: {value}")
        else:
            print_error(f"{description}: NOT SET")
            all_present = False
    
    print("\nOptional Variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print_success(f"{description}: {value}")
        else:
            print_info(f"{description}: Using default")
    
    if not all_present:
        print_warning("\nCreate a .env file based on .env.example")
        print_info("cp .env.example .env")
    
    return all_present


def check_firebase_credentials():
    """Check Firebase credentials file"""
    print_header("4. Checking Firebase Credentials")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    creds_path = os.getenv('FIREBASE_CREDENTIALS_PATH', './firebase-key.json')
    
    if os.path.exists(creds_path):
        print_success(f"Firebase credentials file found: {creds_path}")
        
        # Try to load and validate
        try:
            import json
            with open(creds_path, 'r') as f:
                creds = json.load(f)
            
            required_fields = ['type', 'project_id', 'private_key', 'client_email']
            missing = [f for f in required_fields if f not in creds]
            
            if not missing:
                print_success(f"Credentials valid for project: {creds.get('project_id')}")
                return True
            else:
                print_error(f"Missing fields in credentials: {', '.join(missing)}")
                return False
        except Exception as e:
            print_error(f"Error reading credentials: {str(e)}")
            return False
    else:
        print_error(f"Firebase credentials file not found: {creds_path}")
        print_warning("Download from Firebase Console > Project Settings > Service Accounts")
        return False


def check_directory_structure():
    """Check directory structure"""
    print_header("5. Checking Directory Structure")
    
    required_dirs = [
        'routes',
        'services',
        'models',
        'utils',
        'tests',
        'docs'
    ]
    
    optional_dirs = [
        'data',
        'logs',
        'backups'
    ]
    
    all_present = True
    
    print("Required Directories:")
    for dir_name in required_dirs:
        if os.path.isdir(dir_name):
            # Count files
            file_count = len([f for f in os.listdir(dir_name) if f.endswith('.py')])
            print_success(f"{dir_name}/ ({file_count} Python files)")
        else:
            print_error(f"{dir_name}/ NOT FOUND")
            all_present = False
    
    print("\nOptional Directories:")
    for dir_name in optional_dirs:
        if os.path.isdir(dir_name):
            print_success(f"{dir_name}/ exists")
        else:
            print_info(f"{dir_name}/ will be created on first use")
    
    return all_present


def check_services():
    """Check service files"""
    print_header("6. Checking Service Files")
    
    services = [
        'detector.py',
        'feasibility_analyzer.py',
        'embedder.py',
        'rag_engine.py',
        'vector_store.py',
        'analytics_engine.py',
        'risk_assessor.py',
        'search_engine.py',
        'expertise_mapper.py',
        'input_validator.py',
        'text_processor.py',
        'notification_manager.py',
        'audit_logger.py',
        'data_exporter.py'
    ]
    
    all_present = True
    
    for service in services:
        path = os.path.join('services', service)
        if os.path.exists(path):
            print_success(f"{service}")
        else:
            print_error(f"{service} NOT FOUND")
            all_present = False
    
    return all_present


def check_routes():
    """Check route files"""
    print_header("7. Checking Route Files")
    
    routes = [
        'core.py',
        'detect.py',
        'analyze.py',
        'save.py',
        'query.py',
        'decisions.py',
        'dashboard.py',
        'users.py',
        'analytics.py',
        'risk.py',
        'audit.py',
        'dev.py'
    ]
    
    all_present = True
    
    for route in routes:
        path = os.path.join('routes', route)
        if os.path.exists(path):
            print_success(f"{route}")
        else:
            print_error(f"{route} NOT FOUND")
            all_present = False
    
    return all_present


def test_service_imports():
    """Test importing services"""
    print_header("8. Testing Service Imports")
    
    services_to_test = [
        ('services.input_validator', 'InputValidator'),
        ('services.text_processor', 'TextProcessor'),
        ('services.analytics_engine', 'AnalyticsEngine'),
        ('services.risk_assessor', 'RiskAssessor'),
        ('services.search_engine', 'SearchEngine')
    ]
    
    all_imported = True
    
    for module_name, class_name in services_to_test:
        try:
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            print_success(f"{class_name} imported successfully")
        except Exception as e:
            print_error(f"{class_name} import failed: {str(e)}")
            all_imported = False
    
    return all_imported


def test_flask_app():
    """Test Flask app creation"""
    print_header("9. Testing Flask App")
    
    try:
        # Temporarily suppress output
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            from app import app
        
        if app:
            print_success("Flask app created successfully")
            
            # Count routes
            route_count = len([r for r in app.url_map.iter_rules() if r.endpoint != 'static'])
            print_success(f"Registered {route_count} routes")
            
            return True
    except Exception as e:
        print_error(f"Flask app creation failed: {str(e)}")
        return False


def run_quick_tests():
    """Run quick unit tests"""
    print_header("10. Running Quick Tests")
    
    try:
        import subprocess
        
        # Run only fast tests
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', 'tests/test_input_validator.py', '-v', '--tb=short', '-x'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Count passed tests
            passed = result.stdout.count(' PASSED')
            print_success(f"All tests passed ({passed} tests)")
            return True
        else:
            print_error("Some tests failed")
            print_info("Run 'python run_tests.py' for details")
            return False
    except subprocess.TimeoutExpired:
        print_warning("Tests timed out (taking too long)")
        return False
    except Exception as e:
        print_warning(f"Could not run tests: {str(e)}")
        return True  # Don't fail setup if tests can't run


def print_summary(checks):
    """Print summary of all checks"""
    print_header("Setup Verification Summary")
    
    total = len(checks)
    passed = sum(checks.values())
    failed = total - passed
    
    print(f"Total Checks: {total}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {failed}{Colors.RESET}")
    print()
    
    if failed == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ All checks passed! System is ready.{Colors.RESET}")
        print()
        print("Next steps:")
        print_info("1. Start the server: python app.py")
        print_info("2. Test endpoints: curl http://localhost:5000/health")
        print_info("3. View all routes: curl http://localhost:5000/routes")
        print_info("4. Run full tests: python run_tests.py")
        return True
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Some checks failed. Please fix the issues above.{Colors.RESET}")
        return False


def main():
    """Main setup verification"""
    print(f"\n{Colors.BOLD}TechAtlas Backend - Setup & Verification{Colors.RESET}")
    print("This script will verify your installation and configuration.\n")
    
    checks = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'Environment Variables': check_environment_variables(),
        'Firebase Credentials': check_firebase_credentials(),
        'Directory Structure': check_directory_structure(),
        'Service Files': check_services(),
        'Route Files': check_routes(),
        'Service Imports': test_service_imports(),
        'Flask App': test_flask_app(),
        'Quick Tests': run_quick_tests()
    }
    
    success = print_summary(checks)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
