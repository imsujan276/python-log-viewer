twine:
	pip install build twine

build:
	rm -rf dist/*
	python -m build

test-publish:
	twine upload --repository testpypi dist/*

test-install:
	pip install --index-url https://test.pypi.org/simple/ python-log-viewer

publish:
	twine upload dist/*