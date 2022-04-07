"""Unit tests for parsing results retrieved from the API."""

import re
import sys
import textwrap

import pytest

import barflyextract.extract
from barflyextract.extract import RecipePlaylistItem


def test_process_happy_path_item(happy_path_item):
    result = barflyextract.extract.process(happy_path_item)
    assert result
    assert result["title"] != happy_path_item["title"]
    assert result["title"] == "Bobby Burns"
    assert result["description"] == happy_path_item["description"]
    assert (
        result["recipe"]
        == textwrap.dedent(
            """
            2oz (60ml) Scotch Whiskey
            .75oz (22.5ml) Sweet Vermouth
            .25oz (7.5ml) Bènèdictine
            2 Dashes Angostura Bitters
            Lemon Twist
            """
        ).strip()
    )


@pytest.mark.xfail  # TODO: test blocked paragraphs
def test_process_blocked_paragraphs():  # TODO: fixture with blocked paragraphs
    raise NotImplementedError()


def test_process_blocked_item(blocked_item):
    result = barflyextract.extract.process(blocked_item)
    assert not result


def test_process_no_recipe_item(no_recipe_item):
    result = barflyextract.extract.process(no_recipe_item)
    assert not result


def test_process_scraped_items(happy_path_item, blocked_item):
    input_items = [
        happy_path_item,
        blocked_item,
        happy_path_item,
        blocked_item,
        blocked_item,
    ]
    passed, skipped = barflyextract.extract.process_scraped_items(input_items)
    assert skipped == [blocked_item] * 3
    assert [item["title"] for item in passed] == ["Bobby Burns"] * 2


def test_print_markdown(capsys):
    input_items: list[RecipePlaylistItem] = [
        {"title": "One", "description": "doesnt matter", "recipe": "Two"},
        {"title": "Three", "description": "doesnt matter", "recipe": "Four"},
    ]
    barflyextract.extract.print_markdown(sys.stdout, input_items)
    output, _ = capsys.readouterr()
    assert (
        output
        == textwrap.dedent(
            """
            # One

            Two

            # Three

            Four

            """
        ).lstrip()
    )


@pytest.fixture
def happy_path_item():
    return {
        "title": "Master The Classics: Bobby Burns",
        "description": (
            "This cocktail wasn't actually named after Scottish poet Robert Burns (1759"
            " - 1796) that doesn't stop the Scottish from  drinking this cocktail to"
            ' his honor every January 25th during a celebration known as "Burns'
            ' Night". \n\nThis Scotch Based Riff on a Manhattan (basically a Rob Roy'
            " with splash of Benedictine) was first published by Harry Craddock in his"
            " Savoy Cocktail book published in 1930. The drink most definitely predates"
            " Craddock, and it is possible we'll never know it's true origin. But after"
            " Craddock printed it, it definitely became popular as evidenced by it's"
            " inclusion in the books: Old Waldorf Astoria Bar Days published in 1931 by"
            " Albert Stevens Crocket and again by David A. Embury in his 1948 book The"
            " Fine Art Of Mixing Drinks. \n\nHere\u2019s Links to the gear I use in"
            " this episode:\nGraduated Jigger: https://amzn.to/2Op81j6\nBarfly Julep"
            " Strainer: https://amzn.to/2T9KKkN\nBarfly Stirring Spoon:"
            " https://amzn.to/2Oy65VX\nJapanese Bitters Dasher:"
            " https://amzn.to/2OtPzGn\nCocktail Kingdom Mixing Glass:"
            " https://amzn.to/2FiIlRX\nOXO Y Peeler: https://amzn.to/2RY7xQ7\nAngostura"
            " Bitters: https://amzn.to/2J5tqcf\n\nWe are proud that our official apron"
            " sponsor is Stagger Lee Goods. Alfred Ramos hand stitches each of these"
            " amazing quality aprons in his Northern California workshop. He Does"
            " custom work and has aprons for just about every position in a restaurant"
            " and bar so do yourself a favor and check him"
            " out:\nhttps://www.staggerleegoods.com\n\nIf you are interested in helping"
            " us offset the cost of production you should check out our Patreon page"
            " which has a bunch of great perks and goes a long way to helping us bring"
            " you quality content. You can find that"
            " here:\nhttps://www.patreon.com/theeducatedbarfly\n\nHere's The"
            " Specs:\n\n2oz (60ml) Scotch Whiskey\n.75oz (22.5ml) Sweet Vermouth\n.25oz"
            " (7.5ml) B\u00e8n\u00e8dictine\n2 Dashes Angostura Bitters\nLemon Twist"
        ),
    }


@pytest.fixture
def blocked_item(happy_path_item):
    return happy_path_item | {"title": "Tasting Notes: Bobby Burns"}


@pytest.fixture
def no_recipe_item(happy_path_item):
    no_recipe = re.sub(
        r"2oz.*", "", happy_path_item["description"], flags=re.DOTALL | re.MULTILINE
    )
    return happy_path_item | {"description": no_recipe}
