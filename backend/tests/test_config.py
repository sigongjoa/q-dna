"""Tests for app/core/config.py"""
import pytest
from unittest.mock import patch
import os


def test_settings_import():
    """Test settings can be imported"""
    from app.core.config import settings

    assert settings is not None


def test_settings_has_database_url():
    """Test settings has DATABASE_URL"""
    from app.core.config import settings

    assert hasattr(settings, 'DATABASE_URL')


def test_settings_has_project_name():
    """Test settings has PROJECT_NAME"""
    from app.core.config import settings

    assert hasattr(settings, 'PROJECT_NAME')


def test_settings_structure():
    """Test Settings class structure"""
    from app.core.config import Settings

    assert Settings is not None

    # Check class has Config
    assert hasattr(Settings, 'Config') or hasattr(Settings, 'model_config')
