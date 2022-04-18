=============
barflyextract
=============


Scrape The Educated Barfly's cocktail recipes from its YouTube channel.


Prerequisites
=============

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

1. Enable Google Docs read/write access for `your app
   <https://console.cloud.google.com/apis/dashboard>`_.
1. Download `your app's OAuth 2.0 Client ID
   <https://console.cloud.google.com/apis/credentials>`_ to a
   file ``credentials.json`` in this project's directory.
1. .. code-block:: sh

    make update-db

For more commands and details, see `CONTRIBUTING <./CONTRIBUTING.rst>`_.

Note
====

This project has been set up using PyScaffold 4.2.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.
