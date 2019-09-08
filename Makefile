clean:
	rm playlist.json recipes.md

playlist.json:
	python src/barflyextract/api.py > playlist.json

recipes.md: playlist.json
	python src/barflyextract/extract.py < playlist.json > recipes.md
