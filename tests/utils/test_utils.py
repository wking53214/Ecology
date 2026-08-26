import json

from dedup import deduplicate_corpus
from preprocess import parse_json


def test_deduplication_removes_exact_repeated_segments(tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "notes.md").write_text(
        "Unique segment.\n\nRepeated segment.\n\nRepeated segment.\n"
    )

    deduplicate_corpus(str(corpus))

    remaining = (corpus / "notes.md").read_text()
    segments = [s.strip() for s in remaining.split("\n\n") if s.strip()]
    assert segments == ["Unique segment.", "Repeated segment."]


def test_deduplication_is_whitespace_normalized(tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "notes.md").write_text(
        "Same   text  here.\n\nSame text here.\n"
    )

    deduplicate_corpus(str(corpus))

    remaining = (corpus / "notes.md").read_text()
    segments = [s.strip() for s in remaining.split("\n\n") if s.strip()]
    assert len(segments) == 1


def test_parse_json_chat_export_produces_role_tagged_markdown(tmp_path):
    output_dir = tmp_path / "corpus"
    export = tmp_path / "chat.json"
    export.write_text(json.dumps({
        "messages": [
            {"role": "user", "content": "Hello."},
            {"role": "assistant", "content": "Hi there."},
        ]
    }))

    parse_json(str(export), str(output_dir))

    produced = (output_dir / "chat_corpus.md").read_text()
    assert "**USER**: Hello." in produced
    assert "**ASSISTANT**: Hi there." in produced


def test_parse_json_skips_empty_messages(tmp_path):
    output_dir = tmp_path / "corpus"
    export = tmp_path / "chat.json"
    export.write_text(json.dumps([
        {"role": "user", "content": ""},
        {"role": "user", "content": "Real content."},
    ]))

    parse_json(str(export), str(output_dir))

    produced = (output_dir / "chat_corpus.md").read_text()
    assert produced.count("**USER**") == 1
