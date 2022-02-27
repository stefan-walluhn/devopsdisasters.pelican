.DEFAULT_GOAL := output

bin/pip:
	python -m venv .
	./bin/python -m pip install --upgrade pip

bin/pelican: bin/pip requirements.txt
	./bin/python -m pip install --requirement requirements.txt

.PHONY: install
install: bin/pelican

.PHONY: output
output: install
	./bin/pelican content -t themes/solid

.PHONY: clean
clean:
	rm -rf output node_modules

.PHONY: mrproper
mrproper: clean
	rm -rf bin include lib lib64
	rm -rf __pycache__

