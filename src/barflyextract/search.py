"""Search for recipes."""

import dataclasses
import sys
from collections.abc import Iterator

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag


@dataclasses.dataclass(kw_only=True)
class SearchResult:
    """A recipe matched during search.

    Reconstituted from this project's generated HTML of recipes.
    """

    title: str
    recipe: str


def _extract_title(recipe: Tag) -> str:
    title = ""
    previous_sibling = recipe.previous_sibling
    while previous_sibling and not title:
        if isinstance(previous_sibling, Tag):
            title = previous_sibling.get_text(strip=True)
        elif isinstance(previous_sibling, NavigableString):
            title = str(previous_sibling).strip()
        previous_sibling = previous_sibling.previous_sibling
    return title


def search(recipe_html: str, *query: str) -> Iterator[SearchResult]:
    """Search the given recipe HTML for recipes containing all tokens in the given query."""
    soup = BeautifulSoup(recipe_html, "html.parser")
    for recipe in soup.find_all("ul"):
        if not isinstance(recipe, Tag):
            continue
        title = _extract_title(recipe)
        recipe_text = recipe.get_text(separator="\n", strip=True)
        haystack = f"{title}\n{recipe_text}".lower()
        if all(token.lower() in haystack for token in query):
            yield SearchResult(title=title, recipe=recipe_text.strip())


def main() -> None:
    """Search for recipes."""
    if len(sys.argv) < 3:
        print("Usage: search.py <recipe_html> <query...>", file=sys.stderr)
        raise SystemExit(2)
    recipe_db_filename = sys.argv[1]
    query_tokens = sys.argv[2:]
    with open(recipe_db_filename, encoding="utf-8") as fil:
        html = fil.read()

    hits = search(html, *query_tokens)

    for hit in hits:
        print(hit.title)
        print(hit.recipe)
        print()


if __name__ == "__main__":
    main()
