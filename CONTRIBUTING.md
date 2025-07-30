# Contributing to Proxmox AI Infrastructure Assistant

Thank you for your interest in contributing to the Proxmox AI Infrastructure Assistant! This project leverages local AI to make infrastructure automation accessible to everyone, and we welcome contributions from the community.

## 🎯 Project Vision

Our mission is to democratize Infrastructure as Code (IaC) through:
- **Local AI Processing**: Complete privacy with no external dependencies
- **Skill-Level Adaptation**: Support for beginners through experts
- **Security-First Design**: Enterprise-grade security from the ground up
- **Hardware Optimization**: Efficient use of available computing resources

## 🚀 Getting Started

### Development Environment Setup

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/proxmox-ai-assistant.git
cd proxmox-ai-assistant
```

2. **Set up Python environment:**
```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .[dev]
```

3. **Install Ollama for local AI:**
```bash
# Linux/macOS
curl -fsSL https://ollama.ai/install.sh | sh
ollama serve
ollama pull llama3.1:8b-instruct-q4_0
```

4. **Run tests:**
```bash
pytest
```

5. **Set up pre-commit hooks:**
```bash
pre-commit install
```

### Development Dependencies

The development environment includes:
- **Testing**: pytest, pytest-cov, pytest-asyncio
- **Code Quality**: black, isort, mypy, flake8
- **Documentation**: sphinx, mkdocs
- **Security**: bandit, safety

## 📝 How to Contribute

### 1. Code Contributions

#### Types of Contributions We Welcome

- **Bug fixes**: Issues with existing functionality
- **Feature enhancements**: Improvements to existing features
- **New features**: New capabilities that align with project goals
- **Performance optimizations**: Improvements to speed or resource usage
- **Documentation**: Improvements to docs, examples, or guides
- **Testing**: Additional test coverage or testing infrastructure
- **AI model optimizations**: Better hardware utilization or model selection

#### Before You Start

1. **Check existing issues**: Look for related issues or discussions
2. **Create an issue**: For significant changes, create an issue to discuss the approach
3. **Fork the repository**: Create your own fork to work in
4. **Create a feature branch**: Use descriptive branch names

```bash
git checkout -b feature/improve-hardware-detection
git checkout -b fix/ansible-generation-bug
git checkout -b docs/add-expert-examples
```

#### Development Workflow

1. **Write your code**: Follow the coding standards below
2. **Add tests**: Include unit and integration tests
3. **Update documentation**: Update relevant docs and docstrings
4. **Run the test suite**: Ensure all tests pass
5. **Submit a pull request**: Use the PR template

### 2. Code Standards

#### Python Code Style

We use these tools to maintain code quality:

```bash
# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/

# Security scanning
bandit -r src/
```

#### Code Quality Guidelines

- **Type hints**: Use type hints for all function signatures
- **Docstrings**: Follow Google-style docstrings
- **Error handling**: Proper exception handling with logging
- **Testing**: Comprehensive test coverage (>90%)
- **Security**: Security-first coding practices

#### Example Code Structure

```python
"""
Module for hardware detection and optimization.

This module provides functionality for automatic hardware detection
and AI model optimization based on available system resources.
"""

import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

import structlog

logger = structlog.get_logger(__name__)

@dataclass
class HardwareSpecs:
    """Hardware specifications for optimization."""
    cpu_cores: int
    memory_gb: float
    gpu_available: bool
    storage_type: str

class HardwareDetector:
    """
    Automatic hardware detection and optimization.
    
    Detects system hardware capabilities and recommends optimal
    configurations for local AI model execution.
    """
    
    def __init__(self) -> None:
        """Initialize hardware detector."""
        self.specs: Optional[HardwareSpecs] = None
        
    def detect_hardware(self) -> HardwareSpecs:
        """
        Detect current hardware specifications.
        
        Returns:
            HardwareSpecs: Detected hardware capabilities
            
        Raises:
            DetectionError: If hardware detection fails
        """
        try:
            # Implementation here
            logger.info("Hardware detection completed successfully")
            return self.specs
        except Exception as e:
            logger.error("Hardware detection failed", error=str(e))
            raise DetectionError(f"Failed to detect hardware: {e}")
```

### 3. Testing Guidelines

#### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_hardware_detector.py
│   ├── test_ai_client.py
│   └── test_cli_commands.py
├── integration/             # Integration tests
│   ├── test_full_workflow.py
│   └── test_ai_integration.py
├── security/               # Security tests
│   ├── test_credential_handling.py
│   └── test_network_security.py
└── fixtures/               # Test data and fixtures
    ├── sample_configs/
    └── mock_responses/
```

#### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch
from proxmox_ai.core.hardware_detector import HardwareDetector

class TestHardwareDetector:
    """Test suite for hardware detection functionality."""
    
    @pytest.fixture
    def detector(self):
        """Create hardware detector for testing."""
        return HardwareDetector()
    
    def test_detect_hardware_success(self, detector):
        """Test successful hardware detection."""
        with patch('psutil.cpu_count', return_value=8):
            with patch('psutil.virtual_memory') as mock_memory:
                mock_memory.return_value.total = 16 * 1024**3  # 16GB
                specs = detector.detect_hardware()
                assert specs.cpu_cores == 8
                assert specs.memory_gb == 16.0
    
    def test_detect_hardware_failure(self, detector):
        """Test hardware detection error handling."""
        with patch('psutil.cpu_count', side_effect=Exception("Hardware error")):
            with pytest.raises(DetectionError):
                detector.detect_hardware()
```

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/security/

# Run tests with specific markers
pytest -m "not slow"
pytest -m "security"
```

### 4. Documentation Contributions

#### Documentation Structure

```
docs/
├── user-guides/            # User documentation by skill level
├── api/                    # API documentation
├── architecture/           # Technical architecture
├── operations/             # Installation and operations
├── security/               # Security documentation
├── troubleshooting/        # Common issues and solutions
└── examples/               # Code examples and tutorials
```

#### Documentation Standards

- **Clarity**: Write for your target audience (beginner/intermediate/expert)
- **Examples**: Include practical, working examples
- **Maintenance**: Keep documentation updated with code changes
- **Accessibility**: Use clear headings, lists, and formatting

#### Building Documentation

```bash
# Build documentation locally
mkdocs serve

# Build for production
mkdocs build
```

## 🔒 Security Considerations

### Security-First Development

- **Credential handling**: Never log or expose sensitive information
- **Input validation**: Validate all user inputs and file contents
- **Dependency management**: Regularly update and audit dependencies
- **Local processing**: Ensure all AI processing remains local
- **Network security**: Secure all network communications

### Security Review Process

All contributions undergo security review:

1. **Automated security scanning**: Bandit, safety, and dependency checks
2. **Manual code review**: Security-focused code review
3. **Testing**: Security-specific test cases
4. **Documentation**: Security implications documented

### Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities.

Instead, please email security@proxmox-ai.local with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact assessment
- Suggested fix (if available)

We will respond within 48 hours and work with you to resolve the issue.

## 🎨 UI/UX Contributions

### CLI User Experience

- **Consistency**: Consistent command structure and options
- **Helpfulness**: Clear help text and examples
- **Feedback**: Appropriate progress indicators and status messages
- **Error handling**: Helpful error messages with suggested solutions

### Output Formatting

- **Skill-level appropriate**: Adapt complexity to user skill level
- **Actionable**: Provide clear next steps
- **Structured**: Use consistent formatting and organization
- **Accessible**: Support different output formats (text, JSON, etc.)

## 📊 Performance Considerations

### Local AI Optimization

- **Memory efficiency**: Minimize memory usage for broader hardware support
- **Response time**: Optimize for reasonable response times
- **Hardware utilization**: Efficient use of available CPU/GPU resources
- **Caching**: Intelligent caching to improve performance

### Code Performance

- **Async operations**: Use async/await for I/O operations
- **Resource management**: Proper cleanup of resources
- **Caching**: Cache expensive operations where appropriate
- **Profiling**: Profile performance-critical code paths

## 🚦 Pull Request Process

### Before Submitting

1. **Rebase your branch**: Keep your branch up to date with main
2. **Run all tests**: Ensure the test suite passes
3. **Update documentation**: Include relevant documentation updates
4. **Security check**: Run security scans
5. **Self-review**: Review your own code for quality and clarity

### Pull Request Template

When creating a PR, please include:

```markdown
## Description
Brief description of the changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Security enhancement

## Testing
- [ ] Added unit tests for new functionality
- [ ] Added integration tests where applicable
- [ ] All existing tests pass
- [ ] Tested on multiple hardware configurations (if applicable)

## Security
- [ ] No sensitive information exposed
- [ ] Input validation implemented
- [ ] Security implications documented
- [ ] Dependencies updated and scanned

## Documentation
- [ ] Code is self-documenting with clear docstrings
- [ ] User documentation updated (if applicable)
- [ ] API documentation updated (if applicable)
- [ ] Examples updated (if applicable)

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Rebased on latest main branch
- [ ] Commit messages are clear and descriptive
```

### Review Process

1. **Automated checks**: CI/CD pipeline runs automated tests and checks
2. **Community review**: Other contributors may review and comment
3. **Maintainer review**: Project maintainers perform final review
4. **Security review**: Security-focused review for sensitive changes
5. **Merge**: Approved changes are merged to main branch

## 🏆 Recognition

### Contributors

We recognize contributions in several ways:
- **Contributors file**: All contributors are listed
- **Release notes**: Significant contributions highlighted
- **Community recognition**: Recognition in community channels

### Types of Recognition

- **Code contributors**: Direct code contributions
- **Documentation contributors**: Documentation improvements
- **Community helpers**: Helping others in issues and discussions
- **Security researchers**: Responsible disclosure of security issues
- **Testers**: Finding and reporting bugs
- **Advocates**: Promoting the project and helping users

## 🤝 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- **Be respectful**: Treat everyone with respect and kindness
- **Be inclusive**: Welcome newcomers and different perspectives
- **Be collaborative**: Work together constructively
- **Be patient**: Help others learn and grow
- **Be professional**: Maintain professional conduct in all interactions

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests, discussions
- **GitHub Discussions**: General questions and community discussions
- **Pull Requests**: Code contributions and reviews
- **Security**: security@proxmox-ai.local for security issues

### Getting Help

- **Documentation**: Check existing documentation first
- **Search issues**: Look for existing issues and discussions
- **Ask questions**: Create a discussion or issue for help
- **Community**: Engage with the community for support

## 📅 Release Process

### Release Cycle

- **Semantic versioning**: We follow semantic versioning (MAJOR.MINOR.PATCH)
- **Release schedule**: Regular releases with security patches as needed
- **LTS versions**: Long-term support for major versions

### Release Types

- **Major releases**: Breaking changes, new major features
- **Minor releases**: New features, improvements
- **Patch releases**: Bug fixes, security patches

## 🎯 Roadmap and Priorities

### Current Focus Areas

1. **Hardware optimization**: Expanding support for different hardware configurations
2. **AI model improvements**: Better model selection and optimization
3. **Security enhancements**: Continuous security improvements
4. **Documentation**: Comprehensive documentation for all skill levels
5. **Testing**: Expanding test coverage and automation
6. **Performance**: Optimizing for better performance and resource usage

### Future Directions

- **Plugin system**: Extensible architecture for custom integrations
- **Advanced AI features**: More sophisticated AI capabilities
- **Cloud integration**: Optional cloud integrations while maintaining local-first approach
- **Multi-language support**: Support for additional programming languages
- **Enterprise features**: Advanced features for enterprise deployments

## 📞 Contact

For questions about contributing:
- **General questions**: Create a GitHub discussion
- **Technical questions**: Create a GitHub issue
- **Security issues**: security@proxmox-ai.local
- **Maintainers**: Contact through GitHub

Thank you for contributing to making infrastructure automation accessible to everyone!

---

**Remember**: Every contribution, no matter how small, makes a difference. Welcome to the community!