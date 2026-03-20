.PHONY: dev venv

venv:
	python -m venv .venv
	.venv/bin/pip install -r requirements.txt || .venv\Scripts\pip install -r requirements.txt


dev: 
	python scripts/dev.py