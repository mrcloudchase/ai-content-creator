"""
Configuration file for pytest.
"""
import pytest
import os
import sys

# Add asyncio marker to pytest
def pytest_configure(config):
    """Configure pytest with asyncio."""
    config.addinivalue_line(
        "markers", "asyncio: mark test as an asyncio test"
    ) 