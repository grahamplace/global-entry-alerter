.PHONY:

format: black flake8

black:
	poetry run black .

flake8:
	poetry run flake8 .
