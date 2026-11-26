import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from skill_distribution import SOURCES, MARKETPLACES

SKILL_SOURCES = {
    "tovli-plan": "tovli-plan",
    "tovli-agentic-planner": "tovli-agentic-planner",
    "tovli-adr": "tovli-adr",
    "tovli-explain": "git-branch-change-explainer",
    "tovli-post-writer": "tovli-post-writer",
    "tovli-interview-prep": "tovli-interview-prep",
    "tovli-cv-optimize": "tovli-cv-optimize",
}
MARKETS = {
    "tovli-planning": {"tovli-plan", "tovli-agentic-planner", "tovli-adr"},
    "tovli-explainer": {"tovli-explain"},
    "tovli-writer": {"tovli-post-writer"},
    "tovli-career": {"tovli-interview-prep", "tovli-cv-optimize"},
}


class DistributionTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name)
        self.checkout = self.workspace / "source checkout"
        self.checkout.mkdir()
        self.project = self.workspace / "target project"
        self.project.mkdir()
        shutil.copytree(ROOT / "scripts", self.checkout / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
        self.git("init", "--quiet")
        self.git("config", "user.name", "Distribution test")
        self.git("config", "user.email", "test@tovli.invalid")
        self.git("config", "commit.gpgsign", "false")
        self.git("config", "core.autocrlf", "false")
        (self.checkout / "LICENSE").write_bytes(b"Test license\n")
        for skill, source in SKILL_SOURCES.items():
            folder = self.checkout / source
            (folder / "assets").mkdir(parents=True)
            (folder / "SKILL.md").write_bytes(
                f"---\nname: {skill}\ndescription: Test skill description.\n---\nTest skill.\n".encode()
            )
            (folder / "assets" / "example.txt").write_bytes(b"Original asset\n")
        self.revision = self.commit("Skill snapshot")

    def git(self, *args):
        result = subprocess.run(
            ["git", *map(str, args)], cwd=self.checkout, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def commit(self, message):
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", message)
        return self.git("rev-parse", "HEAD")

    def cli(self, *args, expected=0):
        result = subprocess.run(
            [sys.executable, "-B", str(self.checkout / "scripts" / "tovli_skills.py"), *map(str, args)],
            cwd=self.workspace, stdin=subprocess.DEVNULL, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result.stdout + result.stderr

    def install(self, *args, **expectation):
        return self.cli("install", "--client", "codex", "--scope", "project",
                        "--project-dir", self.project, *args, **expectation)

    def load_json(self, path):
        return json.loads(path.read_text(encoding="utf-8"))

    def test_real_catalog_is_tracked_and_distributable(self):
        self.assertEqual(SKILL_SOURCES, SOURCES)
        self.assertEqual(MARKETS, {market.name: set(market.skills) for market in MARKETPLACES})
        for source in SKILL_SOURCES.values():
            skill = ROOT / source / "SKILL.md"
            self.assertTrue(skill.is_file(), f"Missing {skill}")
            for path in (ROOT / source).rglob("*"):
                if path.is_file():
                    ignored = subprocess.run(
                        ["git", "check-ignore", "-q", str(path.relative_to(ROOT))],
                        cwd=ROOT,
                    )
                    if ignored.returncode == 0:
                        continue
                    tracked = subprocess.run(
                        ["git", "ls-files", "--error-unmatch", str(path.relative_to(ROOT))],
                        cwd=ROOT, capture_output=True, text=True,
                    )
                    self.assertEqual(tracked.returncode, 0, f"Add {path} to Git")
            shutil.rmtree(self.checkout / source)
            shutil.copytree(ROOT / source, self.checkout / source, ignore=shutil.ignore_patterns("__pycache__"))
        self.commit("Real skill catalog")
        self.install("--all")
        self.cli("build-marketplaces", "--output", self.workspace / "real catalog", "--version", "0.1.0")

    def test_missing_scope_does_not_write(self):
        output = self.cli("install", "--client", "codex", "--all", expected=2)
        self.assertIn("Ask the user to choose project or user scope", output)
        self.assertEqual(list(self.project.iterdir()), [])
        self.assertFalse((self.workspace / ".agents").exists())
        self.assertIn("Unknown skill", self.install("../outside", expected=2))
        self.assertEqual(list(self.project.iterdir()), [])

    def test_names_and_resources_for_both_project_clients(self):
        (self.checkout / "git-branch-change-explainer/assets/example.txt").write_bytes(b"Checkout edit\n")
        for client, folder in (("codex", ".agents"), ("claude", ".claude")):
            with self.subTest(client=client):
                output = self.cli("install", "--client", client, "--scope", "project",
                                  "--project-dir", self.project, "tovli-explain")
                self.assertIn(self.revision, output)
                root = self.project / folder / "skills"
                self.assertEqual([skill.name for skill in root.iterdir()], ["tovli-explain"])
                installed = root / "tovli-explain"
                self.assertIn("name: tovli-explain", (installed / "SKILL.md").read_text())
                self.assertEqual((installed / "assets" / "example.txt").read_bytes(), b"Original asset\n")

    def test_updates_restore_and_uninstall_preserve_unrelated_skills(self):
        self.install("--all")
        self.assertEqual(self.install("--all").count("already matches"), len(SKILL_SOURCES))
        skills = self.project / ".agents" / "skills"
        unrelated = skills / "my-skill"
        unrelated.mkdir()
        (unrelated / "SKILL.md").write_bytes(b"Unrelated skill\n")
        source_asset = self.checkout / "tovli-plan" / "assets" / "example.txt"
        source_asset.write_bytes(b"New release\n")
        next_revision = self.commit("Updated plan skill")
        self.assertIn("tovli-plan: updated", self.install("--ref", next_revision, "tovli-plan"))
        installed_asset = skills / "tovli-plan" / "assets" / "example.txt"
        self.assertEqual(installed_asset.read_bytes(), b"New release\n")
        self.install("--ref", self.revision, "tovli-plan")
        self.assertEqual(installed_asset.read_bytes(), b"Original asset\n")
        self.cli("uninstall", "--client", "codex", "--scope", "project", "--project-dir", self.project, "--all")
        self.assertEqual(list(skills.iterdir()), [unrelated])

    def test_conflict_is_found_before_other_changes(self):
        self.install("tovli-post-writer")
        skills = self.project / ".agents" / "skills"
        local = skills / "tovli-post-writer" / "SKILL.md"
        local.write_bytes(b"User edit\n")
        output = self.install("--all", expected=1)
        self.assertIn("[ERROR]", output)
        self.assertIn("local changes", output)
        self.assertIn("No selected skills were changed by this operation", output)
        self.assertIn("Some may already be installed", output)
        self.assertFalse((skills / "tovli-plan").exists())
        output = self.cli("uninstall", "--client", "codex", "--scope", "project",
                          "--project-dir", self.project, "tovli-post-writer", expected=1)
        self.assertIn("Cannot complete uninstallation", output)
        self.assertEqual(local.read_bytes(), b"User edit\n")

    def test_recovers_an_interrupted_replacement(self):
        self.install("tovli-plan")
        skills = self.project / ".agents" / "skills"
        stage = skills / ".tovli-install-stage"
        backups = stage / "backups"
        backups.mkdir(parents=True)
        (stage / "owner").write_bytes(b"Tovli Skills installer v1\n")
        (skills / "tovli-plan").rename(backups / "tovli-plan")
        self.assertIn("already matches", self.install("tovli-plan"))
        self.assertEqual((skills / "tovli-plan" / "assets" / "example.txt").read_bytes(), b"Original asset\n")
        self.assertFalse(stage.exists())

    def test_rejects_linked_destination(self):
        outside = self.workspace / "other"
        outside.mkdir()
        try:
            (self.project / ".agents").symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("This account cannot create directory symlinks.")
        output = self.install("tovli-plan", expected=1)
        self.assertIn("symbolic link", output)
        self.assertEqual(list(outside.iterdir()), [])

    def test_deterministic_packages_and_fast_forward_release_refs(self):
        one = self.workspace / "build one"
        two = self.workspace / "build two"
        self.cli("build-marketplaces", "--output", one, "--version", "0.1.0", "--git")
        bare = one / "marketplaces.git"
        self.cli("build-marketplaces", "--output", two, "--version", "0.1.0", "--git", "--base", bare)
        for name, skills in MARKETS.items():
            with self.subTest(market=name):
                catalog = one / name
                relative = f"./plugins/{name}"
                self.assertEqual(self.load_json(catalog / ".agents/plugins/marketplace.json")["plugins"][0]["source"]["path"], relative)
                self.assertEqual(self.load_json(catalog / ".claude-plugin/marketplace.json")["plugins"][0]["source"], relative)
                plugin = catalog / "plugins" / name
                self.assertEqual({path.name for path in (plugin / "skills").iterdir()}, skills)
                self.assertEqual(self.load_json(catalog / "SOURCE.json")["revision"], self.revision)
                files = [path.relative_to(catalog) for path in catalog.rglob("*") if path.is_file()]
                self.assertEqual(len(files), sum(path.is_file() for path in (two / name).rglob("*")))
                for path in files:
                    self.assertEqual((catalog / path).read_bytes(), (two / name / path).read_bytes())
                branch = f"refs/heads/marketplace/{name}"
                self.assertEqual(self.git("--git-dir", bare, "rev-parse", branch),
                                 self.git("--git-dir", two / "marketplaces.git", "rev-parse", branch))
        (self.checkout / "tovli-plan/assets/example.txt").write_bytes(b"Update\n")
        self.commit("New release")
        third = self.workspace / "build three"
        result = self.cli("build-marketplaces", "--output", third, "--version", "0.1.0",
                          "--git", "--base", bare, expected=1)
        self.assertIn("Increase the release version", result)
        self.assertFalse(third.exists())
        self.cli("build-marketplaces", "--output", third, "--version", "0.2.0", "--git", "--base", bare)
        for name in MARKETS:
            branch = f"refs/heads/marketplace/{name}"
            previous = self.git("--git-dir", bare, "rev-parse", branch)
            self.assertEqual(self.git("--git-dir", third / "marketplaces.git", "rev-parse", branch + "^"), previous)

    def test_selected_marketplace_only_prepares_its_branch(self):
        baseline = self.workspace / "all marketplaces"
        self.cli("build-marketplaces", "--output", baseline, "--version", "0.2.0", "--git")
        base = baseline / "marketplaces.git"
        self.git("--git-dir", base, "update-ref", "-d", "refs/heads/marketplace/tovli-career")

        output = self.workspace / "career release"
        self.cli("build-marketplaces", "--marketplace", "tovli-career", "--output", output,
                 "--version", "0.1.0", "--git", "--base", base)
        self.assertEqual({path.name for path in output.iterdir()}, {"tovli-career", "marketplaces.git"})
        self.assertEqual(self.git("--git-dir", output / "marketplaces.git", "for-each-ref",
                                  "--format=%(refname)", "refs/heads"), "refs/heads/marketplace/tovli-career")


if __name__ == "__main__":
    unittest.main()
