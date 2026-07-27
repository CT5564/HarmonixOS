# Agent Tools
#
# Defines the tools available to agents and executes them.
# Each tool is an OpenAI-compatible function schema
# backed by a real Python function.

import json
import os

from services.codebase.search import search_code
from services.codebase.reader import read_file as _read_file
from services.codebase_service import (
    extract_search_terms,
    format_search_results,
    format_section,
)

# ── Tool Definitions (OpenAI format) ──

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_code",
            "description": (
                "Search the Harmonix codebase for code matching a query. "
                "Returns file paths, line numbers, and matching lines. "
                "Use this to find where something is defined or used."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (keywords, function name, etc.)"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Max results to return (default 15)",
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": (
                "Read the contents of a file in the Harmonix project. "
                "Returns the full file content. Use this after search_code "
                "to read the file you need to modify."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path relative to project root, e.g. 'services/database.py'"
                    }
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": (
                "Edit a file by replacing an exact string match. "
                "The find string must be an exact character-for-character match "
                "of existing code including all whitespace and indentation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path relative to project root"
                    },
                    "find": {
                        "type": "string",
                        "description": "Exact string to find in the file (old code)"
                    },
                    "replace": {
                        "type": "string",
                        "description": "String to replace it with (new code)"
                    }
                },
                "required": ["filepath", "find", "replace"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "description": (
                "Create a new file in the Harmonix project. "
                "Use this only for files that don't exist yet."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path relative to project root"
                    },
                    "content": {
                        "type": "string",
                        "description": "Full content of the new file"
                    }
                },
                "required": ["filepath", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "finish",
            "description": (
                "Signal that you are done. Call this when you have completed "
                "all edits and have a summary of what was done."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "Summary of all changes made"
                    }
                },
                "required": ["summary"]
            }
        }
    },
]


# ── Tool Execution ──

def _resolve_path(filepath: str) -> str:
    """Resolve a relative path against the project root."""

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.normpath(os.path.join(root, filepath))


async def execute_tool(
    name: str,
    arguments: dict
) -> str:
    """Execute a tool call and return the result as a string."""

    try:
        if name == "search_code":
            query = arguments["query"]
            max_results = arguments.get("max_results", 15)

            terms = extract_search_terms(query)
            all_results = []
            for term in terms:
                results = search_code(term, max_results=max_results)
                for r in results:
                    if r not in all_results:
                        all_results.append(r)

            return (
                format_search_results(all_results, max_chars=5000)
                or "No results found."
            )

        elif name == "read_file":
            filepath = arguments["filepath"]

            # read_file() already prepends PROJECT_ROOT
            content = _read_file(filepath, max_chars=30000)
            return format_section(filepath, content)

        elif name == "edit_file":
            filepath = arguments["filepath"]
            find = arguments["find"]
            replace = arguments["replace"]
            resolved = _resolve_path(filepath)

            with open(resolved, "r", encoding="utf-8") as f:
                content = f.read()

            if find not in content:
                return (
                    f"ERROR: find string not found in {filepath}. "
                    "Use read_file to get the current content and "
                    "try again with an exact match."
                )

            count = content.count(find)
            if count > 1:
                return (
                    f"ERROR: find string matches {count} locations "
                    f"in {filepath}. Provide more surrounding context "
                    "to make the match unique."
                )

            new_content = content.replace(find, replace, 1)

            with open(resolved, "w", encoding="utf-8") as f:
                f.write(new_content)

            return f"OK: Edited {filepath}"

        elif name == "create_file":
            filepath = arguments["filepath"]
            content = arguments["content"]
            resolved = _resolve_path(filepath)

            if os.path.exists(resolved):
                return (
                    f"ERROR: {filepath} already exists. "
                    "Use edit_file to modify it."
                )

            os.makedirs(os.path.dirname(resolved), exist_ok=True)

            with open(resolved, "w", encoding="utf-8") as f:
                f.write(content)

            return f"OK: Created {filepath}"

        elif name == "finish":
            return "DONE"

        else:
            return f"ERROR: Unknown tool '{name}'"

    except Exception as e:
        return f"ERROR executing {name}: {e}"
