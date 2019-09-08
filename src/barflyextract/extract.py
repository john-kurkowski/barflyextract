import json
import re
import sys

MEASURE_RE = re.compile(r"\d(oz|ml)")
PARAGRAPHS_RE = re.compile(r"\n{2,}")


def print_markdown(items):
    for item in items:
        print(f"# {item['title']}")
        print()
        print(f"# {item['recipe']}")
        print()


def process(item):
    paras = PARAGRAPHS_RE.split(item["description"])
    recipe_start_i = next(
        (i for i, s in enumerate(paras) if MEASURE_RE.search(s)), None
    )
    if recipe_start_i is None:
        return None

    recipe = "\n\n".join(paras[recipe_start_i:])

    item["recipe"] = recipe
    return item


def run():
    items = filter(bool, [process(item) for item in json.load(sys.stdin)])
    print_markdown(items)


if __name__ == "__main__":
    run()
