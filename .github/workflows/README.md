# GitHub Actions Workflows

This directory contains GitHub Actions workflows for continuous integration and testing.

## Workflows

### 1. `test.yml` - Comprehensive Testing
- **Purpose**: Main testing workflow that runs the full test suite
- **Triggers**: Push to main/master branches, pull requests
- **Matrix**: 
  - Python versions: 3.7, 3.8, 3.9, 3.10, 3.11, 3.12
  - Optional dependencies: with/without pandas
  - Operating systems: Ubuntu (all versions), Windows (3.8, 3.11, 3.12), macOS (3.8, 3.11, 3.12)
- **Features**:
  - Code coverage reporting
  - Upload coverage to Codecov
  - Cross-platform testing

### 2. `ci.yml` - Code Quality and Build
- **Purpose**: Code quality checks and package building
- **Triggers**: Push to main/master branches, pull requests
- **Jobs**:
  - **Lint**: Code style checking with flake8, black, and isort
  - **Security**: Security scanning with bandit and safety
  - **Build**: Package building and validation with twine

### 3. `minimal.yml` - Minimal Dependencies Test
- **Purpose**: Ensure core functionality works without optional dependencies
- **Triggers**: Push to main/master branches, pull requests
- **Matrix**: Python versions 3.7-3.12
- **Features**:
  - Tests without pandas dependency
  - Basic functionality verification
  - Import testing

## Usage

These workflows run automatically on:
- Push to `main` or `master` branches
- Pull requests targeting `main` or `master` branches

## Coverage Reporting

The main test workflow uploads coverage reports to Codecov. To enable this:
1. Sign up for [Codecov](https://codecov.io/)
2. Connect your repository
3. The workflow will automatically upload coverage data

## Local Testing

To run tests locally similar to the CI:

```bash
# Install dependencies
pip install pytest coverage pandas

# Run tests with coverage
coverage run --source=pubchempy -m pytest tests/ -v

# Generate coverage report
coverage report -m
```

## Updating README Badges

Consider updating the README.rst file to use GitHub Actions badges instead of Travis CI:

Replace the Travis CI badge:
```rst
.. image:: http://img.shields.io/travis/mcs07/PubChemPy/master.svg?style=flat
    :target: https://travis-ci.org/mcs07/PubChemPy
```

With a GitHub Actions badge:
```rst
.. image:: https://github.com/mcs07/PubChemPy/workflows/Tests/badge.svg
    :target: https://github.com/mcs07/PubChemPy/actions
```

## Migrating from Travis CI

This replaces the legacy `.travis.yml` configuration with modern GitHub Actions that provide:
- Better matrix testing across Python versions and operating systems
- Faster execution
- Better integration with GitHub
- More comprehensive testing scenarios 