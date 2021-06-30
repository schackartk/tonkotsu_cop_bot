.PHONY: test

test:
	python3 -m pytest -xv --flake8 --pylint
	python3 -m pytest -xv --mypy assess_bayes.py
	python3 -m pytest -xv --mypy bayes.py
	python3 -m pytest -xv --mypy bot.py