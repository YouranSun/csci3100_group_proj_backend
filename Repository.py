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

    def generate_diff(self, mode="cached"):
        """
        生成与指定对象的差异。
        
        :param mode: 差异模式，可选：
            - "cached"：暂存区 vs HEAD（等价于 git diff --cached）
            - "working"：工作区 vs 暂存区（等价于 git diff）
            - "head"：工作区 vs HEAD（等价于 git diff HEAD）
        :return: diff 文本字符串
        """
        valid_modes = {"cached", "working", "head"}
        if mode not in valid_modes:
            raise ValueError(f"mode 必须是 {valid_modes} 之一")

        if mode == "cached":
            diff_text = self.repo.git.diff("--cached")
        elif mode == "working":
            diff_text = self.repo.git.diff()
        elif mode == "head":
            diff_text = self.repo.git.diff("HEAD")

        return diff_text

    def staged_changes(self):
        """
        返回暂存区中文件与 HEAD 的结构化变更摘要。
        类似于 `git diff --cached --name-status`
        """
        diffs = self.repo.index.diff("HEAD")
        return [
            {"path": diff.a_path, "change_type": diff.change_type}
            for diff in diffs
        ]

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