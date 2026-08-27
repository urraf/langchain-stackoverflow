# 🚀 langchain-stackoverflow

[![PyPI version](https://badge.fury.io/py/langchain-stackoverflow.svg)](https://badge.fury.io/py/langchain-stackoverflow)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**LangChain retrievers for Stack Overflow** — search questions and fetch full answers across the Stack Exchange network as LangChain `Document` objects. **No API keys required** (optional for higher rate limits).

Perfect for building coding assistants, RAG applications, and troubleshooting agents.

## ✨ Features

| Retriever | What it does | API Key Required? |
|---|---|---|
| `StackOverflowSearchRetriever` | Search questions by keyword or tags | ❌ No! |
| `StackOverflowAnswerRetriever` | Fetch all answers for a question | ❌ No! |

## 📦 Installation

```bash
pip install langchain-stackoverflow
```

## 🚀 Quick Start

### Search Questions

```python
from langchain_stackoverflow import StackOverflowSearchRetriever

retriever = StackOverflowSearchRetriever(
    max_results=3,
    sort="votes",           # "relevance", "votes", "creation", "activity"
    site="stackoverflow",   # any Stack Exchange site (e.g. "serverfault")
    tagged="python;pandas", # Optional: filter by tags
    accepted_only=True,     # Optional: only show questions with accepted answers
)

docs = retriever.invoke("how to merge dataframes")

for doc in docs:
    print(f"❓ {doc.page_content.splitlines()[0]}") # Print question title
    print(f"   👍 {doc.metadata['score']} votes | 💬 {doc.metadata['answer_count']} answers")
    print(f"   🔗 {doc.metadata['url']}")
```

### Fetch Answers

```python
from langchain_stackoverflow import StackOverflowAnswerRetriever

retriever = StackOverflowAnswerRetriever(sort="votes")

# Pass the Stack Overflow URL or just the question ID
docs = retriever.invoke("https://stackoverflow.com/questions/53645882/pandas-merge-two-dataframes-with-different-columns")

for doc in docs:
    if doc.metadata['is_accepted']:
        print("✅ ACCEPTED ANSWER:")
    else:
        print("💡 ANSWER:")
    
    print(f"Score: {doc.metadata['score']}")
    print(f"{doc.page_content[:150]}...\n")
```

## 🔑 Rate Limits & API Keys

By default, the Stack Exchange API allows **300 requests per day** per IP address without an API key. 

If you need more, you can register a free app at [Stack Apps](https://stackapps.com/) to get an API key, which increases your quota to **10,000 requests per day**.

Pass your key to the retriever:
```python
retriever = StackOverflowSearchRetriever(api_key="your_key_here")
```

## 📄 License

MIT — see [LICENSE](LICENSE) for details.
