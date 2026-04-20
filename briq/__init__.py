"""
Briq Python Client Library

A Python client for the Briq messaging platform API.
Aligned with Briq API version 0.8.
"""

__version__ = "0.2.0"

from .client import Client
from .config import Config

__all__ = ["Client", "Config"]
