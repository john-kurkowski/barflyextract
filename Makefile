DIRS=build
$(info $(shell mkdir -p $(DIRS)))

clean:
	rm -rf build/

build/playlist.json:
	python src/barflyextract/api.py > build/playlist.json

build/recipes.md: build/playlist.json
	python src/barflyextract/extract.py < build/playlist.json > build/recipes.md
