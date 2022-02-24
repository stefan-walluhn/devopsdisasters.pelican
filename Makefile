.DEFAULT_GOAL := output

bin/pip:
	python -m venv .

bin/pelican: bin/pip requirements.txt
	./bin/pip install --requirement requirements.txt

.PHONY: output
output: bin/pelican
	./bin/pelican content

.PHONY: clean
clean:
	rm -rf output node_modules

.PHONY: mrproper
mrproper: clean
	rm -rf bin include lib lib64
	rm -rf __pycache__

