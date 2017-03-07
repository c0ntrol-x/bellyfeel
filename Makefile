# .DEFAULT_GOAL :=
# .RECIPEPREFIX = "    "

.PHONY: blog static bellyfeel dist tests pip

all: clean provision
run: run-bellyfeel
pip:
	@pip install --disable-pip-version-check --no-cache-dir -U pip
	@pip install --no-cache-dir -r development.txt


tests: unit functional

deploy: clean
	ansible-playbook -i provisioning/inventory provisioning/playbook.yml
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

functional: db
	@nosetests --nologcapture -s --with-coverage --cover-erase --cover-package=bellyfeel --rednose --verbosity=3 tests/functional

online-check:
	@printf "\033[1;30mchecking main website (https)...\033[0m"
	@curl -s https://bellyfeel.io/.check | grep OK >> smoke.log
	@printf "\033[1;32mOK\033[0m\n"

provision: static deploy

clean:
	@rm -f provisioning/*.retry
	@find . -name '*.pyc' -delete
