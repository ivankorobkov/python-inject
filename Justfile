set shell := ["bash", "-euc"]

python_oldest := "3.10" # Oldest supported version
python_latest := "3.14" # Newest supported version
python := "3.14" # Default version for dev loop
python_versions := "3.10 3.11 3.12 3.13 3.14"

taplo := "uvx taplo@0.9.3"

@_default:
    just --list --unsorted

fmt:
    uv run --only-group ruff ruff format .
    uv run --only-group ruff ruff check --fix --show-fixes .
    {{ taplo }} format
    just --fmt

# Dev loop
dev: fmt lint test

# Full check
check: lock-check lint lint-toml lint-yaml public-typing typing test-all

# Install locked dependencies
[group('project')]
init:
    uv sync

[group('project')]
dist:
    uv build

[group('project')]
publish:
    uv publish

[group('project')]
clean:
    rm -rf dist .mypy_cache .pytest_cache .ruff_cache .uv-cache

[group('test')]
test version=python *args:
    uv run --python {{ version }} --no-default-groups --group tests pytest {{ args }}

# Test all supported Python versions
[group('test')]
test-all:
    for v in {{ python_versions }}; do just test "$v"; done

[group('test')]
coverage version=python:
    uv run --python {{ version }} --no-default-groups --group tests \
        pytest --cov=. --cov-branch --cov-report=term-missing:skip-covered

# Type check our code
[group('typing')]
typing version=python_oldest:
    # --python-version is a mypy target flag, not a host interpreter
    uv run --no-default-groups --group mypy mypy --python-version {{ version }} .

# Type check as if we're a consumer of the library
[group('typing')]
public-typing version=python_oldest:
    uv run --no-default-groups --group mypy mypy --python-version {{ version }} typing_checks

[group('typing')]
public-typing-all:
    for v in {{ python_oldest }} {{ python_latest }}; do just public-typing "$v"; done

[group('lint')]
lint:
    uv run --only-group ruff ruff format --diff .
    uv run --only-group ruff ruff check .

[group('lint')]
lint-toml:
    {{ taplo }} lint
    {{ taplo }} format --check --diff

[group('lint')]
lint-yaml:
    uv run --only-group yamllint yamllint --strict .

[group('lint')]
lock-check:
    uv lock --check
