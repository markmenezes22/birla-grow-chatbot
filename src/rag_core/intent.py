"""
Intent Classification — Refusal Engine.

Blocks advisory/non-factual queries using keyword heuristic matching.
No LLM call needed: the corpus is narrow (5 mutual funds) and the 
advisory boundary is well-defined.
"""
import re
from typing import Tuple

# Advisory trigger patterns (case-insensitive)
ADVISORY_PATTERNS = [
    r"should i invest",
    r"should i buy",
    r"should i sell",
    r"should i redeem",
    r"which is better",
    r"which fund is best",
    r"which one should",
    r"recommend",
    r"suggestion",
    r"good investment",
    r"bad investment",
    r"worth investing",
    r"safe to invest",
    r"risky",
    r"best fund",
    r"worst fund",
    r"buy or sell",
    r"hold or sell",
    r"compare.*better",
    r"predict",
    r"future performance",
    r"will.*go up",
    r"will.*go down",
    r"guaranteed",
    r"assured returns",
    r"can i trust",
    r"my portfolio",
    r"how much should i",
    r"advice",
]

REFUSAL_MESSAGE = (
    "I can only provide factual information about mutual funds. "
    "For investment advice, please consult a SEBI-registered financial advisor. "
    "Learn more: https://www.amfiindia.com/investor-corner/knowledge-center.html"
)


def classify_intent(query: str) -> Tuple[str, str | None]:
    """
    Classifies a user query as either 'factual' or 'advisory'.
    
    Returns:
        A tuple of (intent, refusal_message).
        - ("factual", None) if the query is factual.
        - ("advisory", refusal_message) if the query asks for advice.
    """
    query_lower = query.lower().strip()
    
    for pattern in ADVISORY_PATTERNS:
        if re.search(pattern, query_lower):
            return ("advisory", REFUSAL_MESSAGE)
    
    return ("factual", None)


if __name__ == "__main__":
    test_queries = [
        "What is the exit load for Birla Sun Life Liquid Fund?",
        "Should I invest in the small cap fund?",
        "What is the NAV of the large cap fund?",
        "Which is better, liquid fund or small cap?",
        "Who is the fund manager of Digital India Fund?",
        "Is this a good investment for beginners?",
        "What are the top holdings?",
        "Recommend a fund for me",
        "What is the expense ratio?",
        "Will this fund go up next year?",
    ]
    
    for q in test_queries:
        intent, msg = classify_intent(q)
        status = "✓ FACTUAL" if intent == "factual" else "✗ ADVISORY"
        print(f"  {status}: {q}")
