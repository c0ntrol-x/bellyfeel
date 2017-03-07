all: dependencies build

dependencies:
	npm install

build: dependencies
	webpack --progress --colors

watch:
	webpack --progress --colors --watch

serve: build
	python servestatic.py
