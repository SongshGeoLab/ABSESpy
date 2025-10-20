setup:
	make install-tests
	make install-jupyter
	make setup-pre-commit
	make install-docs

# 安装必要的代码检查工具
# black: https://github.com/psf/black
# flake8: https://github.com/pycqa/flake8
# isort: https://github.com/PyCQA/isort
# nbstripout: https://github.com/kynan/nbstripout
# pydocstyle: https://github.com/PyCQA/pydocstyle
# pre-commit-hooks: https://github.com/pre-commit/pre-commit-hooks

setup-dependencies:
	uv sync

setup-pre-commit:
	uv add --dev flake8 isort nbstripout pydocstyle pre-commit-hooks interrogate sourcery mypy bandit black pylint ruff

install-jupyter:
	uv add --dev ipykernel jupyterlab jupyterlab-execute-time

install-tests:
	uv add hydra-core
	uv add --dev pytest allure-pytest pytest-cov pytest-clarity pytest-sugar

# https://timvink.github.io/mkdocs-git-authors-plugin/index.html
install-docs:
	uv add --group docs mkdocs mkdocs-material mkdocs-git-revision-date-localized-plugin mkdocs-minify-plugin mkdocs-redirects mkdocs-awesome-pages-plugin mkdocs-git-authors-plugin 'mkdocstrings[python]' mkdocs-bibtex mkdocs-macros-plugin mkdocs-jupyter mkdocs-callouts mkdocs-glightbox pymdown-extensions

test:
	uv run pytest -vs --clean-alluredir --alluredir tmp/allure_results --cov=abses  --no-cov-on-fail

test-all:
	uv run --with tox tox -p auto

report:
	uv run allure serve tmp/allure_results

jupyter:
	uv run jupyter lab

diagram:
	pyreverse -o png -p ABSESpy abses
	mv *.png img/.

show_logs:
	find . -type f -name "*.log"

clean_logs:
	./remove-logs.sh

rm_log:
	echo "Removing .coverage and *.log files..."
	ls .coverage* 1>/dev/null 2>&1 && rm .coverage* || true
	ls *.log 1>/dev/null 2>&1 && rm *.log || true
