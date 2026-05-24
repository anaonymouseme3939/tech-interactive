#!/usr/bin/env python3
"""
Dashboard module for TECH INTERACTIVE
"""

try:
    from .window import DashboardWindow
    __all__ = ['DashboardWindow']
except ImportError:
    __all__ = []
