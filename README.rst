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

.. code-block:: sh

    # Your YouTube Data API v3 key here (perhaps from a dotenv)
    export API_KEY=myapikeyhere

    make clean
    make
    open build/recipes.html


Testing
=======

.. code-block:: sh

   python setup.py test



Note
====

This project has been set up using PyScaffold 3.2.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.
