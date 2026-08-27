"""LangChain Stack Overflow integration.

Retrievers for searching questions and fetching answers from Stack Exchange sites.

Install:
    pip install langchain-stackoverflow

Usage:
    from langchain_stackoverflow import StackOverflowSearchRetriever, StackOverflowAnswerRetriever

    # Search questions
    retriever = StackOverflowSearchRetriever(max_results=5)
    docs = retriever.invoke("python list comprehension")

    # Get answers for a question
    answers_retriever = StackOverflowAnswerRetriever()
    docs = answers_retriever.invoke("https://stackoverflow.com/questions/123456/example-question")
"""

from langchain_stackoverflow.retrievers import (
    StackOverflowSearchRetriever,
    StackOverflowAnswerRetriever,
)

__all__ = [
    "StackOverflowSearchRetriever",
    "StackOverflowAnswerRetriever",
]

__version__ = "0.1.0"
