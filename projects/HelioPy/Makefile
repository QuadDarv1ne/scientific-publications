.PHONY: help install install-dev test lint format type-check clean docs build

help:
	@echo "Available commands:"
	@echo "  install        Install package in editable mode"
	@echo "  install-dev    Install with development dependencies"
	@echo "  test           Run tests with coverage"
	@echo "  lint           Run ruff linter"
	@echo "  format         Format code with black"
	@echo "  type-check     Run mypy type checker"
	@echo "  clean          Clean build artifacts"
	@echo "  docs           Build documentation"
	@echo "  build          Build distribution packages"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev,docs]"
	pre-commit install

test:
	pytest --cov=heliopy --cov-report=html --cov-report=term-missing

test-fast:
	pytest tests/unit/

lint:
	ruff check heliopy/ tests/

lint-fix:
	ruff check heliopy/ tests/ --fix

format:
	black heliopy/ tests/ examples/

type-check:
	mypy heliopy/ --ignore-missing-imports

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

docs:
	cd docs && sphinx-build -b html . _build/html

docs-clean:
	rm -rf docs/_build/

build: clean
	python -m build

all-checks: format lint type-check test

pre-commit:
	pre-commit run --all-files
