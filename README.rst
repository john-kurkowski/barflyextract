=============
barflyextract
=============


Scrape The Educated Barfly's cocktail recipes from its YouTube channel.


Prerequisites
=============

- ``cargo``
- ``pandoc``
- ``python``


Install
=======

.. code-block:: sh

    pip install --editable .


Usage
=====

Scrape the latest data to a file
--------------------------------

.. code-block:: sh

    # Your YouTube Data API v3 key here (perhaps from a dotenv)
    export API_KEY=myapikeyhere

    make
    open build/recipes.html


Update the database
-------------------

1. Enable Google Drive API access for `your app
   <https://console.cloud.google.com/apis/dashboard>`_.
1. Download `your app's OAuth 2.0 Client ID
   <https://console.cloud.google.com/apis/credentials>`_ to a
   file ``credentials.json`` in this project's directory.
1. .. code-block:: sh

    make update-db

Contribute
==========

Install for local development:

.. code-block:: sh

    pip install --editable '.[testing]'
    pre-commit install

Tests
-----

Run all tests, lints, and typechecks with the following command.

.. code-block:: sh

    tox --parallel

See tox.ini for individual commands used. For convenience, you should be able
to run them directly without a ton of arguments, e.g. ``pytest``.
