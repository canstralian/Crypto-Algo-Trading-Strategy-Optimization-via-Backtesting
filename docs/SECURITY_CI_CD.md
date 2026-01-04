# CI/CD Security Best Practices

This document outlines security best practices for our CI/CD pipelines and provides guidance on maintaining secure GitHub Actions workflows.

## Table of Contents

- [GitHub Actions Security](#github-actions-security)
  - [Why Pin Actions to Commit SHAs](#why-pin-actions-to-commit-shas)
  - [How to Verify Commit SHAs](#how-to-verify-commit-shas)
  - [Finding Commit SHAs for Action Tags](#finding-commit-shas-for-action-tags)
- [Secret Management](#secret-management)
- [Dependency Security](#dependency-security)
- [Branch Protection](#branch-protection)
- [Token Permissions](#token-permissions)
- [Periodic Security Reviews](#periodic-security-reviews)

## GitHub Actions Security

### Why Pin Actions to Commit SHAs

GitHub Actions can be referenced using tags (e.g., `v3`), branches (e.g., `main`), or specific commit SHAs. While tags and branches are convenient, they are **mutable** and can be changed by action maintainers or compromised by attackers. This poses a security risk:

- **Tag Hijacking**: An attacker who compromises an action repository could update a tag to point to malicious code
- **Supply Chain Attacks**: Malicious updates to popular actions could compromise your CI/CD pipeline
- **Reproducibility**: Using commit SHAs ensures your workflows run the exact same code every time

**Best Practice**: Always pin third-party GitHub Actions to specific commit SHAs for production workflows.

### How to Verify Commit SHAs

Before pinning an action to a commit SHA, you should verify that the SHA corresponds to the expected version and hasn't been tampered with.

#### Method 1: Using `git ls-remote`

The `git ls-remote` command allows you to query a remote Git repository without cloning it:

```bash
# Get the commit SHA for a specific tag
git ls-remote https://github.com/actions/checkout.git | grep "refs/tags/v3$"
# Output: f43a0e5ff2bd294095638e18286ca9a3d1956744	refs/tags/v3

# Get the commit SHA for a branch
git ls-remote https://github.com/actions/checkout.git | grep "refs/heads/main"
# Output: <commit-sha>	refs/heads/main

# List all tags to find the latest version
git ls-remote https://github.com/actions/checkout.git | grep "refs/tags/" | grep -v "\^{}"
```

#### Method 2: Using GitHub Web Interface

1. Navigate to the action's GitHub repository (e.g., https://github.com/actions/checkout)
2. Click on the "Tags" or "Releases" tab
3. Find the desired version (e.g., `v3`)
4. Click on the tag to see the commit it points to
5. Copy the full commit SHA (40 characters)

#### Method 3: Using GitHub API

```bash
# Get tag information via GitHub API
curl -s https://api.github.com/repos/actions/checkout/git/refs/tags/v3 | jq -r '.object.sha'
```

### Finding Commit SHAs for Action Tags

Here's a step-by-step guide to finding the commit SHA for a specific action version:

#### Example: Finding the SHA for `actions/checkout@v3`

1. **Identify the action repository**: `https://github.com/actions/checkout`

2. **Use git ls-remote to find the commit SHA**:
   ```bash
   git ls-remote https://github.com/actions/checkout.git | grep "refs/tags/v3$"
   ```
   
3. **Verify the output**:
   ```
   f43a0e5ff2bd294095638e18286ca9a3d1956744	refs/tags/v3
   ```
   
4. **Use the full SHA in your workflow**:
   ```yaml
   - uses: actions/checkout@f43a0e5ff2bd294095638e18286ca9a3d1956744  # v3
   ```
   
   **Note**: Always include a comment with the tag/version for maintainability.

#### Example: Finding the SHA for a minor version

If you want to pin to a specific minor version (e.g., `v3.1.0`):

```bash
# List all v3.x tags
git ls-remote https://github.com/actions/checkout.git | grep "refs/tags/v3\."

# Find specific version
git ls-remote https://github.com/actions/checkout.git | grep "refs/tags/v3.1.0$"
```

#### Example: Verifying multiple actions at once

Create a script to verify all actions in your workflow:

```bash
#!/bin/bash
# verify-actions.sh

declare -A actions=(
    ["actions/checkout"]="v3"
    ["actions/setup-python"]="v4"
    ["actions/cache"]="v3"
)

for action in "${!actions[@]}"; do
    version="${actions[$action]}"
    echo "Checking $action@$version"
    git ls-remote https://github.com/$action.git | grep "refs/tags/${version}$"
    echo ""
done
```

### Updating Pinned Actions

When using commit SHAs, you need a process to update them:

1. **Enable Dependabot**: Configure `.github/dependabot.yml` to automatically check for updates
2. **Review Updates**: When Dependabot creates a PR, review the changes carefully
3. **Test Thoroughly**: Ensure updated actions don't break your workflows
4. **Update Comments**: Keep version comments in sync with the actual version

Example Dependabot configuration:

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "github-actions"
```

## Secret Management

### Scanning for Secrets

Our CI/CD pipeline includes automated secret scanning using TruffleHog:

```yaml
- name: Run trufflehog scans
  uses: trufflesecurity/trufflehog@<commit-sha>
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
    scan_folder: ./
```

This scan runs on every pull request to detect accidentally committed secrets before they reach the main branch.

### Best Practices for Secrets

1. **Never commit secrets** to version control
2. **Use GitHub Secrets** for storing sensitive data
3. **Rotate secrets regularly** (at least quarterly)
4. **Use environment-specific secrets** (dev, staging, prod)
5. **Limit secret scope** - only grant access to workflows that need them
6. **Audit secret usage** - regularly review which workflows have access to secrets

### If a Secret is Leaked

1. **Immediately revoke** the compromised credential
2. **Rotate the secret** with a new value
3. **Review access logs** for unauthorized usage
4. **Update the secret** in GitHub Secrets
5. **Investigate** how the leak occurred and prevent recurrence

## Dependency Security

### Automated Dependency Scanning

We use multiple tools to ensure dependency security:

1. **pip-audit**: Scans Python dependencies for known vulnerabilities
   ```yaml
   - name: Audit Python dependencies
     uses: pypa/gh-action-pip-audit@<commit-sha>
     with:
       inputs: requirements.txt requirements-dev.txt
   ```

2. **Trivy**: Comprehensive vulnerability scanner for containers and dependencies
   ```yaml
   - name: Run Trivy scanner
     uses: aquasecurity/trivy-action@<commit-sha>
   ```

3. **Dependabot**: Automated dependency updates
   - Configured to check weekly for updates
   - Creates PRs for vulnerable dependencies
   - Supports Python, Docker, and GitHub Actions

### Dependency Best Practices

1. **Pin exact versions** in production (e.g., `package==1.2.3`)
2. **Review dependency updates** before merging
3. **Test thoroughly** after dependency updates
4. **Minimize dependencies** - fewer dependencies = smaller attack surface
5. **Use virtual environments** to isolate dependencies
6. **Scan regularly** - don't wait for Dependabot alerts

### Handling Vulnerability Alerts

When a vulnerability is detected:

1. **Assess severity** - Critical/High should be addressed immediately
2. **Check for patches** - Update to a patched version if available
3. **Find alternatives** - If no patch exists, consider alternative packages
4. **Apply workarounds** - Implement temporary mitigations if needed
5. **Document decisions** - Record why certain vulnerabilities are accepted

## Branch Protection

### Required Settings

Configure branch protection for critical branches (`main`, `develop`, `production`):

1. **Require pull request reviews**
   - At least 1 approving review
   - Dismiss stale reviews on new commits
   - Require review from code owners

2. **Require status checks**
   - All CI tests must pass
   - Branch must be up to date before merging

3. **Require signed commits**
   - Ensures commit authenticity
   - Prevents commit tampering

4. **Prevent force pushes**
   - Protects against accidental history rewrites
   - Maintains audit trail

5. **Restrict who can push**
   - Limit to specific users or teams
   - Prevent accidental direct pushes

### Configuration Example

Navigate to: `Settings → Branches → Branch protection rules`

```
Branch name pattern: main

☑ Require a pull request before merging
  ☑ Require approvals: 1
  ☑ Dismiss stale pull request approvals when new commits are pushed
  ☑ Require review from Code Owners

☑ Require status checks to pass before merging
  ☑ Require branches to be up to date before merging
  Status checks:
    - test
    - security
    - build

☑ Require signed commits
☑ Include administrators
☑ Restrict who can push to matching branches
```

## Token Permissions

### GitHub Token Security

GitHub Actions provides a `GITHUB_TOKEN` for authentication. Follow these best practices:

1. **Use minimum required permissions**
   ```yaml
   permissions:
     contents: read      # Read repository contents
     pull-requests: read # Read PR information
     # Never grant 'write' unless absolutely necessary
   ```

2. **Explicitly declare permissions** per job
   ```yaml
   jobs:
     test:
       permissions:
         contents: read
         checks: write  # Only for publishing test results
       steps:
         # ...
   ```

3. **Use read-only tokens by default**
   ```yaml
   permissions: read-all
   ```

4. **Avoid workflow-level write permissions**
   - Grant write access only to specific jobs that need it
   - Reduces blast radius if workflow is compromised

### Third-Party Token Integration

When integrating with external services:

1. **Use short-lived tokens** when possible (e.g., OIDC)
2. **Rotate regularly** - Set expiration dates
3. **Scope narrowly** - Grant minimum required permissions
4. **Use separate tokens** for dev/staging/prod
5. **Monitor usage** - Review audit logs for anomalies

### OIDC Authentication

For cloud providers (AWS, GCP, Azure), use OpenID Connect instead of long-lived credentials:

```yaml
jobs:
  deploy:
    permissions:
      id-token: write  # Required for OIDC
      contents: read
    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
          aws-region: us-east-1
```

Benefits:
- No long-lived credentials stored in GitHub Secrets
- Automatic token rotation
- Fine-grained access control via IAM policies

## Periodic Security Reviews

### Weekly Reviews

- [ ] Review Dependabot PRs and merge approved updates
- [ ] Check for new security advisories in GitHub Security tab
- [ ] Verify all CI/CD workflows completed successfully

### Monthly Reviews

- [ ] Audit GitHub Actions workflow permissions
- [ ] Review access to GitHub Secrets
- [ ] Check for outdated pinned action SHAs
- [ ] Review branch protection rules
- [ ] Audit user access and permissions

### Quarterly Reviews

- [ ] Rotate all secrets and tokens
- [ ] Review and update security documentation
- [ ] Conduct security training for team members
- [ ] Perform dependency audit (even for non-vulnerable packages)
- [ ] Review and update incident response procedures

### Annual Reviews

- [ ] Complete security assessment of entire CI/CD pipeline
- [ ] Update security policies and procedures
- [ ] Review compliance with security standards (SOC 2, ISO 27001, etc.)
- [ ] Conduct penetration testing of deployment infrastructure
- [ ] Review and update disaster recovery plans

## Security Incident Response

### Workflow Compromise

If you suspect a workflow has been compromised:

1. **Immediately disable** the workflow
2. **Revoke all secrets** used by the workflow
3. **Review workflow run logs** for suspicious activity
4. **Audit recent changes** to workflow files
5. **Investigate** how the compromise occurred
6. **Remediate** the vulnerability
7. **Re-enable** only after thorough review

### Dependency Compromise

If a dependency is compromised:

1. **Remove or downgrade** the affected dependency immediately
2. **Scan codebase** for signs of malicious code execution
3. **Review deployment history** to identify affected deployments
4. **Rollback** affected deployments if necessary
5. **Communicate** with stakeholders about potential impact
6. **Document** the incident and lessons learned

## Additional Resources

- [GitHub Actions Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [OWASP CI/CD Security Cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/CI_CD_Security_Cheat_Sheet.html)
- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [TruffleHog Documentation](https://github.com/trufflesecurity/trufflehog)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

## Questions or Concerns?

If you have questions about CI/CD security or notice potential security issues, please:

1. **For general questions**: Open a discussion in the repository
2. **For security vulnerabilities**: Follow our [Security Policy](../SECURITY.md) (if it exists) or contact the maintainers privately
3. **For urgent security incidents**: Contact the security team immediately

---

**Last Updated**: 2026-01-04  
**Document Owner**: DevOps/Security Team  
**Review Frequency**: Quarterly
