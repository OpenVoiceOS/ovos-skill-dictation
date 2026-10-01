"""Per-worker XDG isolation for the ovoscope e2e suite.

Under ``pytest-xdist`` every worker boots its own MiniCroft, and they otherwise
share the default XDG paths — racing to create the same Padatious cache /
identity directories and intermittently raising ``FileExistsError``. Give each
worker (and the non-xdist run) its own private XDG tree so those writes never
collide. Keyed off ``PYTEST_XDIST_WORKER`` so it works whether or not xdist is
installed.
"""
import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def _isolate_xdg(tmp_path_factory):
    worker = os.environ.get("PYTEST_XDIST_WORKER", "master")
    root = tmp_path_factory.mktemp(f"xdg-{worker}")
    for var in ("XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_CACHE_HOME",
                "XDG_STATE_HOME"):
        path = root / var.lower()
        path.mkdir(parents=True, exist_ok=True)
        os.environ[var] = str(path)
    yield
