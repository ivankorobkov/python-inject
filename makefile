SHELL               :=	bash
.DELETE_ON_ERROR:
.SHELLFLAGS         :=	-ceu
MAKEFLAGS           +=	--no-builtin-rules \
                        --warn-undefined-variables

.PHONY: init dist upload clean pytest

init:
	uv sync

dist:
	uv build

upload:
	uv publish

clean:
	rm -rf ./dist/*
	rm -rf ./.mypy_cache
	rm -rf ./.pytest_cache
	rm -rf ./.ruff_cache
	rm -rf ./.tox
	rm -rf ./.uv-cache

pytest:
	uv run pytest tests
