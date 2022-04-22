DIRS=build
$(info $(shell mkdir -p $(DIRS)))

all: build/recipes.html

clean:
	rm -rf build/

build/playlist.json:
	python src/barflyextract/api.py $@.tmp
	mv $@.tmp $@

build/recipes.html: build/recipes.md
	pandoc --from markdown+hard_line_breaks --to html --output $@.tmp $<
	mv $@.tmp $@

build/recipes.md: build/playlist.json
	python src/barflyextract/extract.py $< $@.tmp
	mv $@.tmp $@
