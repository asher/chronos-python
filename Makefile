.PHONY: test
test:
	tox

.PHONY: itests
itests:
	tox -e itests
	tox -e itests-py3
