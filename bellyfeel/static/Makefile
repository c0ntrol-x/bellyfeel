all: dist

build:
	@npm install

dist: build
	@mkdir -p dist/{css,js,fonts,img,swatch}
	@rsync -putavoz node_modules/bootstrap/dist/ dist/
	@rsync -putavoz node_modules/quill/dist/ dist/quill/
	@rsync -putavoz node_modules/quill/themes/ dist/quill/themes/
	@rsync -putavoz node_modules/quill/modules/ dist/quill/modules/
	@rsync -putavoz node_modules/font-awesome/ dist/
	@rsync -putavoz node_modules/highlight.js/ dist/
	@cp -v node_modules/marked/marked.min.js dist/js/
	@cp -v node_modules/vue/dist/vue.min.js dist/js/
	@cp -v node_modules/jquery/dist/jquery* dist/js/
	@cp -v node_modules/underscore/underscore* dist/js/
	@cp -rfv node_modules/bootswatch/{paper,cosmo,yeti} dist/swatch/

.PHONY: dist
