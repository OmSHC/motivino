#!/usr/bin/env python
"""
Test runner script for Interactive Student Motivation News Website.
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

def setup_django():
    """Setup Django environment."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motivation_news.settings')
    django.setup()

def run_tests():
    """Run all tests."""
    setup_django()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    
    # Test patterns
    test_patterns = [
        'apps.users.tests',
        'apps.content.tests', 
        'apps.core.tests',
    ]
    
    print("🧪 Running tests for Interactive Student Motivation News Website...")
    print("=" * 60)
    
    failures = test_runner.run_tests(test_patterns)
    
    if failures:
        print(f"\n❌ {failures} test(s) failed!")
        return False
    else:
        print("\n✅ All tests passed!")
        return True

def run_coverage():
    """Run tests with coverage."""
    try:
        import coverage
    except ImportError:
        print("❌ Coverage not installed. Install with: pip install coverage")
        return False
    
    setup_django()
    
    # Start coverage
    cov = coverage.Coverage()
    cov.start()
    
    # Run tests
    success = run_tests()
    
    # Stop coverage and generate report
    cov.stop()
    cov.save()
    
    print("\n📊 Coverage Report:")
    print("=" * 40)
    cov.report()
    
    # Generate HTML report
    cov.html_report(directory='htmlcov')
    print(f"\n📁 HTML coverage report generated in 'htmlcov' directory")
    
    return success

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--coverage':
        success = run_coverage()
    else:
        success = run_tests()
    
    sys.exit(0 if success else 1)
