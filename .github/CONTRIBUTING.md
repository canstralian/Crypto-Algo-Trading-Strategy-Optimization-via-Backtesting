# Contributing to Crypto Strategy Optimizer

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## 🌟 How Can I Contribute?

### Reporting Bugs

Before creating a bug report:
1. **Check existing issues** to avoid duplicates
2. **Use the latest version** to ensure the bug still exists
3. **Gather information** about your environment and steps to reproduce

When creating a bug report, use the bug report template and include:
- Clear description of the issue
- Steps to reproduce
- Expected vs. actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs or screenshots

### Suggesting Features

We welcome feature suggestions! Please:
1. **Check existing feature requests** first
2. **Use the feature request template**
3. **Explain the use case** clearly
4. **Describe the expected behavior**

### Contributing Code

We follow a standard GitHub workflow:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Test thoroughly**
5. **Commit with clear messages**
6. **Push to your fork**
7. **Open a Pull Request**

## 🚀 Development Setup

### Prerequisites

- Python 3.11 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Setup Steps

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/crypto-optimizer.git
cd crypto-optimizer

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# 4. Install pre-commit hooks
pre-commit install

# 5. Run tests to verify setup
pytest
```

## 📝 Code Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 88 characters (Black default)
- **Formatting**: Use Black for code formatting
- **Linting**: Use Ruff for linting
- **Type hints**: Use type hints for all functions
- **Docstrings**: Use Google-style docstrings

### Code Formatting

Before committing, format your code:

```bash
# Format with Black
black .

# Lint with Ruff
ruff check .

# Type check with mypy
mypy src/
```

### Example Code Style

```python
"""Module docstring explaining the purpose."""

from typing import List, Optional
from datetime import datetime


class MyClass:
    """Class docstring.

    Attributes:
        attribute_name: Description of the attribute.
    """

    def my_function(
        self,
        param1: str,
        param2: int,
        optional_param: Optional[float] = None,
    ) -> List[str]:
        """Function docstring.

        Args:
            param1: Description of param1.
            param2: Description of param2.
            optional_param: Description of optional parameter.

        Returns:
            Description of return value.

        Raises:
            ValueError: When something goes wrong.
        """
        # Implementation
        pass
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_config.py

# Run specific test
pytest tests/test_config.py::test_strategy_validation
```

### Writing Tests

- Write tests for all new features
- Aim for >80% code coverage
- Use descriptive test names
- Include both positive and negative test cases

```python
def test_strategy_config_validation_success():
    """Test that valid strategy config passes validation."""
    config = StrategyConfig(
        name="Test Strategy",
        ma_fast=10,
        ma_slow=30,
    )
    assert config.ma_fast < config.ma_slow


def test_strategy_config_validation_fails_when_ma_slow_less_than_fast():
    """Test that validation fails when slow MA < fast MA."""
    with pytest.raises(ValueError, match="Slow MA must be greater"):
        StrategyConfig(
            name="Invalid Strategy",
            ma_fast=30,
            ma_slow=10,  # Invalid: slow < fast
        )
```

## 🎨 UI/UX Guidelines

When contributing UI/UX changes, follow these principles:

### 1. Progressive Disclosure
Don't overwhelm users with all options at once. Show basic options first, advanced options when needed.

### 2. Clear Feedback
- Show progress for long operations
- Use color coding (green=success, red=error, yellow=warning)
- Provide actionable error messages

### 3. Intelligent Defaults
Choose sensible defaults that work for most users.

### 4. Validation
Validate user input early and provide helpful error messages:

```python
# ❌ Bad
if ma_slow <= ma_fast:
    raise ValueError("Invalid MA values")

# ✅ Good
if ma_slow <= ma_fast:
    raise ValueError(
        f"Slow MA ({ma_slow}) must be greater than Fast MA ({ma_fast}). "
        "Typically, slow MA should be 2-3x the fast MA period."
    )
```

### 5. Error Handling
Always use the custom error classes with solutions:

```python
# ❌ Bad
raise Exception("API call failed")

# ✅ Good
raise DataFetchError.rate_limit_exceeded(
    exchange="binance",
    retry_after=60
)
```

## 📚 Documentation

### Code Documentation

- Add docstrings to all modules, classes, and functions
- Use type hints
- Include examples in docstrings when helpful

### User Documentation

When adding features, update:
- `README.md` - For user-facing features
- `UI_UX_ANALYSIS.md` - For UI/UX changes
- Inline help text in CLI commands

### Commit Messages

Write clear, descriptive commit messages:

```
feat: Add RSI strategy template

- Implement RSI mean reversion strategy
- Add validation for RSI parameters
- Include example configuration in templates

Closes #123
```

Format: `<type>: <subject>`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

## 🔍 Code Review Process

All submissions require review. We look for:

1. **Code Quality**
   - Follows style guidelines
   - Properly formatted and linted
   - Type hints included
   - Well documented

2. **Functionality**
   - Works as intended
   - No breaking changes (unless discussed)
   - Handles edge cases

3. **Testing**
   - Adequate test coverage
   - Tests pass
   - Manual testing performed

4. **UI/UX** (if applicable)
   - Follows UI/UX guidelines
   - User-friendly error messages
   - Progress indicators for long operations

5. **Security**
   - No security vulnerabilities introduced
   - Proper input validation
   - Secure credential handling

## 🐛 Bug Triage

Bug priority levels:

- **Critical**: System crashes, data loss, security issues
- **High**: Major functionality broken
- **Medium**: Feature works but has issues
- **Low**: Minor issues, cosmetic problems

## 💬 Communication

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussions
- **Pull Requests**: For code contributions

## 📜 Code of Conduct

### Our Standards

- **Be respectful**: Treat everyone with respect
- **Be collaborative**: Work together constructively
- **Be inclusive**: Welcome newcomers
- **Be professional**: Keep discussions focused and productive

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information

### Enforcement

Violations may result in:
1. Warning
2. Temporary ban
3. Permanent ban

Report violations to the project maintainers.

## 🙏 Recognition

Contributors will be recognized in:
- `CONTRIBUTORS.md` file
- GitHub contributors page
- Release notes (for significant contributions)

## 📞 Questions?

If you have questions:
1. Check the documentation
2. Search existing issues
3. Ask in GitHub Discussions
4. Create a new issue

## 🎉 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!

---

**Happy Contributing! 🚀**
