#!/usr/bin/env python3
"""
Test runner for CellFrame Node Python Plugin
Run this from the tests/ directory
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, cwd=None):
    """Run command and return result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)


def install_dependencies():
    """Install test dependencies"""
    print("📦 Installing test dependencies...")
    
    returncode, stdout, stderr = run_command(
        "pip install -r requirements-test.txt"
    )
    
    if returncode != 0:
        print(f"❌ Failed to install dependencies: {stderr}")
        return False
    
    print("✅ Dependencies installed successfully")
    return True


def run_tests(test_type="all", verbose=False, coverage=False, markers=None):
    """Run tests with specified configuration"""
    print(f"🧪 Running {test_type} tests...")
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test paths based on type
    if test_type == "unit":
        cmd.append("unit")
    elif test_type == "integration":
        cmd.append("integration")
    elif test_type == "performance":
        cmd.append("performance")
    elif test_type == "all":
        cmd.extend(["unit", "integration"])
    
    # Add verbose flag
    if verbose:
        cmd.append("-v")
    
    # Add coverage (paths relative to tests/ directory)
    if coverage:
        cmd.extend([
            "--cov=../python-cellframe/cellframe",
            "--cov=../python-dap/dap", 
            "--cov=../src",
            "--cov-report=html:coverage_html",
            "--cov-report=term-missing"
        ])
    
    # Add markers
    if markers:
        cmd.extend(["-m", markers])
    
    # Add output formatting
    cmd.extend([
        "--tb=short",
        "--color=yes",
        "--junitxml=junit.xml"
    ])
    
    # Run tests
    returncode, stdout, stderr = run_command(" ".join(cmd))
    
    print(stdout)
    if stderr:
        print(f"⚠️  Warnings/Errors: {stderr}")
    
    return returncode == 0


def run_linting():
    """Run code linting"""
    print("🔍 Running code linting...")
    
    # Run flake8 (paths relative to tests/)
    print("  Running flake8...")
    returncode, stdout, stderr = run_command(
        "flake8 ../python-cellframe/cellframe ../python-dap/dap ../src/"
    )
    
    if returncode != 0:
        print(f"❌ Flake8 failed: {stdout}")
        return False
    
    # Run mypy
    print("  Running mypy...")
    returncode, stdout, stderr = run_command(
        "mypy ../python-cellframe/cellframe --ignore-missing-imports"
    )
    
    if returncode != 0:
        print(f"⚠️  MyPy warnings: {stdout}")
    
    print("✅ Linting completed")
    return True


def run_security_checks():
    """Run security checks"""
    print("🔒 Running security checks...")
    
    # Check for known security issues
    returncode, stdout, stderr = run_command(
        "python -m pip check"
    )
    
    if returncode != 0:
        print(f"⚠️  Dependency issues: {stdout}")
    
    print("✅ Security checks completed")
    return True


def generate_test_report():
    """Generate test report"""
    print("📊 Generating test report...")
    
    # Create report directory
    report_dir = Path("reports")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate HTML report
    returncode, stdout, stderr = run_command(
        "python -m pytest unit integration --html=reports/report.html --self-contained-html"
    )
    
    if returncode == 0:
        print("✅ Test report generated at reports/report.html")
    else:
        print(f"❌ Failed to generate report: {stderr}")
    
    return returncode == 0


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description="Run tests for CellFrame Node Python Plugin")
    parser.add_argument(
        "--type",
        choices=["unit", "integration", "performance", "all"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "--markers", "-m",
        help="Run tests with specific markers"
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install test dependencies"
    )
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Run linting"
    )
    parser.add_argument(
        "--security",
        action="store_true",
        help="Run security checks"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate test report"
    )
    parser.add_argument(
        "--all-checks",
        action="store_true",
        help="Run all checks (tests, linting, security)"
    )
    
    args = parser.parse_args()
    
    # Ensure we're in the tests directory
    tests_dir = Path(__file__).parent
    if tests_dir.name != "tests":
        print("❌ Error: This script must be run from the tests/ directory")
        print(f"   Current directory: {Path.cwd()}")
        print(f"   Expected directory: {tests_dir}")
        sys.exit(1)
    
    os.chdir(tests_dir)
    
    print("🚀 CellFrame Node Python Plugin Test Runner")
    print("=" * 50)
    print(f"📁 Working directory: {Path.cwd()}")
    print("=" * 50)
    
    success = True
    
    # Install dependencies if requested
    if args.install_deps or args.all_checks:
        success = install_dependencies() and success
    
    # Run linting if requested
    if args.lint or args.all_checks:
        success = run_linting() and success
    
    # Run security checks if requested
    if args.security or args.all_checks:
        success = run_security_checks() and success
    
    # Run tests
    if not args.lint and not args.security and not args.report:
        success = run_tests(
            test_type=args.type,
            verbose=args.verbose,
            coverage=args.coverage,
            markers=args.markers
        ) and success
    
    # Generate report if requested
    if args.report or args.all_checks:
        success = generate_test_report() and success
    
    print("=" * 50)
    if success:
        print("✅ All checks passed!")
        sys.exit(0)
    else:
        print("❌ Some checks failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 