SHELL := /bin/bash

dev:
	pip install -r requirements/requirements-dev.txt

docs:
	cd docs; make html
