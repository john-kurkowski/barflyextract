import json
import logging
import re
import sys

import unidecode

from barflyextract.util import partition

MEASURE_RE = re.compile(r"^\S*\d(oz|ml)")
PARAGRAPHS_RE = re.compile(r"\n{2,}")
TYPE_NAME_RE = re.compile(r"(?P<type>.*):\s*(?P<name>.*)")


def print_markdown(items):
    sorted_items = sorted(items, key=lambda item: unidecode.unidecode(item["title"]))

    for item in sorted_items:
        print(f"# {item['title']}")
        print()
        print(item["recipe"])
        print()


def process(item):
    blocked_types = ("Home Bar", "Tasting")
    is_blocked = any(item["title"].startswith(s) for s in blocked_types)
    if is_blocked:
        return None

    paras = PARAGRAPHS_RE.split(item["description"])
    recipe_start_i = next(
        (i for i, s in enumerate(paras) if MEASURE_RE.search(s)), None
    )
    if recipe_start_i is None:
        # TODO: reduce false negatives
        logging.info("""No recipe found in "%s". Skipping.""", item["title"])
        return None

    logging.debug(
        """Recipe found in "%s" at paragraph %d. Taking it and remaining %d paragraphs.""",
        item["title"],
        recipe_start_i,
        len(paras) - recipe_start_i - 1,
    )
    recipe = "\n\n".join(paras[recipe_start_i:])

    name_match = TYPE_NAME_RE.match(item["title"])
    title = name_match.group("name") if name_match else item["title"]

    item["title"] = title
    item["recipe"] = recipe
    return item


def run():
    logging.basicConfig(level=logging.INFO)

    items, skipped = partition(process(item) for item in json.load(sys.stdin))
    items = list(items)
    skipped = list(skipped)

    print_markdown(items)

    logging.info(
        """Collected %d recipes. Skipped %d items.""", len(items), len(skipped)
    )


if __name__ == "__main__":
    run()
