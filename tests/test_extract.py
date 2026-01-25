"""Unit tests for parsing results retrieved from the API."""

import re
import sys

import pytest
import syrupy

import barflyextract.extract
from barflyextract.datasource import PlaylistItem
from barflyextract.extract import RecipePlaylistItem


def test_process_happy_path_item(
    happy_path_item: PlaylistItem, snapshot: syrupy.assertion.SnapshotAssertion
) -> None:
    """Test that a happy path item is processed correctly."""
    result = barflyextract.extract.process(happy_path_item)
    assert result
    assert result["title"] != happy_path_item["title"]
    assert result == snapshot


def test_process_multi_recipe_item(
    multi_recipe_item: PlaylistItem, snapshot: syrupy.assertion.SnapshotAssertion
) -> None:
    """Test that an item with multiple recipes is correctly processed."""
    result = barflyextract.extract.process(multi_recipe_item)
    assert result
    assert result["description"] == multi_recipe_item["description"]
    assert result == snapshot


def test_process_recipe_label_title() -> None:
    """Ensure recipe titles skip the literal 'Recipe' label."""
    item: PlaylistItem = {
        "title": "Something: Margarita Negra",
        "description": (
            "Intro text.\n\nRecipe\nMargarita Negra\n1oz (30ml) Tequila Blanco\n"
            "1oz (30ml) Mr Black Coffee Liqueur\n1oz (30ml) Lime Juice\n"
            ".5oz (15ml) Agave\n2 Lime Wheel Garnish"
        ),
    }
    result = barflyextract.extract.process(item)
    assert result
    assert "## Margarita Negra" in result["recipe"]
    assert "## Recipe" not in result["recipe"]
    assert "* Margarita Negra" not in result["recipe"]


def test_process_repeated_recipe_labels() -> None:
    """Ensure repeated recipe labels are removed before title detection."""
    item: PlaylistItem = {
        "title": "Amaretto Bitter",
        "description": (
            "Intro text.\n\nRecipe\nRecipe\nAmaretto Bitter\n1oz (30ml) Lemon Juice\n"
            "1 Tsp Rich Simple Syrup (2:1)\n1 1/2oz (45ml) Amaretto\n"
            "3/4oz (22ml) Jamaica Rum Overproof\n1/4oz (7.5ml) Aperol\n"
            "1 Egg White\nAmaretti Cookie Garnish"
        ),
    }
    result = barflyextract.extract.process(item)
    assert result
    assert "## Amaretto Bitter" in result["recipe"]
    assert "## Recipe" not in result["recipe"]


def test_process_measurement_title_detection() -> None:
    """Ensure measurement-first lines are not treated as titles."""
    item: PlaylistItem = {
        "title": "The Scofflaw",
        "description": (
            "Intro text.\n\nRecipe\nThe Scofflaw\n1 1/2oz (45ml) Rye whiskey\n"
            "3/4oz (22ml) Dry Vermouth\n3/4oz (22ml) Lemon Juice\n"
            "1/2oz (15ml) Grenadine\n2 Dashes Orange Bitters\nLemon Twist"
        ),
    }
    result = barflyextract.extract.process(item)
    assert result
    assert "## 1 1/2oz" not in result["recipe"]
    assert "* 1 1/2oz (45ml) Rye whiskey" in result["recipe"]


@pytest.mark.xfail  # TODO: test blocked paragraphs
def test_process_blocked_paragraphs() -> None:  # TODO: fixture with blocked paragraphs
    """TODO."""
    raise NotImplementedError()


def test_process_blocked_item(blocked_item: PlaylistItem) -> None:
    """Test that a blocked item is not processed."""
    result = barflyextract.extract.process(blocked_item)
    assert not result


def test_blocked_line_item(blocked_line_item: PlaylistItem) -> None:
    """Test that an item with blocked lines is successfully processed."""
    result = barflyextract.extract.process(blocked_line_item)
    assert result


def test_process_no_recipe_item(no_recipe_item: PlaylistItem) -> None:
    """Test that an item with no recipe is not processed."""
    result = barflyextract.extract.process(no_recipe_item)
    assert not result


def test_process_scraped_items(
    happy_path_item: PlaylistItem, blocked_item: PlaylistItem
) -> None:
    """Test that scraped items are correctly split into passed and skipped."""
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


def test_print_markdown(
    capsys: pytest.CaptureFixture[str], snapshot: syrupy.assertion.SnapshotAssertion
) -> None:
    """Test that a list of RecipePlaylistItems is correctly printed."""
    input_items: list[RecipePlaylistItem] = [
        {"title": "One", "description": "doesnt matter", "recipe": "Two"},
        {"title": "Three", "description": "doesnt matter", "recipe": "Four"},
    ]
    barflyextract.extract.print_markdown(sys.stdout, input_items)
    output, _ = capsys.readouterr()
    assert output == snapshot


def test_print_markdown_dedupes(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test that duplicate recipes are only printed once."""
    input_items: list[RecipePlaylistItem] = [
        {"title": "One", "description": "doesnt matter", "recipe": "Two"},
        {"title": "One", "description": "doesnt matter", "recipe": "Two"},
    ]
    barflyextract.extract.print_markdown(sys.stdout, input_items)
    output, _ = capsys.readouterr()
    assert output.count("# One") == 1


def test_print_markdown_dedupes_shared_blocks(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test that duplicate recipe blocks are removed across different items."""
    input_items: list[RecipePlaylistItem] = [
        {
            "title": "Video A",
            "description": "doesnt matter",
            "recipe": "## Hightail Out\n\n* Gin\n\n## Other\n\n* Vodka",
        },
        {
            "title": "Hightail Out",
            "description": "doesnt matter",
            "recipe": "## Hightail Out\n\n* Gin",
        },
    ]
    barflyextract.extract.print_markdown(sys.stdout, input_items)
    output, _ = capsys.readouterr()
    assert output.count("## Hightail Out") == 1
    assert "## Other" in output


@pytest.fixture
def happy_path_item() -> PlaylistItem:
    """Return a typical playlist item with a recipe."""
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
def multi_recipe_item() -> PlaylistItem:
    """Return a typical playlist item with multiple recipe."""
    return {
        "title": "Celebrating National Applejack Month with 5 Cocktails!",
        "description": (
            "Not only is it officially fall but October is National Applejack Month and"
            " we decided to celebrate with five distinctive cocktails to help you ring"
            " in the Holiday Season!\n\nApplejack, in short, is American Apple Brandy"
            " and it is the first American Distilled Spirit. Some may argue that we"
            " were distilling Rum beforehand, but I would argue back that Rum is a"
            " product of the Caribbean  and therefore not an American Product. The term"
            " Applejack comes from the Colonial method of making Apple Brandy called"
            " Jacking, the process of freeze fermenting cider then removing the ice and"
            " increasing alcohol content. The Story of Applejack and the story of the"
            " Laird's family are intertwined (you'll notice I'm using Laird's Bonded"
            " Applejack). Since 1698 something like 12 generations of the Lairds family"
            " have been making Applejack in Monmouth County New Jersey (hence it's"
            " nickname Jersey Lightning). The first Laird, William landed in New Jersey"
            " from Scotland and was believed to be a distiller by trade, when he looked"
            " around at available product to distill he landed on apples which were"
            " plentiful in the region. The weather and soil wasn't hospitable to Rye,"
            " Corn or Barley and Whiskey had not yet begun pouring through the"
            " Cumberland Gap, so Apple Cider and then Applejack it was! Today Laird's &"
            " Co. is the oldest licensed distillery in the United States and it is"
            " still family Run.\n\nHere's  Links to the tools I use in this"
            " episode:\nBarfly Shaking Set (Gold):\u00a0https://amzn.to/2WAhHIg\nBarfly"
            " Copper Measuring Cup:\u00a0https://amzn.to/2BA24Yk\nBarfly Hawthorn"
            " Strainer:\u00a0https://amzn.to/2OkFZ8v\nBarfly Fine"
            " Strainer:\u00a0https://amzn.to/2X44wD8\n\nIf you like our channel, please"
            " click and subscribe\nhttps://tinyurl.com/SubBarfly\n\nIf you guys want to"
            " check out our full amazon store you can do so here:"
            " https://www.amazon.com/shop/theeducatedbarfly\n\nWe are happy to announce"
            " that we are officially sponsored by Barfly Mixology Gear. Barfly makes"
            " very high quality professional bar equipment. Their barware essentials"
            " and accessories are designed to deliver optimal appearance, temperature"
            " consistency and proportion in every glass so you can achieve masterful"
            " results. Definitely check them out at:"
            " https://www.barflybymercer.com/home/\n\nWe are proud that our official"
            " apron sponsor is Stagger Lee Goods. Alfred Ramos hand stitches each of"
            " these amazing quality aprons in his Northern California workshop. He Does"
            " custom work and has aprons for just about every position in a restaurant"
            " and bar so do yourself a favor and check him"
            " out:\nhttps://www.staggerleegoods.com\n\nWe have a discount code with"
            " Stagger Lee right now for 20% off your order just type: BARFLYSLG20 at"
            " check out.\n\nIf you are interested in helping us offset the cost of"
            " production you should check out our Patreon page which has a bunch of"
            " great perks and goes a long way to helping us bring you quality content."
            " You can find that"
            " here:\nhttps://www.patreon.com/theeducatedbarfly\n\nInstagram:"
            " https://www.instagram.com/theeducatedbarfly\nFacebook:"
            " https://www.facebook.com/theeducatedbarfly\nFor T-Shirts:"
            " https://teespring.com/stores/the-educated-barfly\n\nHere's The Specs For"
            " Each Drink:\n Pall Mall\n1oz (30ml)  Applejack\n1oz (30ml) Rye\n.75oz"
            " (22.5ml) Lemon\n.75oz (22.5ml) Grenadine\n2 Orange Slices\n2 dashes"
            " Angostura Bitters\nNo Garnish\n\nAutumn in Jersey\n2oz (60ml)"
            " Applejack\n.75oz (22.5ml) Lemon\n.75oz (22.5ml) Orgeat\n2 Dashes"
            " Angostura Bitters\nMint Sprig Garnish\n\nBlack Mamba\n1oz (30ml) Gin\n1oz"
            " Mulled Wine Syrup\n.5oz (15ml) Applejack\n.75oz (22.5ml) Lemon"
            " Juice\n.25oz Fernet Branca\n\nFor Mulled Wine Syrup combine .5 Cups House"
            " Mulling Spices ( Mix Allspice berries, Cardamom pods, Cinnamon Sticks,"
            " Clove, dried orange peel, dried lemon peel and Corriander Seed) with 1"
            " cup Demerara Sugar and 1 Cup Rich wine such as Merlot or Cabernet. Simmer"
            " for ten minutes until reduces slightly, cool and strain our solids. Keeps"
            " 2 weeks).\n\nLegends Of The Fall\n1.5oz (45ml) Applejack\n.5oz (15ml) Rye"
            " Whiskey\n1 Heavy Barspoon Falernum\n1 Dash Allspice Dram\nOn Rocks,"
            " Orange and Lemon Twist\n\nGarden State Julep\n2oz (60ml) Applejack\n.75oz"
            " (22.5ml) Lemon Sherbet\n3oz (90ml) Dry Ros\u00e9\nPinch Of Mint\nPinch"
            " Sea Salt\nGarnish Mint Sprig/Red Berries/Lemon Wheel\n\nTo make Lemon"
            " Sherbet coat the peels of 4 Lemons in .5 cups sugar, muddle Peels to"
            " release oils and let sit at least 3 hours but preferably overnight. Then"
            " add 12oz of Lemon Juice. Heat gently in a  pot and stir slowly (DO NOT"
            " SIMMER OR BRING TO BOIL) once sugar is fully dissolved, remove from heat,"
            " allow to cool and strain out solids. Resulting syrup lasts 2 to 3 weeks"
            " in the refrigerator."
        ),
    }


@pytest.fixture
def blocked_line_item() -> PlaylistItem:
    """Return a typical playlist item with blocked lines."""
    return {
        "title": "Tiki Cocktail: Three Dots and a Dash",
        "description": (
            'This cocktail was created by the legendary father of all Tiki Donn "The'
            ' Beachcomber" Beach during WWII. The name is in reference to the morse'
            " code call sign for Victory. There's really not much to it than that."
            " Enjoy!\n\nHere's Links to the tools I'm using:\n\n12oz Bar Ice Scoop:"
            " https://amzn.to/2PfUkiR\nBarfly Graduated Jigger:"
            " https://amzn.to/2r3slt2\nJapanese Bitters Dasher:"
            " https://amzn.to/2OtPzGn\nAngostura Bitters:"
            " https://amzn.to/2J5tqcf\nLuxardo Cherries:"
            " https://amzn.to/2SUzZ60\nVitaMix Blender: https://amzn.to/2rjc3wl\n\nWe"
            " are proud that our official apron sponsor is Stagger Lee Goods. Alfred"
            " Ramos hand stitches each of these amazing quality aprons in his Northern"
            " California workshop. He Does custom work and has aprons for just about"
            " every position in a restaurant and bar so do yourself a favor and check"
            " him out:\nhttps://www.staggerleegoods.com\n\nIf you are interested in"
            " helping us offset the cost of production you should check out our Patreon"
            " page which has a bunch of great perks and goes a long way to helping us"
            " bring you quality content. You can find that"
            " here:\nhttps://www.patreon.com/theeducatedbarfly\n\nHere's The"
            " Specs:\n\n1.5oz (45ml) Martinique Rum\n.5oz (15ml) Demerara Rum\n.25oz"
            " (7.5ml) Pimento Dram\n.25oz (7.5ml) Velvet Falernum\n.5oz (15ml) Lime"
            " Juice\n.5oz (15ml) Honey Syrup\n.5oz (15ml) Orange Juice\n2 Dashes"
            " Angostura Bitters\n3 Luxardo Cherries & Pineapple Cube Garnish"
        ),
    }


@pytest.fixture
def blocked_item(happy_path_item: PlaylistItem) -> PlaylistItem:
    """Return a playlist item that should not successfully process, although it contains a recipe."""
    copy = happy_path_item.copy()
    copy["title"] = "Tasting Notes: Bobby Burns"
    return copy


@pytest.fixture
def no_recipe_item(happy_path_item: PlaylistItem) -> PlaylistItem:
    """Return a playlist item that should not successfully process, because it contains no recipe."""
    no_recipe = re.sub(
        r"2oz.*", "", happy_path_item["description"], flags=re.DOTALL | re.MULTILINE
    )
    copy = happy_path_item.copy()
    copy["description"] = no_recipe
    return copy
