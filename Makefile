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
