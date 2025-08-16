SHELL               :=	bash
.DELETE_ON_ERROR:
.SHELLFLAGS         :=	-ceu
MAKEFLAGS           +=	--no-builtin-rules \
                        --warn-undefined-variables

.PHONY: dist pytest test

dist:
	if ! python3 -m pip freeze | grep -q build; then python3 -m pip install --upgrade build; fi
	python3 -m build --outdir=dist --sdist --wheel ./

install_dev:
	python3 -m pip install --upgrade pip
	python3 -m pip install --upgrade --editable=./

upload:
	if ! python3 -m pip freeze | grep -q twine; then python3 -m pip install --upgrade twine; fi
	python3 -m twine upload dist/*

clean:
	rm -rf ./build/*
	rm -rf ./dist/*
	rm -rf ./.mypy_cache
	rm -rf ./.pytest_cache

pytest:
	if ! command -v pytest &>/dev/null; then python3 -m pip install --upgrade pytest; fi
	pytest tests

test:
	if ! command -v nosetests &>/dev/null; then python3 -m pip install --upgrade nose; fi
	nosetests tests
