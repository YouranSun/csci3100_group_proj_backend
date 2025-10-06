from dotenv import load_dotenv
load_dotenv()

from Repository import Repository
from llm.openai import OpenAILLM
from function.generate_commit_message import generate_commit_message

repo = Repository("./example/")
diffs = repo.diff_with_head()

for d in diffs:
    print(f"File path: {d['file']}")
    print(f"Old start lineno: {d['old_start']}, New start lineno: {d['new_start']}")
    print("Old content:")
    for line in d['old_lines']:
        print("  -", line)
    print("New content:")
    for line in d['new_lines']:
        print("  +", line)
    print("-" * 60)

llm = OpenAILLM(model="gpt-4o-mini")
message = generate_commit_message(llm, diffs)

print("\n📝 Suggested commit message:\n")
print(message)