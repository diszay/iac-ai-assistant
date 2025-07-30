# 📚 Documentation Index

Welcome to the comprehensive documentation for the **Proxmox AI Infrastructure Assistant**. This index will help you find exactly what you need.

## 🚀 Getting Started

- **[GETTING_STARTED.md](../GETTING_STARTED.md)** - Complete setup and installation guide
- **[README.md](../README.md)** - Project overview and quick start
- **[setup/](setup/)** - Detailed setup and configuration guides

## 📖 User Guides

### By Skill Level
- **[Beginner Guide](user-guides/beginner.md)** - New to IaC? Start here!
- **[Intermediate Guide](user-guides/intermediate.md)** - Production-ready workflows
- **[Expert Guide](user-guides/expert.md)** - Advanced enterprise configurations

### By Topic
- **[CLI Reference](cli-reference.md)** - Complete command documentation
- **[Operations Guide](operations/installation.md)** - Installation and maintenance
- **[Training Materials](training/)** - Workshops and learning resources

## 🏗️ Architecture & Technical Docs

- **[Architecture Overview](architecture/overview.md)** - System design and components
- **[Technical Architecture](architecture/technical-architecture.md)** - Detailed technical specs
- **[Decision Records](architecture/decision-records/)** - Architectural decisions (ADRs)
- **[API Reference](api/)** - API documentation and authentication

## 🔒 Security Documentation

- **[Security Overview](../SECURITY.md)** - Security policies and procedures
- **[Local AI Privacy](security/local-ai-privacy.md)** - Privacy benefits of local AI
- **[Security Assessment](security/assessment.md)** - Security implementation details
- **[Security Runbooks](security/runbooks/)** - Incident response and procedures
- **[Test Reports](security/)** - Security validation and test results

## 🛠️ Setup & Deployment

- **[Setup Guides](setup/)** - Installation and configuration
  - [GitOps Setup](setup/GITOPS_SETUP.md)
  - [Workflow Setup](setup/WORKFLOW_SETUP.md)
- **[Deployment Guides](deployment/)** - Production deployment
- **[Configuration Examples](../config/)** - Sample configurations

## 🧩 Troubleshooting & Support

- **[Common Issues](troubleshooting/common-issues.md)** - FAQ and solutions
- **[AI Models Issues](troubleshooting/ai-models.md)** - Local AI troubleshooting
- **[Hardware Issues](troubleshooting/hardware.md)** - Hardware-specific problems
- **[Knowledge Base](knowledge-base/)** - Searchable solutions

## 🎯 Project Management

- **[Project Activity](project-management/activity.md)** - Development timeline
- **[Master Plan](project-management/master-plan.md)** - Strategic roadmap
- **[Security Requirements](project-management/security-requirements-spec.md)** - Security specifications
- **[Risk Assessment](project-management/risk-assessment-mitigation.md)** - Risk management
- **[Agent Coordination](project-management/agent-coordination-matrix.md)** - Team structure

## 🔄 Development & Contributing

- **[Contributing Guide](../CONTRIBUTING.md)** - How to contribute
- **[Development Setup](setup/)** - Developer environment setup
- **[Testing Documentation](../tests/)** - Testing frameworks and procedures
- **[License](../LICENSE)** - MIT License

## 📊 Quick Reference

### Most Common Tasks

1. **First Time Setup**: [GETTING_STARTED.md](../GETTING_STARTED.md)
2. **Generate Infrastructure**: [CLI Reference](cli-reference.md) → AI Commands
3. **Troubleshoot Issues**: [Troubleshooting](troubleshooting/common-issues.md)
4. **Security Best Practices**: [Security Overview](../SECURITY.md)
5. **Advanced Configuration**: [Expert Guide](user-guides/expert.md)

### Command Quick Reference

```bash
# System status and health
python -m src.proxmox_ai.cli.main status
python -m src.proxmox_ai.cli.main doctor

# AI code generation
python -m src.proxmox_ai.cli.main ai generate terraform "description" --skill level
python -m src.proxmox_ai.cli.main ai generate ansible "description" --skill level

# Configuration management
python -m src.proxmox_ai.cli.main config show
python -m src.proxmox_ai.cli.main config test
```

## 🎓 Learning Path

### New Users (Beginner)
1. Read [GETTING_STARTED.md](../GETTING_STARTED.md)
2. Follow [Beginner Guide](user-guides/beginner.md)
3. Try basic AI generation commands
4. Review [Common Issues](troubleshooting/common-issues.md)

### Experienced Users (Intermediate)
1. Review [Intermediate Guide](user-guides/intermediate.md)
2. Study [Architecture Overview](architecture/overview.md)
3. Explore [Security Documentation](security/)
4. Set up production workflows

### Power Users (Expert)
1. Master [Expert Guide](user-guides/expert.md)
2. Understand [Technical Architecture](architecture/technical-architecture.md)
3. Contribute using [Contributing Guide](../CONTRIBUTING.md)
4. Help others in the community

## 🔍 Search Tips

- Use your browser's search function (Ctrl+F) within documents
- Check the [Knowledge Base](knowledge-base/) for searchable solutions
- Look at similar issues in [Troubleshooting](troubleshooting/)
- Check [CLI Reference](cli-reference.md) for specific commands

## 💡 Need Help?

1. **Documentation Issue?** Check if answer exists in this index
2. **Setup Problem?** Start with [Troubleshooting](troubleshooting/common-issues.md)
3. **Feature Question?** Review [CLI Reference](cli-reference.md)
4. **Bug Report?** See [Contributing Guide](../CONTRIBUTING.md)
5. **Security Concern?** Read [Security Policy](../SECURITY.md)

---

**Last Updated**: Documentation is continuously updated with new features and improvements.

**Navigation Tip**: Use the browser's back button to return to this index from any documentation page.