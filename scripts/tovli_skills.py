#!/usr/bin/env python3
"""Install standalone Tovli Skills or build native Git marketplaces."""

import argparse
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
from tempfile import TemporaryDirectory

from skill_distribution import (
    DistributionError, MARKETPLACES, SOURCES, build_marketplace, prepare_git_refs,
    read_snapshot, write_json, write_skill,
)


HOST_PATHS = {"codex": ".agents", "claude": ".claude"}
RECEIPT = ".tovli-install.json"
STAGE = ".tovli-install-stage"
MARKER = "Tovli Skills installer v1\n"


def kind(path):
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return None
    if stat.S_ISLNK(metadata.st_mode) or (
        getattr(metadata, "st_file_attributes", 0) & stat.FILE_ATTRIBUTE_REPARSE_POINT
    ):
        raise DistributionError(f"Refusing to use a symbolic link or reparse point: {path}")
    if stat.S_ISDIR(metadata.st_mode):
        return "directory"
    if stat.S_ISREG(metadata.st_mode):
        return "file"
    raise DistributionError(f"Unsupported file type: {path}")


def directory(path, create=False):
    existing = kind(path)
    if existing is None and create:
        path.mkdir(exist_ok=True)
        existing = kind(path)
    if existing is None:
        return False
    if existing != "directory":
        raise DistributionError(f"Expected a directory: {path}")
    return True


def digest(files):
    result = hashlib.sha256()
    for path, content in sorted((str(path), content) for path, content in files.items()):
        label = path.encode("utf-8")
        result.update(len(label).to_bytes(8, "big") + label)
        result.update(hashlib.sha256(content).digest())
    return result.hexdigest()


def existing_files(root):
    files = {}

    def visit(folder):
        entries = list(folder.iterdir())
        if not entries and folder != root:
            files[folder.relative_to(root).as_posix() + "/"] = b""
        for path in entries:
            entry = kind(path)
            if path == root / RECEIPT and entry == "file":
                continue
            if entry == "directory":
                visit(path)
            elif entry == "file":
                files[path.relative_to(root).as_posix()] = path.read_bytes()
    visit(root)
    return files


def read_receipt(path):
    receipt = path / RECEIPT
    if kind(receipt) != "file":
        return None
    try:
        data = json.loads(receipt.read_text(encoding="utf-8"))
    except (ValueError, UnicodeError):
        return None
    if not isinstance(data, dict) or data.get("format") != 1 or data.get("skill") != path.name:
        return None
    return data


@contextmanager
def install_lock(host):
    lock = host / ".tovli-install.lock"
    if kind(lock) not in (None, "file"):
        raise DistributionError(f"Expected an installer lock file: {lock}")
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
    fd = os.open(lock, flags, 0o600)
    try:
        if kind(lock) != "file" or not stat.S_ISREG(os.fstat(fd).st_mode):
            raise DistributionError(f"Expected an installer lock file: {lock}")
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            raise DistributionError(f"Could not lock {lock}. Finish any concurrent Tovli install and retry.") from error
        yield
    finally:
        os.close(fd)


def clear_stage(root, stage):
    if not directory(stage) or stage.resolve().parent != root.resolve():
        raise DistributionError(f"Unexpected installer staging directory: {stage}")
    staging_folders = {"pending", "backups", "removed"}
    if {child.name for child in stage.iterdir()} - (staging_folders | {"owner"}):
        raise DistributionError(f"Unexpected files in installer staging directory: {stage}")
    for name in sorted(staging_folders):
        child = stage / name
        if directory(child):
            if child.resolve().parent != stage.resolve():
                raise DistributionError(f"Unexpected installer staging path: {child}")
            shutil.rmtree(child)
    (stage / "owner").unlink()
    stage.rmdir()


def recover(root, stage):
    if not directory(stage):
        return
    marker = stage / "owner"
    if kind(marker) is None and not any(stage.iterdir()):
        stage.rmdir()
        return
    if kind(marker) != "file" or marker.read_text(encoding="utf-8") != MARKER:
        raise DistributionError(f"Unrecognized installer staging directory: {stage}")
    backups = stage / "backups"
    if directory(backups):
        for saved in sorted(backups.iterdir()):
            if saved.name not in SOURCES or not directory(saved):
                raise DistributionError(f"Unexpected installer backup: {saved}")
            target = root / saved.name
            if not directory(target):
                saved.rename(target)
            elif read_receipt(target) is None:
                raise DistributionError(f"An unmanaged install blocks recovery. Backup: {saved}")
    clear_stage(root, stage)


def apply_to_scope(args, names, snapshot):
    host = args.root / HOST_PATHS[args.client]
    if not directory(host, create=snapshot is not None):
        return [(name, "already absent") for name in names]
    with install_lock(host):
        root = host / "skills"
        if not directory(root, create=snapshot is not None):
            return [(name, "already absent") for name in names]
        stage = root / STAGE
        recover(root, stage)
        results = []
        changes = []
        for name in names:
            target = root / name
            desired = digest(snapshot.skills[name]) if snapshot else None
            if directory(target):
                current = digest(existing_files(target))
                if current == desired:
                    results.append((name, "already matches"))
                    continue
                receipt = read_receipt(target)
                if receipt is None or receipt.get("digest") != current:
                    raise DistributionError(f"Existing skill contains unmanaged files or local changes: {target}")
                changes.append((name, "updated" if snapshot else "removed", current, desired))
            elif snapshot:
                changes.append((name, "installed", None, desired))
            else:
                results.append((name, "already absent"))
        if not changes:
            return results

        stage.mkdir()
        (stage / "owner").write_bytes(MARKER.encode("utf-8"))
        pending = stage / "pending"
        pending.mkdir()
        backups = stage / "backups"
        backups.mkdir()
        removed = stage / "removed"
        removed.mkdir()
        try:
            if snapshot:
                for name, _, _, desired in changes:
                    prepared = pending / name
                    write_skill(prepared, snapshot.skills[name])
                    write_json(prepared / RECEIPT, {
                        "format": 1, "skill": name, "revision": snapshot.revision, "digest": desired,
                    })
            for name, status, previous, _ in changes:
                target = root / name
                if previous is not None and (
                    not directory(target) or digest(existing_files(target)) != previous
                ):
                    raise DistributionError(f"Existing skill changed during the operation: {target}")
                if status == "updated":
                    target.rename(backups / name)
                if status == "removed":
                    target.rename(removed / name)
                else:
                    if kind(target) is not None:
                        raise DistributionError(f"An install appeared during the operation: {target}")
                    (pending / name).rename(target)
                results.append((name, status))
        except BaseException:
            recover(root, stage)
            raise
        clear_stage(root, stage)
        return results


def collect_scope(parser, args):
    if args.scope is None:
        message = "--scope is required. Ask the user to choose project or user scope."
        if not (sys.stdin.isatty() and sys.stdout.isatty()):
            parser.error(message)
        try:
            args.scope = input("Choose project or user scope [project/user]: ").strip()
        except EOFError:
            parser.error(message)
        if args.scope not in ("project", "user"):
            parser.error("Choose project or user scope.")
    if args.scope == "project":
        if args.project_dir is None:
            parser.error("--project-dir is required for project scope. Use the target project directory.")
        args.root = args.project_dir.resolve(strict=True)
    else:
        if args.project_dir is not None:
            parser.error("--project-dir is only valid with project scope.")
        args.root = Path.home().resolve(strict=True)
    if not directory(args.root):
        parser.error(f"Directory does not exist: {args.root}")


def build(args):
    output = args.output.resolve()
    if kind(args.output) is not None or kind(output) is not None:
        raise DistributionError(f"Build output already exists: {output}")
    if not re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", args.version):
        raise DistributionError("Use a release version in X.Y.Z form.")
    snapshot = read_snapshot(args.ref, tuple(SOURCES))
    output.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".tovli-build-", dir=output.parent) as temp:
        stage = Path(temp) / "marketplaces"
        stage.mkdir()
        for market in MARKETPLACES:
            build_marketplace(stage / market.name, market, snapshot, args.version)
        if args.git:
            prepare_git_refs(stage, args.base, args.version)
        if kind(output) is not None:
            raise DistributionError(f"Build output already exists: {output}")
        stage.rename(output)
    print(f"Built {len(MARKETPLACES)} marketplaces from {snapshot.revision} in {output}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("install", "uninstall"):
        sub = commands.add_parser(command)
        sub.add_argument("--client", required=True, choices=HOST_PATHS)
        sub.add_argument("--scope", choices=("project", "user"))
        sub.add_argument("--project-dir", type=Path)
        sub.add_argument("--all", action="store_true", help="Select all public skills")
        sub.add_argument("skills", nargs="*", metavar="SKILL", help="Public name from the README")
        if command == "install":
            sub.add_argument("--ref", default="HEAD", help="Git commit, tag or branch in this checkout")
    sub = commands.add_parser("build-marketplaces", help="Generate self-contained native catalogs and packages")
    sub.add_argument("--output", type=Path, required=True)
    sub.add_argument("--version", required=True)
    sub.add_argument("--ref", default="HEAD", help="Git commit, tag or branch in this checkout")
    sub.add_argument("--git", action="store_true", help="Prepare Git marketplace branches in a bare output repository")
    sub.add_argument("--base", help="Optional Git URL or repository with the existing marketplace branch history")
    args = parser.parse_args()
    try:
        if args.command == "build-marketplaces":
            if args.base and not args.git:
                parser.error("--base requires --git.")
            build(args)
            return 0
        if args.all == bool(args.skills):
            parser.error("Choose one or more skill names, or use --all.")
        names = tuple(SOURCES) if args.all else tuple(dict.fromkeys(args.skills))
        for name in names:
            if name not in SOURCES:
                parser.error(f"Unknown skill: {name}. Available skills: {', '.join(SOURCES)}")
        collect_scope(parser, args)
        snapshot = read_snapshot(args.ref, names) if args.command == "install" else None
        actions = dict(apply_to_scope(args, names, snapshot))
        print(f"{args.client} {args.scope} skills at {args.root / HOST_PATHS[args.client] / 'skills'}")
        if snapshot:
            print(f"Selected source revision: {snapshot.revision}")
        for name in names:
            invocation = f" (${name})" if args.client == "codex" else f" (/{name})"
            print(f"{name}: {actions[name]}{invocation if snapshot else ''}")
        return 0
    except (DistributionError, OSError, ValueError) as error:
        print(f"Tovli Skills: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
