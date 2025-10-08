from dotenv import load_dotenv
load_dotenv()

from Repository import Repository
from llm.openai import OpenAILLM
from function.generate_commit_message import generate_commit_message
from function.generate_abstract import generate_repository_abstract, print_summary_tree
from db.abstract_db import AbstractDB

repo = Repository("./example/")
diffs = repo.diff_with_head()

llm = OpenAILLM(model="gpt-4o-mini")
message = generate_commit_message(llm, diffs)

print("\n Suggested commit message:\n")
print(message)

# 生成摘要并保存到数据库
print("Generating repository summary and saving to DB...")
root_summary = generate_repository_abstract(llm, repo)
print("\nRepository root summary (from LLM):")
print(root_summary, "...\n")  

# 打开数据库并打印树形结构
print("Printing summary tree from DB...")
db = AbstractDB(str(repo.repo_path))
print_summary_tree(db)
db.close()
