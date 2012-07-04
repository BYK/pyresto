SHELL := /bin/bash

init:
	python setup.py develop
	pip install -r requirements.txt

test:
	python -m unittest discover

docs:
	cd docs; make html
