"""Functions to extract recipes from text, usually author-provided video descriptions."""

import json
import logging
import re
import sys
from collections.abc import Iterable
from contextlib import AbstractContextManager, nullcontext
from typing import TextIO

import unidecode

from barflyextract.datasource import PlaylistItem

IGNORED_LINE_RE = re.compile(r"(here.*spec)", re.IGNORECASE)
MEASURE_RE = re.compile(r"^\S*\d\s*(oz|ml|g)", re.MULTILINE)
PARAGRAPHS_RE = re.compile(r"\n{2,}")
TYPE_NAME_RE = re.compile(r"(?P<type>.*):\s*(?P<name>.*)")
URL_RE = re.compile(r"\bhttps?://")


class RecipePlaylistItem(PlaylistItem):
    """A PlaylistItem that also contains an extracted recipe."""

    recipe: str


def print_markdown(fil: TextIO, items: Iterable[RecipePlaylistItem]) -> None:
    """Emit the given recipes as Markdown to the given file-like object."""
    sorted_items = sorted(items, key=lambda item: unidecode.unidecode(item["title"]))

    for item in sorted_items:
        print(f"# {item['title']}", file=fil)
        print(file=fil)
        print(item["recipe"], file=fil)
        print(file=fil)


def process(item: PlaylistItem) -> RecipePlaylistItem | None:
    """Extract a recipe from the given PlaylistItem.

    Returns None if it doesn't contain a recipe.
    """
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

    def is_blocked_line(line: str) -> bool:
        return bool(IGNORED_LINE_RE.search(line))

    def is_blocked_para(para: str) -> bool:
        return bool(URL_RE.search(para))

    def format_para(para: str) -> str:
        lines = [
            stripped
            for line in para.splitlines()
            if (stripped := line.strip()) and stripped and not is_blocked_line(stripped)
        ]

        if not lines:
            return ""

        word_count = len(lines[0].split())
        is_description = word_count > 10
        is_measurement = MEASURE_RE.search(lines[0])
        is_title = not is_description and not is_measurement

        if is_title:
            lines[0] = "## " + lines[0] + "\n"
        elif not is_description and is_measurement:
            lines[0] = "* " + lines[0]
        else:
            pass
        formatted_lines = [lines[0]] + ["* " + line for line in lines[1:]]

        return "\n".join(formatted_lines)

    recipe_start_i, recipe_start = maybe_recipe_starts
    recipe_remainder = paras[recipe_start_i + 1 :]
    recipe = [format_para(recipe_start)] + [
        format_para(para) for para in recipe_remainder if not is_blocked_para(para)
    ]
    logging.debug(
        """Recipe found in "%s" at paragraph %d. Taking it and remaining %d paragraphs.""",
        item["title"],
        recipe_start_i,
        len(recipe) - 1,
    )

    name_match = TYPE_NAME_RE.match(item["title"])
    title = name_match.group("name") if name_match else item["title"]

    return {
        "description": item["description"],
        "recipe": "\n\n".join(recipe),
        "title": title,
    }


def process_scraped_items(
    input_items: Iterable[PlaylistItem],
) -> tuple[list[RecipePlaylistItem], list[PlaylistItem]]:
    """Split the given PlaylistItems into ones with a recipe and ones without."""
    items: list[RecipePlaylistItem] = []
    skipped: list[PlaylistItem] = []
    for item in input_items:
        processed = process(item)
        if processed:
            items.append(processed)
        else:
            skipped.append(item)

    return (items, skipped)


def run() -> None:
    """Extract recipes from the given JSON file of PlaylistItems."""
    logging.basicConfig(level=logging.INFO)

    with (
        sys.stdin if sys.argv[1] == "-" else open(sys.argv[1], encoding="utf-8")
    ) as fil:
        items, skipped = process_scraped_items(json.load(fil))

    cm: TextIO | AbstractContextManager[TextIO] = (
        nullcontext(sys.stdout) if len(sys.argv) <= 2 else open(sys.argv[2], "w")
    )
    with cm as outfile:
        print_markdown(outfile, items)

    logging.info(
        """Collected %d recipes. Skipped %d items.""", len(items), len(skipped)
    )


if __name__ == "__main__":
    run()
