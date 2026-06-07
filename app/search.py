import os
from dotenv import load_dotenv
load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

def web_search(query: str, max_results: int = 5) -> str:
    """Search the web and return results as formatted text."""
    if not TAVILY_API_KEY:
        return f"[Web search unavailable — no API key] Query was: {query}"
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(
            query=query,
            search_depth="basic",
            max_results=max_results
        )
        results = response.get("results", [])
        if not results:
            return f"No results found for: {query}"
        formatted = f"Web search results for '{query}':\n\n"
        for i, r in enumerate(results, 1):
            formatted += f"{i}. {r.get('title', 'No title')}\n"
            formatted += f"   {r.get('content', 'No content')[:300]}\n"
            formatted += f"   Source: {r.get('url', '')}\n\n"
        return formatted
    except Exception as e:
        return f"Search failed: {str(e)}"

def should_search(task: str) -> bool:
    """Decide if a task needs web search."""
    search_keywords = [
        "research", "find", "search", "latest", "current",
        "recent", "today", "news", "what is", "who is",
        "how much", "price", "statistics", "data", "facts",
        "trend", "market", "compare", "analysis", "report"
    ]
    task_lower = task.lower()
    return any(kw in task_lower for kw in search_keywords)