all: init mypy yapf flake8 coverage

init:
	pip install -r requirements.txt
	pre-commit install -t pre-commit -t pre-push

test:
	pytest

coverage:
	pytest --cov memory_db --cov-report xml --cov-report term-missing

mypy:
	python -m mypy .

yapf:
	python -m yapf -d -r .

flake8:
	python -m flake8 .

tox2actions:
	@tox -l | perl -ne 'print if s/^py(\d)(\d+)-django(\d)(\d+)$$/{"python-version": "\1.\2", "django-version": "\3.\4"}/gs'

.github/workflows/actions.yml: setup.cfg
	yq '.jobs.build.strategy.matrix.include = [$(shell ${MAKE} tox2actions | paste -s -d,)]' -i $@
