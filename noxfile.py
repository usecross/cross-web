"""Nox sessions for testing and linting."""

import nox

# Configure nox to use uv
nox.options.default_venv_backend = "uv"
nox.options.reuse_existing_virtualenvs = True

# Python versions to test
PYTHON_VERSIONS = ["3.9", "3.10", "3.11", "3.12", "3.13"]

# Framework versions to test
DJANGO_VERSIONS = ["5.0", "5.1", "5.2"]
FLASK_VERSIONS = ["2.3", "3.0", "3.1"]
STARLETTE_VERSIONS = ["0.37", "0.38", "0.39", "0.40", "0.41"]


@nox.session(python=PYTHON_VERSIONS, tags=["tests"])
def tests(session: nox.Session) -> None:
    """Run the complete test suite with all dependencies."""
    session.run_install(
        "uv",
        "sync",
        "--extra=dev",
        "--extra=integrations",
        "--no-default-groups",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run(
        "pytest",
        "--cov=src",
        "--cov-report=xml",
        "--cov-report=term-missing",
        "-v",
    )


@nox.session(python=["3.9", "3.12"], tags=["tests"])
@nox.parametrize("django", DJANGO_VERSIONS)
def tests_django(session: nox.Session, django: str) -> None:
    """Test Django adapter with different Django versions."""
    session.run_install(
        "uv",
        "sync",
        "--extra=dev",
        "--extra=integrations",
        "--no-default-groups",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.install(f"django~={django}.0")
    session.run("pytest", "tests/request/test_adapters.py::TestDjangoAdapters", "-v")


@nox.session(python=["3.9", "3.12"], tags=["tests"])
@nox.parametrize("flask", FLASK_VERSIONS)
def tests_flask(session: nox.Session, flask: str) -> None:
    """Test Flask adapter with different Flask versions."""
    session.run_install(
        "uv",
        "sync",
        "--extra=dev",
        "--extra=integrations",
        "--no-default-groups",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.install(f"flask~={flask}.0")
    session.run("pytest", "tests/request/test_adapters.py::TestFlaskAdapters", "-v")


@nox.session(python=["3.9", "3.12"], tags=["tests"])
@nox.parametrize("starlette", STARLETTE_VERSIONS)
def tests_starlette(session: nox.Session, starlette: str) -> None:
    """Test Starlette adapter with different Starlette versions."""
    session.run_install(
        "uv",
        "sync",
        "--extra=dev",
        "--extra=integrations",
        "--no-default-groups",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.install(f"starlette~={starlette}.0")
    session.run("pytest", "tests/request/test_starlette.py", "-v")


@nox.session(python=["3.12"], name="tests-frameworks", tags=["tests"])
def tests_frameworks(session: nox.Session) -> None:
    """Test all framework adapters."""
    # Install base package
    session.run_install(
        "uv",
        "sync",
        "--extra=dev",
        "--no-default-groups",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )

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
        session.run("pytest", f"tests/request/test_adapters.py::{test_class}", "-v")


@nox.session(python=["3.12"], name="tests-fastapi", tags=["tests"])
def tests_fastapi(session: nox.Session) -> None:
    """Test FastAPI integration."""
    session.run_install(
        "uv",
        "sync",
        "--extra=dev",
        "--no-default-groups",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("pytest", "tests/response/test_fastapi.py", "-v")


@nox.session(python=["3.12"])
def lint(session: nox.Session) -> None:
    """Run linting checks."""
    session.run_install(
        "uv",
        "sync",
        "--extra=dev",
        "--no-default-groups",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("ruff", "check", ".")
    session.run("ruff", "format", "--check", ".")


@nox.session(python=["3.12"])
def mypy(session: nox.Session) -> None:
    """Run type checking with mypy."""
    session.install("-e", ".[dev]")
    session.install("mypy")
    session.run("mypy", "src")


@nox.session(python=["3.12"], name="tests-minimal", tags=["tests"])
def tests_minimal(session: nox.Session) -> None:
    """Test with minimal dependencies (only pydantic)."""
    session.install("-e", ".[dev]")
    # This should test that the library works without any web frameworks installed
    session.run("pytest", "tests/response/test_response.py", "-v", "-k", "not fastapi")
