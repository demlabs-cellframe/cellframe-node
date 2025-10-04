# Professional Allure Reports for Cellframe Node QA

## 🎯 Professional Approach

This QA framework uses **official Allure Report** from [allurereport.org](https://allurereport.org/) - the industry standard for test reporting.

**Why Allure?**
- ✅ **Professional**: Used by companies worldwide
- ✅ **Standardized**: No custom JSON formats
- ✅ **Rich Features**: Steps, attachments, categories, trends
- ✅ **Easy to maintain**: Huge community support
- ✅ **Multi-language**: Python, Java, JavaScript, C#, Ruby, Go, etc.

---

## 🏗 Architecture

```
pytest                    ← Test framework
  ↓
allure-pytest            ← Official Allure adapter
  ↓
allure-results/          ← JSON test results
  ↓
allure CLI               ← Report generator
  ↓
allure-report/           ← Beautiful HTML report
```

---

## 📦 Components

### 1. Test Suite (`test_cellframe_qa.py`)
Professional pytest tests with Allure annotations:

```python
import allure

@allure.feature("Installation")
@allure.story("Package Installation")
@allure.severity(allure.severity_level.CRITICAL)
class TestInstallation:
    
    @allure.title("Verify node version")
    @allure.description("Get and verify Cellframe Node version")
    def test_node_version(self):
        with allure.step("Execute cellframe-node -version"):
            # Test code here
            pass
```

### 2. Configuration (`pytest.ini`)
Standard pytest configuration with Allure settings

### 3. Dependencies (`requirements.txt`)
```
pytest>=7.4.0
allure-pytest>=2.13.2
```

### 4. Docker (`Dockerfile.qa-pytest`)
Production-ready environment with:
- Ubuntu 24.04
- Python 3 + pytest
- Official Allure CLI (Java)
- Cellframe Node

---

## 🚀 Quick Start

### Local Testing

#### 1. Install dependencies
```bash
cd qa-tests
pip install -r requirements.txt

# Install Allure CLI (macOS)
brew install allure

# Install Allure CLI (Linux)
wget https://github.com/allure-framework/allure2/releases/download/2.24.1/allure-2.24.1.tgz
sudo tar -xzf allure-2.24.1.tgz -C /opt/
sudo ln -s /opt/allure-2.24.1/bin/allure /usr/local/bin/allure
```

#### 2. Run tests
```bash
# Run tests and generate Allure results
pytest test_cellframe_qa.py --alluredir=allure-results -v

# Generate and view report
allure serve allure-results
```

### Docker Testing

#### 1. Build image
```bash
docker build -f Dockerfile.qa-pytest -t cellframe-qa-pytest .
```

#### 2. Run tests in Docker
```bash
# Run tests
docker run --rm --privileged \
    -v $(pwd)/allure-results:/opt/qa-tests/allure-results \
    -v $(pwd)/allure-report:/opt/qa-tests/allure-report \
    cellframe-qa-pytest

# View report locally
allure serve allure-results
```

#### 3. One-line test & view
```bash
docker run --rm --privileged \
    -v $(pwd)/allure-results:/opt/qa-tests/allure-results \
    cellframe-qa-pytest && \
allure serve allure-results
```

---

## 📊 Allure Features

### Features Used

1. **@allure.feature()** - Group tests by feature
2. **@allure.story()** - Sub-group by user story
3. **@allure.severity()** - Test priority (BLOCKER, CRITICAL, NORMAL, MINOR, TRIVIAL)
4. **@allure.title()** - Custom test name
5. **@allure.description()** - Test description
6. **@allure.step()** - Test steps with details
7. **@allure.attach()** - Attach logs, screenshots, files
8. **@allure.issue()** - Link to issue tracker
9. **@allure.environment()** - Environment info

### Example: Full Featured Test

```python
@allure.feature("Network Status")
@allure.story("Network Connectivity")
@allure.severity(allure.severity_level.CRITICAL)
class TestNetworkStatus:
    
    @allure.title("Verify Backbone network status")
    @allure.description("Check if Backbone network is operational")
    @allure.issue("NET-001", "Network connectivity")
    def test_backbone_status(self):
        with allure.step("Get Backbone network status"):
            code, stdout, stderr = run_command(
                "cellframe-node-cli net -net Backbone get status"
            )
            
        with allure.step("Verify status command succeeded"):
            assert code == 0, f"Command failed: {stderr}"
            
            allure.attach(
                stdout,
                name="Backbone Status",
                attachment_type=allure.attachment_type.TEXT
            )
        
        with allure.step("Check network is active"):
            assert "net: Backbone" in stdout
```

### Report Views

Allure report includes:
- **Overview**: Total tests, pass rate, duration
- **Suites**: Tests grouped by classes
- **Graphs**: Charts and statistics
- **Timeline**: Execution timeline
- **Behaviors**: BDD-style view (Features/Stories)
- **Packages**: Python package structure
- **Categories**: Failed test categories
- **History**: Historical trends (if configured)

---

## 🔧 Advanced Configuration

### pytest.ini Customization

```ini
[pytest]
# Allure markers
markers =
    critical: Critical tests that must pass
    smoke: Smoke tests for quick validation
    
# Run only critical tests
addopts = -m critical
```

### Run specific tests

```bash
# Run only critical tests
pytest -m critical --alluredir=allure-results

# Run only network tests
pytest -k "network" --alluredir=allure-results

# Run specific class
pytest test_cellframe_qa.py::TestNetworkStatus --alluredir=allure-results
```

### Parallel execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n 4 --alluredir=allure-results
```

---

## 📈 CI/CD Integration

### GitLab CI

```yaml
qa_tests_allure:
  stage: qa_tests
  image: docker:latest
  services:
    - docker:dind
  script:
    - cd qa-tests
    - docker build -f Dockerfile.qa-pytest -t cellframe-qa .
    - |
      docker run --rm --privileged \
        -v $(pwd)/allure-results:/opt/qa-tests/allure-results \
        cellframe-qa
  artifacts:
    when: always
    paths:
      - qa-tests/allure-results/
      - qa-tests/allure-report/
    reports:
      junit: qa-tests/allure-results/*.xml
    expire_in: 1 week
```

### View Reports in CI

1. **Download artifacts** from GitLab pipeline
2. **Unzip** `allure-results/` directory
3. **Run locally**:
   ```bash
   allure serve allure-results
   ```

### Optional: Allure Server

For persistent reports, deploy **Allure Server**:
- https://github.com/kochetkov-ma/allure-server
- https://github.com/fescobar/allure-docker-service

---

## 🎨 Customization

### Add custom categories

Create `categories.json` in `allure-results/`:

```json
[
  {
    "name": "Network Issues",
    "matchedStatuses": ["failed"],
    "messageRegex": ".*network.*"
  },
  {
    "name": "Timeout Errors",
    "matchedStatuses": ["broken"],
    "messageRegex": ".*timeout.*"
  }
]
```

### Add environment info

Create `environment.properties`:

```properties
Browser=Chrome
Browser.Version=120.0
Stand=Production
Node.Version=5.5-0
OS=Ubuntu 24.04
```

### Add executors info

Create `executor.json`:

```json
{
  "name": "GitLab CI",
  "type": "gitlab",
  "buildName": "Pipeline #123",
  "buildUrl": "https://gitlab.com/...",
  "reportUrl": "https://...",
  "reportName": "QA Report"
}
```

---

## 🐛 Troubleshooting

### Issue: Allure command not found

```bash
# Install Allure CLI
wget https://github.com/allure-framework/allure2/releases/download/2.24.1/allure-2.24.1.tgz
sudo tar -xzf allure-2.24.1.tgz -C /opt/
sudo ln -s /opt/allure-2.24.1/bin/allure /usr/local/bin/allure
```

### Issue: Java not installed

```bash
# Allure requires Java
sudo apt-get install openjdk-17-jre-headless
```

### Issue: Port 8080 already in use

```bash
# Use different port
allure serve allure-results -p 8081
```

---

## 📚 Documentation

- **Allure Report**: https://allurereport.org/
- **Allure pytest**: https://docs.qameta.io/allure-report/frameworks/python/pytest/
- **Pytest**: https://docs.pytest.org/
- **Allure GitHub**: https://github.com/allure-framework

---

## ✅ Best Practices

1. **Use descriptive test names** - Clear @allure.title()
2. **Add steps** - Break tests into logical steps
3. **Attach evidence** - Screenshots, logs, API responses
4. **Set severity** - Prioritize critical tests
5. **Link issues** - Connect tests to Jira/GitLab issues
6. **Keep tests fast** - Use fixtures and parallel execution
7. **Review reports** - Analyze trends and patterns
8. **Clean results** - Don't accumulate old results

---

## 🎯 Summary

**Before (Custom bash scripts):**
- ❌ Hard to maintain custom JSON generator
- ❌ No standard format
- ❌ Limited features
- ❌ No community support

**After (Official Allure):**
- ✅ Industry standard tool
- ✅ Rich features out of the box
- ✅ Easy to extend
- ✅ Huge community
- ✅ Professional reports
- ✅ CI/CD ready

**Result:** Professional, maintainable, and powerful QA framework! 🚀

