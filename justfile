# Generate HTML recipe list
default: generate-html

clean:
  rm -rf build/

# Scrape relevant video metadata from YouTube
generate-playlist: _scaffold_build_dir
  {{ if path_exists('build/playlist.json') == "false" { 'python src/barflyextract/datasource.py build/playlist.json' } else { "" } }}

# Generate HTML recipe list
generate-html: generate-md
  pandoc --from markdown+hard_line_breaks --to html --output build/recipes.html build/recipes.md

# Generate Markdown recipe list
generate-md: generate-playlist
  python src/barflyextract/extract.py build/playlist.json build/recipes.md

# Update central database of recipes
update-db: generate-html
  python src/barflyextract/db.py build/recipes.html

# Test recipes

test:
  tox --parallel

# Private recipes

@_scaffold_build_dir:
  mkdir -p build
