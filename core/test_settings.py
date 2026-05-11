"""Compatibility shim for test settings.

Some commands and environments reference ``core.test_settings`` while others
use ``core.settings_test``. Keep a single source of truth by re-exporting the
full test configuration from ``settings_test``.
"""

from .settings_test import *  # noqa: F401,F403
