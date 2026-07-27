from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".idea",
    ".vscode",
    "node_modules",
}


def read_file(
    file_path: str,
    max_chars: int = 20000
) -> str:

    requested_path = (
        PROJECT_ROOT / file_path
    ).resolve()

    # Security check:
    # Prevent reading files outside HarmonixOS
    try:

        requested_path.relative_to(
            PROJECT_ROOT
        )

    except ValueError:

        raise ValueError(
            "Access denied: "
            "file is outside the HarmonixOS project."
        )

    # Prevent access to ignored directories
    if any(
        ignored in requested_path.parts
        for ignored in IGNORED_DIRS
    ):

        raise ValueError(
            "Access denied: "
            "file is inside a protected directory."
        )

    if not requested_path.exists():

        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    if not requested_path.is_file():

        raise ValueError(
            f"Not a file: {file_path}"
        )

    content = requested_path.read_text(
        encoding="utf-8"
    )

    if len(content) > max_chars:

        content = (
            content[:max_chars]
            + "\n\n"
            "[FILE TRUNCATED]"
        )

    return content