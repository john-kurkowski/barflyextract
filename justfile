default: html

clean:
  rm -rf build/

playlist: _build
  {{ if path_exists('build/playlist.json') == "false" { 'python src/barflyextract/datasource.py build/playlist.json' } else { "" } }}

html: md
  pandoc --from markdown+hard_line_breaks --to html --output build/recipes.html build/recipes.md

md: playlist
  python src/barflyextract/extract.py build/playlist.json build/recipes.md

update-db: html
  python src/barflyextract/db.py build/recipes.html

@_build:
  mkdir -p build
