=============
barflyextract
=============


Scrape The Educated Barfly's cocktail recipes from its YouTube channel.


Prerequisites
=============

- ``cargo``
- ``just``
- ``pandoc``
- ``python``


Install
=======

.. code-block:: sh

    just bootstrap


Usage
=====

Scrape the latest data to a file
--------------------------------

.. code-block:: sh

    # Your YouTube Data API v3 key here (perhaps from a dotenv)
    export API_KEY=myapikeyhere

    just
    open build/recipes.html


Update the database
-------------------

1. Enable Google Drive API access for `your app
   <https://console.cloud.google.com/apis/dashboard>`_.
1. Download `your app's OAuth 2.0 Client ID
   <https://console.cloud.google.com/apis/credentials>`_ to a
   file ``credentials.json`` in this project's directory.
1. .. code-block:: sh

    just update-db

Contribute
==========

Tests
-----

Run all tests, lints, and typechecks with the following command.

.. code-block:: sh

    just test

For individual checks, you can run ``just lint``, ``just typecheck``, or
``just pytest``.

Disclaimer
==========

This is an unofficial tool for extracting publicly available YouTube data and
is not affiliated with or endorsed by The Educated Barfly, YouTube, or Google.
Content remains owned by its creators. Use only in compliance with applicable
laws and service terms. You provide your own API credentials and assume all
usage costs.
