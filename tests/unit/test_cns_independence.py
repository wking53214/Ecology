"""Ecology is independent of CNS, and these tests hold whether or not CNS is installed.

Each runs in a fresh interpreter in which ``cns`` is blocked outright (``sys.modules['cns'] = None`` makes any import
of it fail), so the result does not depend on what the test environment happens to contain. They never skip.
"""
import ast
import os
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BLOCK = "import sys; sys.modules['cns'] = None; sys.modules['cns.gate'] = None\n"
ENV = {"PYTHONPATH": str(ROOT), "PATH": os.environ.get("PATH", "/usr/bin:/bin"), "PYTHONDONTWRITEBYTECODE": "1"}
PIN = "cns @ git+https://github.com/wking53214/CNS.git@v1.8.0"


def run(code: str, *, block: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-c", (BLOCK if block else "") + textwrap.dedent(code)],
                          capture_output=True, text=True, env=ENV, timeout=120)


def ok(done: subprocess.CompletedProcess) -> None:
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip().endswith("ok"), done.stdout


def test_the_connector_imports_with_cns_blocked():
    ok(run("import ecology_cns_connector; print('ok')"))


def test_ecology_still_does_its_job_with_cns_blocked():
    # Verification and the finding record are Ecology's evidence-bound answer; the *_content functions are pure.
    ok(run("""
        import ecology_cns_connector as c
        from containment import verify
        from finding import to_finding_record
        passage = "The reactor coolant pump failed because the seal cracked."
        extract = verify("why did the reactor coolant pump fail", passage)
        assert extract and extract in passage, extract
        record = to_finding_record("The seal cracked.", [{"source": "log.md", "extract": extract}], n_results=1)
        assert record.verified and record.source_material == ("log.md",)
        refused = to_finding_record("The retrieved corpus does not contain a verifiable answer to this query.", [], 1)
        assert refused.verified is False and refused.confidence is None
        assert c.finding_content(record)["verified"] is True and c.finding_content(refused)["verified"] is False
        answer = {"query": "q", "answer": "a", "sources": [{"source": "log.md", "extract": extract}]}
        assert c.answer_content(answer)["evidence"][0]["source"] == "log.md"
        print('ok')
    """))


def test_the_connector_says_what_is_missing_when_cns_is_blocked():
    ok(run("""
        from ecology_cns_connector import CnsNotInstalled, answer_digest, binds, cns_available, finding_digest
        from finding import FindingRecord
        answer = {"query": "q", "answer": "a", "sources": []}
        finding = FindingRecord("c", "m", (), None, False)
        assert cns_available() is False
        for call in (lambda: answer_digest(answer), lambda: finding_digest(finding), lambda: binds(object(), answer)):
            try:
                call()
            except CnsNotInstalled as e:
                assert isinstance(e, ImportError)
                assert "pip install -r requirements-cns.txt" in str(e)
            else:
                raise SystemExit("computed a digest without cns")
        print('ok')
    """))


def test_importing_ecologys_modules_does_not_load_cns_even_when_it_is_installed():
    ok(run("""
        import sys
        import containment, ecology_cns_connector, finding
        assert not [m for m in sys.modules if m == "cns" or m.startswith("cns.")], "cns was loaded"
        print('ok')
    """, block=False))


def test_no_live_module_imports_cns_by_statement():
    # Live modules: the top level, src/ and scripts/. corpus/ is harvested data kept for retrieval (pytest.ini and
    # ruff.toml treat it the same way) and tests/ imports cns.gate on purpose; neither is part of Ecology's modules.
    paths = [p for p in ROOT.glob("*.py")] + list((ROOT / "src").rglob("*.py")) + list((ROOT / "scripts").rglob("*.py"))
    assert (ROOT / "ecology_cns_connector.py") in paths and len(paths) > 20
    offenders = {}
    for path in paths:
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else \
                [node.module] if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module else []
            bad = [n for n in names if n == "cns" or n.startswith("cns.")]
            if bad:
                offenders.setdefault(str(path.relative_to(ROOT)), []).extend(bad)
    assert offenders == {}


def test_ecology_declares_no_runtime_dependency_and_pins_the_cns_extra():
    for name in ("requirements.txt", "requirements-dev.txt"):
        text = (ROOT / name).read_text(encoding="utf-8").lower()
        assert "cns" not in text, name
    lines = (ROOT / "requirements-cns.txt").read_text(encoding="utf-8").splitlines()
    assert [line for line in lines if line.strip() and not line.startswith("#")] == [PIN]
    assert len([line for line in lines if line.startswith("#")]) == 1
