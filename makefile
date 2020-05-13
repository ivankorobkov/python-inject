.PHONY: dist test test37

dist:
	python3 setup.py sdist

upload:
	python3 -m twine upload dist/*

clean:
	rm -rf ./build/*

test:
	nosetests test

test37:
	nosetests test
	nosetests test37
