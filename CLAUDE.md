Świetna uwaga! To bardzo przydatny dodatek do CLAUDE.md. Oto zaktualizowana wersja z sekcją Visual Development:

# CLAUDE.md

This file provides comprehensive guidance to Claude Code (claude.ai/code) for maintaining high-quality software development standards across all projects.

## 🎯 Core Development Philosophy

### Test-Driven Development (TDD)
**MANDATORY**: All development follows strict TDD methodology
1. **RED**: Write a failing test that defines the desired behavior
2. **GREEN**: Write minimal code to make the test pass
3. **REFACTOR**: Improve code quality while keeping tests green

```bash
# The TDD Cycle - ALWAYS follow this order:
1. Write test → See it fail
2. Write code → Make test pass
3. Refactor → Improve implementation
4. Repeat
```

### 🚀 Development Principles
- **YAGNI** (You Aren't Gonna Need It): Don't add functionality until actually needed
- **DRY** (Don't Repeat Yourself): Extract common logic into reusable components
- **KISS** (Keep It Simple, Stupid): Prefer simple, readable solutions over clever ones
- **SOLID**: Follow SOLID principles for maintainable architecture
- **Clean Code**: Code is written for humans to read, not just machines to execute

## 🎨 Visual Development

### Design Principles
- Comprehensive design checklist in `/context/design-principles.md`
- Brand style guide in `/context/style-guide.md`
- Component library documentation in `/context/components.md`
- When making visual (front-end, UI/UX) changes, always refer to these files for guidance

### Quick Visual Check
**IMMEDIATELY after implementing any front-end change:**

1. **Identify what changed** - Review the modified components/pages
2. **Navigate to affected pages** - Use browser tools or `mcp__playwright__browser_navigate` to visit each changed view
3. **Verify design compliance** - Compare against `/context/design-principles.md` and `/context/style-guide.md`
4. **Validate feature implementation** - Ensure the change fulfills the user's specific request
5. **Check acceptance criteria** - Review any provided context files or requirements
6. **Capture evidence** - Take screenshots at multiple viewports:
   - Mobile: 375px
   - Tablet: 768px  
   - Desktop: 1440px
7. **Check for errors** - Review browser console for JavaScript errors
8. **Test interactions** - Verify hover states, animations, and transitions

### Visual Testing Checklist
```bash
# Before committing any UI changes:
- [ ] Responsive design verified (mobile, tablet, desktop)
- [ ] Cross-browser testing completed (Chrome, Firefox, Safari, Edge)
- [ ] Accessibility standards met (WCAG 2.1 AA)
- [ ] Dark mode compatibility (if applicable)
- [ ] Loading states implemented
- [ ] Error states designed
- [ ] Empty states handled
- [ ] Animation performance optimized (<60fps)
- [ ] Images optimized and lazy-loaded
- [ ] Touch targets minimum 44x44px
```

### Comprehensive Design Review
Invoke design review for thorough validation when:
- Completing significant UI/UX features
- Before finalizing PRs with visual changes
- Needing comprehensive accessibility testing
- Implementing new design patterns
- Major refactoring of UI components

### UI/UX Best Practices
1. **Consistency**: Use established patterns and components
2. **Feedback**: Provide immediate visual feedback for all interactions
3. **Progressive Enhancement**: Core functionality works without JavaScript
4. **Performance**: Optimize for perceived performance
5. **Accessibility**: Design for all users from the start

### CSS Architecture
```scss
// Follow BEM methodology
.block {}
.block__element {}
.block--modifier {}

// Component structure
.card {
  &__header {}
  &__body {}
  &__footer {}
  
  &--featured {
    .card__header {}
  }
}
```

### Component Development Standards
```jsx
// Component checklist:
- [ ] Props validated with PropTypes/TypeScript
- [ ] Default props defined
- [ ] Error boundaries implemented
- [ ] Memoization applied where needed
- [ ] Accessibility attributes (ARIA)
- [ ] Keyboard navigation support
- [ ] RTL support considered
- [ ] Theme variables used
- [ ] Storybook story created
- [ ] Unit tests written
```

## 🐳 Docker-First Development

### Containerization Policy
**ALL applications MUST be containerized. NO EXCEPTIONS.**

```bash
# ✅ CORRECT - Everything runs in containers
docker-compose up -d
docker-compose exec app npm test
docker-compose run --rm test-runner pytest

# ❌ WRONG - Never run directly on host
npm install
python app.py
npm test
```

### Docker Best Practices
1. **Multi-stage builds**: Optimize image size
2. **Layer caching**: Order Dockerfile commands for optimal caching
3. **Security scanning**: Always scan images for vulnerabilities
4. **Non-root users**: Never run containers as root
5. **Health checks**: Implement proper health check endpoints

## 📋 Git Workflow & Standards

### Branch Strategy
```bash
main/master          # Production-ready code only
├── develop         # Integration branch for features
├── feature/*       # New features (from develop)
├── fix/*          # Bug fixes (from develop or main)
├── hotfix/*       # Emergency fixes (from main)
├── release/*      # Release preparation (from develop)
└── chore/*        # Maintenance tasks
```

### Commit Message Format (Conventional Commits)
```bash
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, semicolons, etc)
- `refactor`: Code restructuring without behavior change
- `perf`: Performance improvements
- `test`: Adding or modifying tests
- `build`: Build system or dependencies
- `ci`: CI/CD configuration
- `chore`: Maintenance tasks
- `revert`: Reverting previous commit
- `ui`: Visual/UI changes

**Examples:**
```bash
feat(auth): implement JWT authentication
fix(api): resolve race condition in user creation
docs(readme): add installation instructions
refactor(core): extract validation logic to utilities
test(user): add integration tests for user service
perf(db): add indexes to improve query performance
ui(dashboard): implement responsive grid layout
```

### Pull Request Standards
1. **One PR = One Feature/Fix**: Keep PRs focused and small
2. **Description Template**: Use standardized PR template
3. **Tests Required**: Every PR must include relevant tests
4. **Review Required**: Minimum one approval before merge
5. **CI Must Pass**: All checks green before merge
6. **Visual Review**: Screenshots for UI changes
7. **Squash on Merge**: Keep history clean

## 🧪 Testing Standards

### Testing Pyramid
```
        /\
       /E2E\        <- 10% (Critical user journeys)
      /------\
     /Integration\   <- 30% (Component interactions)
    /------------\
   /     Unit     \  <- 60% (Individual functions/methods)
  /________________\
```

### Visual Testing
```javascript
// Visual regression testing
describe('Component Visual Tests', () => {
  it('should match visual snapshot', async () => {
    const component = render(<MyComponent />);
    const screenshot = await page.screenshot();
    expect(screenshot).toMatchImageSnapshot();
  });
  
  it('should handle responsive breakpoints', async () => {
    const viewports = [375, 768, 1440];
    for (const width of viewports) {
      await page.setViewport({ width, height: 800 });
      const screenshot = await page.screenshot();
      expect(screenshot).toMatchImageSnapshot(`viewport-${width}`);
    }
  });
});
```

### Coverage Requirements
- **Minimum**: 80% overall coverage
- **Critical paths**: 100% coverage for business logic
- **New code**: 90% coverage for new features
- **UI Components**: 70% coverage (including snapshot tests)
- **Exclusions**: Only config files and type definitions

### Test Structure (AAA Pattern)
```javascript
describe('Feature', () => {
  it('should behave correctly', () => {
    // Arrange - Set up test data and conditions
    const input = createTestData();
    
    // Act - Execute the function/feature
    const result = functionUnderTest(input);
    
    // Assert - Verify the outcome
    expect(result).toBe(expectedValue);
  });
});
```

### Test Categories
1. **Unit Tests**: Test individual functions in isolation
2. **Integration Tests**: Test component interactions
3. **E2E Tests**: Test complete user workflows
4. **Visual Tests**: Snapshot and regression testing
5. **Performance Tests**: Verify response times and load handling
6. **Accessibility Tests**: WCAG compliance validation
7. **Security Tests**: Check for vulnerabilities
8. **Smoke Tests**: Quick validation of critical functionality

## 🔒 Security Best Practices

### Secret Management
```bash
# ❌ NEVER commit secrets
password = "admin123"  # FORBIDDEN!

# ✅ ALWAYS use environment variables
password = os.getenv('DB_PASSWORD')  # CORRECT!
```

### Security Checklist
- [ ] No hardcoded credentials
- [ ] Input validation on all user inputs
- [ ] SQL injection prevention (use parameterized queries)
- [ ] XSS protection (sanitize outputs)
- [ ] CSRF tokens for state-changing operations
- [ ] Rate limiting on APIs
- [ ] Secure headers (CSP, HSTS, etc.)
- [ ] Dependency scanning for vulnerabilities
- [ ] Regular security audits
- [ ] Content Security Policy implemented

## 📚 Documentation Standards

### Code Documentation
```python
def calculate_discount(price: float, discount_rate: float) -> float:
    """
    Calculate the discounted price.
    
    Args:
        price: Original price in dollars
        discount_rate: Discount percentage (0-100)
    
    Returns:
        Discounted price after applying the discount
        
    Raises:
        ValueError: If discount_rate is not between 0 and 100
        
    Example:
        >>> calculate_discount(100, 20)
        80.0
    """
```

### Project Documentation
1. **README.md**: Project overview, setup, and usage
2. **CONTRIBUTING.md**: Contribution guidelines
3. **CHANGELOG.md**: Version history and changes
4. **API.md**: API documentation for services
5. **ARCHITECTURE.md**: System design and decisions
6. **SECURITY.md**: Security policies and procedures
7. **DESIGN.md**: UI/UX guidelines and patterns
8. **PERFORMANCE.md**: Performance benchmarks and optimization

### Documentation Rules
- **Write for your future self**: Assume no context
- **Examples over explanation**: Show, don't just tell
- **Keep it current**: Update docs with code changes
- **Diagrams for complexity**: Use visual aids for architecture
- **Link don't duplicate**: Reference existing docs
- **Screenshots for UI**: Visual documentation for interfaces

## 🚀 Performance Guidelines

### Performance Targets
- **Page Load**: < 3 seconds on 3G
- **Time to Interactive**: < 5 seconds
- **First Contentful Paint**: < 1.5 seconds
- **API Response**: < 200ms for simple queries
- **Database Queries**: < 100ms for indexed queries
- **Build Time**: < 5 minutes for CI/CD
- **Test Suite**: < 10 minutes for full suite

### Frontend Performance
```javascript
// Performance optimization checklist
- [ ] Code splitting implemented
- [ ] Lazy loading for routes
- [ ] Images optimized (WebP with fallbacks)
- [ ] Critical CSS inlined
- [ ] JavaScript minified and compressed
- [ ] Service worker for caching
- [ ] Preload/prefetch critical resources
- [ ] Virtual scrolling for long lists
- [ ] Debounced/throttled event handlers
```

### Optimization Strategies
1. **Database**: Proper indexing, query optimization
2. **Caching**: Redis/Memcached for frequent data
3. **CDN**: Static assets delivery
4. **Code Splitting**: Lazy loading for frontend
5. **Compression**: Gzip/Brotli for responses
6. **Monitoring**: APM tools for bottleneck detection
7. **Bundle Analysis**: Regular bundle size audits

## 📦 Dependency Management

### Dependency Rules
1. **Lock Files**: Always commit lock files (package-lock.json, Pipfile.lock)
2. **Version Pinning**: Pin major versions in production
3. **Regular Updates**: Weekly dependency updates for security
4. **Audit**: Run security audits before deployment
5. **Minimal Dependencies**: Evaluate necessity before adding
6. **License Check**: Verify licenses are compatible

```bash
# Regular maintenance commands
npm audit fix              # Fix npm vulnerabilities
pip-audit                  # Python security audit
docker scan image:tag      # Container scanning
npx bundle-phobia         # Check package size before adding
```

## 🔄 CI/CD Requirements

### Pipeline Stages
```yaml
stages:
  - lint        # Code quality checks
  - test        # Run test suites
  - build       # Build artifacts
  - visual      # Visual regression tests
  - security    # Security scanning
  - performance # Performance benchmarks
  - deploy      # Deploy to environment
```

### Quality Gates
- [ ] All tests passing
- [ ] Code coverage met
- [ ] No critical vulnerabilities
- [ ] Performance benchmarks met
- [ ] Visual tests passing
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Bundle size within limits

## 🎭 Environment Management

### Environment Hierarchy
```
Development → Staging → Production
    ↓           ↓           ↓
  Local      Pre-prod    Live users
```

### Environment Variables
```bash
# .env.example (commit this)
DATABASE_URL=postgresql://user:pass@localhost/db
REDIS_URL=redis://localhost:6379
API_KEY=your_api_key_here
FEATURE_FLAG_NEW_UI=false

# .env (never commit)
DATABASE_URL=postgresql://actual:password@db/myapp
REDIS_URL=redis://prod-redis:6379
API_KEY=sk_live_actual_key
FEATURE_FLAG_NEW_UI=true
```

## 📊 Monitoring & Observability

### Three Pillars
1. **Logs**: Structured logging with correlation IDs
2. **Metrics**: Business and technical metrics
3. **Traces**: Distributed tracing for requests

### Frontend Monitoring
```javascript
// Track user interactions
analytics.track('Button Clicked', {
  button_name: 'Submit',
  page: 'Checkout',
  user_id: user.id,
  timestamp: Date.now()
});

// Monitor performance
const perfData = {
  fcp: performance.timing.firstContentfulPaint,
  lcp: performance.timing.largestContentfulPaint,
  cls: performance.timing.cumulativeLayoutShift,
  fid: performance.timing.firstInputDelay
};
```

### Logging Standards
```python
# Structured logging example
logger.info("User action", extra={
    "user_id": user.id,
    "action": "login",
    "ip_address": request.ip,
    "correlation_id": request.id,
    "user_agent": request.headers.get('User-Agent')
})
```

## 🚨 Error Handling

### Error Handling Principles
1. **Fail Fast**: Detect and report errors early
2. **Graceful Degradation**: Provide fallbacks when possible
3. **User-Friendly Messages**: Clear, actionable error messages
4. **Detailed Logging**: Log full context for debugging
5. **No Silent Failures**: Always handle or propagate errors
6. **Error Boundaries**: Catch React component errors

```javascript
// Frontend error boundary
class ErrorBoundary extends React.Component {
  componentDidCatch(error, errorInfo) {
    // Log to error reporting service
    errorReporter.log({ error, errorInfo });
    
    // Show user-friendly error UI
    this.setState({ hasError: true });
  }
  
  render() {
    if (this.state.hasError) {
      return <ErrorFallback />;
    }
    return this.props.children;
  }
}
```

## 📈 Version Management

### Semantic Versioning (SemVer)
```
MAJOR.MINOR.PATCH (e.g., 2.1.3)
  │      │     │
  │      │     └── Bug fixes, minor updates
  │      └──────── New features (backwards compatible)
  └──────────────── Breaking changes
```

### Version Bump Triggers
- **PATCH**: Bug fixes, dependency updates, documentation
- **MINOR**: New features, enhancements, deprecations
- **MAJOR**: Breaking changes, major refactors, API changes

## ♿ Accessibility Standards

### WCAG 2.1 AA Compliance
```html
<!-- Accessibility checklist -->
- [ ] Semantic HTML used
- [ ] ARIA labels where needed
- [ ] Keyboard navigation works
- [ ] Focus indicators visible
- [ ] Color contrast ratios met (4.5:1 normal, 3:1 large)
- [ ] Alt text for images
- [ ] Form labels associated
- [ ] Error messages announced
- [ ] Skip links implemented
- [ ] Page language declared
```

### Testing Accessibility
```javascript
// Automated accessibility testing
import { axe } from '@axe-core/react';

describe('Accessibility', () => {
  it('should have no violations', async () => {
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

## 🎯 Definition of Done

A feature is DONE when:
- [ ] Code complete and follows standards
- [ ] Tests written and passing (>80% coverage)
- [ ] Visual tests passing
- [ ] Accessibility validated
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] CI/CD pipeline passing
- [ ] Deployed to staging environment
- [ ] Acceptance criteria met
- [ ] Performance requirements met
- [ ] Security requirements met
- [ ] Design review completed (for UI changes)

## 🤖 AI Assistant Guidelines

### When working with Claude:
1. **Provide Context**: Share relevant code, errors, and goals
2. **Be Specific**: Clear, detailed questions get better answers
3. **Iterate**: Refine solutions through conversation
4. **Verify**: Always test suggested solutions
5. **Learn**: Understand the why, not just the what
6. **Visual Context**: Include screenshots for UI issues

### Claude's Responsibilities:
- Follow all standards in this document
- Write tests before implementation
- Provide clear, maintainable solutions
- Explain reasoning and trade-offs
- Suggest improvements and best practices
- Flag potential issues and risks
- Verify visual changes against design system
- Check accessibility implications

## 🏆 Golden Rules

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

## 📝 Quick Reference Checklist

### Before committing:
- [ ] Tests written and passing
- [ ] Code follows style guide
- [ ] Documentation updated
- [ ] No hardcoded values
- [ ] Error handling implemented
- [ ] Performance acceptable
- [ ] Security considered
- [ ] Accessibility checked (for UI)
- [ ] Visual review completed (for UI)

### Before creating PR:
- [ ] Branch up to date with target
- [ ] Commits follow convention
- [ ] CI/CD passing
- [ ] Changelog updated
- [ ] PR description complete
- [ ] Screenshots attached (for UI)
- [ ] Reviewers assigned
- [ ] Labels added

### Before deployment:
- [ ] All checks passing
- [ ] Performance tested
- [ ] Security scanned
- [ ] Visual regression tested
- [ ] Rollback plan ready
- [ ] Monitoring configured
- [ ] Feature flags configured
- [ ] Documentation published
- [ ] Stakeholders notified

---

**Remember**: Excellence is not a skill, it's an attitude. Every line of code is an opportunity to make the system better, more maintainable, and more valuable to users. Quality is everyone's responsibility, and great software is built with attention to detail at every level.