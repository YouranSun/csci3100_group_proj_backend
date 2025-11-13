from dotenv import load_dotenv
load_dotenv()

from repository import Repository
from llm.openai_llm import OpenAILLM
from function.generate_commit_message import generate_commit_message
from function.generate_summary import generate_repository_abstract, print_summary_tree
from function.generate_atomic_commits import generate_atomic_commits
from db.summary_db import AbstractDB

from openai import OpenAI

client = OpenAI(api_key="YOUR_API_KEY_HERE")

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say hello from OpenAI"}],
)

print(response.choices[0].message.content)
exit()

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

atomic_diffs = generate_atomic_commits(diffs)
print(atomic_diffs)