# Contributing to HelioPy Development

This document provides additional guidelines for developers contributing to HelioPy.

## Development Setup

### Installing Development Dependencies

```bash
pip install -e ".[dev]"
```

This installs:
- pytest and pytest-cov for testing
- black for code formatting
- ruff for linting
- mypy for type checking
- pre-commit for git hooks

### Setting Up Pre-commit Hooks

Pre-commit hooks automatically check your code before each commit:

```bash
pip install pre-commit
pre-commit install
```

The hooks will run:
- trailing whitespace removal
- end-of-file fixing
- YAML/JSON/TOML validation
- black formatting
- ruff linting
- mypy type checking
- isort import sorting
- bandit security checks
- pydocstyle documentation checks

### Running Pre-commit Manually

To run pre-commit on all files:

```bash
pre-commit run --all-files
```

## Code Quality Standards

### Formatting with Black

HelioPy uses black with line length of 100:

```bash
black heliopy/ tests/ --line-length=100
```

### Linting with Ruff

Run ruff to check for code quality issues:

```bash
ruff check heliopy/
```

Auto-fix issues where possible:

```bash
ruff check heliopy/ --fix
```

### Type Checking with mypy

Run type checks:

```bash
mypy heliopy/ --ignore-missing-imports
```

## Testing

### Running Tests

Run all tests:

```bash
pytest tests/
```

Run with coverage:

```bash
pytest --cov=heliopy --cov-report=html --cov-report=term-missing
```

Run specific test file:

```bash
pytest tests/unit/test_utils.py
```

Run specific test:

```bash
pytest tests/unit/test_utils.py::TestMathUtils::test_spherical_to_cartesian
```

### Writing Tests

- Place tests in `tests/unit/` or `tests/integration/`
- Test file names must start with `test_`
- Test class names must start with `Test`
- Test function names must start with `test_`

Example test:

```python
import pytest
from heliopy.utils import math_utils


class TestMathUtils:
    def test_spherical_to_cartesian(self):
        """Test spherical to Cartesian conversion."""
        r, theta, phi = 1.0, 0.0, 0.0
        x, y, z = math_utils.spherical_to_cartesian(r, theta, phi)
        assert abs(x - 0.0) < 1e-10
        assert abs(y - 0.0) < 1e-10
        assert abs(z - 1.0) < 1e-10
```

## Documentation

### Building Documentation

Install documentation dependencies:

```bash
pip install -e ".[docs]"
```

Build HTML documentation:

```bash
cd docs
sphinx-build -b html . _build/html
```

Or use the Makefile:

```bash
cd docs
make html
```

### Writing Docstrings

HelioPy uses NumPy-style docstrings:

```python
def function_name(param1: int, param2: str) -> bool:
    """
    Brief description of the function.

    More detailed description if needed. Can span multiple lines
    and include examples.

    Parameters
    ----------
    param1 : int
        Description of param1.
    param2 : str
        Description of param2.

    Returns
    -------
    bool
        Description of return value.

    Raises
    ------
    ValueError
        When param1 is negative.

    Examples
    --------
    >>> function_name(5, "test")
    True
    """
    pass
```

## Continuous Integration

### GitHub Actions

The CI pipeline runs on:
- Python 3.8, 3.9, 3.10, 3.11
- Ubuntu, Windows, macOS

It performs:
1. Code formatting check (black)
2. Linting (ruff)
3. Type checking (mypy)
4. Unit tests (pytest)
5. Coverage reporting (codecov)

### Coverage Requirements

- Aim for >80% code coverage
- All new features should include tests
- Coverage reports are uploaded to Codecov

## Release Process

### Version Numbering

HelioPy follows [Semantic Versioning](https://semver.org/):
- MAJOR.MINOR.PATCH (e.g., 1.2.3)
- MAJOR: breaking changes
- MINOR: new features (backward compatible)
- PATCH: bug fixes

### Creating a Release

1. Update version in `heliopy/__init__.py`
2. Update `CHANGELOG.md`
3. Create a git tag:
   ```bash
   git tag -a v0.2.0 -m "Release version 0.2.0"
   git push origin v0.2.0
   ```
4. GitHub Actions will automatically create a release

## Tips and Best Practices

### Performance

- Use NumPy vectorization instead of loops
- Profile code with `cProfile` before optimizing
- Cache expensive computations

### Code Style

- Follow PEP 8
- Use type hints where possible
- Keep functions small and focused
- Write self-documenting code

### Git Workflow

- Create feature branches: `feature/your-feature-name`
- Keep commits atomic and focused
- Write clear commit messages
- Squash commits before merging

### Getting Help

- Check existing issues and PRs
- Ask questions in GitHub Discussions
- Join our community chat (if available)
- Read the documentation thoroughly

## Resources

- [NumPy Documentation](https://numpy.org/doc/stable/)
- [Astropy Documentation](https://docs.astropy.org/)
- [SciPy Documentation](https://docs.scipy.org/doc/scipy/)
- [Matplotlib Documentation](https://matplotlib.org/stable/contents.html)
- [Python Testing with pytest](https://docs.pytest.org/)
