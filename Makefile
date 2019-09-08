clean:
	rm playlist.json

playlist.json:
	python src/barflyextract/api.py > playlist.json
