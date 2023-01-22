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

	@echo "  serve-docs 		  Serve documentation"
	@echo "  build-docs 		  Build documentation"
	@echo "  deploy-docs 		  Deploy documentation"


.PHONY: venv-install
venv-install:
	@echo "Installing..."
	@if [ ! -f "${POETRY}" ]; then \
		${MAKE} poetry-setup; \
	fi
	@${MAKE} poetry-install

.PHONY: poetry-setup
poetry-setup:
	@echo "Installing poetry..."
	@curl -sSL https://install.python-poetry.org | python3 -
	@${eval include ${HOME}/.poetry/env}

.PHONY: poetry-install
poetry-install:
	@${POETRY} config virtualenvs.in-project true && \
	${POETRY} config virtualenvs.prompt ${VENV_NAME} && \
	${POETRY} install ${poetry-install-flags}

.PHONY: poetry-update
poetry-update:
	@${POETRY} update

.PHONY: poetry-update-lock
poetry-update-lock:
	@${POETRY} update --lock

.PHONY: poetry-add
poetry-add:
	@${POETRY} add ${PACKAGE}

.PHONY: poetry-add-dev
poetry-add-dev:
	@${POETRY} add --group dev ${PACKAGE}

.PHONY: poetry-remove
poetry-remove:
	@${POETRY} remove ${PACKAGE}

.PHONY: poetry-remove-dev
poetry-remove-dev:
	@${POETRY} remove --group dev ${PACKAGE}

.PHONY: pre-commit-install
pre-commit-install: venv-install
	${VENV}/bin/pre-commit install

.PHONY: pre-commit-uninstall
pre-commit-uninstall:
	${VENV}/bin/pre-commit uninstall

.PHONY: pre-commit-run
pre-commit-run: venv-install
	${venv-activate} && pre-commit run --all-files

.PHONY: mypy
mypy: venv-install
	${VENV}/bin/mypy --config pyproject.toml

.PHONY: lint
lint: mypy pre-commit-run

.PHONY: unit-tests
unit-tests: venv-install
	${POETRY} run pytest ./tests/unit_tests -n auto

COV_REPORT_FORMAT?=xml
.PHONY: unit-tests-with-cov
unit-tests-with-cov: venv-install
	${POETRY} run pytest ./tests/unit_tests --cov --cov-config=setup.cfg --cov-report ${COV_REPORT_FORMAT} -n auto

.PHONY: open-coverage-report
open-coverage-report:
	cd coverage_report/coverage.html && \
	open -a index.html

.PHONY: serve-docs
serve-docs:
	${POETRY} run mkdocs serve

.PHONY: build-docs
build-docs:
	${POETRY} run mkdocs build

.PHONY: deploy-docs
deploy-docs:
	${POETRY} run mkdocs gh-deploy
