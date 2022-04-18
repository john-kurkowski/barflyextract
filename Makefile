DIRS=build
$(info $(shell mkdir -p $(DIRS)))

.PHONY: all
all: build/recipes.html

.PHONY: clean
clean:
	rm -rf build/

build/playlist.json:
	python src/barflyextract/datasource.py $@.tmp
	mv $@.tmp $@

build/recipes.html: build/recipes.md
	pandoc --from markdown+hard_line_breaks --to html --output $@.tmp $<
	mv $@.tmp $@

build/recipes.md: build/playlist.json
	python src/barflyextract/extract.py $< $@.tmp
	mv $@.tmp $@

.PHONY: update-db
update-db: build/recipes.html
	python src/barflyextract/db.py $<
