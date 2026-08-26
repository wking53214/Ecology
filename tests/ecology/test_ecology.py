import ollama

from ecology import ingest_directory, ActiveKnowledgeObject


def test_ingest_directory_splits_files_into_paragraph_cells(tmp_path):
    (tmp_path / "notes.md").write_text("First paragraph.\n\nSecond paragraph.\n")

    cells = ingest_directory(str(tmp_path))

    assert len(cells) == 2
    assert all(isinstance(c, ActiveKnowledgeObject) for c in cells)
    contents = {c.content for c in cells}
    assert contents == {"First paragraph.", "Second paragraph."}


def test_ingest_directory_cell_identity_includes_filename_and_index(tmp_path):
    (tmp_path / "notes.md").write_text("Only paragraph.\n")

    cells = ingest_directory(str(tmp_path))

    assert cells[0].identity == "notes.md[Cell-1]"


def test_ingest_directory_recurses_into_subdirectories(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "nested.md").write_text("Nested content.\n")

    cells = ingest_directory(str(tmp_path))

    assert len(cells) == 1
    assert cells[0].identity == "sub/nested.md[Cell-1]"
    assert cells[0].source == "sub/nested.md"


def test_ingest_directory_identity_is_collision_free_across_subdirectories(tmp_path):
    # Two same-named files in different subdirectories must not collide,
    # since identity is used as the vector-store id.
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    (tmp_path / "a" / "notes.md").write_text("From a.\n")
    (tmp_path / "b" / "notes.md").write_text("From b.\n")

    cells = ingest_directory(str(tmp_path))

    identities = {c.identity for c in cells}
    assert identities == {"a/notes.md[Cell-1]", "b/notes.md[Cell-1]"}


def test_ingest_directory_respects_gitignore(tmp_path):
    (tmp_path / ".gitignore").write_text("skip.md\n")
    (tmp_path / "skip.md").write_text("Should not appear.\n")
    (tmp_path / "keep.md").write_text("Should appear.\n")

    cells = ingest_directory(str(tmp_path))

    assert len(cells) == 1
    assert cells[0].identity == "keep.md[Cell-1]"


def test_ingest_directory_missing_path_returns_empty_list():
    assert ingest_directory("/nonexistent/path/for/ecology/tests") == []


def test_receive_message_returns_verified_extract(monkeypatch):
    responses = iter([
        {"message": {"content": "YES"}},
        {"message": {"content": "The car is red."}},
    ])
    monkeypatch.setattr(ollama, "chat", lambda **kwargs: next(responses))

    cell = ActiveKnowledgeObject(identity="x", content="The car is red. It has four wheels.", timestamp=0, source="x.md")
    result = cell.receive_message("What color is the car?")

    assert result == "The car is red."


def test_receive_message_returns_none_when_irrelevant(monkeypatch):
    monkeypatch.setattr(ollama, "chat", lambda **kwargs: {"message": {"content": "NO"}})

    cell = ActiveKnowledgeObject(identity="x", content="The car is red.", timestamp=0, source="x.md")
    result = cell.receive_message("How do I cook pasta?")

    assert result is None


def test_receive_message_rejects_extraction_not_present_in_content(monkeypatch):
    # Model claims relevance and returns text that isn't actually a
    # substring of the cell's own content -- the containment check must
    # reject this rather than treat it as a grounded answer.
    responses = iter([
        {"message": {"content": "YES"}},
        {"message": {"content": "The car is blue."}},
    ])
    monkeypatch.setattr(ollama, "chat", lambda **kwargs: next(responses))

    cell = ActiveKnowledgeObject(identity="x", content="The car is red.", timestamp=0, source="x.md")
    result = cell.receive_message("What color is the car?")

    assert result is None


def test_receive_message_rejects_unknown_extraction(monkeypatch):
    responses = iter([
        {"message": {"content": "YES"}},
        {"message": {"content": "UNKNOWN"}},
    ])
    monkeypatch.setattr(ollama, "chat", lambda **kwargs: next(responses))

    cell = ActiveKnowledgeObject(identity="x", content="The car is red.", timestamp=0, source="x.md")
    result = cell.receive_message("Who makes the car?")

    assert result is None
