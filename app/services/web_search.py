import logging
import os
from typing import List
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


def _search_tavily(query: str, api_key: str, max_results: int = 3) -> List[Document]:
    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": max_results,
            },
            timeout=10,
        )
        if not response.ok:
            logger.warning(
                f"Tavily search failed (HTTP {response.status_code}): {response.text}"
            )
            return []

        data = response.json()
        results = data.get("results", [])
        documents = []
        for item in results:
            content = item.get("content") or item.get("snippet") or ""
            url = item.get("url") or ""
            title = item.get("title") or "Web Search Result"
            if content.strip():
                documents.append(
                    Document(
                        page_content=content.strip(),
                        metadata={
                            "source": url,
                            "title": title,
                            "source_type": "web_search",
                        },
                    )
                )
        return documents
    except Exception as error:
        logger.warning(f"Tavily web search error: {error}")
        return []


def _search_serper(query: str, api_key: str, max_results: int = 3) -> List[Document]:
    try:
        response = requests.post(
            "https://google.serper.dev/search",
            headers={
                "X-API-KEY": api_key,
                "Content-Type": "application/json",
            },
            json={"q": query, "num": max_results},
            timeout=10,
        )
        if not response.ok:
            logger.warning(
                f"Serper search failed (HTTP {response.status_code}): {response.text}"
            )
            return []

        data = response.json()
        results = data.get("organic", [])
        documents = []
        for item in results:
            snippet = item.get("snippet") or ""
            link = item.get("link") or ""
            title = item.get("title") or "Web Search Result"
            if snippet.strip():
                documents.append(
                    Document(
                        page_content=snippet.strip(),
                        metadata={
                            "source": link,
                            "title": title,
                            "source_type": "web_search",
                        },
                    )
                )
        return documents
    except Exception as error:
        logger.warning(f"Serper web search error: {error}")
        return []


def _search_duckduckgo(query: str, max_results: int = 3) -> List[Document]:
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        }
        response = requests.post(
            "https://html.duckduckgo.com/html/",
            data={"q": query},
            headers=headers,
            timeout=10,
        )
        if not response.ok:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        documents = []
        for item in soup.select(".result")[:max_results]:
            title_node = item.select_one(".result__title a")
            snippet_node = item.select_one(".result__snippet")
            if title_node and snippet_node:
                title = title_node.get_text(strip=True)
                raw_href = title_node.get("href", "")
                # Decode DuckDuckGo redirect url if applicable
                url = raw_href
                if "uddg=" in raw_href:
                    try:
                        url = unquote(raw_href.split("uddg=")[1].split("&")[0])
                    except Exception:
                        url = raw_href

                snippet = snippet_node.get_text(strip=True)
                if snippet:
                    documents.append(
                        Document(
                            page_content=snippet,
                            metadata={
                                "source": url,
                                "title": title,
                                "source_type": "web_search",
                            },
                        )
                    )
        return documents
    except Exception as error:
        logger.warning(f"DuckDuckGo search error: {error}")
        return []


def perform_web_search(query: str, max_results: int = 3) -> List[Document]:
    """Perform web search using Tavily, Serper, or DuckDuckGo as fallback."""
    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key:
        docs = _search_tavily(query, tavily_key, max_results)
        if docs:
            return docs

    serper_key = os.getenv("SERPER_API_KEY")
    if serper_key:
        docs = _search_serper(query, serper_key, max_results)
        if docs:
            return docs

    return _search_duckduckgo(query, max_results)

