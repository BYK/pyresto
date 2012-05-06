SHELL := /bin/bash

init:
	python setup.py develop
	pip install -r requirements.txt

test:
	nosetests -v tests/*

docs:
	cd docs; make html
