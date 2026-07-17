import pytest
import importlib

def test_dependency_integrity():
    # List of dependencies to verify. 
    # Works for both built-in (asyncio) and installed (pytest) modules.
    required_packages = ["pytest", "asyncio", "re", "json", "hashlib"]
    
    for pkg in required_packages:
        try:
            importlib.import_module(pkg)
        except ImportError:
            pytest.fail(f"Critical dependency missing or unusable: {pkg}")
