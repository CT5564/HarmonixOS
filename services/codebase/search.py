from pathlib import Path


# HarmonixOS project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]


IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    ".env",
    "__pycache__",
    ".idea",
    ".vscode",
    "node_modules",
}


ALLOWED_EXTENSIONS = {
    ".py",
    ".json",
    ".txt",
    ".md",
    ".yaml",
    ".yml",
}


def search_code(
    query: str,
    max_results: int = 20
) -> list[dict]:

    query = query.lower().strip()

    if not query:
        return []

    results = []

    for path in PROJECT_ROOT.rglob("*"):

        # Skip directories we don't want Harmonix reading
        if any(
            ignored in path.parts
            for ignored in IGNORED_DIRS
        ):
            continue

        if not path.is_file():
            continue

        if path.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue

        try:

            content = path.read_text(
                encoding="utf-8"
            )

        except (
            UnicodeDecodeError,
            PermissionError
        ):
            continue

        lines = content.splitlines()

        for line_number, line in enumerate(
            lines,
            start=1
        ):

            if query in line.lower():

                results.append(
                    {
                        "file": str(
                            path.relative_to(
                                PROJECT_ROOT
                            )
                        ),
                        "line": line_number,
                        "content": line.strip()
                    }
                )

                if len(results) >= max_results:
                    return results

    return results