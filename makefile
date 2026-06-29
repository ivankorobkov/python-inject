SHELL               :=	bash
.DELETE_ON_ERROR:
.SHELLFLAGS         :=	-ceu
MAKEFLAGS           +=	--no-builtin-rules \
                        --warn-undefined-variables

.PHONY: init dist upload clean pytest test

init:
	uv sync

dist:
	uv build

upload:
	uv publish

clean:
	rm -rf ./build/*
	rm -rf ./dist/*
	rm -rf ./.mypy_cache
	rm -rf ./.pytest_cache

pytest:
	uv run pytest tests

test:
	uv run --with nose nosetests tests
