"""Standard test runner for local and CI usage.

Usage examples:
    python scripts/automation/test_runner.py
    python scripts/automation/test_runner.py core
    python scripts/automation/test_runner.py core/tests/test_context_status_plano.py

By default this runner executes pytest and uses core.settings_test.
"""

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SETTINGS = "core.settings_test"
SETTINGS_OVERRIDE_ENV = "TEST_SETTINGS_MODULE"


def build_command(targets: list[str]) -> list[str]:
    command = [sys.executable, "-m", "pytest"]
    command.extend(targets)
    command.append("-q")
    return command


def main() -> int:
    targets = sys.argv[1:]
    settings_module = os.getenv(SETTINGS_OVERRIDE_ENV, DEFAULT_SETTINGS)
    env = os.environ.copy()
    env["DJANGO_SETTINGS_MODULE"] = settings_module

    command = build_command(targets)
    print("==> Standard test runner")
    print(f"Working dir: {ROOT}")
    print(f"DJANGO_SETTINGS_MODULE={settings_module}")
    print("Command:", " ".join(command))

    result = subprocess.run(command, cwd=ROOT, env=env)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
