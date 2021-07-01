.PHONY: test

test:
	python3 -m pytest -xv --flake8 --pylint --mypy bot.py bayes.py test_bot.py
