import os
import subprocess

import pytest

from commit_loader import cells_from_git_repo, parse_git_log

_ENV = {
    **os.environ,
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_SYSTEM": os.devnull,
}


def _git(repo, *args, when=None, author="William N. King"):
    env = dict(_ENV)
    env.update({
        "GIT_AUTHOR_NAME": author, "GIT_AUTHOR_EMAIL": "w@example.com",
        "GIT_COMMITTER_NAME": author, "GIT_COMMITTER_EMAIL": "w@example.com",
    })
    if when:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = when
    subprocess.run(["git", "-C", str(repo), *args], check=True, env=env,
                   capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path):
    repo = tmp_path / "CCC"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    (repo / "recurrence.py").write_text("x = 1\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "Add recurrence detection\n\nCounts repeat sightings.",
         when="2026-10-05T09:00:00-04:00")
    (repo / "recurrence.py").write_text("x = 2\n")
    (repo / "README.md").write_text("readme\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "Split recurrence matching out to CCCb",
         when="2026-10-06T14:30:00-04:00", author="Claude")
    _git(repo, "mv", "README.md", "GUIDE.md")
    _git(repo, "commit", "-q", "-m", "Rename README", when="2026-10-07T08:00:00-04:00")
    return repo


def test_one_cell_per_commit_oldest_first(repo):
    cells = list(cells_from_git_repo(repo))
    assert [c.content.splitlines()[0] for c in cells] == [
        "Add recurrence detection", "Split recurrence matching out to CCCb", "Rename README",
    ]


def test_cells_carry_the_real_author_time_and_author(repo):
    first, second, _ = cells_from_git_repo(repo)
    assert first.date_str == "2026-10-05"
    assert first.occurred_at.startswith("2026-10-05T09:00:00")
    assert first.speaker == "William N. King"
    assert second.speaker == "Claude"
    assert second.timestamp > first.timestamp


def test_identity_and_source_name_the_repo_and_commit(repo):
    cell = next(cells_from_git_repo(repo))
    assert cell.identity == f"CCC@{cell.sha}"
    assert cell.source == f"CCC/commit/{cell.sha}"
    assert len(cell.sha) == 40


def test_content_lists_the_files_each_commit_changed(repo):
    first, second, third = cells_from_git_repo(repo)
    assert "Counts repeat sightings." in first.content
    assert "added: recurrence.py" in first.content
    assert "modified: recurrence.py" in second.content
    assert "added: README.md" in second.content
    assert "renamed: README.md -> GUIDE.md" in third.content


def test_limit_takes_the_oldest_commits(repo):
    assert len(list(cells_from_git_repo(repo, limit=2))) == 2


def test_repo_name_override(repo):
    cell = next(cells_from_git_repo(repo, repo_name="wking53214/CCC"))
    assert cell.identity.startswith("wking53214/CCC@")


def test_oversized_commit_splits_and_keeps_time_and_author(tmp_path):
    repo = tmp_path / "big"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    (repo / "f").write_text("x")
    _git(repo, "add", ".")
    message = "Long change\n\n" + "\n\n".join(f"Paragraph {i} " + "word " * 40 for i in range(20))
    _git(repo, "commit", "-q", "-m", message, when="2026-01-02T00:00:00+00:00")
    cells = list(cells_from_git_repo(repo, max_cell_chars=400))
    assert len(cells) > 1
    assert [c.identity.rsplit(".", 1)[1] for c in cells] == [str(i) for i in range(len(cells))]
    assert {c.date_str for c in cells} == {"2026-01-02"}
    assert all(len(c.content) <= 400 for c in cells)


def test_merge_commits_skipped_unless_asked(tmp_path):
    repo = tmp_path / "m"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    (repo / "a").write_text("a")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "base")
    _git(repo, "checkout", "-q", "-b", "side")
    (repo / "b").write_text("b")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "side work")
    _git(repo, "checkout", "-q", "main")
    (repo / "c").write_text("c")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "main work")
    _git(repo, "merge", "-q", "--no-ff", "-m", "Merge side", "side")
    messages = [c.content.splitlines()[0] for c in cells_from_git_repo(repo)]
    assert "Merge side" not in messages
    assert len(messages) == 3
    with_merges = [c.content.splitlines()[0] for c in cells_from_git_repo(repo, include_merges=True)]
    assert "Merge side" in with_merges


def test_not_a_repository_is_a_clear_error(tmp_path):
    with pytest.raises(ValueError, match="not a readable git repository"):
        list(cells_from_git_repo(tmp_path))


def test_parse_tolerates_messages_with_tabs_and_blank_lines():
    text = "\x1eabc\x1fW\x1f2026-01-01T00:00:00+00:00\x1fTitle\n\n\tindented line\n\x1f\n\nM\tf.py\n"
    ((sha, author, when, message, changes),) = list(parse_git_log(text))
    assert sha == "abc" and author == "W"
    assert "\tindented line" in message
    assert changes == ["modified: f.py"]
