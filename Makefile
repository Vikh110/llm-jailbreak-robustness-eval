# Convenience targets. Every target is a thin wrapper around a plain `python` command,
# so the same steps work on Windows without make (see README).
PY ?= python

.PHONY: help install install-dev verify verify-full test lint analysis models

help:
	@echo "install      CPU dependencies for analysis, verification and tests"
	@echo "install-dev  + pytest and ruff"
	@echo "verify       26 independent checks without model weights (seconds, no GPU)"
	@echo "verify-full  26 checks including SHA-256 of the pinned model weights (needs 'make models')"
	@echo "test         unit and end-to-end tests"
	@echo "lint         ruff"
	@echo "analysis     recompute 04_results/ from the locked data (overwrites the committed files)"
	@echo "models       download the dataset and the 3 models at the pinned revisions (~5 GB)"

install:
	$(PY) -m pip install -r requirements-analysis.txt

install-dev:
	$(PY) -m pip install -r requirements-dev.txt

verify:
	$(PY) 03_pipeline/07_verify.py --skip-weights

verify-full:
	$(PY) 03_pipeline/07_verify.py

test:
	$(PY) -m pytest

lint:
	$(PY) -m ruff check .

analysis:
	cd 03_pipeline && $(PY) 05_analysis.py

models:
	$(PY) -m pip install huggingface_hub
	cd 03_pipeline && $(PY) 00_download_models.py
