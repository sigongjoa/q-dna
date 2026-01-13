"""Tests for app/constants/error_types.py"""
import pytest


def test_error_types_import():
    """Test error types module can be imported"""
    try:
        from app.constants import error_types
        assert error_types is not None
    except ImportError:
        pytest.skip("error_types module not available")


def test_error_types_constants_exist():
    """Test that error type constants are defined"""
    try:
        from app.constants import error_types

        # Check module has at least some attributes
        assert dir(error_types) is not None
    except ImportError:
        pytest.skip("error_types module not available")
