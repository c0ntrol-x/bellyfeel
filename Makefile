# .DEFAULT_GOAL :=
# .RECIPEPREFIX = "    "

.PHONY: blog static bellyfeel dist tests pip

all: clean provision
run: run-bellyfeel
pip:
	@pip install --disable-pip-version-check --no-cache-dir -U pip
	@pip install --no-cache-dir -r development.txt
	@python setup.py develop

tests: unit functional

deploy: clean
	ansible-playbook -vvvv -i provisioning/inventory provisioning/playbook.yml
	make online-check

run-bellyfeel:
	PYTHONPATH=$(PYTHONPATH):$(shell pwd) python bellyfeel/application.py

static: static-bellyfeel
static-bellyfeel: clean
	cd bellyfeel/static && make

vault-edit:
	ansible-vault edit provisioning/bellyfeel-vault.yml

unit:
	@nosetests --nologcapture -s --with-coverage --cover-erase --cover-package=bellyfeel --rednose --verbosity=3 tests/unit

db:
	./scripts/create-db.sh
	bellyfeel create-admin admin@bellyfeel.local

functional: db
	@nosetests --nologcapture -s --with-coverage --cover-erase --cover-package=bellyfeel --rednose --verbosity=3 tests/functional

online-check:
	@./scripts/online-check.sh

provision: static deploy

clean:
	@rm -f provisioning/*.retry
	@find . -name '*.pyc' -delete
