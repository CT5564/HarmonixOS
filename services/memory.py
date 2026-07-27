import re
import asyncio

import services.task_service as task_service
import services.note_service as note_service
import services.notion_service as notion_service

STOP_WORDS = {

"harmonix",
    # ============================================================
    # ARTICLES
    # ============================================================

    "a",
    "an",
    "the",

    # ============================================================
    # PRONOUNS
    # ============================================================

    "i",
    "me",
    "my",
    "mine",
    "myself",

    "you",
    "your",
    "yours",
    "yourself",

    "he",
    "him",
    "his",
    "himself",

    "she",
    "her",
    "hers",
    "herself",

    "it",
    "its",
    "itself",

    "we",
    "us",
    "our",
    "ours",
    "ourselves",

    "they",
    "them",
    "their",
    "theirs",
    "themselves",

    # ============================================================
    # QUESTION WORDS
    # ============================================================

    "what",
    "when",
    "where",
    "who",
    "whom",
    "whose",
    "which",
    "why",
    "how",

    # ============================================================
    # QUESTION PHRASES
    # ============================================================

    "what's",
    "whats",
    "when's",
    "whens",
    "where's",
    "wheres",
    "who's",
    "whos",
    "why's",
    "whys",
    "how's",
    "hows",

    # ============================================================
    # COMMON VERBS
    # ============================================================

    "be",
    "am",
    "is",
    "are",
    "was",
    "were",
    "been",
    "being",

    "do",
    "does",
    "did",
    "done",
    "doing",

    "have",
    "has",
    "had",
    "having",

    "can",
    "could",
    "may",
    "might",
    "must",
    "shall",
    "should",
    "will",
    "would",

    # ============================================================
    # COMMON QUESTION / MEMORY VERBS
    # ============================================================

    "tell",
    "tells",
    "told",
    "say",
    "says",
    "said",

    "remember",
    "remembered",
    "recall",
    "recalled",

    "think",
    "thought",
    "know",
    "knew",

    "find",
    "found",
    "look",
    "looking",
    "search",
    "searching",

    "show",
    "shows",
    "showed",

    "give",
    "gave",
    "get",
    "got",

    # ============================================================
    # PREPOSITIONS
    # ============================================================

    "about",
    "above",
    "across",
    "after",
    "against",
    "along",
    "among",
    "around",
    "at",
    "before",
    "behind",
    "below",
    "beneath",
    "beside",
    "between",
    "beyond",
    "by",
    "despite",
    "down",
    "during",
    "except",
    "for",
    "from",
    "in",
    "inside",
    "into",
    "near",
    "of",
    "off",
    "on",
    "onto",
    "out",
    "outside",
    "over",
    "past",
    "through",
    "to",
    "toward",
    "under",
    "until",
    "up",
    "upon",
    "with",
    "within",
    "without",

    # ============================================================
    # CONJUNCTIONS
    # ============================================================

    "and",
    "or",
    "but",
    "nor",
    "yet",
    "so",

    "because",
    "although",
    "though",
    "while",
    "if",
    "unless",
    "since",

    # ============================================================
    # COMMON FILLER WORDS
    # ============================================================

    "just",
    "really",
    "very",
    "quite",
    "rather",
    "pretty",
    "actually",
    "basically",
    "literally",
    "probably",
    "maybe",
    "perhaps",
    "still",
    "also",
    "even",
    "already",
    "again",
    "only",
    "kind",
    "sort",
    "thing",
    "things",

    # ============================================================
    # TIME / CONVERSATIONAL FILLERS
    # ============================================================

    "now",
    "then",
    "today",
    "tomorrow",
    "yesterday",
    "currently",
    "recently",
    "earlier",
    "later",

    # ============================================================
    # MEMORY / REFERENCE FILLERS
    # ============================================================

    "something",
    "anything",
    "everything",
    "nothing",
    "someone",
    "somebody",
    "anyone",
    "anybody",

    "stuff",
    "one",
    "ones",

    # ============================================================
    # COMMON CHAT WORDS
    # ============================================================

    "hey",
    "hi",
    "hello",
    "please",
    "thanks",
    "thank",
    "okay",
    "ok",
    "yeah",
    "yes",
    "no",
}

PERSONAL_TERMS = {
    "i",
    "me",
    "my",
    "mine",
    "myself",
    "about me",
    "my project",
    "my projects",
    "my task",
    "my tasks",
    "my note",
    "my notes",
    "my name",
}

def is_personal_query(query: str) -> bool:

    words = set(
        re.findall(
            r"\b[\w'-]+\b",
            query.lower()
        )
    )

    return bool(
        words.intersection({
            "i",
            "me",
            "my",
            "mine",
            "myself"
        })
    )


def extract_keywords(query: str) -> list[str]:

    words = re.findall(
        r"\b[\w'-]+\b",
        query.lower()
    )

    keywords = [
        word
        for word in words
        if word not in STOP_WORDS
        and len(word) > 2
    ]

    return keywords


async def retrieve_memory(
    query: str,
    author_name: str | None = None,
    author_id: str | None = None

):

    keywords = extract_keywords(query)

    # Only search the current user's name
    # when the query is personal
    if (
        author_name
        and is_personal_query(query)
    ):

        if not any(
            keyword.lower() == author_name.lower()
            for keyword in keywords
        ):

            keywords.append(author_name)


    # No searchable terms
    if not keywords:

        return {
            "tasks": [],
            "notes": []
        }

    tasks = []
    notes = []
    notion_pages = []
    print(
        f"Extracted memory keywords: {keywords}"
    )

    # Search all keywords concurrently
    async def search_keyword(keyword):
        task_results = await task_service.search_for_tasks(
            author_id, keyword
        )
        note_results = await note_service.search_for_notes(
            keyword
        )
        page_results = await notion_service.search_pages(
            keyword
        )
        database_results = await notion_service.search_databases(
            keyword
        )
        return task_results, note_results, page_results, database_results

    results = await asyncio.gather(
        *(search_keyword(kw) for kw in keywords)
    )

    for task_results, note_results, page_results, database_results in results:
        for task in task_results:
            if task not in tasks:
                tasks.append(task)

        for note in note_results:
            if note not in notes:
                notes.append(note)

        for page in page_results:
            if page not in notion_pages:
                notion_pages.append(page)

        for database in database_results:
            if database not in notion_pages:
                notion_pages.append(database)

    # ============================================================
    # RETRIEVE NOTION PAGE CONTENT
    # ============================================================

    enriched_notion_pages = []


    for page in notion_pages:

        try:

            if page["type"] == "database":

                content = (
                    await notion_service.get_database_content(
                        page["id"]
                    )
                )

            else:

                content = (
                    await notion_service.get_page_content(
                        page["id"]
                    )
                )


            enriched_notion_pages.append(
                {
                    "id": page["id"],
                    "title": page["title"],
                    "type": page["type"],
                    "content": content
                }
            )


        except Exception as e:

            print(
                f"[Notion Error] "
                f"{page['title']}: {e}"
            )

            continue


    return {
        "tasks": tasks,
        "notes": notes,
        "notion_pages": enriched_notion_pages
    }