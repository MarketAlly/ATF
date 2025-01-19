# Contributing to ATF

We love your input! We want to make contributing to ATF as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Improving documentation

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code follows the style guidelines.
6. Issue that pull request!

## Pull Request Process

1. Update the README.md with details of changes if applicable.
2. Update the docs/ folder with any new documentation.
3. The PR will be merged once you have the sign-off of two other developers.

## Development Setup

1. Clone your fork:
```bash
git clone https://github.com/your-username/atf.git
cd atf
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

4. Set up pre-commit hooks:
```bash
pre-commit install
```

## Code Style

We use several tools to maintain code quality:

1. Black for code formatting:
```bash
black .
```

2. isort for import sorting:
```bash
isort .
```

3. mypy for type checking:
```bash
mypy .
```

4. pylint for code analysis:
```bash
pylint **/*.py
```

### Style Guidelines

- Use type hints for all function definitions
- Include docstrings for all modules, classes, and functions
- Follow PEP 8 naming conventions
- Keep functions focused and small
- Use meaningful variable names
- Comment complex algorithms

Example:
```python
from typing import List, Optional

def process_feed_items(items: List[dict], max_items: Optional[int] = None) -> List[dict]:
    """Process feed items and return filtered results.

    Args:
        items: List of feed items to process
        max_items: Optional maximum number of items to return

    Returns:
        List of processed feed items
    """
    processed_items = [
        item for item in items
        if _validate_item(item)
    ]
    
    if max_items is not None:
        return processed_items[:max_items]
    return processed_items
```

## Testing

### Writing Tests

1. All new features should include tests
2. Update tests when modifying features
3. Use pytest for testing
4. Aim for high test coverage

Example test:
```python
import pytest
from atf.validator import validate_feed

def test_validate_feed():
    # Given
    test_feed = create_test_feed()
    
    # When
    result = validate_feed(test_feed)
    
    # Then
    assert result.is_valid
    assert len(result.errors) == 0
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=./ --cov-report=xml

# Run specific test
pytest tests/test_validator.py
```

## Security Guidelines

1. Never commit sensitive data
2. Use secure defaults
3. Follow security best practices
4. Review security implications

## Documentation

### API Documentation

- Use clear, concise language
- Include example usage
- Document all parameters
- Note any limitations

Example:
```python
def sign_feed(content: str, key_path: str) -> str:
    """Sign feed content with provided key.
    
    Args:
        content: The feed content to sign
        key_path: Path to the signing key
        
    Returns:
        Base64-encoded signature
        
    Raises:
        KeyError: If key file not found
        SigningError: If signing fails
    """
```

### User Documentation

- Keep it user-focused
- Include practical examples
- Provide troubleshooting guides
- Update for new features

## Issue Reporting

### Bug Reports

When reporting bugs, include:
1. Quick summary
2. Steps to reproduce
3. Expected behavior
4. Actual behavior
5. Environment details

Example:
```markdown
### Bug: Feed Validation Fails

**Steps to Reproduce:**
1. Create feed using generator
2. Run validator
3. Observe error

**Expected:**
Feed validates successfully

**Actual:**
Validation fails with error: [error details]

**Environment:**
- OS: Ubuntu 20.04
- Python: 3.11
- ATF Version: 1.0.0
```

### Feature Requests

When requesting features:
1. Describe the problem
2. Suggest a solution
3. Note alternatives
4. Discuss tradeoffs

## Release Process

1. Update version numbers:
   - setup.py
   - documentation
   - changelog

2. Create release notes:
   - New features
   - Bug fixes
   - Breaking changes

3. Tag the release:
```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome all contributors
- Focus on constructive feedback
- Put users first

### Enforcement

- First violation: Warning
- Second violation: Temporary ban
- Third violation: Permanent ban

## Questions?

- Check existing issues
- Read the documentation
- Contact maintainers