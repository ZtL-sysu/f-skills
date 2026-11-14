"""Protocol tests for the lightweight research-github-sync skill.

The skill intentionally ships no runtime scripts. These tests simulate an agent
following the written protocol inside temporary Git repositories, and check that
the templates, workflow and safety rules are actually usable.
"""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills" / "research-github-sync"
ASSETS = SKILL / "assets"


def run(*args, cwd=None, ok=True):
    proc = subprocess.run(args, cwd=cwd, text=True, encoding="utf-8", capture_output=True)
    if ok:
        assert proc.returncode == 0, (args, proc.stdout, proc.stderr)
    return proc


def git(repo, *args, ok=True):
    return run("git", "-C", str(repo), *args, ok=ok)


def init_repo(path):
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init", "-q")
    git(path, "config", "user.name", "Fixture")
    git(path, "config", "user.email", "fixture@example.invalid")
    return path


def init_docs(project, agent_id="codex"):
    """Simulate 'first entry': copy only missing templates, never overwrite."""
    collab = project / "collaboration"
    (collab / "agents").mkdir(parents=True, exist_ok=True)
    entry = project / "AGENTS.md"
    if not entry.exists():
        shutil.copy(ASSETS / "AGENTS.md", entry)
    for name in ("STATE.md", "TASKS.md"):
        dst = collab / name
        if not dst.exists():
            shutil.copy(ASSETS / name, dst)
    agent_file = collab / "agents" / (agent_id + ".md")
    if not agent_file.exists():
        agent_file.write_text(
            (ASSETS / "AGENT.md").read_text(encoding="utf-8").replace("<agent_id>", agent_id),
            encoding="utf-8",
        )
    return collab


def clone_pair(base):
    remote = base / "remote.git"
    run("git", "init", "-q", "--bare", str(remote))
    clones = []
    for name in ("a", "b"):
        path = base / name
        run("git", "clone", "-q", str(remote), str(path))
        git(path, "config", "user.name", "Fixture")
        git(path, "config", "user.email", "fixture@example.invalid")
        clones.append(path)
    return remote, clones[0], clones[1]


class SkillContract(unittest.TestCase):
    def test_00_minimal_tree_and_no_legacy(self):
        files = sorted(str(p.relative_to(SKILL)) for p in SKILL.rglob("*") if p.is_file())
        self.assertEqual(files, [
            "SKILL.md", "agents/openai.yaml", "assets/AGENT.md",
            "assets/AGENTS.md", "assets/STATE.md", "assets/TASKS.md",
        ])
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        lines = text.splitlines()
        self.assertGreaterEqual(len(lines), 100)
        self.assertLessEqual(len(lines), 160)
        for banned in ("auto_merge.py", "checkpoint_manifest.py", "FORMAT.md",
                       "无脑合并", "每 15", "manifest.json 生成", "METRICS.csv 的固定列"):
            self.assertNotIn(banned, text)
        for required in ("STATE.md", "TASKS.md", "agents/", "AGENTS.md", "先发现", "串行",
                         "force push", "git add .", "已验证", "PROTOCOL.md",
                         "Overview", "Key Decisions", "Superseded", "Resume Entry",
                         "阶段 A", "阶段 B", "独立复核", "安全检查",
                         "必做", "自取"):
            self.assertIn(required, text)
        ui = (SKILL / "agents/openai.yaml").read_text(encoding="utf-8")
        for banned in ("只多不少", "自动合并", "检查点"):
            self.assertNotIn(banned, ui)

    def test_01_new_project_initialization(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            (root / "src").mkdir(parents=True)
            (root / "src" / "main.py").write_text("print(1)\n")
            collab = init_docs(root)
            made = sorted(p.name for p in collab.rglob("*") if p.is_file())
            self.assertEqual(len(made), 3, made)
            self.assertTrue((root / "AGENTS.md").is_file())
            self.assertEqual((root / "src" / "main.py").read_text(), "print(1)\n")
            (collab / "STATE.md").write_text("custom state\n", encoding="utf-8")
            (root / "AGENTS.md").write_text("custom entry\n", encoding="utf-8")
            init_docs(root)
            self.assertEqual((root / "AGENTS.md").read_text(), "custom entry\n")
            self.assertEqual((collab / "STATE.md").read_text(), "custom state\n")
            self.assertEqual(len([p for p in collab.glob("STATE*")]), 1)
            self.assertEqual(len([p for p in collab.rglob("*") if p.is_file()]), 3)
            init_docs(root, "workbuddy")
            self.assertEqual(len([p for p in (collab / "agents").glob("*.md")]), 2)
            self.assertEqual((collab / "STATE.md").read_text(), "custom state\n")

    def test_02_reuse_existing_docs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            (root / "experiments").mkdir(parents=True)
            readme = "# Project\n" + "long detail " * 30 + "\n"
            (root / "README.md").write_text(readme)
            (root / "AGENTS.md").write_text("Agent conventions\n")
            (root / "experiments" / "results.json").write_text('{"acc":0.9}\n')
            collab = init_docs(root)
            self.assertEqual((root / "AGENTS.md").read_text(), "Agent conventions\n")
            self.assertEqual(len(list(root.glob("AGENTS*"))), 1)
            (collab / "STATE.md").write_text(
                "# State\n\n## Goal\nSee [README](../README.md) and [AGENTS.md](../AGENTS.md).\n\n"
                "## Verified\n- accuracy in [results.json](../experiments/results.json)\n",
                encoding="utf-8",
            )
            state = (collab / "STATE.md").read_text()
            self.assertEqual((root / "README.md").read_text(), readme)
            self.assertNotIn("long detail", state)
            self.assertIn("../README.md", state)
            self.assertIn("../experiments/results.json", state)
            self.assertEqual((root / "experiments" / "results.json").read_text(), '{"acc":0.9}\n')
            self.assertFalse((collab / "METRICS.csv").exists())
            self.assertFalse((collab / "checkpoints").exists())

    def test_03_agent_handoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            collab = init_docs(root, "codex")
            (collab / "STATE.md").write_text("# State\n\n## Goal\n复现 baseline 并写论文\n")
            (collab / "TASKS.md").write_text(
                "| Task | Status | Owner |\n|---|---|---|\n| baseline | doing | codex |\n")
            (collab / "agents" / "codex.md").write_text(
                "# Agent: codex\n\n## 当前任务\nbaseline 实验\n\n"
                "## 已完成\n数据加载，证据：experiments/loader.json\n\n"
                "## 关键发现\n原始划分有泄漏，改用 split_v2\n\n"
                "## 未完成与阻塞\n指标未跑完\n\n"
                "## 下一步\npython train.py --split v2\n\n"
                "## 相关位置\nexperiments/loader.json, commit abc123\n",
                encoding="utf-8",
            )
            bundle = "\n".join(p.read_text(encoding="utf-8") for p in [
                collab / "STATE.md", collab / "TASKS.md", collab / "agents" / "codex.md",
            ])
            for key in ("复现 baseline", "experiments/loader.json", "指标未跑完",
                        "python train.py --split v2", "doing", "split_v2"):
                self.assertIn(key, bundle)

    def test_04_normal_edits_and_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = init_repo(Path(tmp) / "repo")
            (repo / "code.py").write_text("def f():\n    return 1  # bug\n")
            (repo / "notes.md").write_text("结论：方法 A 有效\n错误行待删除\n")
            git(repo, "add", "code.py", "notes.md")
            git(repo, "commit", "-qm", "initial")
            first = git(repo, "rev-parse", "HEAD").stdout.strip()
            (repo / "code.py").write_text("def f():\n    return 2  # fixed\n")
            (repo / "notes.md").write_text("结论：方法 A 无效（已更正）\n")
            git(repo, "add", "code.py", "notes.md")
            git(repo, "commit", "-qm", "fix bug and correct conclusion")
            self.assertEqual(len(git(repo, "log", "--oneline").stdout.strip().splitlines()), 2)
            self.assertIn("return 1", git(repo, "show", first + ":code.py").stdout)
            self.assertNotIn("错误行", (repo / "notes.md").read_text())
            text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("允许修改代码", text)
            self.assertNotIn("禁止删除已有行", text)

    def test_05_parallel_isolation_and_conflicts(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            remote, a, b = clone_pair(base)
            (a / "collaboration" / "agents").mkdir(parents=True)
            (a / "shared.md").write_text("base\n")
            (a / "collaboration" / "agents" / "codex.md").write_text("A record\n")
            git(a, "add", "shared.md", "collaboration/agents/codex.md")
            git(a, "commit", "-qm", "base")
            git(a, "push", "-q", "origin", "HEAD:refs/heads/main")
            git(b, "fetch", "-q", "origin")
            git(b, "checkout", "-q", "-B", "main", "FETCH_HEAD")

            (a / "a.py").write_text("A\n")
            git(a, "add", "a.py")
            git(a, "commit", "-qm", "A work")
            git(a, "push", "-q", "origin", "HEAD:refs/heads/main")
            (b / "b.py").write_text("B\n")
            (b / "collaboration" / "agents").mkdir(parents=True, exist_ok=True)
            (b / "collaboration" / "agents" / "workbuddy.md").write_text("B record\n")
            git(b, "add", "b.py", "collaboration/agents/workbuddy.md")
            git(b, "commit", "-qm", "B work")
            self.assertNotEqual(git(b, "push", "origin", "HEAD:refs/heads/main", ok=False).returncode, 0)
            git(b, "fetch", "-q", "origin")
            merged = git(b, "merge", "--no-edit", "FETCH_HEAD", ok=False)
            self.assertEqual(merged.returncode, 0, merged.stdout + merged.stderr)
            git(b, "push", "-q", "origin", "HEAD:refs/heads/main")
            verify = base / "verify"
            run("git", "clone", "-q", str(remote), str(verify))
            for rel in ("a.py", "b.py", "collaboration/agents/codex.md",
                        "collaboration/agents/workbuddy.md"):
                self.assertTrue((verify / rel).exists(), rel)

            git(a, "fetch", "-q", "origin")
            git(a, "merge", "--no-edit", "FETCH_HEAD")
            (a / "shared.md").write_text("A version\n")
            git(a, "add", "shared.md")
            git(a, "commit", "-qm", "A edits shared")
            git(a, "push", "-q", "origin", "HEAD:refs/heads/main")
            (b / "shared.md").write_text("B version\n")
            git(b, "add", "shared.md")
            git(b, "commit", "-qm", "B edits shared")
            git(b, "fetch", "-q", "origin")
            conflict = git(b, "merge", "--no-edit", "FETCH_HEAD", ok=False)
            self.assertNotEqual(conflict.returncode, 0)
            self.assertIn("<<<<<<<", (b / "shared.md").read_text())
            git(b, "merge", "--abort")

            tasks = ("| Task | Status | Owner | Scope |\n|---|---|---|---|\n"
                     "| exp | doing | codex | experiments/ |\n"
                     "| data | doing | workbuddy | experiments/ |\n")
            doing_scopes = [line.split("|")[4].strip() for line in tasks.splitlines()
                            if "| doing |" in line]
            self.assertEqual(len(doing_scopes), len(set(doing_scopes)) + 1)

    def test_06_push_rejection_keeps_local_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            remote, a, b = clone_pair(base)
            (a / "base.txt").write_text("base\n")
            git(a, "add", "base.txt")
            git(a, "commit", "-qm", "base")
            git(a, "push", "-q", "origin", "HEAD:refs/heads/main")
            git(b, "fetch", "-q", "origin")
            git(b, "checkout", "-q", "-B", "main", "FETCH_HEAD")
            (a / "a.txt").write_text("A\n")
            git(a, "add", "a.txt")
            git(a, "commit", "-qm", "A")
            git(a, "push", "-q", "origin", "HEAD:refs/heads/main")
            remote_head = run("git", "--git-dir", str(remote), "rev-parse", "main").stdout.strip()

            (b / "b.txt").write_text("B\n")
            git(b, "add", "b.txt")
            git(b, "commit", "-qm", "B")
            local_head = git(b, "rev-parse", "HEAD").stdout.strip()
            rejected = git(b, "push", "origin", "HEAD:refs/heads/main", ok=False)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(git(b, "rev-parse", "HEAD").stdout.strip(), local_head)
            self.assertEqual(run("git", "--git-dir", str(remote), "rev-parse", "main").stdout.strip(), remote_head)
            record = b / "collaboration" / "agents" / "workbuddy.md"
            record.parent.mkdir(parents=True)
            record.write_text("Sync: 未同步；本地提交 " + local_head + "；恢复：fetch + merge 后 push\n",
                              encoding="utf-8")
            self.assertNotIn("已同步", record.read_text())
            git(b, "fetch", "-q", "origin")
            git(b, "merge", "--no-edit", "FETCH_HEAD")
            git(b, "push", "-q", "origin", "HEAD:refs/heads/main")
            self.assertEqual(run("git", "--git-dir", str(remote), "rev-parse", "main").stdout.strip(),
                             git(b, "rev-parse", "HEAD").stdout.strip())

    def test_07_legacy_project_compatibility(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            collab = root / "collaboration"
            (collab / "tasks" / "t1" / "agents" / "a1" / "checkpoints" / "c1").mkdir(parents=True)
            legacy = {
                "PROJECT.md": "Goal: reproduce baseline\n",
                "PROTOCOL.md": "Protocol v1\n",
                "tasks/t1/TASK.md": "Task t1\n",
                "tasks/t1/agents/a1/HANDOFF.md": "Handoff a1\n",
                "tasks/t1/agents/a1/checkpoints/c1/CHECKPOINT.md": "Checkpoint\n",
                "tasks/t1/agents/a1/checkpoints/c1/manifest.json": "{}\n",
                "METRICS.csv": "metric,value\nacc,0.9\n",
            }
            for rel, content in legacy.items():
                (collab / rel).write_text(content)
            before = {rel: (collab / rel).read_bytes() for rel in legacy}
            (collab / "STATE.md").write_text(
                "# State\n\n## Goal\n见 [PROJECT.md](PROJECT.md) 与 [PROTOCOL.md](PROTOCOL.md)。\n\n"
                "## Next\n见 [tasks/t1/TASK.md](tasks/t1/TASK.md)。\n",
                encoding="utf-8",
            )
            for rel, data in before.items():
                self.assertEqual((collab / rel).read_bytes(), data, rel)
            state = (collab / "STATE.md").read_text()
            self.assertIn("PROJECT.md", state)
            self.assertIn("PROTOCOL.md", state)
            self.assertIn("tasks/t1/TASK.md", state)
            self.assertTrue((collab / "tasks").is_dir())

    def test_08_sensitive_files_and_workspace_safety(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = init_repo(base / "repo")
            (repo / "src").mkdir()
            for name, content in {"src/main.py": "print(1)\n", ".env": "FAKE_SECRET_FOR_TEST=1\n",
                                  "id_rsa": "PRIVATE KEY\n", "token.txt": "fake-token-for-test\n",
                                  "weights.bin": "W" * 2048}.items():
                (repo / name).write_text(content)
            init_docs(repo)
            git(repo, "add", "--", "src/main.py", "collaboration/STATE.md",
                "collaboration/TASKS.md", "collaboration/agents/codex.md")
            staged = git(repo, "diff", "--cached", "--name-only").stdout
            for secret in (".env", "id_rsa", "token.txt", "weights.bin"):
                self.assertNotIn(secret, staged)

            repo2 = init_repo(base / "repo2")
            (repo2 / "src").mkdir()
            (repo2 / "src" / "main.py").write_text("print(1)\n")
            git(repo2, "add", "src/main.py")
            git(repo2, "commit", "-qm", "initial")
            before = git(repo2, "rev-parse", "HEAD").stdout.strip()
            (repo2 / "staged.txt").write_text("other agent staged\n")
            git(repo2, "add", "staged.txt")
            (repo2 / "dirty.txt").write_text("other agent uncommitted\n")
            staged = git(repo2, "diff", "--cached", "--name-only").stdout.strip().splitlines()
            self.assertIn("staged.txt", staged)
            self.assertEqual(git(repo2, "rev-parse", "HEAD").stdout.strip(), before)
            self.assertIn("dirty.txt", git(repo2, "status", "--porcelain").stdout)
            self.assertEqual(git(repo2, "rev-parse", "HEAD").stdout.strip(), before)
            text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
            for rule in ("不用 `git add .`", "reset --hard", "git clean", "串行", "未同步"):
                self.assertIn(rule, text)


    def test_09_zero_context_handoff_path(self):
        """Integration check: the four entry files carry enough to resume without a repo-wide scan."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            (root / "src").mkdir(parents=True)
            (root / "experiments" / "configs").mkdir(parents=True)
            (root / "experiments" / "results").mkdir(parents=True)
            (root / "src" / "evaluate.py").write_text("print('fixture')\n")
            (root / "experiments" / "configs" / "main.yaml").write_text("T: 4\n")
            (root / "experiments" / "results" / "main.json").write_text('{"acc":0.87,"synthetic":true}\n')
            collab = init_docs(root)
            (collab / "STATE.md").write_text(
                "# Project State\n\n## Overview\n"
                "- 项目目标：验证稀疏路由省显存\n- 当前阶段：主实验完成，补泛化证据\n"
                "- 当前路线：T=4 稀疏路由\n- 下一步重点：dataset_b 实验\n\n"
                "## Key Decisions\n### 2026-11-10：改用稀疏路由\n"
                "- 决定：稀疏路由\n- 原因：显存预算 4GB\n- 放弃方案：全量邻接\n"
                "- 依据：experiments/results/main.json\n\n"
                "## Verified（已验证，有证据）\n- acc 0.87，证据：experiments/results/main.json\n\n"
                "## Hypothesis（当前假设）\n- dataset_b 上不掉点\n\n"
                "## Pending（待验证）\n- 更长 T 收益\n\n"
                "## Superseded（已推翻／已替代，勿引用）\n- 旧结论 91.2% → 作废原因：划分未对齐\n\n"
                "## Next\n1. 运行 evaluate.py\n", encoding="utf-8")
            (collab / "TASKS.md").write_text(
                "| Task | Status | Owner | Scope |\n|---|---|---|---|\n"
                "| 主实验 | done | codex | experiments/results/main.json |\n"
                "| 泛化实验 | todo | — | src/evaluate.py |\n"
                "| 论文 | doing | workbuddy | paper/draft.md |\n")
            (collab / "agents" / "codex.md").write_text(
                "# Agent: codex\n\n## 下一步（Resume Entry）\n"
                "- 目标：dataset_b 泛化\n- 入口：experiments/configs/main.yaml\n"
                "- 已有结果：experiments/results/main.json\n"
                "- 建议动作：1. 核对配置 2. 运行 src/evaluate.py\n"
                "- 注意：不要重跑主实验；论文由 workbuddy 负责\n", encoding="utf-8")
            entry_files = [root / "AGENTS.md", collab / "STATE.md",
                           collab / "TASKS.md", collab / "agents" / "codex.md"]
            bundle = "\n".join(p.read_text(encoding="utf-8") for p in entry_files)
            for key in ("项目目标", "当前阶段", "当前路线", "下一步重点", "Key Decisions",
                        "原因", "放弃方案", "依据", "Verified", "Hypothesis", "Pending",
                        "Superseded", "已推翻", "Resume Entry", "入口", "已有结果",
                        "不要重跑主实验", "doing", "进程锁", "全盘扫描"):
                self.assertIn(key, bundle)
            for rel in ("experiments/configs/main.yaml", "experiments/results/main.json",
                        "src/evaluate.py"):
                self.assertIn(rel, bundle)
                self.assertTrue((root / rel).is_file(), rel)
            entry = (root / "AGENTS.md").read_text(encoding="utf-8")
            for pointer in ("STATE.md", "TASKS.md", "agents/", "结束"):
                self.assertIn(pointer, entry)

    def test_10_mature_project_and_parallel_handoff(self):
        """Control A: mature project reuse. Control B: agent C resumes a todo task."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "mature"
            (root / "docs").mkdir(parents=True)
            (root / "src").mkdir(parents=True)
            (root / "experiments" / "results").mkdir(parents=True)
            init_repo(root)
            (root / "README.md").write_text("# Mature\n" + "detail " * 50)
            (root / "AGENTS.md").write_text("custom project entry\n")
            (root / "docs" / "old_report.md").write_text("old research plan\n")
            (root / "experiments" / "results" / "latest.json").write_text('{"synthetic": true}\n')
            (root / "src" / "exp.py").write_text("A result\n")
            git(root, "add", "-A")
            git(root, "commit", "-qm", "mature history")
            before = {rel: (root / rel).read_bytes() for rel in
                      ("README.md", "AGENTS.md", "docs/old_report.md",
                       "experiments/results/latest.json", "src/exp.py")}
            collab = init_docs(root)
            (collab / "STATE.md").write_text(
                "# Project State\n\n## Overview\n"
                "- 项目目标：见 [README.md](../README.md)\n"
                "- 当前阶段：见 [latest.json](../experiments/results/latest.json)\n"
                "- 当前路线：轻量模型\n\n"
                "## Superseded（已推翻／已替代，勿引用）\n"
                "- 旧路线见 [old_report.md](../docs/old_report.md)，已被轻量模型替代\n",
                encoding="utf-8")
            state = (collab / "STATE.md").read_text(encoding="utf-8")
            for rel, data in before.items():
                self.assertEqual((root / rel).read_bytes(), data, rel)
            self.assertNotIn("detail detail", state)
            self.assertIn("../README.md", state)
            self.assertIn("../docs/old_report.md", state)
            self.assertIn("Superseded", state)
            (collab / "TASKS.md").write_text(
                "| Task | Status | Owner | Scope |\n|---|---|---|---|\n"
                "| 实验 | doing | codex | src/ |\n"
                "| 论文 | todo | claude | paper/ |\n")
            tasks = (collab / "TASKS.md").read_text()
            doing_owners = [line.split("|")[3].strip() for line in tasks.splitlines()
                            if "| doing |" in line]
            self.assertEqual(doing_owners, ["codex"])
            self.assertIn("| 论文 | todo | claude | paper/ |", tasks)
            (root / "paper").mkdir()
            (root / "paper" / "notes.md").write_text("C handoff\n")
            self.assertEqual((root / "src" / "exp.py").read_text(), "A result\n")
            self.assertEqual((root / "AGENTS.md").read_text(), "custom project entry\n")


if __name__ == "__main__":
    unittest.main(verbosity=2)
