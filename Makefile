VERSION = $(shell python3 setup.py --version)

.PHONY: help release clean doc showdoc

help:
	@echo "doc: Build documentation"
	@echo "cleandoc: Clean documentation"
	@echo "showdoc: Show documentation in webbrowser"
	@echo "release: Package and release to PyPI"
	@echo "cleanrelease: Clean release packaging"
	@echo "clean: Clean all"

doc:
	make -C doc html

cleandoc:
	make -C doc clean

showdoc:
	python3 -m webbrowser -t "doc/_build/html/index.html"

release:
	python3 setup.py --version | egrep -q -v '[a-zA-Z]' # Fail on dev/rc versions
	git commit -e -m "Release of $(VERSION)"            # Fail on nothing to commit
	git tag -a -m "Release of $(VERSION)" $(VERSION)    # Fail on existing tags
	git push origin HEAD                                # Fail on out-of-sync upstream
	git push origin tag $(VERSION)                      # Fail on dublicate tag
	python3 setup.py sdist register upload              # Release to pypi

cleanrelease:
	rm -rf build/ dist/ MANIFEST 2>/dev/null || true
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '._*' -exec rm -f {} +

clean: cleanrelease cleandoc
