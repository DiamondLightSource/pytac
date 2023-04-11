import subprocess
import sys

from pytac import __version__


def test_cli_version():
    cmd = [sys.executable, "-m", "pytac", "--version"]
    assert subprocess.check_output(cmd).decode().strip() == __version__
