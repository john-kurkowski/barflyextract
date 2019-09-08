import json
import logging
import re
import sys

import unidecode

from barflyextract.util import partition

MEASURE_RE = re.compile(r"^\S*\d\s*(oz|ml)", re.MULTILINE)
PARAGRAPHS_RE = re.compile(r"\n{2,}")
TYPE_NAME_RE = re.compile(r"(?P<type>.*):\s*(?P<name>.*)")
URL_RE = re.compile(r"\bhttps?://")


def print_markdown(items):
    sorted_items = sorted(items, key=lambda item: unidecode.unidecode(item["title"]))

    for item in sorted_items:
        print(f"# {item['title']}")
        print()
        print(item["recipe"])
        print()


def process(item):
    blocked_types = ("Home Bar", "Tasting")
    is_blocked_type = any(item["title"].startswith(s) for s in blocked_types)
    if is_blocked_type:
        return None

    paras = PARAGRAPHS_RE.split(item["description"])
    recipe_start_i, recipe_start = next(
        ((i, s) for i, s in enumerate(paras) if MEASURE_RE.search(s)), (None, None)
    )
    if recipe_start_i is None:
        logging.info("""No recipe found in "%s". Skipping.""", item["title"])
        logging.debug(item["description"])
        return None

    def is_blocked_para(para):
        return URL_RE.search(para)

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


def run():
    logging.basicConfig(level=logging.INFO)

    with sys.stdin if sys.argv[1] == "-" else open(sys.argv[1], "r") as fil:
        items, skipped = partition(process(item) for item in json.load(fil))
    items = list(items)
    skipped = list(skipped)

    print_markdown(items)

    logging.info(
        """Collected %d recipes. Skipped %d items.""", len(items), len(skipped)
    )


if __name__ == "__main__":
    run()
