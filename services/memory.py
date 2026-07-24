import re

import services.task_service as task_service
import services.note_service as note_service


STOP_WORDS = {
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
    "what",
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
    "just",
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
    "thing",
    "things",
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


async def retrieve_memory(query: str):

    keywords = extract_keywords(query)

    if not keywords:

        return {
            "tasks": [],
            "notes": []
        }

    tasks = []
    notes = []

    # Search each meaningful keyword
    for keyword in keywords:

        task_results = (
            await task_service.search_for_tasks(
                keyword
            )
        )

        note_results = (
            await note_service.search_for_notes(
                keyword
            )
        )

        # Prevent duplicate tasks
        for task in task_results:

            if task not in tasks:

                tasks.append(task)

        # Prevent duplicate notes
        for note in note_results:

            if note not in notes:

                notes.append(note)

    return {
        "tasks": tasks,
        "notes": notes
    }