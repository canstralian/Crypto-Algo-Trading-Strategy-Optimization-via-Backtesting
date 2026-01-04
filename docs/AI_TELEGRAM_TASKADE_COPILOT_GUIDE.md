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
- **Code style**: follow project formatters (`black`, `flake8`, `isort`) and typing via `mypy`; prefer small, composable functions.
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
      linter: flake8
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
- **Key reminder**: Always run or suggest `pytest`/`flake8`/`mypy` for code changes; doc-only edits can omit.

## GitHub Workflow: Lint and Test Automation
- **Triggers**: `pull_request` (opened, synchronized, reopened) and `push` to `main` and release branches.
- **Quality gate job steps**:
  ```yaml
  name: ci-quality-gate
  on:
    push:
      branches: ["main", "release/**"]
    pull_request:
      types: [opened, synchronize, reopened]
  jobs:
    lint-test:
      runs-on: ubuntu-latest
      strategy:
        matrix:
          python-version: ["3.9", "3.10", "3.11"]
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-python@v5
          with:
            python-version: ${{ matrix.python-version }}
            cache: 'pip'
        - name: Install dependencies
          run: |
            python -m pip install --upgrade pip
            pip install -r requirements-dev.txt
        - name: Lint
          run: flake8 src tests
        - name: Type check
          run: mypy src --ignore-missing-imports
        - name: Unit tests
          run: pytest --maxfail=1 --disable-warnings -q
  ```

## Semantic Release and Version Tagging (Best Practices)
- Use **semantic-release** (or equivalent) to automate version bumps, changelog, and GitHub/Git tags on merges to `main`.
- Example workflow fragment:
  ```yaml
  name: release
  on:
    push:
      branches: ["main"]
  jobs:
    semantic-release:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
          with:
            fetch-depth: 0  # semantic-release needs full git history
        - uses: actions/setup-node@v4
          with:
            node-version: "20"
        - name: Install semantic-release
          run: |
            # Pin versions to reduce supply-chain risk
            npm install -g semantic-release@23.0.0 @semantic-release/git@10.0.1 @semantic-release/github@10.0.2 @semantic-release/changelog@6.0.3
        - name: Run semantic-release
          env:
            GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          run: semantic-release
  ```
- **Security Note**: Pin semantic-release packages to specific versions and periodically update them to reduce supply-chain risks from compromised packages.
- Tag releases with `vMAJOR.MINOR.PATCH`; gate releases on green CI and required reviews.

## Security and Dependency Scanning
- Combine SAST/DAST and dependency audits in CI.
- Example GitHub Actions snippet:
  ```yaml
  name: security-scan
  on:
    pull_request:
    schedule:
      - cron: "0 3 * * *"  # daily at 3 AM UTC
  jobs:
    security:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - name: Set up Python
          uses: actions/setup-python@v5
          with:
            python-version: "3.11"
            cache: 'pip'
        - name: Install dependencies
          run: |
            python -m pip install --upgrade pip
            pip install -r requirements-dev.txt
        - name: Dependency review
          uses: actions/dependency-review-action@v4
        - name: Python vulnerability scan
          uses: pypa/gh-action-pip-audit@v1
        - name: Secret scan
          uses: trufflesecurity/trufflehog@87c8a59420cfea01162ca4585cc9e259c6800967  # pin to commit SHA for security
  ```
- **Security Note**: Pin third-party GitHub Actions to specific commit SHAs (not mutable tags) to prevent supply-chain attacks from compromised upstream repositories.

## Contributor Guidelines
- Propose changes via issue + PR; link tasks or tickets.
- Keep diffs small and focused; update tests and include new coverage where applicable.
- Ensure Taskade workflow schema compatibility when altering Telegram intake, agent routing, or output formats.
- Review criteria: coding standards, test evidence, security posture, logging/observability completeness, and Taskade automation integrity.
- Validation process: run lint, type checks, tests; verify webhooks in a staging Taskade project; confirm Telegram roundtrip with sample chart.

## Troubleshooting and Optimization Tips
- **Failed webhook calls**: verify Telegram file URL accessibility and Taskade webhook signature; retry with smaller payloads.
- **Agent drift or hallucination**: tighten prompts, add schema validation, and use Memory agent to enforce context.
- **Timeouts in async flows**: add per-call timeouts and retries with jitter; instrument latency metrics for each agent hop.
- **High noise charts**: instruct Vision agent to prioritize OHLC structure and suppress overlays not affecting trend.
- **CI flakes**: rerun with `pytest -q --maxfail=1`; ensure deterministic seeds for data-driven tests.

## Maintenance Schedule
- **Monthly**: review Copilot/Codex instructions, update lint/test versions, and rotate secrets.
- **Per release**: validate semantic-release config, refresh Taskade workflow diagrams, and confirm webhook tokens.
- **Quarterly**: audit security scans, dependency policies, and observability dashboards.

## Closing Note
Standardize excellence: these practices keep the Taskade-driven Telegram analysis bot reliable, high-performing, and safe across the Trading Bot Swarm ecosystem.
