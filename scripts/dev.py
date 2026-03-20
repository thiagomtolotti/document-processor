import os
from pathlib import Path
import subprocess
import sys


if __name__ == "__main__":
    is_windows = sys.platform == "win32"

    base_path = Path(__file__).parent.parent
    python_exec = (
        base_path / ".venv" / "Scripts" / "python.exe"
        if is_windows
        else base_path / ".venv" / "bin" / "python"
    )

    dev_path = base_path / "src" / "app" / "main.py"

    subprocess.run(
        [str(python_exec), "-m", "fastapi", "dev", "app/main.py"],
        env={**os.environ, "PYTHONPATH": str(base_path / "src")},
        cwd=str(base_path / "src"),
    )
