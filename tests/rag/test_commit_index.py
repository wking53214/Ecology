"""index_commit_history: a repository's commits into their own collection."""

import os
import subprocess

import pytest

import rag_engine
from rag_engine import COMMIT_COLLECTION_NAME, HISTORY_COLLECTION_NAME, index_commit_history


@pytest.fixture(autouse=True)
def stub_embedder(monkeypatch):
    # Same stand-in the other rag tests use: no ONNX model download in CI.
    monkeypatch.setattr(rag_engine, "_embed", lambda texts: [[1.0, float(len(t) % 7), 0.0] for t in texts])


def _repo(tmp_path, name="CCC", commits=(("first change", "2026-10-05T09:00:00+00:00"),
                                          ("second change", "2026-10-06T09:00:00+00:00"))):
    repo = tmp_path / name
    repo.mkdir()
    env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
           "GIT_AUTHOR_NAME": "William N. King", "GIT_AUTHOR_EMAIL": "w@example.com",
           "GIT_COMMITTER_NAME": "William N. King", "GIT_COMMITTER_EMAIL": "w@example.com"}
    subprocess.run(["git", "-C", str(repo), "init", "-q", "-b", "main"], check=True, env=env)
    for i, (message, when) in enumerate(commits):
        (repo / f"f{i}.py").write_text(str(i))
        subprocess.run(["git", "-C", str(repo), "add", "."], check=True, env=env)
        subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", message], check=True,
                       env={**env, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when})
    return repo


def test_commits_land_in_their_own_collection_with_real_date_and_author(tmp_path):
    repo = _repo(tmp_path)
    collection = index_commit_history(str(repo), db_path=str(tmp_path / "db"))
    assert collection.name == COMMIT_COLLECTION_NAME != HISTORY_COLLECTION_NAME
    assert collection.count() == 2
    got = collection.get(include=["metadatas", "documents"])
    dates = sorted(m["date"] for m in got["metadatas"])
    assert dates == ["2026-10-05", "2026-10-06"]
    assert {m["speaker"] for m in got["metadatas"]} == {"William N. King"}
    assert all(m["source"].startswith("CCC/commit/") for m in got["metadatas"])
    assert any("added: f0.py" in d for d in got["documents"])


def test_rerun_adds_only_new_commits_and_a_second_repo_appends(tmp_path):
    db = str(tmp_path / "db")
    repo = _repo(tmp_path)
    assert index_commit_history(str(repo), db_path=db).count() == 2
    assert index_commit_history(str(repo), db_path=db).count() == 2
    other = _repo(tmp_path, name="CNS", commits=(("cns change", "2026-10-07T09:00:00+00:00"),))
    assert index_commit_history(str(other), db_path=db).count() == 3
