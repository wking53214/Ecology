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
    assert cells[0].identity == "nested.md[Cell-1]"


def test_ingest_directory_respects_gitignore(tmp_path):
    (tmp_path / ".gitignore").write_text("skip.md\n")
    (tmp_path / "skip.md").write_text("Should not appear.\n")
    (tmp_path / "keep.md").write_text("Should appear.\n")

    cells = ingest_directory(str(tmp_path))

    assert len(cells) == 1
    assert cells[0].identity == "keep.md[Cell-1]"


def test_ingest_directory_missing_path_returns_empty_list():
    assert ingest_directory("/nonexistent/path/for/ecology/tests") == []
