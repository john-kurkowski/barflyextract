import json
import logging
import re
import sys
import unidecode
from typing import Any, Iterable, Optional, TextIO, cast

from barflyextract.util import partition

MEASURE_RE = re.compile(r"^\S*\d\s*(oz|ml|g)", re.MULTILINE)
PARAGRAPHS_RE = re.compile(r"\n{2,}")
TYPE_NAME_RE = re.compile(r"(?P<type>.*):\s*(?P<name>.*)")
URL_RE = re.compile(r"\bhttps?://")

Item = dict[str, Any]


def print_markdown(fil: TextIO, items: Iterable[Item]) -> None:
    sorted_items = sorted(items, key=lambda item: unidecode.unidecode(item["title"]))

    for item in sorted_items:
        print(f"# {item['title']}", file=fil)
        print(file=fil)
        print(item["recipe"], file=fil)
        print(file=fil)


def process(item: Item) -> Optional[Item]:
    blocked_types = ("Home Bar", "Tasting")
    is_blocked_type = any(item["title"].startswith(s) for s in blocked_types)
    if is_blocked_type:
        return None

    paras = PARAGRAPHS_RE.split(item["description"])
    maybe_recipe_starts = next(
        ((i, s) for i, s in enumerate(paras) if MEASURE_RE.search(s)), None
    )
    if not maybe_recipe_starts:
        logging.info("""No recipe found in "%s". Skipping.""", item["title"])
        logging.debug(item["description"])
        return None

    def is_blocked_para(para: str) -> bool:
        return bool(URL_RE.search(para))

    recipe_start_i, recipe_start = maybe_recipe_starts
    recipe_remainder = paras[recipe_start_i + 1 :]
    recipe = [recipe_start] + [
        para for para in recipe_remainder if not is_blocked_para(para)
    ]
    logging.debug(
        """Recipe found in "%s" at paragraph %d. Taking it and remaining %d paragraphs.""",
        item["title"],
        recipe_start_i,
        len(recipe) - 1,
    )

    name_match = TYPE_NAME_RE.match(item["title"])
    title = name_match.group("name") if name_match else item["title"]

    item["title"] = title
    item["recipe"] = "\n\n".join(recipe)
    return item


def run() -> None:
    logging.basicConfig(level=logging.INFO)

    with (
        sys.stdin if sys.argv[1] == "-" else open(sys.argv[1], "r", encoding="utf-8")
    ) as fil:
        items, skipped = partition(process(item) for item in json.load(fil))
    items = cast(list[Item], list(items))
    skipped = list(skipped)

    with (sys.stdout if len(sys.argv) <= 2 else open(sys.argv[2], "w")) as outfile:
        print_markdown(outfile, items)

    logging.info(
        """Collected %d recipes. Skipped %d items.""", len(items), len(skipped)
    )


if __name__ == "__main__":
    run()
