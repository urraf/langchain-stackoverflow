import pytest
from langchain_stackoverflow import (
    StackOverflowSearchRetriever,
    StackOverflowAnswerRetriever
)

def test_search_retriever():
    retriever = StackOverflowSearchRetriever(max_results=2, sort="votes")
    docs = retriever.invoke("python list comprehension")
    assert len(docs) > 0
    assert "source" in docs[0].metadata
    assert docs[0].metadata["source"] == "stackoverflow_search"

def test_answer_retriever():
    retriever = StackOverflowAnswerRetriever()
    # A famous stackoverflow question: "How to check if a directory exists"
    # https://stackoverflow.com/questions/8933237
    docs = retriever.invoke("https://stackoverflow.com/questions/8933237")
    assert len(docs) > 0
    assert "source" in docs[0].metadata
    assert docs[0].metadata["source"] == "stackoverflow_answers"
