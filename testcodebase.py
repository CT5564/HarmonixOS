from services.codebase import search_code
from services.codebase import read_file


print("=" * 50)
print("SEARCHING CODEBASE")
print("=" * 50)

results = search_code(
    "search_for_tasks"
)

for result in results:

    print(
        f"{result['file']}:"
        f"{result['line']}"
    )

    print(
        f"  {result['content']}"
    )

    print()


print("=" * 50)
print("READING FILE")
print("=" * 50)

content = read_file(
    "services/task_service.py"
)

print(content)