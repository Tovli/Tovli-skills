"""Find installed Ruflo and Claude Flow launchers without running them."""

import argparse
import json
import os
from pathlib import Path


CLI_NAMES = ("ruflo", "claude-flow")
LAUNCHER_SUFFIXES = (".exe", ".ps1", ".cmd", ".bat") if os.name == "nt" else ("",)


def find_launcher(name: str, directories: list[Path]) -> Path | None:
    for directory in directories:
        for suffix in LAUNCHER_SUFFIXES:
            launcher = directory / f"{name}{suffix}"
            if launcher.is_file() and os.access(launcher, os.X_OK):
                return launcher
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", nargs="?", type=Path, default=Path.cwd())
    args = parser.parse_args()
    project_root = args.project_root.resolve()
    if not project_root.is_dir():
        parser.error(f"project root is not a directory: {project_root}")

    local_bin = project_root / "node_modules" / ".bin"
    path_dirs = [Path(entry).absolute() for entry in os.get_exec_path() if entry]
    candidates = []
    seen = set()
    for source, directories in (("project", [local_bin]), ("path", path_dirs)):
        for name in CLI_NAMES:
            launcher = find_launcher(name, directories)
            if launcher is not None and launcher not in seen:
                candidates.append({"name": name, "path": str(launcher), "source": source})
                seen.add(launcher)

    print(json.dumps({"project_root": str(project_root), "candidates": candidates}))


if __name__ == "__main__":
    main()
