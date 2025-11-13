FILE_ABSTRACT_SYSTEM_PROMPT = """\
You are an assistant that summarizes source code files.
Please provide a concise summary of this file’s purpose, structure, and main logic.
Focus on what the file does rather than implementation details (No more than 10 words).
"""

DIRECTORY_ABSTRACT_SYSTEM_PROMPT = """\
You are an assistant that summarizes a software module or directory.
Please summarize the overall purpose and main functionality of this directory,
highlighting how its components interact or what logical grouping they form (No more than 10 words).
"""

def build_file_summary_prompt(file_name: str, file_content: str) -> str:
    """
    构造用于生成单个文件摘要的 prompt。
    """
    return f"""
{FILE_ABSTRACT_SYSTEM_PROMPT}

File name: {file_name}

Here is the file content:

{file_content}

Return only the summary (in plain English or Chinese, depending on input language).
"""


def build_directory_summary_prompt(dir_name: str, child_summaries: str) -> str:
    """
    构造用于生成目录层级摘要的 prompt。
    """
    return f"""
{DIRECTORY_ABSTRACT_SYSTEM_PROMPT}

Directory name: {dir_name}

Below are summaries of its child files and subdirectories:

{child_summaries}

Return only the summary (in plain English or Chinese, depending on input language).
"""