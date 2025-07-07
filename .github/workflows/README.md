```markdown
[![Tests](https://github.com/keceli/PubChemPy/workflows/Tests/badge.svg)](https://github.com/keceli/PubChemPy/actions?query=workflow%3ATests)
[![Code Quality](https://github.com/keceli/PubChemPy/workflows/Code%20Quality/badge.svg)](https://github.com/keceli/PubChemPy/actions?query=workflow%3A%22Code+Quality%22)
[![codecov](https://codecov.io/gh/keceli/PubChemPy/branch/main/graph/badge.svg)](https://codecov.io/gh/keceli/PubChemPy)
```

# GitHub Actions Workflows

This directory contains GitHub Actions workflows for automated testing and continuous integration.

## Workflows

### 1. `test.yml` - Main Test Suite
- **Purpose**: Comprehensive testing across multiple Python versions and platforms
- **Python versions**: 3.9, 3.10, 3.11, 3.12
- **Platforms**: Ubuntu (all versions), Windows (3.11, 3.12), macOS (3.11, 3.12)
- **Features**:
  - Tests with and without optional dependencies (pandas)
  - Code coverage reporting
  - Codecov integration
  - **Rate limiting**: Sequential execution with delays to prevent PubChem server overload

### 2. `ci.yml` - Code Quality and Build
- **Purpose**: Code quality checks and package building
- **Features**:
  - Linting (flake8, black, isort)
  - Security scanning (bandit, safety)
  - Package building and validation

### 3. `minimal.yml` - Minimal Dependencies Test
- **Purpose**: Test core functionality without optional packages
- **Python versions**: 3.9, 3.10, 3.11, 3.12
- **Features**:
  - Tests basic import and functionality
  - Excludes pandas-dependent tests
  - **Rate limiting**: Limited parallel execution with delays

## Rate Limiting and Server Protection

### Problem
PubChemPy tests make many API calls to PubChem's REST service. When multiple CI jobs run in parallel (different Python versions, different platforms), they can overwhelm PubChem's servers, causing 503 ServerBusy errors.

### Solution
We've implemented comprehensive rate limiting:

1. **Sequential Job Execution**:
   - `test-windows` waits for `test` to complete
   - `test-macos` waits for `test-windows` to complete
   - This prevents all platforms from hitting the API simultaneously

2. **Limited Parallel Execution**:
   - `max-parallel: 2` for Ubuntu tests (was 8 parallel jobs)
   - `max-parallel: 1` for Windows and macOS tests
   - `max-parallel: 2` for minimal tests

3. **Random Delays**:
   - Each job waits 10-30 seconds before starting tests
   - Staggers API requests across different jobs

4. **Automatic Rate Limiting**:
   - `tests/conftest.py` monkey-patches `pubchempy.request()`
   - Enforces minimum 300ms delay between API calls
   - Thread-safe implementation for parallel test execution

5. **Robust Error Handling**:
   - Tests skip gracefully on server errors instead of failing
   - Retry logic with exponential backoff
   - Comprehensive server error handling

### Configuration
- **Before**: 12+ parallel jobs hitting PubChem simultaneously
- **After**: Maximum 2 parallel jobs with 300ms+ delays between requests
- **Result**: Dramatically reduced 503 ServerBusy errors

## Badge Updates

If you're migrating from Travis CI, update your README.md badges:

**Old Travis CI badge:**
```markdown
[![Build Status](https://travis-ci.org/username/PubChemPy.svg?branch=main)](https://travis-ci.org/username/PubChemPy)
```

**New GitHub Actions badges:**
```markdown
[![Tests](https://github.com/username/PubChemPy/workflows/Tests/badge.svg)](https://github.com/username/PubChemPy/actions?query=workflow%3ATests)
[![Code Quality](https://github.com/username/PubChemPy/workflows/Code%20Quality/badge.svg)](https://github.com/username/PubChemPy/actions?query=workflow%3A%22Code+Quality%22)
[![codecov](https://codecov.io/gh/username/PubChemPy/branch/main/graph/badge.svg)](https://codecov.io/gh/username/PubChemPy)
```

## Local Testing

To run tests locally with the same rate limiting:

```bash
# Install dependencies
pip install -e .
pip install pytest coverage pandas

# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/ -v -k "not slow"  # Skip slow tests
pytest tests/ -v -k "network"   # Only network tests
pytest tests/ -v -k "not pandas" # Skip pandas tests

# Run with coverage
coverage run --source=pubchempy -m pytest tests/ -v
coverage report -m
```

## Troubleshooting

### Server Busy Errors
If you still see 503 ServerBusy errors:
1. Check if multiple workflows are running simultaneously
2. Increase delays in workflow files
3. Reduce `max-parallel` values further
4. Consider running tests on a schedule instead of every push

### Rate Limiting Too Aggressive
If tests are too slow:
1. Reduce delays in `tests/conftest.py`
2. Increase `max-parallel` values carefully
3. Use more session-scoped fixtures to reduce API calls

### Local Development
The rate limiting is automatically applied during testing. For development without rate limiting:
```python
# Temporarily disable rate limiting
import pubchempy
pubchempy.request = pubchempy._original_request  # If available
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