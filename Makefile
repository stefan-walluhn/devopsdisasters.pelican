.DEFAULT_GOAL := publish

bin/pip:
	python -m venv .
	./bin/python -m pip install --upgrade pip

bin/pelican: bin/pip requirements.txt
	./bin/python -m pip install --requirement requirements.txt

.PHONY: install
install: bin/pelican

.PHONY: publish
publish: install
	./bin/pelican --theme-path themes/solid --settings publishconf.py --output htdocs

.PHONY: deploy
deploy: publish
	rsync -av --delete -e ssh htdocs www.devopsdisasters.net:/srv/www/net.devopsdisasters.www/

.PHONY: clean
clean:
	rm -rf output node_modules

.PHONY: mrproper
mrproper: clean
	rm -rf bin include lib lib64
	rm -rf __pycache__

