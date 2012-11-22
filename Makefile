SHELL := /bin/bash

release:
	python setup.py sdist upload

dev:
	pip install -r requirements/requirements-dev.txt

docs:
	cd docs; make html
