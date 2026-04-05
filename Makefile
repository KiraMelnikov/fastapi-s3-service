PWD=$(shell pwd)
TEST_PATH=$(PWD)/tests/
VENV_ACTIVATE=. $(PWD)/.venv/bin/activate

.SILENT:
.PHONY: fmt validation test check
fmt:
	echo $(PWD)
	echo "Formatting code with isort and black..."
	$(VENV_ACTIVATE) \
	&& poetry run isort app/ \
	&& poetry run black app/

.SILENT:
.PHONY: validation
validation:
	echo "Running code validation with flake8, pylint, and mypy..."
	$(VENV_ACTIVATE) \
	&& poetry run flake8 app/ \
	&& poetry run pylint app/ \
	&& poetry run mypy app/

.SILENT:
.PHONY: test
test:
	echo "Running tests with pytest..."
	$(VENV_ACTIVATE) \
	&& poetry run pytest -v $(TEST_PATH)

.SILENT:
.PHONY: check
check:
	make fmt
	make validation
	make test