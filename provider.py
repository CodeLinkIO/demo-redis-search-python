from models import SearchQuery, SearchResult
from redis_search import search_articles, suggest_articles


class Provider:
    def search(self, searh_query: SearchQuery) -> SearchResult:
        print(f"Searching articles with query {searh_query}")
        articles = search_articles(searh_query)
        print(f"Found {len(articles)} articles.")
        return SearchResult(
            results=articles,
            count=len(articles),
            has_more=len(articles) == searh_query.limit,
        )

    def suggest(self, query: str) -> list[str]:
        print(f"Suggesting articles with query {query}")
        suggestions = suggest_articles(query)
        print(f"Found {len(suggestions)} suggestions.")
        return suggestions
