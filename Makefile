.DEFAULT_GOAL := static

bin/pip:
	python -m venv .
	./bin/python -m pip install --upgrade pip

bin/pelican: bin/pip requirements.txt
	./bin/python -m pip install --requirement requirements.txt

.PHONY: install
install: bin/pelican

.PHONY: static
static: install
	./bin/pelican content -t themes/solid

.PHONY: deploy
deploy: clean static
	rsync -av --delete -e ssh output www.devopsdisasters.net:/srv/www/net.devopsdisasters.www/

.PHONY: clean
clean:
	rm -rf output node_modules

.PHONY: mrproper
mrproper: clean
	rm -rf bin include lib lib64
	rm -rf __pycache__

