# GitHub Configuration

This directory contains configuration files for GitHub features.

## Dependabot Configuration

The `dependabot.yml` file configures [Dependabot](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/about-dependabot-version-updates), GitHub's automated dependency update tool. It helps keep the project's dependencies up-to-date by automatically creating pull requests when new versions are available.

### Current Configuration

The Dependabot configuration monitors:

1. **Python Dependencies**: Checks for updates to Python packages in `pyproject.toml` weekly.
2. **GitHub Actions**: Monitors GitHub Actions workflows for updates weekly (will be active when workflows are added).
3. **Pre-commit Hooks**: Checks for updates to pre-commit hooks in `.pre-commit-config.yaml` weekly.

Minor and patch dependency updates are configured to **automatically merge** after passing checks, using a squash merge strategy. Major updates, which might contain breaking changes, will create pull requests for manual review but won't be auto-merged. This approach reduces maintenance overhead by automatically applying non-breaking updates while ensuring breaking changes receive proper review.

### Benefits

- Keeps dependencies secure by updating to versions with security fixes
- Reduces technical debt by preventing dependencies from becoming outdated
- Automates the tedious task of updating dependencies
- Allows for controlled review of updates through pull requests
- Minimizes maintenance overhead with automatic merging of non-breaking updates

### Customization

To modify the Dependabot configuration, edit the `.github/dependabot.yml` file. See the [Dependabot documentation](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file) for all available options.
