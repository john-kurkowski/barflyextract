import json
import logging
import re
import sys

MEASURE_RE = re.compile(r"\d(oz|ml)")
PARAGRAPHS_RE = re.compile(r"\n{2,}")


def print_markdown(items):
    for item in items:
        print(f"# {item['title']}")
        print()
        print(item["recipe"])
        print()


def process(item):
    paras = PARAGRAPHS_RE.split(item["description"])
    recipe_start_i = next(
        (i for i, s in enumerate(paras) if MEASURE_RE.search(s)), None
    )
    if recipe_start_i is None:
        logging.debug("""No recipe found in "%s". Skipping.""", item["title"])
        return None

    logging.debug(
        """Recipe found in "%s" at paragraph %d. Taking it and remaining %d paragraphs.""",
        item["title"],
        recipe_start_i,
        len(paras) - recipe_start_i - 1,
    )
    recipe = "\n\n".join(paras[recipe_start_i:])

    item["recipe"] = recipe
    return item


def run():
    logging.basicConfig(level=logging.DEBUG)

    items = filter(bool, (process(item) for item in json.load(sys.stdin)))
    print_markdown(items)


if __name__ == "__main__":
    run()
