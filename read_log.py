"""A record of input that was seen but not turned into cells.

The loaders skip things on purpose: messages too short to be a cell, manifest
entries with no transcript, files that do not parse. That is fine. What was
not fine is that the skips left no trace, so "4,000 cells from 500
conversations" could not be told apart from "the other 1,400 messages were
silently dropped". A ReadLog is passed in, filled as the loaders go, and read
afterwards. Passing none changes nothing.

Standard library only. Each entry says what kind of skip, where, and why, and
nothing here changes what a loader yields.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

# Skip kinds. Strings, so a new loader can add its own without editing this file.
MESSAGE_TOO_SHORT = "message_too_short"
CONVERSATION_TOO_SHORT = "conversation_too_short"
MANIFEST_ENTRY_NO_ID = "manifest_entry_no_id"
TRANSCRIPT_MISSING = "transcript_missing"
DECODE_LOSS = "decode_loss"
PYTHON_UNPARSABLE = "python_unparsable"
GIT_RECORD_MALFORMED = "git_record_malformed"


@dataclass(frozen=True)
class Skip:
    kind: str
    where: str
    reason: str = ""


@dataclass
class ReadLog:
    skips: list[Skip] = field(default_factory=list)

    def note(self, kind: str, where: str, reason: str = "") -> None:
        self.skips.append(Skip(kind, where, reason))

    def counts(self) -> dict[str, int]:
        return dict(Counter(s.kind for s in self.skips))

    def __len__(self) -> int:
        return len(self.skips)

    def __bool__(self) -> bool:  # an empty log is still a log
        return True
