from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict, Any

import hashlib
import json

@dataclass
class Hunk:
    old_start: int
    new_start: int
    old_lines: List[str]
    new_lines: List[str]


class AtomicDiff:

    def __init__(
        self,
        id: str = None,
        file_path: str = None,
        is_new_file: bool = False,
        is_deleted_file: bool = False,
        hunk: Hunk = None,
    ):
        self.file_path = file_path
        self.is_new_file = is_new_file
        self.is_deleted_file = is_deleted_file
        self.hunk = hunk
        d_dict = self.to_dict();
        self.id = hashlib.sha256(json.dumps(d_dict, sort_keys=True).encode("utf-8")).hexdigest()

    def build_from_dict(self, diff_dict: Dict[str, Any]):
        self.file_path = diff_dict["file_path"]
        self.is_new_file = diff_dict["is_new_file"]
        self.is_deleted_file = diff_dict["is_deleted_file"]
        self.hunk = Hunk(diff_dict["old_start"], diff_dict["new_start"], diff_dict["old_lines"], diff_dict["new_lines"])
        self.id =  hashlib.sha256(json.dumps(diff_dict, sort_keys=True).encode("utf-8")).hexdigest()

    def to_dict(self):
        return {
            "file_path": self.file_path,
            "is_new_file": self.is_new_file,
            "is_deleted_file": self.is_deleted_file,
            "old_start": self.hunk.old_start if self.hunk else None,
            "new_start": self.hunk.new_start if self.hunk else None,
            "old_lines": self.hunk.old_lines if self.hunk else None,
            "new_lines": self.hunk.new_lines if self.hunk else None
        }

    # ------------ APPLY ------------

    def apply(self, repo_root: Path):
        file = repo_root / self.file_path

        if self.is_new_file:
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text("\n".join(self._reconstruct_from_new_file()))
            return

        if self.is_deleted_file:
            if file.exists():
                file.unlink()
            return

        if not file.exists():
            raise ValueError(f"File not found while applying diff: {file}")

        lines = file.read_text().splitlines()

        self._apply_hunk(lines, self.hunk)

        file.write_text("\n".join(lines))

    def _apply_hunk(self, lines: List[str], hunk: Hunk):
        if hunk is None:
            return
        idx = hunk.old_start - 1

        # 验证旧内容
        old_slice = lines[idx: idx + len(hunk.old_lines)]

        print("old_start: ", hunk.old_start)
        print(old_slice)
        print(hunk.old_lines)
        print(hunk.new_lines)

        if old_slice != hunk.old_lines:
            raise ValueError(
                f"Hunk mismatch @ {self.file_path}:{hunk.old_start}\n"
                f"Expected: {hunk.old_lines}\nGot: {old_slice}"
            )

        # 替换
        lines[idx: idx + len(hunk.old_lines)] = hunk.new_lines
