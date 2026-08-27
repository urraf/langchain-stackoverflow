"""LangChain retrievers for Stack Overflow / Stack Exchange data.

This module provides two retrievers for fetching Stack Exchange data
as LangChain Document objects:

- StackOverflowSearchRetriever: Search questions by keyword or tags.
- StackOverflowAnswerRetriever: Fetch all answers for a given question.
"""

from __future__ import annotations

from typing import Any

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import Field, PrivateAttr

from langchain_stackoverflow._client import StackOverflowClient


class StackOverflowSearchRetriever(BaseRetriever):
    """Search Stack Overflow questions. No API key required (optional for higher limits)."""
    
    api_key: str | None = Field(
        default=None,
        description="Optional Stack Apps API key for higher rate limits."
    )
    max_results: int = Field(
        default=10,
        description="Maximum number of search results to return."
    )
    sort: str = Field(
        default="relevance",
        description="Sort order. Options: 'relevance', 'votes', 'creation', 'activity'."
    )
    site: str = Field(
        default="stackoverflow",
        description="Stack Exchange site ID (e.g., 'stackoverflow', 'serverfault')."
    )
    tagged: str | None = Field(
        default=None,
        description="Semicolon-separated list of tags to filter by."
    )
    accepted_only: bool = Field(
        default=False,
        description="Only return questions that have an accepted answer."
    )
    
    _client: StackOverflowClient = PrivateAttr()
    
    def model_post_init(self, __context: Any) -> None:
        """Initialize the Stack Exchange API client."""
        super().model_post_init(__context)
        self._client = StackOverflowClient(api_key=self.api_key)
        
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> list[Document]:
        """Search Stack Exchange and return matching questions as Documents."""
        results = self._client.search_questions(
            query=query,
            max_results=self.max_results,
            sort=self.sort,
            site=self.site,
            tagged=self.tagged,
            accepted_only=self.accepted_only,
        )
        
        documents: list[Document] = []
        for item in results:
            title = item.get("title", "")
            url = item.get("link", "")
            body_markdown = item.get("body_markdown", item.get("body", ""))
            
            content = f"Question: {title}\n"
            if url:
                content += f"\nURL: {url}\n"
            if body_markdown:
                content += f"\nBody:\n{body_markdown}\n"
                
            metadata = {
                "source": f"{self.site}_search",
                "question_id": str(item.get("question_id", "")),
                "url": url,
                "author": item.get("owner", {}).get("display_name", ""),
                "score": item.get("score", 0),
                "answer_count": item.get("answer_count", 0),
                "is_answered": item.get("is_answered", False),
                "accepted_answer_id": str(item.get("accepted_answer_id", "")),
                "tags": item.get("tags", []),
                "created_at_ts": item.get("creation_date", 0),
                "view_count": item.get("view_count", 0),
            }
            documents.append(Document(page_content=content.strip(), metadata=metadata))
            
        return documents


class StackOverflowAnswerRetriever(BaseRetriever):
    """Fetch answers for a Stack Overflow question. No API key required."""
    
    api_key: str | None = Field(
        default=None,
        description="Optional Stack Apps API key for higher rate limits."
    )
    sort: str = Field(
        default="votes",
        description="Sort order. Options: 'votes', 'creation', 'activity'."
    )
    site: str = Field(
        default="stackoverflow",
        description="Stack Exchange site ID (e.g., 'stackoverflow', 'serverfault')."
    )
    
    _client: StackOverflowClient = PrivateAttr()
    
    def model_post_init(self, __context: Any) -> None:
        """Initialize the Stack Exchange API client."""
        super().model_post_init(__context)
        self._client = StackOverflowClient(api_key=self.api_key)
        
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> list[Document]:
        """Fetch answers for a question and return as Documents."""
        question_id = self._client.extract_question_id(query)
        answers = self._client.get_answers(
            question_id=question_id,
            sort=self.sort,
            site=self.site,
        )
        
        documents: list[Document] = []
        for i, answer in enumerate(answers):
            body_markdown = answer.get("body_markdown", answer.get("body", ""))
            
            metadata = {
                "source": f"{self.site}_answers",
                "answer_id": str(answer.get("answer_id", "")),
                "question_id": str(answer.get("question_id", "")),
                "author": answer.get("owner", {}).get("display_name", ""),
                "score": answer.get("score", 0),
                "is_accepted": answer.get("is_accepted", False),
                "created_at_ts": answer.get("creation_date", 0),
                "answer_index": i,
            }
            
            documents.append(Document(page_content=body_markdown, metadata=metadata))
            
        return documents
