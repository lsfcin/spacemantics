# verify:fast contract — the checker test suite must be green to commit (code/VERIFY.md).

.PHONY: verify-fast test check

verify-fast:
	python3 -m pytest tests -q

test: verify-fast

check:
	python3 -m checker examples/office.json
