# AI-Powered Telegram Chart-Analysis Bot with Taskade Orchestration

## Purpose and Scope
- Deliver a modular, agentic chart-analysis bot for the Trading Bot Swarm ecosystem where **Telegram is the interface**, **Taskade** runs automations, coordination, and storage, and **AI models** provide reasoning.
- Codify strict configuration and behavior for **GitHub Copilot** and **Codex** to act as disciplined pair programmers: adhere to lint/tests by default, respect security defaults, and avoid generating risky code.
- Standardize quality gates (lint, tests, release, security scans) so contributions remain reliable, performant, and safe.

## System Overview: Taskade + Telegram + Multi-Agent Team
- **Data flow**: Telegram receives chart screenshots → Taskade webhook intake → multi-agent workflow → consolidated analysis returned to Telegram.
- **Core agents inside Taskade**:
  - **Vision agent**: extract chart structure, indicators, overlays, annotations.
  - **Market-structure agent**: trends, key levels, patterns (HTF/LTF alignment).
  - **Momentum/indicator agent**: RSI/MACD/oscillators, divergences, volume profile notes.
  - **Scenario agent**: bullish/bearish pathways, invalidation triggers, catalyst watch.
  - **Risk agent**: uncertainty flags, low-signal environments, data-quality warnings.
  - **Memory agent**: maintains chart history, conversation context, and previous calls.
- **Taskade automations**:
  - **Webhook intake** from Telegram (file + message payload) to Taskade project.
  - **Trigger** multi-agent workflow on new item; pass attachment URLs/metadata to Vision agent.
  - **Routing** intermediate outputs between agents; aggregate into final report.
  - **Return** final analysis to Telegram via webhook/HTTP response; emit alerts or dashboard updates.
- **Taskade as backend**: no hosting required; use Taskade for state storage, workflow dashboards, audit trails, and expansion (alerts/tools).

## Configuration Overview for Copilot/Codex in Trading Bot Swarm
- **Testing & linting**: always propose running unit tests, integration tests, and linters when code changes; documentation-only changes can skip.
- **Code style**: follow project formatters (e.g., `black`, `ruff`, `isort`) and typing via `mypy`; prefer small, composable functions.
- **Async patterns**: use `asyncio`/`aiohttp`/`httpx` with cancellation handling, timeouts, and context managers; avoid blocking calls in async flows.
- **Security defaults**: prefer parameterized queries, secret management via env/Taskade vaults, input validation, least privilege for tokens/webhooks.
- **Logging & observability**: use structured logging, correlation IDs per Telegram message/task, and emit metrics for agent runtimes and errors.
- **CI/CD integration**: PRs must pass lint/test workflows; semantic versioning; protected branches require reviews and green checks.
- **Version control**: keep PRs small; reference issue/task IDs; avoid committing secrets or large binaries; update changelog on releases.

## Custom Instruction Behavior for Codex and Copilot
- **Behavioral rules**:
  - Default to safe, minimal-scopes changes; never auto-create credentials or disable security checks.
  - Suggest tests for every code change; explicitly state when no tests apply (e.g., docs-only).
  - Keep comments concise; prefer code clarity over verbose narration.
  - Respect Taskade workflow contracts (input/output schemas, webhook signatures).
  - Avoid speculative trading advice; focus on analysis mechanics.
- **Example custom instructions (conceptual YAML)**:
  ```yaml
  copilot:
    role: "Pair programmer for Trading Bot Swarm"
    defaults:
      enforce_linters: true
      enforce_tests: true
      skip_when_docs_only: true
    security:
      avoid_secrets_in_code: true
      prefer_env_vars: true
      validate_inputs: true
    style:
      formatter: black
      linter: ruff
      typing: mypy
      async_guidelines: "timeouts, cancellation, context managers"
    review:
      checklist:
        - confirm tests suggested
        - confirm security posture preserved
        - confirm logging uses structured fields
  codex:
    role: "Code generation under review gate"
    defaults:
      propose_test_names: true
      include_lint_commands: true
    boundaries:
      no_sensitive_data: true
      no_auto_credentials: true
    taskade:
      webhook_contract: "telegram_payload -> vision -> market -> momentum -> scenario -> risk -> memory -> summary"
  ```
- **Key reminder**: Always run or suggest `pytest`/`ruff`/`mypy` for code changes; doc-only edits can omit.

## GitHub Workflow: Lint and Test Automation

### Current CI/CD Pipeline Configuration

The repository uses GitHub Actions with a comprehensive CI/CD pipeline (`.github/workflows/ci-cd.yml`) that includes:

- **Triggers**: 
  - `push` to `main` and `develop` branches
  - `pull_request` to `main` and `develop` branches
  - `release` events (created)

- **Quality Gate Job** (Multi-Python version testing):
  ```yaml
  name: CI/CD Pipeline
  on:
    push:
      branches: [ main, develop ]
    pull_request:
      branches: [ main, develop ]
    release:
      types: [ created ]
  
  jobs:
    test:
      name: Test Suite
      runs-on: ubuntu-latest
      strategy:
        matrix:
          python-version: ['3.9', '3.10', '3.11']
      
      steps:
        - uses: actions/checkout@v3
        
        - name: Set up Python ${{ matrix.python-version }}
          uses: actions/setup-python@v4
          with:
            python-version: ${{ matrix.python-version }}
        
        - name: Cache pip packages
          uses: actions/cache@v3
          with:
            path: ~/.cache/pip
            key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
        
        - name: Install dependencies
          run: |
            python -m pip install --upgrade pip
            pip install -r requirements.txt
            pip install -r requirements-dev.txt
        
        - name: Create required directories
          run: mkdir -p data logs cache config
        
        - name: Lint with flake8
          run: |
            flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
            flake8 src/ --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics
        
        - name: Format check with black
          run: black --check src/ tests/
        
        - name: Type check with mypy
          continue-on-error: true
          run: mypy src/ --ignore-missing-imports
        
        - name: Security check with bandit
          run: bandit -r src/ -f json -o bandit-report.json
          continue-on-error: true
        
        - name: Run tests with pytest
          run: |
            pytest tests/ -v --cov=src --cov-report=xml --cov-report=html --cov-report=term
        
        - name: Upload coverage to Codecov
          uses: codecov/codecov-action@v3
          with:
            file: ./coverage.xml
            flags: unittests
  ```

### Security Scanning Job

The pipeline includes dedicated security scanning with Trivy:

```yaml
security:
  name: Security Scan
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy results to GitHub Security
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
```

### Docker Build and Deploy Jobs

The pipeline automatically builds Docker images and deploys on releases:

```yaml
build:
  name: Build Docker Image
  runs-on: ubuntu-latest
  needs: test
  if: github.event_name == 'push' || github.event_name == 'release'
  
  steps:
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Docker Hub
      if: github.event_name == 'release'
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        push: ${{ github.event_name == 'release' }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

deploy:
  name: Deploy to Production
  needs: [test, build]
  if: github.event_name == 'release'
  environment:
    name: production
```

### Recommended Enhancements for Bot Integration

For Telegram/Taskade bot workflows, consider adding:

```yaml
name: bot-integration-tests
on:
  pull_request:
    paths:
      - 'src/bot/**'
      - 'src/agents/**'
  
jobs:
  test-bot:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Mock Telegram API Tests
        run: |
          pytest tests/bot/ -v -k telegram
      
      - name: Mock Taskade Integration Tests
        run: |
          pytest tests/bot/ -v -k taskade
      
      - name: Agent Workflow Tests
        run: |
          pytest tests/agents/ -v --timeout=60
```

## Semantic Release and Version Tagging (Best Practices)

### Overview
Use **semantic versioning** (MAJOR.MINOR.PATCH) to communicate changes clearly:
- **MAJOR**: Breaking changes or incompatible API changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/) for automated versioning:

```bash
# Features (MINOR bump)
git commit -m "feat: add vision agent chart extraction"
git commit -m "feat(telegram): support batch chart upload"

# Fixes (PATCH bump)
git commit -m "fix: resolve webhook signature validation"
git commit -m "fix(agent): prevent memory agent context overflow"

# Breaking changes (MAJOR bump)
git commit -m "feat!: redesign agent communication protocol"
git commit -m "BREAKING CHANGE: taskade webhook payload structure changed"

# Other types (no version bump)
git commit -m "docs: update troubleshooting guide"
git commit -m "chore: update dependencies"
git commit -m "test: add integration tests for momentum agent"
git commit -m "ci: update GitHub Actions to v4"
```

### Automated Release Workflow

For projects using semantic-release, create `.github/workflows/release.yml`:

```yaml
name: Semantic Release
on:
  push:
    branches: 
      - main

jobs:
  release:
    name: Create Release
    runs-on: ubuntu-latest
    permissions:
      contents: write
      issues: write
      pull-requests: write
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for changelog
          persist-credentials: false
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install semantic-release
        run: |
          npm install -g \
            semantic-release@^22.0.0 \
            @semantic-release/git@^10.0.0 \
            @semantic-release/github@^9.0.0 \
            @semantic-release/changelog@^6.0.0 \
            @semantic-release/exec@^6.0.0
      
      - name: Verify installation
        run: semantic-release --version
      
      - name: Release
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: semantic-release
```

### Semantic Release Configuration

Create `.releaserc.json` in repository root:

```json
{
  "branches": ["main"],
  "plugins": [
    "@semantic-release/commit-analyzer",
    "@semantic-release/release-notes-generator",
    [
      "@semantic-release/changelog",
      {
        "changelogFile": "CHANGELOG.md"
      }
    ],
    [
      "@semantic-release/git",
      {
        "assets": ["CHANGELOG.md", "package.json"],
        "message": "chore(release): ${nextRelease.version} [skip ci]\n\n${nextRelease.notes}"
      }
    ],
    "@semantic-release/github"
  ]
}
```

### Manual Release Process (Alternative)

If not using automated semantic-release:

```bash
# 1. Update version
echo "1.2.3" > VERSION

# 2. Update CHANGELOG.md
# Add section for new version with changes

# 3. Commit changes
git add VERSION CHANGELOG.md
git commit -m "chore: bump version to 1.2.3"

# 4. Create tag
git tag -a v1.2.3 -m "Release v1.2.3"

# 5. Push with tags
git push origin main --tags
```

### Release Checklist

Before creating a release:

- [ ] All tests passing on main branch
- [ ] Security scans completed with no critical issues
- [ ] Documentation updated for new features
- [ ] CHANGELOG.md updated with changes
- [ ] Version number follows semantic versioning
- [ ] Breaking changes clearly documented
- [ ] Migration guide provided (if needed)
- [ ] Docker images built and tested
- [ ] Release notes prepared

### Protected Branch Configuration

Configure branch protection for release integrity:

```yaml
# GitHub repository settings
main:
  required_status_checks:
    - test (3.9)
    - test (3.10)
    - test (3.11)
    - security
  required_approving_reviews: 1
  dismiss_stale_reviews: true
  require_code_owner_reviews: true
  required_linear_history: true
  allow_force_pushes: false
  allow_deletions: false
```

### Release Tags and Docker Images

Automatically tag Docker images with version:

```yaml
- name: Docker meta
  id: meta
  uses: docker/metadata-action@v5
  with:
    images: |
      ghcr.io/${{ github.repository }}
    tags: |
      type=semver,pattern={{version}}
      type=semver,pattern={{major}}.{{minor}}
      type=semver,pattern={{major}}
      type=sha,prefix={{branch}}-
      type=raw,value=latest,enable={{is_default_branch}}
```

### Version Compatibility Matrix

Document compatibility in CHANGELOG.md:

| Version | Python | Telegram Bot API | Taskade API | Breaking Changes |
|---------|--------|------------------|-------------|------------------|
| 2.0.0   | 3.9+   | 6.9+             | v2          | Yes - new payload format |
| 1.5.0   | 3.9+   | 6.8+             | v2          | No |
| 1.4.0   | 3.8+   | 6.7+             | v1          | No |

## Security and Dependency Scanning

### Multi-Layered Security Strategy

The repository implements comprehensive security scanning at multiple levels:

#### 1. Static Application Security Testing (SAST)

**Bandit - Python Security Scanner**
```yaml
- name: Security check with bandit
  run: |
    bandit -r src/ -f json -o bandit-report.json
  continue-on-error: true
```

Common issues detected:
- Hardcoded credentials
- Use of `eval()` or `exec()`
- Insecure cryptographic algorithms
- SQL injection vulnerabilities
- Command injection risks

**Configuration** (`.bandit`):
```yaml
exclude_dirs:
  - /tests/
  - /venv/
skips:
  - B101  # assert_used (acceptable in tests)
```

#### 2. Dependency Vulnerability Scanning

**Trivy - Container and Filesystem Scanner**
```yaml
security:
  name: Security Scan
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
        severity: 'CRITICAL,HIGH'
    
    - name: Upload Trivy results to GitHub Security
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
```

**pip-audit - Python Dependency Scanner**
```yaml
- name: Python vulnerability scan
  uses: pypa/gh-action-pip-audit@v1.0.8
  with:
    inputs: requirements.txt requirements-dev.txt
    vulnerability-service: osv
```

#### 3. Secret Scanning

**TruffleHog - Secret Detection**
```yaml
- name: Secret scan
  uses: trufflesecurity/trufflehog@main
  with:
    path: ./
    base: ${{ github.event.repository.default_branch }}
    head: HEAD
```

**GitHub Secret Scanning**
- Enabled in repository settings
- Automatically scans commits for exposed secrets
- Alerts on API keys, tokens, credentials

#### 4. Dependency Review

For pull requests, scan dependency changes:
```yaml
- name: Dependency Review
  uses: actions/dependency-review-action@v4
  with:
    fail-on-severity: high
    allow-licenses: MIT, Apache-2.0, BSD-3-Clause
```

### Security Best Practices

#### Secure Configuration Management

**Environment Variables** (`.env.example`):
```bash
# Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TASKADE_API_KEY=your_taskade_api_key
TASKADE_WEBHOOK_SECRET=your_webhook_secret

# Security
SECRET_KEY=generate_random_secret_key
JWT_SECRET=generate_jwt_secret
WEBHOOK_SIGNATURE_KEY=generate_signature_key

# API Configuration
API_RATE_LIMIT=100
MAX_UPLOAD_SIZE=10485760  # 10MB
```

**Never commit**:
- `.env` files (add to `.gitignore`)
- API keys or tokens
- Private keys or certificates
- Database credentials
- Webhook secrets

#### Input Validation

**Telegram Payload Validation**:
```python
from pydantic import BaseModel, HttpUrl, Field, validator

class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[TelegramMessage]
    
    @validator('update_id')
    def validate_update_id(cls, v):
        if v < 0:
            raise ValueError('Invalid update_id')
        return v

class TelegramMessage(BaseModel):
    message_id: int
    from_user: TelegramUser
    photo: Optional[list[PhotoSize]]
    text: Optional[str] = Field(None, max_length=4096)
    
    @validator('text')
    def sanitize_text(cls, v):
        if v:
            # Remove potentially harmful characters
            return v.strip()[:4096]
        return v
```

**Taskade Webhook Signature Validation**:
```python
import hmac
import hashlib
from fastapi import HTTPException, Header

async def verify_taskade_webhook(
    payload: bytes,
    signature: str = Header(..., alias="X-Taskade-Signature")
):
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature"
        )
```

#### Rate Limiting and DoS Protection

**API Rate Limiting**:
```python
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/webhook/telegram")
@limiter.limit("10/minute")
async def telegram_webhook(request: Request):
    # Process webhook
    pass
```

**File Upload Size Limits**:
```python
from fastapi import UploadFile, HTTPException

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

async def validate_file_upload(file: UploadFile):
    contents = await file.read()
    
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {MAX_FILE_SIZE} bytes"
        )
    
    # Reset file pointer
    await file.seek(0)
    return file
```

#### Secure Communication

**HTTPS Only**:
```python
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)
```

**Security Headers**:
```python
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000'
        return response

app.add_middleware(SecurityHeadersMiddleware)
```

### Security Scanning Schedule

**Automated Scans**:
```yaml
on:
  pull_request:
  push:
    branches: [main, develop]
  schedule:
    - cron: "0 3 * * *"  # Daily at 3 AM UTC
```

**Manual Security Audits**:
- **Weekly**: Review dependency alerts
- **Monthly**: Manual security audit of critical paths
- **Quarterly**: Third-party security assessment
- **Per Release**: Full security scan before production

### Vulnerability Response Process

1. **Detection**: Automated scan or manual report
2. **Assessment**: Evaluate severity and impact
3. **Prioritization**: 
   - Critical: Fix immediately (< 24 hours)
   - High: Fix within 1 week
   - Medium: Fix within 1 month
   - Low: Fix in next release
4. **Remediation**: Apply patches or workarounds
5. **Verification**: Re-scan to confirm fix
6. **Disclosure**: Update security advisory if public

### Security Checklist for PRs

- [ ] No secrets or credentials committed
- [ ] Input validation implemented for new endpoints
- [ ] Authentication/authorization checked
- [ ] Rate limiting applied where needed
- [ ] Error messages don't leak sensitive information
- [ ] Dependencies updated to secure versions
- [ ] HTTPS enforced for external communications
- [ ] SQL queries parameterized (no string concatenation)
- [ ] File uploads validated and sanitized
- [ ] Logging doesn't include sensitive data

### Secure Credential Storage

**Local Development**:
```bash
# Use .env file (gitignored)
cp .env.example .env
vim .env  # Add actual credentials
```

**CI/CD**:
```yaml
# Use GitHub Secrets
- name: Deploy
  env:
    TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
    TASKADE_API_KEY: ${{ secrets.TASKADE_API_KEY }}
```

**Production**:
- Use cloud provider secrets manager (AWS Secrets Manager, GCP Secret Manager)
- Use Taskade vault for bot-specific credentials
- Rotate secrets quarterly or after team changes
- Use different credentials per environment (dev/staging/prod)

### Security Monitoring and Alerting

**GitHub Security Features**:
- Enable Dependabot alerts
- Enable Dependabot security updates
- Configure code scanning alerts
- Review security advisories

**Runtime Security**:
```python
import logging
from functools import wraps

def security_audit_log(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.info(
            "Security event",
            extra={
                "function": func.__name__,
                "user": get_current_user(),
                "ip": get_client_ip(),
                "timestamp": datetime.utcnow()
            }
        )
        return await func(*args, **kwargs)
    return wrapper
```

## Contributor Guidelines

### Getting Started

1. **Fork and Clone**:
   ```bash
   # Fork repository on GitHub
   git clone https://github.com/YOUR_USERNAME/Crypto-Algo-Trading-Strategy-Optimization-via-Backtesting.git
   cd Crypto-Algo-Trading-Strategy-Optimization-via-Backtesting
   
   # Add upstream remote
   git remote add upstream https://github.com/canstralian/Crypto-Algo-Trading-Strategy-Optimization-via-Backtesting.git
   ```

2. **Set Up Development Environment**:
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   
   # Install pre-commit hooks
   pre-commit install
   ```

3. **Create Feature Branch**:
   ```bash
   # Sync with upstream
   git fetch upstream
   git checkout main
   git merge upstream/main
   
   # Create feature branch
   git checkout -b feature/your-feature-name
   ```

### Contribution Workflow

#### 1. Link to Issue or Task

- Create or find an existing issue
- Comment on the issue to indicate you're working on it
- Reference issue number in commits and PR

#### 2. Make Focused Changes

- **Keep PRs small**: 200-300 lines changed maximum
- **Single responsibility**: One feature or fix per PR
- **Update tests**: Add or modify tests for changed code
- **Update docs**: Include documentation for new features

#### 3. Follow Code Standards

**Code Style**:
```bash
# Format code with black
black src/ tests/

# Check with flake8
flake8 src/ tests/ --max-line-length=100

# Type check with mypy
mypy src/ --ignore-missing-imports
```

**Coding Conventions**:
- Use type hints for all function signatures
- Prefer async/await for I/O operations
- Use descriptive variable names
- Add docstrings to public functions
- Keep functions small and focused (< 50 lines)

**Example Function**:
```python
async def analyze_chart_image(
    image_url: str,
    user_id: int,
    correlation_id: str
) -> ChartAnalysis:
    """
    Analyze a trading chart image using vision and analysis agents.
    
    Args:
        image_url: URL to chart image (must be HTTPS)
        user_id: Telegram user ID for tracking
        correlation_id: Unique ID for request tracking
    
    Returns:
        ChartAnalysis object with trend, levels, and confidence
    
    Raises:
        ImageValidationError: If image is invalid or inaccessible
        AnalysisError: If analysis fails
    """
    logger.info(
        "Starting chart analysis",
        extra={"user_id": user_id, "correlation_id": correlation_id}
    )
    
    try:
        # Implementation
        pass
    except Exception as e:
        logger.error(
            "Chart analysis failed",
            extra={"error": str(e), "correlation_id": correlation_id}
        )
        raise
```

#### 4. Ensure Test Coverage

**Run Tests Locally**:
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_agents.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

**Writing Tests**:
```python
import pytest
from unittest.mock import Mock, AsyncMock, patch

class TestChartAnalysis:
    """Test chart analysis functionality"""
    
    @pytest.fixture
    def mock_vision_agent(self):
        """Mock vision agent for testing"""
        agent = AsyncMock()
        agent.analyze.return_value = {
            "chart_type": "candlestick",
            "timeframe": "1h",
            "indicators": ["MA", "RSI"]
        }
        return agent
    
    @pytest.mark.asyncio
    async def test_analyze_valid_chart(self, mock_vision_agent):
        """Test analysis with valid chart image"""
        result = await analyze_chart_image(
            "https://example.com/chart.png",
            user_id=12345,
            correlation_id="test-123"
        )
        
        assert result.trend in ["bullish", "bearish", "neutral"]
        assert 0.0 <= result.confidence <= 1.0
        assert len(result.key_levels) > 0
    
    @pytest.mark.asyncio
    async def test_analyze_invalid_image(self):
        """Test analysis with invalid image URL"""
        with pytest.raises(ImageValidationError):
            await analyze_chart_image(
                "http://invalid-url",  # HTTP not HTTPS
                user_id=12345,
                correlation_id="test-456"
            )
```

#### 5. Taskade Workflow Compatibility

When modifying Telegram intake, agent routing, or output formats:

**Schema Validation**:
```python
from pydantic import BaseModel

class AgentInput(BaseModel):
    """Standard input schema for all agents"""
    chart_data: dict
    context: dict
    previous_results: Optional[dict] = None

class AgentOutput(BaseModel):
    """Standard output schema for all agents"""
    agent_name: str
    result: dict
    confidence: float
    processing_time: float
```

**Backward Compatibility**:
- Maintain existing webhook endpoints
- Add new fields as optional
- Deprecate old endpoints gradually
- Document migration path in CHANGELOG

#### 6. Commit Message Guidelines

Follow Conventional Commits:

```bash
# Feature
git commit -m "feat(vision): add support for logarithmic chart scale"

# Bug fix
git commit -m "fix(telegram): handle rate limit errors gracefully"

# Documentation
git commit -m "docs(api): add webhook authentication examples"

# Tests
git commit -m "test(agents): add integration tests for agent workflow"

# Refactoring
git commit -m "refactor(core): simplify agent communication protocol"

# Breaking change
git commit -m "feat(api)!: redesign webhook payload structure

BREAKING CHANGE: webhook now expects nested message format"
```

### Pull Request Process

#### 1. Create PR

**PR Title**: Follow conventional commits format
```
feat(telegram): add multi-chart batch processing
```

**PR Description Template**:
```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to break)
- [ ] Documentation update

## Related Issue
Fixes #123

## Changes Made
- Added batch processing endpoint
- Updated Telegram webhook handler
- Added rate limiting for batch requests

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
- [ ] All tests passing locally

## Screenshots (if applicable)
[Add screenshots for UI changes]

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added covering changes
- [ ] All tests pass
- [ ] Security implications considered
```

#### 2. Review Criteria

PRs will be reviewed for:

**Code Quality**:
- Follows coding standards
- Proper error handling
- Efficient algorithms
- No code duplication

**Testing**:
- Tests cover new code
- Tests are meaningful
- Edge cases considered
- Tests pass consistently

**Security**:
- No secrets committed
- Input validation present
- Security best practices followed
- Dependencies are secure

**Documentation**:
- Code is well-commented
- API changes documented
- README updated if needed
- CHANGELOG updated

**Taskade Integration**:
- Webhook contracts maintained
- Agent schemas compatible
- Logging includes correlation IDs
- Observability preserved

#### 3. Validation Process

Before PR approval:

```bash
# 1. Run lint checks
flake8 src/ tests/
black --check src/ tests/

# 2. Run type checks
mypy src/

# 3. Run unit tests
pytest tests/unit/ -v

# 4. Run integration tests
pytest tests/integration/ -v

# 5. Check coverage
pytest tests/ --cov=src --cov-report=term

# 6. Security scan
bandit -r src/

# 7. Verify Taskade workflow (staging environment)
# - Test webhook with sample chart
# - Verify agent routing
# - Confirm Telegram roundtrip
```

### Code Review Guidelines

**For Reviewers**:
- Be respectful and constructive
- Focus on code, not the person
- Explain reasoning for suggestions
- Approve or request changes clearly
- Test changes locally when possible

**For Contributors**:
- Respond to all comments
- Ask for clarification if needed
- Make requested changes promptly
- Mark conversations as resolved
- Thank reviewers for their time

### Continuous Improvement

**After PR Merge**:
1. Monitor for issues in production
2. Watch for related bug reports
3. Update documentation if gaps found
4. Consider follow-up improvements

**Learning Resources**:
- [Python Best Practices](https://docs.python-guide.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Taskade API Documentation](https://taskade.com/developers)
- [Conventional Commits](https://www.conventionalcommits.org/)

### Getting Help

- **Questions**: Open a discussion on GitHub
- **Bug Reports**: Create an issue with reproduction steps
- **Feature Requests**: Create an issue with use case details
- **Security Issues**: Email security@example.com (do not open public issue)

## Troubleshooting and Optimization Tips

### Common Issues and Solutions

#### Webhook Integration Problems
- **Failed webhook calls**: 
  - Verify Telegram file URL accessibility and Taskade webhook signature
  - Check webhook endpoint SSL certificate validity
  - Retry with smaller payloads (limit to 5MB for images)
  - Ensure webhook URL is publicly accessible (use ngrok for local testing)
  - Validate webhook secret in environment variables matches Taskade configuration
  - Check firewall rules and network policies
  - Example test:
    ```bash
    curl -X POST https://your-webhook-url/telegram \
      -H "Content-Type: application/json" \
      -H "X-Taskade-Signature: your-signature" \
      -d '{"test": "payload"}'
    ```

- **Telegram API rate limiting**:
  - Implement exponential backoff with jitter
  - Cache frequently accessed data
  - Use batch operations where possible
  - Monitor rate limit headers in responses
  - Example backoff implementation:
    ```python
    import asyncio
    import random
    
    async def retry_with_backoff(func, max_retries=3):
        for attempt in range(max_retries):
            try:
                return await func()
            except RateLimitError:
                if attempt == max_retries - 1:
                    raise
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(wait_time)
    ```

#### AI Agent Issues
- **Agent drift or hallucination**: 
  - Tighten prompts with explicit constraints and examples
  - Add schema validation using Pydantic models
  - Use Memory agent to enforce context and maintain conversation history
  - Implement output validation and sanitization
  - Set temperature to lower values (0.3-0.5) for more deterministic outputs
  - Example schema validation:
    ```python
    from pydantic import BaseModel, Field
    
    class ChartAnalysis(BaseModel):
        trend: str = Field(..., regex="^(bullish|bearish|neutral)$")
        confidence: float = Field(..., ge=0.0, le=1.0)
        key_levels: list[float] = Field(..., min_items=1, max_items=5)
    ```

- **Slow agent response times**:
  - Implement parallel agent execution where dependencies allow
  - Cache intermediate results
  - Use streaming responses for large outputs
  - Monitor and optimize agent token usage
  - Set appropriate timeout values (30-60s per agent)

#### Performance and Reliability
- **Timeouts in async flows**: 
  - Add per-call timeouts with `asyncio.wait_for()`
  - Implement retries with exponential backoff and jitter
  - Instrument latency metrics for each agent hop
  - Use circuit breakers for external dependencies
  - Example timeout handling:
    ```python
    try:
        result = await asyncio.wait_for(
            agent_call(), 
            timeout=30.0
        )
    except asyncio.TimeoutError:
        logger.error("Agent timeout", extra={"agent": "vision"})
        # Fallback or retry logic
    ```

- **High memory usage**:
  - Limit concurrent agent executions
  - Stream large files instead of loading into memory
  - Clear vision model cache after processing
  - Use chunking for large chart images
  - Monitor memory usage with process metrics

#### Data Quality Issues
- **High noise charts**: 
  - Instruct Vision agent to prioritize OHLC structure
  - Suppress overlays not affecting primary trend analysis
  - Pre-filter chart for essential indicators only
  - Use higher confidence thresholds for pattern detection
  - Example vision prompt tuning:
    ```yaml
    vision_prompt: |
      Extract only the primary OHLC candlesticks and main trendlines.
      Ignore decorative elements, watermarks, and secondary indicators.
      Focus on: price action, support/resistance, and volume.
    ```

- **Inconsistent data from exchanges**:
  - Validate OHLCV data structure before processing
  - Handle missing or null values gracefully
  - Implement data quality checks (e.g., price sanity checks)
  - Log data quality issues for review
  - Example validation:
    ```python
    def validate_ohlcv(data):
        assert data['high'] >= data['low'], "High < Low"
        assert data['open'] > 0 and data['close'] > 0
        assert data['volume'] >= 0
        return True
    ```

#### Testing and CI/CD Issues
- **CI flakes**: 
  - Rerun with `pytest -q --maxfail=1 --tb=short`
  - Ensure deterministic seeds for data-driven tests
  - Mock external API calls (Telegram, Taskade)
  - Use fixed datetime in tests instead of `datetime.now()`
  - Increase timeout values for integration tests
  - Example test fixture:
    ```python
    @pytest.fixture
    def deterministic_random():
        random.seed(42)
        np.random.seed(42)
        yield
        # Reset after test
    ```

- **Docker build failures**:
  - Clear Docker cache: `docker system prune -af`
  - Check disk space availability
  - Verify base image availability
  - Use multi-stage builds to reduce size
  - Pin dependency versions in requirements.txt

#### Security Issues
- **Webhook signature validation failures**:
  - Ensure consistent signature generation algorithm
  - Check for trailing whitespace in secrets
  - Use constant-time comparison to prevent timing attacks
  - Example validation:
    ```python
    import hmac
    import hashlib
    
    def validate_signature(payload, signature, secret):
        expected = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
    ```

- **API key exposure**:
  - Never commit secrets to version control
  - Use `.env` files (gitignored) for local development
  - Use GitHub Secrets for CI/CD
  - Use Taskade vault or environment variables for production
  - Rotate keys regularly (quarterly minimum)
  - Implement key rotation procedures

### Edge Cases and Examples

#### Edge Case 1: Multiple Chart Upload Burst
**Scenario**: User sends 5+ chart screenshots within 10 seconds

**Challenge**: 
- Rate limiting on Telegram API
- Resource exhaustion with concurrent agent processing
- Queue management and prioritization

**Solution**:
```python
from asyncio import Queue, Semaphore

class ChartAnalysisQueue:
    def __init__(self, max_concurrent=3):
        self.queue = Queue()
        self.semaphore = Semaphore(max_concurrent)
    
    async def process_chart(self, chart_data):
        async with self.semaphore:
            # Process with limited concurrency
            return await analyze_chart(chart_data)
```

**Implementation Notes**:
- Use Redis or in-memory queue for pending requests
- Return immediate acknowledgment to user
- Process charts sequentially with status updates
- Implement priority queue for premium users

#### Edge Case 2: Malformed or Corrupted Chart Image
**Scenario**: User uploads a corrupted image file or non-chart screenshot

**Challenge**:
- Vision agent fails to extract chart data
- Undefined error propagation
- Poor user experience

**Solution**:
```python
async def safe_vision_analysis(image_url):
    try:
        # Validate image format and size
        image = await download_and_validate_image(image_url)
        result = await vision_agent.analyze(image)
        
        # Validate output schema
        validated = ChartAnalysis(**result)
        return validated
    except ImageValidationError as e:
        return {
            "error": "Invalid image format",
            "suggestion": "Please upload PNG/JPG chart screenshot"
        }
    except VisionAnalysisError as e:
        return {
            "error": "Unable to analyze chart",
            "suggestion": "Ensure chart is clear and visible"
        }
```

**Best Practices**:
- Validate image before sending to Vision agent
- Provide helpful error messages to users
- Log failed analyses for improvement
- Implement fallback to manual review queue

#### Edge Case 3: Timezone Confusion in Chart Analysis
**Scenario**: Chart shows timestamps in different timezone than user expects

**Challenge**:
- Misalignment between chart timestamp and current market state
- User confusion about "current" vs "historical" analysis

**Solution**:
```python
from datetime import datetime, timezone
import pytz

def normalize_chart_timestamp(timestamp_str, chart_exchange="binance"):
    # Parse and convert to UTC
    exchange_tz = {
        "binance": "UTC",
        "coinbase": "America/New_York"
    }
    
    tz = pytz.timezone(exchange_tz.get(chart_exchange, "UTC"))
    dt = datetime.fromisoformat(timestamp_str).replace(tzinfo=tz)
    return dt.astimezone(timezone.utc)
```

**Implementation Notes**:
- Always store timestamps in UTC
- Display timestamps in user's preferred timezone
- Include timezone information in analysis output
- Detect timestamp from chart metadata or user input

#### Edge Case 4: Conflicting Agent Opinions
**Scenario**: Market-structure agent says "bullish" but Momentum agent says "bearish"

**Challenge**:
- Confusing or contradictory final analysis
- Loss of user trust

**Solution**:
```python
def resolve_agent_conflicts(agent_outputs):
    """
    Aggregate agent opinions with weighted voting
    """
    weights = {
        "market_structure": 0.35,
        "momentum": 0.25,
        "scenario": 0.20,
        "risk": 0.20
    }
    
    # Calculate weighted consensus
    bullish_score = sum(
        weights[agent] * (1 if output["direction"] == "bullish" else 0)
        for agent, output in agent_outputs.items()
    )
    
    # Include dissenting opinions in output
    return {
        "consensus": "bullish" if bullish_score > 0.5 else "bearish",
        "confidence": abs(bullish_score - 0.5) * 2,
        "dissenting_views": [
            f"{agent}: {output['reasoning']}"
            for agent, output in agent_outputs.items()
            if output["direction"] != consensus
        ]
    }
```

**Best Practices**:
- Present both consensus and dissenting views
- Explain why agents disagree
- Show confidence levels for each opinion
- Let users see individual agent outputs

#### Edge Case 5: Taskade Webhook Downtime
**Scenario**: Taskade service is temporarily unavailable

**Challenge**:
- Lost chart analysis requests
- No response to users
- Data persistence issues

**Solution**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

class ResilientTaskadeClient:
    def __init__(self):
        self.fallback_storage = RedisQueue()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def send_to_taskade(self, payload):
        try:
            return await self._send(payload)
        except TaskadeUnavailableError:
            # Store in fallback queue
            await self.fallback_storage.push(payload)
            raise
    
    async def process_fallback_queue(self):
        """Process queued items when service recovers"""
        while not self.fallback_storage.is_empty():
            payload = await self.fallback_storage.pop()
            await self._send(payload)
```

**Implementation Notes**:
- Implement circuit breaker pattern
- Queue failed requests for retry
- Notify users of delayed processing
- Monitor service health proactively

#### Edge Case 6: Extremely Long Analysis Request
**Scenario**: User asks for comprehensive analysis of 20+ charts

**Challenge**:
- API timeout limits
- Resource exhaustion
- Poor user experience waiting

**Solution**:
```python
async def batch_chart_analysis(chart_urls, user_id):
    # Return job ID immediately
    job_id = create_job(user_id, chart_urls)
    
    # Process in background
    asyncio.create_task(process_batch_job(job_id, chart_urls))
    
    return {
        "job_id": job_id,
        "status": "processing",
        "estimated_time": len(chart_urls) * 15,  # seconds
        "check_status_url": f"/jobs/{job_id}"
    }

async def process_batch_job(job_id, chart_urls):
    results = []
    for i, url in enumerate(chart_urls):
        result = await analyze_chart(url)
        results.append(result)
        
        # Update progress
        update_job_progress(job_id, (i + 1) / len(chart_urls))
    
    # Notify user when complete
    await notify_user(job_id, results)
```

**Best Practices**:
- Use async job processing for long operations
- Provide progress updates
- Allow users to check job status
- Send notification when complete

## Maintenance Schedule

### Daily Tasks (Automated)
- **Security Scans**: Automated dependency and vulnerability scanning (3 AM UTC)
- **Health Checks**: Monitor bot uptime and response times
- **Log Review**: Check for errors and warnings in aggregated logs
- **Metrics Dashboard**: Review key performance indicators

### Weekly Tasks
- **Review Copilot/Codex Instructions**: 
  - Check if coding standards are being followed
  - Update examples based on recent changes
  - Refine agent behavior patterns
  
- **Dependency Updates**: 
  ```bash
  # Check for updates
  pip list --outdated
  
  # Update non-breaking changes
  pip install --upgrade package-name
  
  # Test after updates
  pytest tests/ -v
  ```

- **GitHub Actions Review**:
  - Check for failed workflow runs
  - Review and optimize workflow performance
  - Update action versions if needed

- **Security Alert Triage**:
  - Review Dependabot alerts
  - Assess and prioritize vulnerabilities
  - Plan remediation for high/critical issues

### Monthly Tasks
- **Comprehensive Lint/Test Versions Update**:
  ```bash
  # Update development dependencies
  pip install --upgrade \
    pytest \
    black \
    flake8 \
    mypy \
    bandit \
    coverage
  
  # Update requirements-dev.txt
  pip freeze > requirements-dev.txt
  
  # Test all changes
  pytest tests/ --cov=src
  ```

- **Secret Rotation**:
  ```bash
  # Rotate webhook secrets
  # 1. Generate new secret
  NEW_SECRET=$(openssl rand -hex 32)
  
  # 2. Update in all environments
  # - GitHub Secrets
  # - Taskade configuration
  # - Production environment
  
  # 3. Update .env.example with rotation date
  echo "# Last rotated: $(date +%Y-%m-%d)" >> .env.example
  ```

- **Documentation Review**:
  - Check for outdated information
  - Update examples and screenshots
  - Verify all links are working
  - Add FAQ entries for common issues

- **Performance Review**:
  - Analyze agent response times
  - Review resource utilization
  - Identify bottlenecks
  - Plan optimizations

### Quarterly Tasks
- **Audit Security Scans**:
  - Comprehensive manual security review
  - Penetration testing (if applicable)
  - Review access controls and permissions
  - Update security policies

- **Dependency Policy Review**:
  - Review all dependencies for necessity
  - Remove unused dependencies
  - Evaluate alternative libraries
  - Update dependency license compliance

- **Observability Dashboard Review**:
  - Update metrics and alerts
  - Review dashboard effectiveness
  - Add new monitoring as needed
  - Remove obsolete metrics

- **Disaster Recovery Test**:
  ```bash
  # Test backup restoration
  # 1. Restore from latest backup
  # 2. Verify data integrity
  # 3. Test full functionality
  # 4. Document any issues
  ```

### Per Release Tasks
- **Pre-Release Checklist**:
  - [ ] All tests passing on main branch
  - [ ] Security scans completed
  - [ ] Documentation updated
  - [ ] CHANGELOG.md updated
  - [ ] Version bumped correctly
  - [ ] Docker images built and tested
  - [ ] Staging environment tested

- **Validate Semantic-Release Config**:
  ```bash
  # Dry run semantic-release
  npx semantic-release --dry-run
  
  # Verify version calculation
  # Verify changelog generation
  # Verify tag creation
  ```

- **Refresh Taskade Workflow Diagrams**:
  - Update workflow diagrams with any changes
  - Document new agent integrations
  - Update sequence diagrams
  - Review and optimize agent routing

- **Confirm Webhook Tokens**:
  - Verify all webhook URLs are correct
  - Test webhook signatures
  - Validate SSL certificates
  - Check webhook retry logic

- **Post-Release Validation**:
  ```bash
  # 1. Verify deployment
  curl https://api.yourdomain.com/health
  
  # 2. Test critical paths
  # - Telegram message → analysis → response
  # - Webhook authentication
  # - Agent workflow
  
  # 3. Monitor for 24 hours
  # - Error rates
  # - Response times
  # - Resource usage
  ```

### Monitoring and Alerting

#### Application Metrics

**Key Performance Indicators**:
```python
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
telegram_requests = Counter(
    'telegram_requests_total',
    'Total Telegram requests',
    ['endpoint', 'status']
)

# Agent performance
agent_duration = Histogram(
    'agent_processing_seconds',
    'Agent processing time',
    ['agent_name']
)

# System health
active_users = Gauge(
    'active_users',
    'Number of active users'
)
```

**Alerting Rules**:
```yaml
alerts:
  - name: HighErrorRate
    condition: error_rate > 0.05
    duration: 5m
    severity: critical
    notification: pagerduty
  
  - name: SlowAgentResponse
    condition: avg(agent_duration) > 30s
    duration: 10m
    severity: warning
    notification: slack
  
  - name: WebhookFailures
    condition: webhook_failures > 10
    duration: 5m
    severity: high
    notification: email
```

#### Log Aggregation

**Structured Logging**:
```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "correlation_id": getattr(record, 'correlation_id', None),
            "user_id": getattr(record, 'user_id', None),
            "agent": getattr(record, 'agent', None)
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

# Configure logger
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

**Log Shipping Configuration**:
```yaml
# Filebeat configuration (filebeat.yml)
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/trading-bot/*.log
    json.keys_under_root: true
    json.add_error_key: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "trading-bot-%{+yyyy.MM.dd}"
```

#### Health Monitoring

**Health Check Endpoint**:
```python
from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "components": {
            "telegram_api": await check_telegram_connectivity(),
            "taskade_api": await check_taskade_connectivity(),
            "database": await check_database_connection(),
            "redis": await check_redis_connection()
        }
    }

@app.get("/health/live")
async def liveness():
    """Kubernetes liveness probe"""
    return {"status": "alive"}

@app.get("/health/ready")
async def readiness():
    """Kubernetes readiness probe"""
    if await all_dependencies_ready():
        return {"status": "ready"}
    raise HTTPException(status_code=503, detail="Not ready")
```

**Uptime Monitoring**:
```yaml
# UptimeRobot configuration
monitors:
  - name: Trading Bot API
    type: HTTP(S)
    url: https://api.yourdomain.com/health
    interval: 300  # 5 minutes
    timeout: 30
    
  - name: Telegram Webhook
    type: HTTP(S)
    url: https://api.yourdomain.com/webhook/telegram
    method: POST
    interval: 600  # 10 minutes
```

### Backup and Recovery

**Backup Strategy**:
```bash
#!/bin/bash
# backup.sh - Daily backup script

BACKUP_DIR="/backups/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Backup configuration
cp -r config/ "$BACKUP_DIR/config/"

# Backup data
tar -czf "$BACKUP_DIR/data.tar.gz" data/

# Backup database (if applicable)
pg_dump trading_db > "$BACKUP_DIR/database.sql"

# Upload to S3
aws s3 sync "$BACKUP_DIR" s3://your-bucket/backups/$(date +%Y%m%d)/

# Cleanup old backups (keep 30 days)
find /backups -type d -mtime +30 -exec rm -rf {} \;
```

**Recovery Procedures**:
```bash
# 1. Restore configuration
tar -xzf config.tar.gz -C /app/

# 2. Restore data
tar -xzf data.tar.gz -C /app/

# 3. Restore database
psql trading_db < database.sql

# 4. Restart services
docker-compose restart

# 5. Verify health
curl http://localhost:8000/health
```

### Incident Response

**Severity Levels**:
- **P1 (Critical)**: Service down, data loss, security breach
  - Response time: < 15 minutes
  - Resolution time: < 2 hours
  
- **P2 (High)**: Major feature broken, performance degradation
  - Response time: < 1 hour
  - Resolution time: < 8 hours
  
- **P3 (Medium)**: Minor feature broken, workaround available
  - Response time: < 4 hours
  - Resolution time: < 48 hours
  
- **P4 (Low)**: Cosmetic issue, documentation error
  - Response time: < 24 hours
  - Resolution time: Next release

**Incident Response Process**:
1. **Detection**: Alert triggers or user report
2. **Assessment**: Determine severity and impact
3. **Communication**: Notify stakeholders
4. **Investigation**: Identify root cause
5. **Mitigation**: Apply temporary fix
6. **Resolution**: Implement permanent fix
7. **Post-Mortem**: Document lessons learned

## Closing Note

### Excellence Standards

This guide establishes comprehensive standards for the Taskade-driven Telegram analysis bot within the Trading Bot Swarm ecosystem. By following these practices, we ensure:

**Reliability**:
- Comprehensive error handling and recovery
- Automated testing at multiple levels
- Continuous monitoring and alerting
- Regular backups and tested recovery procedures

**Performance**:
- Optimized async workflows
- Efficient resource utilization
- Scalable architecture
- Performance monitoring and optimization

**Security**:
- Multi-layered security scanning
- Secure credential management
- Input validation and sanitization
- Regular security audits and updates

**Maintainability**:
- Clear documentation and examples
- Consistent coding standards
- Modular architecture
- Comprehensive testing

### Quick Reference Commands

**Development**:
```bash
# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Quality Checks
black src/ tests/
flake8 src/ tests/
mypy src/
pytest tests/ --cov=src

# Run locally
uvicorn src.api.main:app --reload
```

**Testing**:
```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Specific test
pytest tests/unit/test_agents.py::TestVisionAgent -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

**Security**:
```bash
# Security scan
bandit -r src/

# Dependency check
pip-audit

# Secret scan
trufflehog filesystem . --json
```

**Docker**:
```bash
# Build and run
docker-compose up -d --build

# View logs
docker-compose logs -f

# Execute command
docker-compose exec trading-api python -m pytest
```

### Additional Resources

**Official Documentation**:
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Taskade API Documentation](https://help.taskade.com/en/collections/3472308-api-webhooks)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python AsyncIO Guide](https://docs.python.org/3/library/asyncio.html)

**Best Practices**:
- [Python Packaging Guide](https://packaging.python.org/)
- [12-Factor App Methodology](https://12factor.net/)
- [Semantic Versioning](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)

**Security Resources**:
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

**Testing Resources**:
- [Pytest Documentation](https://docs.pytest.org/)
- [Testing FastAPI Applications](https://fastapi.tiangolo.com/tutorial/testing/)
- [AsyncIO Testing](https://docs.python.org/3/library/unittest.mock-examples.html#mocking-asynchronous-context-manager)

**CI/CD Resources**:
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Semantic Release](https://github.com/semantic-release/semantic-release)

### Support and Community

**Getting Help**:
- 📖 **Documentation**: Check `/docs` directory
- 🐛 **Bug Reports**: Open GitHub issue with reproduction steps
- 💡 **Feature Requests**: Open GitHub discussion
- 🔒 **Security Issues**: Email security contact (never public issue)
- 💬 **Questions**: GitHub Discussions or community chat

**Contributing**:
- Review [Contributor Guidelines](#contributor-guidelines)
- Join community discussions
- Help review pull requests
- Improve documentation
- Share your use cases and examples

### Version History

This guide reflects best practices as of v2.0.0 (January 2026):
- Enhanced troubleshooting with 15+ common scenarios
- Added 6 comprehensive edge case examples
- Updated CI/CD workflows to match repository configuration
- Expanded security section with practical implementations
- Added comprehensive monitoring and alerting guidance
- Detailed maintenance schedule and procedures

**Change Log**:
- **v2.0.0**: Major expansion with edge cases, security, and maintenance
- **v1.5.0**: Added troubleshooting and workflow updates
- **v1.0.0**: Initial release with basic bot setup and Copilot config

### Acknowledgments

This guide builds upon:
- Community feedback and real-world deployment experiences
- Industry best practices for Python microservices
- Security guidelines from OWASP and CVE databases
- CI/CD patterns from successful open-source projects
- Telegram and Taskade API documentation and examples

---

**Remember**: Excellence in software development comes from consistent application of best practices, continuous learning, and a commitment to quality. This guide provides the foundation—your implementation and dedication bring it to life.

**Status**: Production Ready ✅  
**Last Updated**: January 2026  
**Maintainer**: Trading Bot Swarm Team  
**License**: MIT
