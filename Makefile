all: init mypy yapf flake8 coverage

init:
	pip install -r requirements.txt
	pre-commit install -t pre-commit -t pre-push

test:
	python -m unittest

coverage:
	python -m coverage run -m unittest
	python -m coverage report

mypy:
	python -m mypy .

yapf:
	python -m yapf -d -r .

flake8:
	python -m flake8 .
