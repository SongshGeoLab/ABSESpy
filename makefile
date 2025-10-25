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

# =============================================================================
# 分层测试命令
# =============================================================================

# 基础功能测试 - 第1层：验证核心类能正常创建和基本操作
test-foundation:
	@echo "🧪 Running Foundation Tests (Layer 1)..."
	uv run pytest tests/foundation/ -v --tb=short --cov=abses --cov-report=term-missing

# 用户场景测试 - 第2层：基于实际使用场景的测试
test-scenarios:
	@echo "🎯 Running Scenario Tests (Layer 2)..."
	uv run pytest tests/scenarios/ -v --tb=short --cov=abses --cov-report=term-missing

# 向后兼容性测试 - 保护现有功能
test-compatibility:
	@echo "🔄 Running Backward Compatibility Tests..."
	uv run pytest tests/test_backward_compatibility.py -v --tb=short

# 向后兼容性测试（包含所有兼容性测试）
test-compatibility-all:
	@echo "🔄 Running All Backward Compatibility Tests..."
	uv run pytest tests/test_*compatibility*.py -v --tb=short

# 快速测试 - 只运行基础测试，用于开发时快速验证
test-quick:
	@echo "⚡ Running Quick Tests (Foundation only)..."
	uv run pytest tests/foundation/ -v --tb=short

# 完整测试 - 运行所有分层测试（只包含通过的测试）
test-layered:
	@echo "🏗️ Running All Layered Tests..."
	@echo "Layer 1: Foundation Tests"
	uv run pytest tests/foundation/ -v --tb=short --cov=abses --cov-report=term-missing
	@echo "Layer 2: Scenario Tests"
	uv run pytest tests/scenarios/ -v --tb=short --cov=abses --cov-report=term-missing
	@echo "✅ All layered tests completed successfully!"

# 测试覆盖率报告
test-coverage:
	@echo "📊 Generating Test Coverage Report..."
	uv run pytest tests/foundation/ tests/scenarios/ --cov=abses --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

# 开发测试 - 快速验证，不生成覆盖率报告
test-dev:
	@echo "🔧 Running Development Tests..."
	uv run pytest tests/foundation/ tests/scenarios/ -v --tb=short -x

# 测试特定功能
test-agents:
	@echo "🤖 Testing Agent-related functionality..."
	uv run pytest tests/ -k "agent" -v --tb=short

test-spatial:
	@echo "🗺️ Testing Spatial functionality..."
	uv run pytest tests/ -k "spatial or cell or patch" -v --tb=short

test-model:
	@echo "🏗️ Testing Model functionality..."
	uv run pytest tests/ -k "model" -v --tb=short

# 测试特定模块
test-module:
	@echo "🔍 Testing specific module (usage: make test-module MODULE=agents)"
	@if [ -z "$(MODULE)" ]; then echo "Please specify MODULE=module_name"; exit 1; fi
	uv run pytest tests/ -k "$(MODULE)" -v --tb=short

# 并行测试 - 提高测试速度
test-parallel:
	@echo "🚀 Running Tests in Parallel..."
	uv run pytest tests/foundation/ tests/scenarios/ -n auto -v --tb=short

# 测试帮助 - 显示所有可用的测试命令
test-help:
	@echo "📋 Available Test Commands:"
	@echo ""
	@echo "🧪 Foundation Tests (Layer 1):"
	@echo "  make test-foundation     - Run foundation tests only"
	@echo "  make test-quick          - Quick test (foundation only)"
	@echo ""
	@echo "🎯 Scenario Tests (Layer 2):"
	@echo "  make test-scenarios      - Run scenario tests only"
	@echo ""
	@echo "🔄 Compatibility Tests:"
	@echo "  make test-compatibility      - Run backward compatibility tests"
	@echo "  make test-compatibility-all  - Run all compatibility tests"
	@echo ""
	@echo "🏗️ Complete Test Suites:"
	@echo "  make test-layered        - Run all layered tests (stable)"
	@echo "  make test-dev            - Development tests (fast, stop on first failure)"
	@echo "  make test                - Run all tests (original)"
	@echo "  make test-all            - Run multi-version tests"
	@echo ""
	@echo "🔍 Feature-Specific Tests:"
	@echo "  make test-agents         - Test agent-related functionality"
	@echo "  make test-spatial        - Test spatial functionality"
	@echo "  make test-model          - Test model functionality"
	@echo ""
	@echo "🚀 Performance & Coverage:"
	@echo "  make test-parallel       - Run tests in parallel"
	@echo "  make test-coverage       - Generate coverage report"
	@echo ""
	@echo "🔍 Specific Testing:"
	@echo "  make test-module MODULE=agents - Test specific module"
	@echo ""
	@echo "📊 Reports:"
	@echo "  make report              - View allure test report"

# 测试清理
test-clean:
	@echo "🧹 Cleaning test artifacts..."
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage*
	rm -rf tmp/allure_results/
	@echo "Test artifacts cleaned!"

# 测试安装 - 安装测试相关依赖
install-test-tools:
	@echo "📦 Installing test tools..."
	uv add --dev pytest-xdist pytest-benchmark pytest-mock
	@echo "Test tools installed!"

# =============================================================================
# 原有测试命令（保持兼容性）
# =============================================================================

# 完整测试套件（包含所有测试）
test:
	uv run pytest -vs --clean-alluredir --alluredir tmp/allure_results --cov=abses --no-cov-on-fail

# 多版本测试
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
