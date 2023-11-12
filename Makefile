SHELL=/bin/bash
VENV_NAME=.venv

SRC=fastapi_docx
SRC_PATH=${CURDIR}/${SRC}

VENV?=${VENV_NAME}
PYTHON=${VENV}/bin/python
POETRY=${HOME}/.local/bin/poetry

venv-activate=. ${VENV}/bin/activate
set-python-path=export PYTHONPATH=${SRC_PATH}

poetry-install-flags:=--with dev,docs
# poetry-install-flags='--only-root'
# poetry-install-flags='--only docs'


default: help


.PHONY: help
help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  help                 Show this help message"

	@echo "  venv-install         Install poetry & dependencies"
	@echo "  poetry-setup         Install poetry"
	@echo "  poetry-install       Install dependencies"
	@echo "  poetry-update        Update dependencies"
	@echo "  poetry-update-lock   Update dependencies lock"
	@echo "  poetry-add           Add dependency"
	@echo "  poetry-add-dev       Add dev dependency"
	@echo "  poetry-add-docs      Add docs dependency"
	@echo "  poetry-remove        Remove dependency"
	@echo "  poetry-remove-dev    Remove dev dependency"

	@echo "  pre-commit-install   Install pre-commit hooks"
	@echo "  pre-commit-uninstall Uninstall pre-commit hooks"
	@echo "  pre-commit-run       Run pre-commit hooks"

	@echo "  mypy                 Run mypy"
	@echo "  lint                 Run linters"

	@echo "  unit-tests           Run unit tests"
	@echo "  unit-tests-with-cov  Run unit tests with coverage"
	@echo "  open-coverage-report Open html coverage report"
	@echo "  coverage-badge       Generate coverage badge"

	@echo "  serve-docs 		  Serve documentation"
	@echo "  build-docs 		  Build documentation"
	@echo "  add-cov-to-docs 	  Add coverage to docs"
	@echo "  deploy-docs 		  Deploy documentation"


.PHONY: venv-install
venv-install:
	@echo "Installing..."
	@if [ ! -f "${POETRY}" ]; then \
		${MAKE} poetry-setup; \
	fi
	@${MAKE} poetry-install

poetry-setup:
	@echo "Installing poetry..."
	@curl -sSL https://install.python-poetry.org | python3 -
	@${eval include ${HOME}/.poetry/env}

poetry-install:
	@${POETRY} config virtualenvs.in-project true && \
	${POETRY} config virtualenvs.prompt ${VENV_NAME} && \
	${POETRY} install ${poetry-install-flags}

poetry-build:
	@${POETRY} build

poetry-publish:
	@${POETRY} publish --build

poetry-update:
	@${POETRY} update

poetry-update-lock:
	@${POETRY} update --lock

poetry-add:
	@${POETRY} add ${PACKAGE}

poetry-add-dev:
	@${POETRY} add --group dev ${PACKAGE}

poetry-add-docs:
	@${POETRY} add --group docs ${PACKAGE}

poetry-remove:
	@${POETRY} remove ${PACKAGE}

poetry-remove-dev:
	@${POETRY} remove --group dev ${PACKAGE}

poetry-add-pypi-token:
	@${POETRY} config pypi-token.pypi ${PYPI_TOKEN}

pre-commit-install: venv-install
	${VENV}/bin/pre-commit install

pre-commit-uninstall:
	${VENV}/bin/pre-commit uninstall

pre-commit-run: venv-install
	${venv-activate} && pre-commit run --all-files

mypy: venv-install
	${VENV}/bin/mypy --config pyproject.toml

lint: mypy pre-commit-run

unit-tests: venv-install
	${POETRY} run pytest ./tests/unit_tests -n auto

unit-tests-with-cov: venv-install
	${POETRY} run pytest ./tests/unit_tests --cov \
	--cov-config=setup.cfg --cov-report xml --cov-report html -n auto

open-coverage-report:
	cd coverage_report/coverage.html && \
	open -a index.html

coverage-badge:
	${POETRY} run genbadge coverage \
	-i coverage_report/coverage.xml \
	-o coverage_report/coverage-badge.svg

serve-docs:
	${POETRY} run mkdocs serve

build-docs:
	${POETRY} run mkdocs build

add-cov-to-docs:
	@if [ -d "coverage_report" ]; then \
		rsync -avz --progress coverage_report/ docs/coverage/; \
	else \
		echo "coverage_report directory not found, skipping report copy"; \
	fi;

deploy-docs: add-cov-to-docs
	${POETRY} run mkdocs gh-deploy --force
