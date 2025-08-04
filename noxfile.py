# type: ignore
"""Nox sessions for testing and linting."""

import nox

# Configure nox to use uv
nox.options.default_venv_backend = "uv"
nox.options.reuse_existing_virtualenvs = True

# Python versions to test
PYTHON_VERSIONS = ["3.9", "3.10", "3.11", "3.12", "3.13"]
DJANGO_PYTHON_VERSIONS = ["3.10", "3.11", "3.12", "3.13"]

# Framework versions to test
DJANGO_VERSIONS = ["5.0", "5.1", "5.2"]
FLASK_VERSIONS = ["2.3", "3.0", "3.1"]
STARLETTE_VERSIONS = ["0.47"]


@nox.session(python=PYTHON_VERSIONS, tags=["tests"])
def tests(session: nox.Session) -> None:
    """Run the complete test suite with all dependencies."""
    session.run_install(
        "uv",
        "sync",
        "--dev",
        "--group",
        "integrations",
        "--no-default-groups",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("coverage", "run", "-m", "pytest", "-v")


@nox.session(python=DJANGO_PYTHON_VERSIONS, tags=["tests"])
@nox.parametrize("django", DJANGO_VERSIONS)
def tests_django(session: nox.Session, django: str) -> None:
    """Test Django adapter with different Django versions."""
    session.run_install(
        "uv",
        "sync",
        "--dev",
        "--group",
        "integrations",
        "--no-default-groups",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.install(f"django~={django}.0")
    session.run("coverage", "run", "-m", "pytest", "-m", "django", "-v")


@nox.session(python=["3.9", "3.12"], tags=["tests"])
@nox.parametrize("flask", FLASK_VERSIONS)
def tests_flask(session: nox.Session, flask: str) -> None:
    """Test Flask adapter with different Flask versions."""
    session.run_install(
        "uv",
        "sync",
        "--dev",
        "--group",
        "integrations",
        "--no-default-groups",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.install(f"flask~={flask}.0")
    session.run("coverage", "run", "-m", "pytest", "-m", "flask", "-v")


@nox.session(python=["3.9", "3.12"], tags=["tests"])
@nox.parametrize("starlette", STARLETTE_VERSIONS)
def tests_starlette(session: nox.Session, starlette: str) -> None:
    """Test Starlette adapter with different Starlette versions."""
    session.run_install(
        "uv",
        "sync",
        "--dev",
        "--group",
        "integrations",
        "--no-default-groups",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.install(f"starlette~={starlette}.0")
    session.run("coverage", "run", "-m", "pytest", "-m", "starlette", "-v")


@nox.session(python=["3.12"], name="tests-frameworks", tags=["tests"])
def tests_frameworks(session: nox.Session) -> None:
    """Test all framework adapters."""
    # Install base package
    session.run_install(
        "uv",
        "sync",
        "--dev",
        "--no-default-groups",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )

    # Test each framework adapter separately
    frameworks = {
        "sanic": ["sanic", "sanic-testing"],
        "aiohttp": ["aiohttp", "yarl"],
        "quart": ["quart"],
        "chalice": ["chalice"],
        "litestar": ["litestar", "httpx"],
    }

    for framework, deps in frameworks.items():
        session.install(*deps)
        session.run("coverage", "run", "-m", "pytest", "-m", framework, "-v")


@nox.session(python=["3.12"], name="tests-fastapi", tags=["tests"])
def tests_fastapi(session: nox.Session) -> None:
    """Test FastAPI integration."""
    session.run_install(
        "uv",
        "sync",
        "--dev",
        "--no-default-groups",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.install("fastapi", "httpx", "python-multipart")
    session.run("coverage", "run", "-m", "pytest", "-m", "fastapi", "-v")


@nox.session(python=["3.12"])
def lint(session: nox.Session) -> None:
    """Run linting checks."""
    session.run_install(
        "uv",
        "sync",
        "--dev",
        "--no-default-groups",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("ruff", "check", ".")
    session.run("ruff", "format", "--check", ".")


@nox.session(python=["3.12"])
def mypy(session: nox.Session) -> None:
    """Run type checking with mypy."""
    session.run_install(
        "uv",
        "sync",
        "--dev",
        "--group",
        "integrations",
        "--no-default-groups",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )
    session.run("mypy", "src")


@nox.session(python=["3.12"])
def coverage(session: nox.Session) -> None:
    """Combine coverage data and generate reports."""
    session.run_install(
        "uv",
        "sync",
        "--dev",
        "--no-default-groups",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )

    # Combine coverage data from multiple test runs
    session.run("coverage", "combine", success_codes=[0, 1])

    # Generate HTML report
    session.run("coverage", "html", "--skip-covered", "--skip-empty")

    # Generate markdown report for GitHub Actions summary (if in CI)
    if session.posargs and "--ci" in session.posargs:
        session.run(
            "sh",
            "-c",
            "coverage report --format=markdown >> $GITHUB_STEP_SUMMARY",
            success_codes=[0, 1],
            external=True,
        )

    # Show report in terminal and check coverage threshold
    session.run("coverage", "report", "--fail-under=80")


@nox.session(python=["3.12"], name="test-coverage-html")
def test_coverage_html(session: nox.Session) -> None:
    """Run all tests and generate HTML coverage report (local use only)."""
    session.run_install(
        "uv",
        "sync",
        "--dev",
        "--group",
        "integrations",
        "--no-default-groups",
        f"--python={session.virtualenv.location}",
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )

    # Run all tests with coverage
    session.run("coverage", "run", "-m", "pytest", "-v")

    # Combine any existing coverage files (in case of parallel runs or leftover files)
    session.run("coverage", "combine", success_codes=[0, 1])

    session.run("coverage", "html")
    session.run("coverage", "report")

    # Open the HTML report in the browser (optional)
    import webbrowser
    import pathlib

    html_report = pathlib.Path("htmlcov/index.html").absolute()
    if html_report.exists():
        session.log(f"Opening coverage report at: {html_report}")
        webbrowser.open(f"file://{html_report}")
    else:
        session.warn("HTML coverage report not found")
