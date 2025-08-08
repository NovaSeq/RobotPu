# Contributing to RobotPu

Thank you for your interest in contributing to RobotPu! We welcome contributions from everyone, whether you're a seasoned developer or just getting started.

## Table of Contents
- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Style](#code-style)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)
- [License](#license)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs
- Check if the bug has already been reported in the [Issues](https://github.com/yourusername/RobotPu/issues) section
- If not, create a new issue with a clear title and description
- Include steps to reproduce the bug and relevant error messages

### Suggesting Enhancements
- Open an issue with the "enhancement" label
- Clearly describe the feature and why it would be useful
- Include any relevant examples or references

### Your First Code Contribution
- Look for issues labeled "good first issue" to get started
- Comment on the issue to let others know you're working on it
- Follow the development workflow below

## Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/RobotPu.git
   cd RobotPu
   ```
3. Set up the development environment (add specific setup instructions here)
4. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

1. Make your changes
2. Run tests (add specific test commands here)
3. Ensure your code passes all checks
4. Commit your changes following the [commit message guidelines](#commit-message-guidelines)
5. Push to your fork and open a Pull Request

## Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
- Use meaningful variable and function names
- Add docstrings for all public functions and classes
- Keep lines under 88 characters (PEP 8 recommendation)
- Include type hints for better code clarity

## Commit Message Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Example:
```
feat(ui): add dark mode toggle

Add a new toggle in the settings panel to switch between light and dark themes.

Closes #123
```

## Pull Request Process

1. Ensure any install or build dependencies are removed before the end of the layer when doing a build
2. Update the README.md with details of changes to the interface
3. Increase the version numbers in any examples files and the README.md to the new version that this Pull Request would represent
4. You may merge the Pull Request once you have the sign-off of two other developers, or if you do not have permission to do that, you may request the reviewer to merge it for you

## Reporting Bugs

When reporting bugs, please include:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Environment details (OS, Python version, etc.)
- Any relevant error messages or logs

## Feature Requests

For feature requests, please:
- Use a clear, descriptive title
- Describe the problem you're trying to solve
- Explain why this feature would be valuable
- Include any relevant examples or references

## License

By contributing, you agree that your contributions will be licensed under the project's [LICENSE](LICENSE) file.
