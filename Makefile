.PHONY: verify test

verify:
	python scripts/verify_foundation.py

test:
	pytest -q
