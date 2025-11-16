from typing import List
from Repository.diff import AtomicDiff, Hunk

import re

def parse_diff_blocks(diff_text: str) -> List[AtomicDiff]:
    """
    将 git diff 转换成统一的 AtomicDiff 列表
    """

    results: List[AtomicDiff] = []

    # 拆成多个文件级 diff
    file_splits = re.split(r"^diff --git a/(.+?) b/\1$", diff_text, flags=re.MULTILINE)

    # file_splits 长度为奇数：[ '', file_name, block, file_name, block, ... ]
    i = 1
    while i < len(file_splits):
        filename = file_splits[i]
        block = file_splits[i+1]
        i += 2

        # 新文件检测
        is_new_file = ("new file mode" in block)
        is_deleted_file = ("deleted file mode" in block)

        # 提取 hunks
        for hunk in re.finditer(r"@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@", block):
            old_start = int(hunk.group(1))
            new_start = int(hunk.group(3))

            start = hunk.end()
            # 找下一个 hunk 的开始
            next_hunk = re.search(r"@@ -", block[start:])
            end = start + next_hunk.start() if next_hunk else len(block)

            hunk_text = block[start:end].strip("\n")
            old_lines = []
            new_lines = []

            for line in hunk_text.splitlines():
                if line.startswith("-"):
                    old_lines.append(line[1:])
                elif line.startswith("+"):
                    new_lines.append(line[1:])
                # " " 前缀行不存储，它不是 atomic patch 的内容

            results.append(
                AtomicDiff(
                    file_path=filename,
                    is_new_file=is_new_file,
                    is_deleted_file=is_deleted_file,
                    hunk=Hunk(
                        old_start=old_start,
                        new_start=new_start,
                        old_lines=old_lines,
                        new_lines=new_lines,
                    )
                )
            )

    return results

def adjust_later_groups(groups, diffs, current_index):
    current_group = groups[current_index]
    for diff_id in current_group["diff_ids"]:
        d = diffs[diff_id]

        file_path = d.file_path
        delta = len(d.hunk.new_lines) - len(d.hunk.old_lines)
        if delta == 0:
            continue

        for g in groups[current_index + 1:]:
            for later_id in g["diff_ids"]:
                ld = diffs[later_id]

                if ld.hunk.file_path != file_path:
                    continue

                if ld.hunk.old_start > d.hunk.old_start:
                    ld.hunk.old_start += delta

def adjust_later_diffs(current_group, diffs, current_index):
    diff_id = current_group["diff_ids"][current_index]
    d = diffs[diff_id]
    file_path = d.hunk.file_path
    delta = len(d.hunk.new_lines) - len(d.hunk.old_lines)
    for later_id in current_group["diff_ids"][current_index + 1:]:
        ld = diffs[later_id]

        if ld.file_path != file_path:
            continue

        if ld.hunk.old_start > d.hunk.old_start:
            ld.hunk.old_start += delta