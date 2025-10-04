# Cellframe Node QA Testing

Professional automated testing with **pytest** and **[Allure Report](https://allurereport.org/)**.

## 🚀 Quick Start

### Local Testing

```bash
# Install dependencies
cd qa-tests
pip install -r requirements.txt

# Install Allure CLI (choose one):
# macOS:
brew install allure

# Linux:
wget https://github.com/allure-framework/allure2/releases/download/2.24.1/allure-2.24.1.tgz
sudo tar -xzf allure-2.24.1.tgz -C /opt/
sudo ln -s /opt/allure-2.24.1/bin/allure /usr/local/bin/allure

# Run tests
pytest test_cellframe_qa.py --alluredir=allure-results -v

# View beautiful report
allure serve allure-results
```

### Docker Testing

```bash
cd qa-tests

# Build image
docker build -f Dockerfile.qa-pytest -t cellframe-qa .

# Run tests
docker run --rm --privileged \
  -v $(pwd)/allure-results:/opt/qa-tests/allure-results \
  cellframe-qa

# View report
allure serve allure-results
```

---

## 📊 Test Coverage

| Test Suite | Tests | Coverage |
|-------------|-------|----------|
| Installation | 2 | Package, version |
| File System | 9 | Directories, executables, configs |
| Python Environment | 2 | Python 3.10, pip |
| Node Startup | 2 | Process, logs |
| CLI | 2 | Version, network list |
| Network Status | 2 | Backbone, KelVPN |
| Wallet | 2 | List, create |
| Resources | 2 | Memory, CPU |
| Logs | 3 | Errors, critical issues |
| **Total** | **29** | **100% automated** |

---

## 🎨 Allure Features

- **📈 Rich Reports**: Beautiful HTML reports with charts
- **📝 Test Steps**: Detailed step-by-step execution
- **📎 Attachments**: Logs, configs, command outputs
- **🏷️ Categories**: Automatic error categorization
- **⏱️ Timeline**: Visual execution timeline
- **📊 Trends**: Historical test results
- **🎯 Behaviors**: BDD-style view (Features/Stories)
- **⚠️ Severity**: CRITICAL, NORMAL, MINOR priorities

---

## 📚 Documentation

- **Full Guide**: [ALLURE_PROFESSIONAL.md](ALLURE_PROFESSIONAL.md)
- **Test Code**: [test_cellframe_qa.py](test_cellframe_qa.py)
- **Allure Docs**: https://allurereport.org/

---

## 🔄 CI/CD Integration

QA tests run automatically in GitLab CI:

1. **Trigger**: Push to `master`, `qa/*` branches, or merge requests
2. **Stage**: `qa_tests`
3. **Job**: `qa_functional_tests`
4. **Artifacts**: `allure-results/`, `allure-report/`, logs

**View Pipeline**: https://gitlab.demlabs.net/cellframe/cellframe-node/-/pipelines

---

## ✅ Success Criteria

All tests must pass (100%) for the pipeline to succeed.

Failed tests will show:
- ❌ Test name and severity
- 📝 Failed step with details
- 📎 Attached logs and outputs
- 🔍 Error message and stack trace

---

## 🛠 Adding New Tests

### Example Test

```python
import allure

@allure.feature("My Feature")
@allure.story("My Story")
@allure.severity(allure.severity_level.CRITICAL)
class TestMyFeature:
    
    @allure.title("Verify something important")
    def test_something(self):
        with allure.step("Step 1: Do something"):
            result = do_something()
            allure.attach(str(result), name="Result")
        
        with allure.step("Step 2: Verify result"):
            assert result == expected
```

### Run Specific Tests

```bash
# Run only critical tests
pytest -m critical --alluredir=allure-results

# Run only network tests
pytest -k "network" --alluredir=allure-results

# Run specific class
pytest test_cellframe_qa.py::TestNetworkStatus --alluredir=allure-results
```

---

## 🐛 Troubleshooting

### Java not found

Allure requires Java 11+:

```bash
sudo apt-get install openjdk-17-jre-headless
```

### Port 8080 in use

```bash
allure serve allure-results -p 8081
```

### Docker permission denied

```bash
# Add user to docker group
sudo usermod -aG docker $USER
# Log out and back in
```

---

## 📞 Support

- **Issues**: Create issue in GitLab
- **Documentation**: See `ALLURE_PROFESSIONAL.md`
- **Allure Docs**: https://docs.qameta.io/allure-report/

---

**Built with ❤️ for professional QA**
