# Codebase Service
#
# Provides Harmonix with awareness of its own source code.
# Wraps the low-level codebase search/reader with AI-friendly formatting.

import re

from services.codebase import search_code, read_file
from services.log import get_log

log = get_log(__name__)


# Only filter out words that truly don't help code search.
# Domain words like "code", "task", "note", "router" stay.
STOP_WORDS = {
    "what", "how", "why", "where", "when", "who",
    "does", "do", "did", "is", "are", "was", "were",
    "the", "a", "an", "this", "that",
    "my", "your", "our", "their", "his", "her",
    "can", "could", "would", "should", "will",
    "have", "has", "had", "am", "been", "being",
    "in", "on", "at", "to", "for", "of", "with",
    "and", "or", "but", "not", "no", "so",
    "i", "me", "you", "we", "they", "them",
    "tell", "show", "find", "get", "give",
    "about", "some", "any", "all", "each",
    "just", "also", "very", "really",
    "harmonix",
    "able", "now", "own", "like",
    "want", "need", "try", "use", "using",
    "here", "there", "thing", "things",
}

# Words that indicate the user is asking about code —
# boost these as search terms.
CODE_SIGNALS = {
    "function", "class", "def", "import", "method",
    "file", "module", "service", "cog", "router",
    "task", "note", "memory", "context", "model",
    "database", "notion", "api", "client",
    "dispatch", "extract", "search", "query",
    "command", "slash", "listener", "event",
    "async", "await", "return", "error",
    "data", "config", "setup", "init",
}


def extract_search_terms(query: str) -> list[str]:
    """Extract meaningful search terms from a user query."""

    words = re.findall(r"\b[\w'-]+\b", query.lower())

    terms = [
        word for word in words
        if word not in STOP_WORDS
        and len(word) > 1
    ]

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for term in terms:
        if term not in seen:
            seen.add(term)
            unique.append(term)

    # Prioritize code-relevant signals
    unique.sort(
        key=lambda t: (t not in CODE_SIGNALS, -len(t))
    )

    return unique[:6]


def extract_section(
    content: str,
    match_line: int,
    buffer: int = 15
) -> str:
    """
    Extract a relevant section around a matched line.
    Grabs the enclosing function/class definition.
    """

    lines = content.splitlines()

    if not lines:
        return ""

    start = max(0, match_line - 1 - buffer)
    end = min(len(lines), match_line - 1 + buffer + 1)

    # Expand start to include the function/class def
    for i in range(start, max(start - 10, -1), -1):
        if i < 0:
            break
        stripped = lines[i].strip()
        if stripped.startswith("def ") or stripped.startswith("class ") or stripped.startswith("async def "):
            start = i
            break

    section = lines[start:end]
    return "\n".join(section)


def format_search_results(
    results: list[dict],
    max_chars: int = 3000
) -> str:
    """Format search results into a readable block, grouped by file."""

    if not results:
        return ""

    lines = []
    total = 0

    by_file: dict[str, list[dict]] = {}
    for r in results:
        filepath = r["file"]
        if filepath not in by_file:
            by_file[filepath] = []
        by_file[filepath].append(r)

    for filepath, matches in by_file.items():
        header = f"### {filepath}\n"
        if total + len(header) > max_chars:
            break
        lines.append(header.rstrip())
        total += len(header)

        for m in matches:
            line = f"Line {m['line']}: `{m['content']}`\n"
            if total + len(line) > max_chars:
                break
            lines.append(line.rstrip())
            total += len(line)

        lines.append("")

    return "\n".join(lines)


def format_section(
    filepath: str,
    section: str
) -> str:
    """Format a code section for context injection."""

    if not section:
        return ""

    return f"### {filepath}\n```python\n{section}\n```"


async def search_and_read(
    query: str,
    max_search_results: int = 10,
    max_files_to_read: int = 2,
    max_chars_per_section: int = 2000,
    max_total_chars: int = 4000
) -> str:
    """
    Search the codebase for relevant code, extract the
    most relevant sections, and return formatted context.

    Returns a string ready to inject into the AI prompt.
    """

    terms = extract_search_terms(query)

    if not terms:
        return ""

    log.debug(f"Searching for: {terms}")

    # Search and deduplicate results
    all_results = []
    for term in terms:
        results = search_code(term, max_results=max_search_results)
        for r in results:
            if r not in all_results:
                all_results.append(r)

    if not all_results:
        log.debug("No results found.")
        return ""

    file_count = len(set(r["file"] for r in all_results))
    log.info(f"Found {len(all_results)} matches across {file_count} files")

    # Score files by number of matches
    file_scores: dict[str, int] = {}
    for r in all_results:
        f = r["file"]
        file_scores[f] = file_scores.get(f, 0) + 1

    top_files = sorted(
        file_scores,
        key=file_scores.get,
        reverse=True
    )[:max_files_to_read]

    context_parts = []
    total_chars = 0

    # Search results summary (capped)
    summary = format_search_results(
        all_results,
        max_chars=1500
    )
    if summary:
        context_parts.append(summary)
        total_chars += len(summary)

    # Read relevant sections from top files
    for filepath in top_files:
        if total_chars >= max_total_chars:
            break

        try:
            content = read_file(filepath, max_chars=30000)
        except Exception as e:
            log.error(f"Error reading {filepath}: {e}")
            continue

        # Get the best match line for this file
        file_matches = [
            r for r in all_results if r["file"] == filepath
        ]
        best_line = file_matches[0]["line"] if file_matches else 1

        section = extract_section(
            content,
            best_line,
            buffer=20
        )

        if not section:
            continue

        # Cap section size
        if len(section) > max_chars_per_section:
            section = section[:max_chars_per_section] + "\n# ..."

        formatted = format_section(filepath, section)

        if total_chars + len(formatted) > max_total_chars:
            break

        context_parts.append(formatted)
        total_chars += len(formatted)

    final = "\n".join(context_parts)

    log.debug(f"Context built: {len(final):,} characters")

    return final


async def read_specific_file(
    filepath: str
) -> str:
    """Read a specific file and return formatted content."""

    try:
        content = read_file(filepath)
        return format_section(filepath, content)
    except ValueError as e:
        return f"Error: {e}"
    except FileNotFoundError:
        return f"Error: File not found: {filepath}"


async def search_codebase(
    query: str,
    max_results: int = 20
) -> str:
    """Search the codebase and return formatted results."""

    results = search_code(query, max_results=max_results)

    if not results:
        return "No results found."

    return format_search_results(results)
