MODULE := glotlib2
MODULE_VERS := 0.9.0
MODULE_DEPS :=
MODULES := \
	setup.cfg \
	setup.py \
	glotlib2/shaders/*.py \
	glotlib2/shaders/*.frag \
	glotlib2/shaders/*.vert \
	glotlib2/font_files/*.py \
	glotlib2/font_files/ttf_bitstream_vera_1_10/* \
	glotlib2/*.py \
	glotlib2/glfw/*.py \
	glotlib2/pyside6/*.py
PYTHON := python3

FLAKE_MODULES := glotlib2 tests
LINT_MODULES  := glotlib2 tests
WHEEL_PATH    := dist/$(MODULE)-$(MODULE_VERS)-py3-none-any.whl
TGZ_PATH      := dist/$(MODULE)-$(MODULE_VERS).tar.gz

.PHONY: all
all: test packages

.PHONY: clean
clean:
	rm -rf dist $(MODULE).egg-info build
	find . -name "*.pyc" | xargs rm 2>/dev/null || true
	find . -name __pycache__ | xargs rm -r 2>/dev/null || true

.PHONY: test
test: flake8 lint

.PHONY: flake8
flake8:
	$(PYTHON) -m flake8 $(FLAKE_MODULES)

.PHONY: lint
lint:
	$(PYTHON) -m pylint -j2 $(LINT_MODULES)

.PHONY: install
install: $(WHEEL_PATH) | uninstall
	$(PYTHON) -m pip install $(WHEEL_PATH)

.PHONY: uninstall
uninstall:
	$(PYTHON) -m pip uninstall -y $(MODULE)

.PHONY: packages
packages: $(WHEEL_PATH)

.PHONY: publish
publish: all
	$(PYTHON) -m twine upload $(WHEEL_PATH) $(TGZ_PATH)

$(WHEEL_PATH): $(MODULES) Makefile
	$(PYTHON) -m build
	$(PYTHON) -m twine check $@
