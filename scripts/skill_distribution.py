"""Canonical skill sources and native marketplace build logic."""

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path, PurePosixPath
import json
import os
import re
import subprocess
import tarfile


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "https://github.com/Tovli/Tovli-skills"
SOURCES = {
    "tovli-plan": "tovli-plan",
    "tovli-agentic-planner": "tovli-agentic-planner",
    "tovli-adr": "tovli-adr",
    "tovli-explain": "git-branch-change-explainer",
    "tovli-post-writer": "tovli-post-writer",
}
SKILL_DIRECTORIES = {"agents", "assets", "examples", "references", "scripts", "tests"}
SKILL_FILES = {"SKILL.md", "README.md"}


@dataclass(frozen=True)
class Marketplace:
    name: str
    title: str
    subtitle: str
    description: str
    skills: tuple[str, ...]

    @property
    def branch(self):
        return f"marketplace/{self.name}"


MARKETPLACES = (
    Marketplace(
        "tovli-planning", "Tovli Planning", "Project planning and architecture decisions",
        "Create project plans, design agentic workflows, and record architecture decisions.",
        ("tovli-plan", "tovli-agentic-planner", "tovli-adr"),
    ),
    Marketplace(
        "tovli-explainer", "Tovli Explainer", "Git branch explainers",
        "Explain Git branch changes and create a standalone HTML report.",
        ("tovli-explain",),
    ),
    Marketplace(
        "tovli-writer", "Tovli Writer", "LinkedIn post writing",
        "Draft, review, and polish LinkedIn posts while preserving the author's voice.",
        ("tovli-post-writer",),
    ),
)


class DistributionError(Exception):
    """An actionable error in a skill install or release build."""


@dataclass(frozen=True)
class Snapshot:
    revision: str
    skills: dict[str, dict[PurePosixPath, bytes]]
    license: bytes


def git(*args, cwd=ROOT, env=None):
    result = subprocess.run(
        ["git", *map(str, args)], cwd=cwd, env=env, check=False,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if result.returncode:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise DistributionError(message or f"Git command failed with exit status {result.returncode}.")
    return result.stdout


def read_snapshot(ref, names):
    revision = git("rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}").decode().strip()
    directories = {SOURCES[name]: name for name in names}
    archive = git("archive", "--format=tar", revision, "--", "LICENSE", *directories)
    skills = {name: {} for name in names}
    license_data = None
    with tarfile.open(fileobj=BytesIO(archive), mode="r:") as contents:
        for member in contents:
            path = PurePosixPath(member.name)
            if path == PurePosixPath("LICENSE") and member.isfile():
                license_data = contents.extractfile(member).read()
                continue
            if member.isdir() or len(path.parts) < 2 or path.parts[0] not in directories:
                continue
            relative = PurePosixPath(*path.parts[1:])
            if relative.parts[0] not in SKILL_DIRECTORIES and str(relative) not in SKILL_FILES:
                continue
            if not member.isfile() or any(
                part in {".", ".."} or re.search(r'[\\:<>|?*"\x00-\x1f]', part)
                or part.endswith((" ", ".")) or part.split(".")[0].upper() in WINDOW_DEVICES
                for part in relative.parts
            ) or path.is_absolute():
                raise DistributionError(f"Unsupported file in skill source: {member.name}")
            files = skills[directories[path.parts[0]]]
            if relative in files:
                raise DistributionError(f"Duplicate file in skill source: {member.name}")
            files[relative] = contents.extractfile(member).read()
    for name, files in skills.items():
        spellings = {}
        for path in files:
            for part in (path, *path.parents):
                spelling = part.as_posix()
                if spellings.setdefault(spelling.casefold(), spelling) != spelling:
                    raise DistributionError(f"Case-insensitive path collision in {name}: {spelling}")
        descriptor = files.get(PurePosixPath("SKILL.md"), b"").decode("utf-8")
        header = descriptor.split("---", 2)
        if len(header) != 3 or header[0] or not re.search(
            rf"^name:\s*{re.escape(name)}\s*$", header[1], re.MULTILINE
        ) or not re.search(r"^description:[ \t]*\S", header[1], re.MULTILINE):
            raise DistributionError(f"Missing or invalid SKILL.md metadata for {name}.")
    if license_data is None:
        raise DistributionError("The selected revision has no regular LICENSE file.")
    return Snapshot(revision, skills, license_data)


WINDOW_DEVICES = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"} | {
    f"{prefix}{number}" for prefix in ("COM", "LPT") for number in "123456789¹²³"
}


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def write_skill(destination, files):
    destination.mkdir()
    for relative, payload in sorted(files.items()):
        target = destination.joinpath(*relative.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(payload)


def build_marketplace(destination, market, snapshot, version):
    plugin = destination / "plugins" / market.name
    skill_root = plugin / "skills"
    skill_root.mkdir(parents=True)
    for name in market.skills:
        write_skill(skill_root / name, snapshot.skills[name])
    (plugin / "LICENSE").write_bytes(snapshot.license)
    manifest = {
        "name": market.name, "version": version, "description": market.description,
        "author": {"name": "Tovli"}, "repository": REPOSITORY, "license": "MIT",
    }
    write_json(plugin / ".claude-plugin" / "plugin.json", manifest)
    write_json(plugin / ".codex-plugin" / "plugin.json", {
        **manifest, "skills": "./skills/",
        "interface": {
            "displayName": market.title, "shortDescription": market.subtitle,
            "longDescription": market.description, "developerName": "Tovli",
            "category": "Productivity",
        },
    })
    package_path = f"./plugins/{market.name}"
    write_json(destination / ".agents" / "plugins" / "marketplace.json", {
        "name": market.name, "interface": {"displayName": market.title},
        "plugins": [{
            "name": market.name, "source": {"source": "local", "path": package_path},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity",
        }],
    })
    write_json(destination / ".claude-plugin" / "marketplace.json", {
        "name": market.name, "owner": {"name": "Tovli"},
        "metadata": {"description": market.description},
        "plugins": [{"name": market.name, "source": package_path}],
    })
    write_json(destination / "SOURCE.json", {
        "repository": REPOSITORY, "revision": snapshot.revision, "version": version,
        "marketplace": market.name, "skills": list(market.skills),
    })


def prepare_git_refs(destination, base, version):
    bare = destination / "marketplaces.git"
    git("init", "--bare", "--quiet", bare)
    for market in MARKETPLACES:
        branch = f"refs/heads/{market.branch}"
        parent = []
        if base and git("ls-remote", "--heads", "--", base, branch):
            git("--git-dir", bare, "fetch", "--no-tags", "--", base, branch)
            parent = ["-p", "FETCH_HEAD"]
        index = bare / "build-index"
        env = os.environ | {"GIT_INDEX_FILE": str(index)}
        workspace = destination / market.name
        git("--git-dir", bare, "--work-tree", workspace, "-c", "core.autocrlf=false",
            "add", "--force", "--all", "--", ".", cwd=workspace, env=env)
        tree = git("--git-dir", bare, "write-tree", env=env).decode().strip()
        index.unlink()
        parent_tree = git("--git-dir", bare, "rev-parse", "FETCH_HEAD^{tree}").decode().strip() if parent else None
        if tree == parent_tree:
            commit = git("--git-dir", bare, "rev-parse", "FETCH_HEAD").decode().strip()
        else:
            if parent:
                old = json.loads(git("--git-dir", bare, "show", "FETCH_HEAD:SOURCE.json"))
                if tuple(map(int, version.split("."))) <= tuple(map(int, old["version"].split("."))):
                    raise DistributionError(f"Increase the release version above {old['version']} for {market.name}.")
            commit = git("--git-dir", bare, "-c", "user.name=Tovli Skills",
                         "-c", "user.email=release@tovli.invalid", "-c", "commit.gpgsign=false", "commit-tree",
                         tree, *parent, "-m", f"{market.name} {version}").decode().strip()
        git("--git-dir", bare, "update-ref", branch, commit)
