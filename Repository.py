import re

from git import Repo
from pathlib import Path

class Repository:
    def __init__(self, path="."):
        """
        初始化仓库对象
        :param path: 仓库路径（默认为当前目录）
        """
        self.repo_path = Path(path).resolve()
        try:
            self.repo = Repo(self.repo_path)
        except Exception as e:
            raise RuntimeError(f"无法在 {self.repo_path} 打开 Git 仓库: {e}")

    def parse_diff_blocks(self, diff_text):
        """
        解析 git diff 文本，提取文件名、行号区间、原始内容、新内容。
        """
        results = []
        current_file = None

        # 按文件拆分 diff
        file_blocks = re.split(r"^diff --git a/(.+?) b/\1$", diff_text, flags=re.MULTILINE)

        for block in file_blocks:
            if not block.strip():
                continue

            # 获取文件名
            match_file = re.search(r"^\+\+\+ b/(.+)$", block, re.MULTILINE)
            if not match_file:
                continue
            current_file = match_file.group(1)

            # 查找所有区块头部 @@ -x,y +a,b @@
            for match in re.finditer(r"@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@", block):
                old_start = int(match.group(1))
                new_start = int(match.group(3))

                # 获取本区块的内容
                start_idx = match.end()
                next_match = re.search(r"^@@ ", block[start_idx:], flags=re.MULTILINE)
                end_idx = start_idx + next_match.start() if next_match else len(block)
                hunk_text = block[start_idx:end_idx].strip("\n")

                # 提取原始和新内容
                old_lines = []
                new_lines = []
                for line in hunk_text.splitlines():
                    if line.startswith("-"):
                        old_lines.append(line[1:])
                    elif line.startswith("+"):
                        new_lines.append(line[1:])

                results.append({
                    "file": current_file,
                    "old_start": old_start,
                    "new_start": new_start,
                    "old_lines": old_lines,
                    "new_lines": new_lines,
                })

        return results

    def diff_with_head(self):
        """
        提取暂存区（index）与 HEAD 的结构化差异信息。
        """
        diff_text = self.repo.git.diff("--cached", "--unified=0")
        return self.parse_diff_blocks(diff_text)