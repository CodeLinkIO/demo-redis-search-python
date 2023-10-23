import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel, root_validator

_special_chars_re = r"(\'|\"|\.|\,|\;|\<|\>|\{|\}|\[|\]|\"|\'|\=|\~|\*|\:|\#|\+|\^|\$|\@|\%|\!|\&|\)|\(|/|\-|\\)"


class SortBy(str, Enum):
    date = "date"
    relevance = "relevance"


class Order(str, Enum):
    asc = "asc"
    desc = "desc"


class Article(BaseModel):
    id: str
    title: str
    url: str
    category: str
    description: str
    date: str
    authors: str


class SearchQuery(BaseModel):
    query: str
    offset: Optional[int] = 0
    limit: Optional[int] = 10
    sort_by: Optional[SortBy] = SortBy.relevance
    order: Optional[Order] = Order.desc
    categories: Optional[list[str]] = None

    @root_validator(pre=True)
    def validate_query(cls, values):
        def _remove_special_chars(query: str) -> str:
            query = query.strip()
            while "  " in query:
                query = query.replace("  ", " ")
            return re.sub(_special_chars_re, "", query)

        if "query" not in values:
            raise ValueError("Query is required")
        values["query"] = _remove_special_chars(values["query"])
        if "limit" in values and 20 > int(values["limit"]) < 0:
            raise ValueError("Limit must be between 1 and 20")
        if "offset" in values and int(values["offset"]) < 0:
            raise ValueError("Offset must be greater than 0")
        if "categories" in values and values["categories"] is not None:
            values["categories"] = [
                _remove_special_chars(category) for category in values["categories"].split(",")
            ]
        return values

    def get_caterogy_filter(self):
        if self.categories is None or len(self.categories) == 0:
            return ""
        categories = " | ".join(self.categories)
        return f"@category:{categories}"

    def build_term(self):
        fuzzy_sign = ["%", "%%", "%%%"]
        fuzzy_terms = [self.query]
        for i in range(0, 1):
            fuzzy_words = [
                f"{fuzzy_sign[i]}{word}{fuzzy_sign[i]}"
                for word in self.query.split(" ")
            ]
            fuzzy_term = " ".join(fuzzy_words)
            fuzzy_terms.append(fuzzy_term)
        fuzzy_term = " | ".join(fuzzy_terms)
        fuzzy_term = f"{fuzzy_term} {self.get_caterogy_filter()}"
        fuzzy_term = fuzzy_term.strip()
        return fuzzy_term


class SearchResult(BaseModel):
    count: int
    results: list[Article]
    has_more: bool
