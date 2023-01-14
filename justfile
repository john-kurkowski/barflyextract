default: html

clean:
  rm -rf build/

# Scrape relevant video metadata from YouTube
playlist: _build
  {{ if path_exists('build/playlist.json') == "false" { 'python src/barflyextract/datasource.py build/playlist.json' } else { "" } }}

# Generate HTML recipe list
html: md
  pandoc --from markdown+hard_line_breaks --to html --output build/recipes.html build/recipes.md

# Generate Markdown recipe list
md: playlist
  python src/barflyextract/extract.py build/playlist.json build/recipes.md

# Update central database of recipes
update-db: html
  python src/barflyextract/db.py build/recipes.html

# Test recipes

test:
  tox --parallel

# Private recipes

@_build:
  mkdir -p build
