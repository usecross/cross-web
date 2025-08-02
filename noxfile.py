"""Nox sessions for testing and linting."""

import nox

# Configure nox to use uv
nox.options.default_venv_backend = "uv"
nox.options.reuse_existing_virtualenvs = True

# Python versions to test
PYTHON_VERSIONS = ["3.9", "3.10", "3.11", "3.12", "3.13"]

# Framework versions to test
DJANGO_VERSIONS = ["4.2", "5.0", "5.1"]
FLASK_VERSIONS = ["2.3", "3.0", "3.1"]
STARLETTE_VERSIONS = ["0.37", "0.38", "0.39", "0.40", "0.41"]
PYDANTIC_VERSIONS = ["2.11", "2.12"]


@nox.session(python=PYTHON_VERSIONS)
def tests(session: nox.Session) -> None:
    """Run the complete test suite with all dependencies."""
    session.install("-e", ".[dev]")
    session.run(
        "pytest",
        "--cov=src",
        "--cov-report=xml",
        "--cov-report=term-missing",
        "-v",
    )


@nox.session(python=["3.12"], name="tests-coverage")
def tests_coverage(session: nox.Session) -> None:
    """Run tests with coverage reporting."""
    session.install("-e", ".[dev]")
    session.run(
        "pytest",
        "--cov=src",
        "--cov-report=xml",
        "--cov-report=html",
        "--cov-report=term-missing",
        "-v",
    )


@nox.session(python=["3.9", "3.12"])
@nox.parametrize("django", DJANGO_VERSIONS)
def tests_django(session: nox.Session, django: str) -> None:
    """Test Django adapter with different Django versions."""
    session.install("-e", ".")
    session.install("pytest", "pytest-asyncio")
    session.install(f"django~={django}.0")
    session.run("pytest", "tests/request/test_adapters.py::TestDjangoAdapters", "-v")


@nox.session(python=["3.9", "3.12"])
@nox.parametrize("flask", FLASK_VERSIONS)
def tests_flask(session: nox.Session, flask: str) -> None:
    """Test Flask adapter with different Flask versions."""
    session.install("-e", ".")
    session.install("pytest", "pytest-asyncio", "werkzeug")
    session.install(f"flask~={flask}.0")
    session.run("pytest", "tests/request/test_adapters.py::TestFlaskAdapters", "-v")


@nox.session(python=["3.9", "3.12"])
@nox.parametrize("starlette", STARLETTE_VERSIONS)
def tests_starlette(session: nox.Session, starlette: str) -> None:
    """Test Starlette adapter with different Starlette versions."""
    session.install("-e", ".")
    session.install("pytest", "pytest-asyncio", "httpx")
    session.install(f"starlette~={starlette}.0")
    session.run("pytest", "tests/request/test_starlette.py", "-v")


@nox.session(python=["3.12"])
@nox.parametrize("pydantic", PYDANTIC_VERSIONS)
def tests_pydantic(session: nox.Session, pydantic: str) -> None:
    """Test with different Pydantic versions."""
    session.install("-e", ".")
    session.install("pytest", "pytest-asyncio")
    session.install(f"pydantic~={pydantic}.0")
    session.run("pytest", "tests/", "-v")


@nox.session(python=["3.12"], name="tests-frameworks")
def tests_frameworks(session: nox.Session) -> None:
    """Test all framework adapters."""
    # Install base package
    session.install("-e", ".")
    session.install("pytest", "pytest-asyncio")
    
    # Test each framework adapter separately
    frameworks = {
        "sanic": ["sanic"],
        "aiohttp": ["aiohttp", "yarl"],
        "quart": ["quart"],
        "chalice": ["chalice"],
        "litestar": ["litestar", "httpx"],
    }
    
    for framework, deps in frameworks.items():
        session.install(*deps)
        test_class = f"Test{framework.capitalize()}Adapter"
        session.run(
            "pytest", 
            f"tests/request/test_adapters.py::{test_class}",
            "-v"
        )


@nox.session(python=["3.12"], name="tests-fastapi")
def tests_fastapi(session: nox.Session) -> None:
    """Test FastAPI integration."""
    session.install("-e", ".")
    session.install("pytest", "pytest-asyncio", "fastapi", "httpx")
    session.run("pytest", "tests/response/test_fastapi.py", "-v")


@nox.session(python=["3.12"])
def lint(session: nox.Session) -> None:
    """Run linting checks."""
    session.install("-e", ".[dev]")
    session.run("ruff", "check", ".")
    session.run("ruff", "format", "--check", ".")


@nox.session(python=["3.12"])
def format(session: nox.Session) -> None:
    """Format code with ruff."""
    session.install("ruff")
    session.run("ruff", "check", "--fix", ".")
    session.run("ruff", "format", ".")


@nox.session(python=["3.12"])
def mypy(session: nox.Session) -> None:
    """Run type checking with mypy."""
    session.install("-e", ".[dev]")
    session.install("mypy")
    session.run("mypy", "src")


@nox.session(python=["3.12"], name="tests-minimal")
def tests_minimal(session: nox.Session) -> None:
    """Test with minimal dependencies (only pydantic)."""
    session.install("-e", ".")
    session.install("pytest")
    # This should test that the library works without any web frameworks installed
    session.run("pytest", "tests/response/test_response.py", "-v", "-k", "not fastapi")