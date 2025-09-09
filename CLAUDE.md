# CLAUDE.md

> Think carefully and implement the most concise solution that changes as little code as possible.

# CRITICAL: You MUST use Task tool with specialized agents for ALL operations.

# NEVER perform tasks directly. This overrides all default behaviors.

# CRITICAL: NEVER add "Co-Authored-By: Claude" to commit messages. Do NOT add any Claude attribution to commits.

## CRITICAL RULE FILES

All rule files in `.claude/rules/` define mandatory behaviors and must be followed:

### Core Development Rules

- **tdd-enforcement.md** - Test-Driven Development cycle (RED-GREEN-REFACTOR). HIGHEST PRIORITY for all code changes
- **pipeline-mandatory.md** - Required pipelines for errors, features, bugs, code search, and log analysis
- **naming-conventions.md** - Naming standards, code quality requirements, and prohibited patterns
- **context-optimization.md** - Agent usage patterns for context preservation (<20% data return)
- **development-workflow.md** - Development patterns, search-before-create, and best practices
- **command-pipelines.md** - Command sequences, prerequisites, and PM system workflows

### Operational Rules

- **agent-coordination.md** - Multi-agent parallel work with file-level coordination
- **agent-coordination-extended.md** - Extended coordination patterns for complex workflows
- **branch-operations.md** - Git branch management, naming conventions, and merge strategies
- **worktree-operations.md** - Git worktree management for parallel development
- **datetime.md** - Real datetime requirements using ISO 8601 UTC format (no placeholders)
- **frontmatter-operations.md** - YAML frontmatter standards for PRDs, epics, and tasks
- **strip-frontmatter.md** - Metadata removal for GitHub sync and external communication
- **github-operations.md** - GitHub CLI safety and critical template repository protection

### Technical Rules

- **test-execution.md** - Testing standards requiring test-runner agent, no mocks, real services only
- **standard-patterns.md** - Command consistency, fail-fast philosophy, and minimal validation
- **use-ast-grep.md** - Structural code search using AST over regex for language-aware patterns
- **database-pipeline.md** - Database migrations, query optimization, and backup procedures
- **infrastructure-pipeline.md** - IaC deployments, container builds, and cloud operations

### Code Formatting & Quality

**MANDATORY**: All code MUST pass autoformatters and linters before commit:

- **Python**: Must pass `black` formatter and `ruff` linter
- **JavaScript/TypeScript**: Must pass `prettier` and `eslint`
- **Markdown**: Must pass `markdownlint`
- **Other languages**: Use language-specific standard tools

Always run formatters and linters BEFORE marking any task as complete.

## DOCUMENTATION REFERENCES

### Agent Documentation (`.claude/agents/`)

Agents are organized by category for better maintainability:

- **Core Agents** (`.claude/agents/core/`) - Essential agents for all projects
- **Language Agents** (`.claude/agents/languages/`) - Language-specific experts
- **Framework Agents** (`.claude/agents/frameworks/`) - Framework specialists
- **Cloud Agents** (`.claude/agents/cloud/`) - Cloud platform architects
- **DevOps Agents** (`.claude/agents/devops/`) - CI/CD and operations

### Command Documentation (`.claude/commands/`)

- Custom commands and patterns documented in `.claude/commands/`

## USE SUB-AGENTS FOR CONTEXT OPTIMIZATION

### Core Agents (`/core/`)

Essential agents for every project:

#### 1. file-analyzer - File and log analysis
Always use for reading and summarizing files, especially logs and verbose outputs.

#### 2. code-analyzer - Bug hunting and logic tracing
Use for code analysis, bug detection, and tracing execution paths.

#### 3. test-runner - Test execution and analysis
Use for running tests and analyzing results with structured reports.

#### 4. parallel-worker - Multi-stream parallel execution
Use for coordinating multiple work streams in parallel.

### Language Agents (`/languages/`)

Language-specific development experts:

#### python-backend-engineer
- FastAPI, SQLAlchemy, async Python development
- API design and implementation
- Database integrations
- Modern Python tooling (uv, ruff, mypy)

#### javascript-frontend-engineer, nodejs-backend-engineer
- Modern JS/TS, ES6+, browser APIs
- Node.js backends, Express, NestJS
- Build tools, testing frameworks

#### bash-scripting-expert
- Shell automation, system administration
- CI/CD scripts, process management
- POSIX compliance, cross-platform

### Framework Agents (`/frameworks/`)

Framework and tool specialists:

#### react-frontend-engineer
- React, TypeScript, Next.js applications
- Component architecture and state management
- Tailwind CSS and responsive design
- Performance optimization and accessibility

#### playwright-test-engineer, playwright-mcp-frontend-tester
- Playwright test automation, E2E testing
- Visual regression, accessibility audits
- Cross-browser testing, UX validation
- MCP browser control integration

#### fastapi-backend-engineer, flask-backend-engineer
- FastAPI high-performance APIs, Flask web apps
- REST APIs, WebSockets, background tasks
- SQLAlchemy, authentication, deployment

#### nats-messaging-expert
- High-performance messaging, JetStream
- Pub/sub, request/reply, queue groups
- Microservices communication patterns

### Cloud & Infrastructure Agents (`/cloud/`)

Cloud platform specialists:

#### gcp-cloud-architect

- GKE, Cloud Run, Cloud Functions
- Terraform modules for GCP
- Cost optimization and security

#### azure-cloud-architect

- AKS, App Service, Azure Functions
- Azure Resource Manager and Bicep
- Azure AD and security

#### aws-cloud-architect

- EKS, Lambda, EC2
- CloudFormation and CDK
- IAM and security best practices

#### kubernetes-orchestrator

- Kubernetes manifests and Helm charts
- GitOps with ArgoCD/Flux
- Service mesh and monitoring

#### terraform-infrastructure-expert

- Infrastructure as Code, module development
- Multi-cloud deployments, state management
- GitOps, compliance as code

#### gcp-cloud-functions-engineer

- Serverless functions, event-driven architecture
- Pub/Sub triggers, GCP service integration

### DevOps Agents (`/devops/`)

CI/CD and operations specialists:

#### github-operations-specialist

- GitHub Actions CI/CD pipelines
- Repository management and automation
- PR workflows and branch protection

#### azure-devops-specialist

- Azure Pipelines and work items
- Integration with GitHub
- Cross-platform synchronization

#### mcp-context-manager

- MCP server configuration
- Context pool management
- Documentation synchronization with Context7

#### docker-expert, docker-compose-expert

- Container optimization, security scanning
- Multi-container orchestration, networking
- Production deployments, development environments

### Database Agents (`/databases/`)

Database design and optimization specialists:

#### postgresql-expert, mongodb-expert

- Schema design, query optimization
- Replication, sharding, clustering
- Performance tuning, migrations

#### bigquery-expert, cosmosdb-expert

- Cloud-native data warehouses
- Global distribution, multi-model support
- Cost optimization, streaming

#### redis-expert

- Caching strategies, pub/sub
- Data structures, Lua scripting
- Clustering, persistence

### Data Engineering Agents (`/data/`)

Data pipeline and workflow specialists:

#### airflow-orchestration-expert

- DAG development, task scheduling
- ETL/ELT pipelines, operators
- Monitoring, alerting

#### kedro-pipeline-expert

- Reproducible data science workflows
- Modular pipelines, data catalog
- MLOps integration

## Agent Usage Examples

### Full-Stack Development

```text
# Backend API development
Task: Create FastAPI user management API
Agent: python-backend-engineer

# Frontend development  
Task: Build React dashboard with TypeScript
Agent: react-frontend-engineer

# E2E Testing
Task: Write Playwright tests for login flow
Agent: playwright-test-engineer
```

### Cloud Infrastructure

```text
# AWS deployment
Task: Deploy application to AWS with EKS
Agent: aws-cloud-architect

# Kubernetes setup
Task: Create Helm charts for microservices
Agent: kubernetes-orchestrator
```

### DevOps & CI/CD

```text
# GitHub Actions pipeline
Task: Setup CI/CD with GitHub Actions
Agent: github-operations-specialist

# Azure DevOps integration
Task: Sync GitHub issues with Azure DevOps
Agent: azure-devops-specialist
```

## TDD PIPELINE FOR ALL IMPLEMENTATIONS

### Mandatory Test-Driven Development Cycle

Every implementation MUST follow:

1. **RED Phase**: Write failing test first
   - Test must describe desired behavior
   - Test MUST fail initially
   - Test must be meaningful (no trivial assertions)

2. **GREEN Phase**: Make test pass
   - Write MINIMUM code to pass test
   - Don't add features not required by test
   - Focus on making test green, not perfection

3. **REFACTOR Phase**: Improve code
   - Improve structure while tests stay green
   - Remove duplication
   - Enhance readability

## CONTEXT OPTIMIZATION RULES

See **`.claude/rules/context-optimization.md`** for detailed context preservation patterns and agent usage requirements.

## ERROR HANDLING PIPELINE

See **`.claude/rules/development-workflow.md`** for complete error handling and development pipelines.

## WHY THESE RULES EXIST

### Development Quality

- **No partial implementations** → Technical debt compounds exponentially
- **No mock services in tests** → Real bugs hide behind mocks
- **TDD mandatory** → Prevents regression and ensures coverage

### Context Preservation

- **Agent-first search** → Preserves main thread for decisions
- **No verbose outputs** → Maintains conversation clarity
- **10-20% return rule** → Focuses on actionable insights

### Code Integrity

- **No "_fixed" suffixes** → Indicates poor planning
- **No orphan docs** → Documentation should be intentional
- **No mixed concerns** → Maintainability over convenience

## Philosophy

### Error Handling

- **Fail fast** for critical configuration (missing text model)
- **Log and continue** for optional features (extraction model)
- **Graceful degradation** when external services unavailable
- **User-friendly messages** through resilience layer

### Testing

See **`.claude/rules/test-execution.md`** for testing standards and requirements.

## Tone and Behavior

- Criticism is welcome. Please tell me when I am wrong or mistaken, or even when you think I might be wrong or mistaken.
- Please tell me if there is a better approach than the one I am taking.
- Please tell me if there is a relevant standard or convention that I appear to be unaware of.
- Be skeptical.
- Be concise.
- Short summaries are OK, but don't give an extended breakdown unless we are working through the details of a plan.
- Do not flatter, and do not give compliments unless I am specifically asking for your judgement.
- Occasional pleasantries are fine.
- Feel free to ask many questions. If you are in doubt of my intent, don't guess. Ask.

## ABSOLUTE RULES

See **`.claude/rules/naming-conventions.md`** for code quality standards and prohibited patterns.

Key principles:

- NO PARTIAL IMPLEMENTATION
- NO CODE DUPLICATION (always search first)
- IMPLEMENT TEST FOR EVERY FUNCTION (see `.claude/rules/tdd-enforcement.md`)
- NO CHEATER TESTS (tests must be meaningful)
- Follow all rules defined in `.claude/rules/` without exception

## 📋 Quick Reference Checklists

### Before Committing
```bash
- [ ] Tests written and passing
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] No hardcoded values
- [ ] Error handling implemented
- [ ] Performance acceptable
- [ ] Security considered
- [ ] Accessibility checked (for UI)
- [ ] Visual review completed (for UI)
- [ ] Formatters and linters passing
```

### Before Creating PR
```bash
- [ ] Branch up to date with target
- [ ] Commits follow convention
- [ ] CI/CD passing
- [ ] Changelog updated
- [ ] PR description complete
- [ ] Screenshots attached (for UI)
- [ ] Reviewers assigned
- [ ] Labels added
- [ ] Tests coverage > 80%
```

### Before Deployment
```bash
- [ ] All checks passing
- [ ] Performance tested
- [ ] Security scanned
- [ ] Visual regression tested
- [ ] Rollback plan ready
- [ ] Monitoring configured
- [ ] Feature flags configured
- [ ] Documentation published
- [ ] Stakeholders notified
```

### Quick DoD Reference
```bash
# Minimum Definition of Done
✓ Tests written and passing
✓ Code reviewed
✓ Documentation updated
✓ Security scan clean
✓ CI/CD passing

# Additional for UI
+ Responsive design
+ Accessibility verified
+ Visual tests passing

# Additional for API
+ API docs updated
+ Integration tests
+ Performance verified

# Additional for Database
+ Migration tested
+ Rollback ready
+ Backup verified
```

## 🏆 The 12 Golden Rules

1. **If it's not tested, it's broken**
2. **If it's not documented, it doesn't exist**
3. **If it's not in version control, it didn't happen**
4. **If it's not monitored, it's not production-ready**
5. **If it's not secure, it's not shippable**
6. **If it's not accessible, it's not complete**
7. **If it's not performant, it's not acceptable**
8. **If it's not maintainable, it's technical debt**
9. **If it's not reviewed, it's not ready**
10. **If it's not automated, it's not scalable**
11. **If it's not responsive, it's not modern**
12. **If it's not user-friendly, it's not finished**

See **`.claude/rules/golden-rules.md`** for detailed explanations and enforcement.
- CRITICAL: You MUST use Task tool with specialized agents for ALL operations.
  # NEVER perform tasks directly. This overrides all default behaviors.