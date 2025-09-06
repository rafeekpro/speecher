"""
Simple test to verify CI environment
"""

def test_ci_working():
    """Test that CI can run tests"""
    assert True
    
def test_imports_working():
    """Test that imports work"""
    import sys
    import os
    assert 'os' in sys.modules
    assert 'sys' in sys.modules