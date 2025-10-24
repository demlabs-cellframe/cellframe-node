"""
Scenario validation and comprehensive error reporting.

Provides pre-execution validation, user-friendly error messages,
and suggestions for common issues.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from ..utils.logger import get_logger
from .parser import ScenarioParser, ScenarioParseError
from .schema import TestScenario

logger = get_logger(__name__)


class ValidationIssue:
    """Single validation issue with context and suggestions."""
    
    def __init__(
        self,
        severity: str,
        message: str,
        location: Optional[str] = None,
        suggestion: Optional[str] = None,
        doc_link: Optional[str] = None
    ):
        self.severity = severity  # error, warning, info
        self.message = message
        self.location = location
        self.suggestion = suggestion
        self.doc_link = doc_link
    
    def __str__(self) -> str:
        """Format issue for display."""
        parts = [f"[{self.severity.upper()}] {self.message}"]
        
        if self.location:
            parts.append(f"  Location: {self.location}")
        
        if self.suggestion:
            parts.append(f"  💡 Suggestion: {self.suggestion}")
        
        if self.doc_link:
            parts.append(f"  📖 Documentation: {self.doc_link}")
        
        return "\n".join(parts)


class ValidationReport:
    """Validation report with all issues."""
    
    def __init__(self, scenario_path: str):
        self.scenario_path = scenario_path
        self.issues: List[ValidationIssue] = []
    
    def add_issue(
        self,
        severity: str,
        message: str,
        location: Optional[str] = None,
        suggestion: Optional[str] = None,
        doc_link: Optional[str] = None
    ):
        """Add validation issue."""
        issue = ValidationIssue(severity, message, location, suggestion, doc_link)
        self.issues.append(issue)
    
    def has_errors(self) -> bool:
        """Check if report contains errors."""
        return any(issue.severity == "error" for issue in self.issues)
    
    def has_warnings(self) -> bool:
        """Check if report contains warnings."""
        return any(issue.severity == "warning" for issue in self.issues)
    
    def get_summary(self) -> str:
        """Get summary of issues."""
        errors = sum(1 for i in self.issues if i.severity == "error")
        warnings = sum(1 for i in self.issues if i.severity == "warning")
        
        if errors == 0 and warnings == 0:
            return f"✅ Scenario '{self.scenario_path}' is valid"
        
        parts = [f"Validation results for '{self.scenario_path}':"]
        if errors > 0:
            parts.append(f"  ❌ {errors} error(s)")
        if warnings > 0:
            parts.append(f"  ⚠️  {warnings} warning(s)")
        
        return "\n".join(parts)
    
    def __str__(self) -> str:
        """Format full report."""
        lines = [self.get_summary(), ""]
        
        for issue in self.issues:
            lines.append(str(issue))
            lines.append("")
        
        return "\n".join(lines)


class ScenarioValidator:
    """Validate scenarios with comprehensive error reporting."""
    
    def __init__(self, scenarios_root: Path):
        """Initialize validator."""
        self.scenarios_root = Path(scenarios_root)
        self.parser = ScenarioParser(scenarios_root)
    
    def validate_scenario(self, scenario_path: str) -> ValidationReport:
        """
        Validate scenario and generate report.
        
        Args:
            scenario_path: Path to scenario file
            
        Returns:
            Validation report with all issues
        """
        report = ValidationReport(scenario_path)
        
        try:
            # Try to load scenario
            scenario = self.parser.load_scenario(scenario_path)
            
            # Perform semantic validation
            self._validate_network_config(scenario, report)
            self._validate_variables(scenario, report)
            self._validate_node_references(scenario, report)
            self._validate_timeouts(scenario, report)
            self._validate_best_practices(scenario, report)
            
        except ScenarioParseError as e:
            report.add_issue(
                "error",
                f"Parse error: {str(e)}",
                suggestion="Check YAML syntax and file structure",
                doc_link="tests/scenarios/README.md#writing-scenarios"
            )
        except ValidationError as e:
            for err in e.errors():
                location = " -> ".join(str(loc) for loc in err["loc"])
                report.add_issue(
                    "error",
                    f"Schema validation failed: {err['msg']}",
                    location=location,
                    suggestion=self._get_validation_suggestion(err),
                    doc_link="tests/scenarios/README.md#basic-structure"
                )
        except Exception as e:
            report.add_issue(
                "error",
                f"Unexpected validation error: {str(e)}",
                suggestion="Please report this issue"
            )
        
        return report
    
    def _validate_network_config(self, scenario: TestScenario, report: ValidationReport):
        """Validate network configuration."""
        if not scenario.network.nodes:
            report.add_issue(
                "warning",
                "No nodes defined in network",
                location="network.nodes",
                suggestion="Add at least one node or use network template",
                doc_link="tests/scenarios/README.md#network-templates"
            )
        
        # Check for duplicate node names
        node_names = [node.name for node in scenario.network.nodes]
        duplicates = set([name for name in node_names if node_names.count(name) > 1])
        
        if duplicates:
            report.add_issue(
                "error",
                f"Duplicate node names: {', '.join(duplicates)}",
                location="network.nodes",
                suggestion="Ensure all node names are unique"
            )
    
    def _validate_variables(self, scenario: TestScenario, report: ValidationReport):
        """Validate variable usage."""
        import re
        
        # Collect all variable definitions
        defined_vars = set(scenario.variables.keys())
        
        # Track variables from save operations
        for step in scenario.setup + scenario.test:
            if hasattr(step, 'save') and step.save:
                defined_vars.add(step.save)
        
        # Find all variable usages
        used_vars = set()
        
        def extract_vars(text: str):
            if isinstance(text, str):
                for match in re.finditer(r'\{\{(\w+)\}\}', text):
                    used_vars.add(match.group(1))
        
        # Check all string fields
        for step in scenario.setup + scenario.test:
            if hasattr(step, 'cli'):
                extract_vars(step.cli)
            if hasattr(step, 'rpc'):
                extract_vars(step.rpc)
            if hasattr(step, 'contains'):
                extract_vars(step.contains)
        
        for check in scenario.check:
            if hasattr(check, 'cli'):
                extract_vars(check.cli)
            if hasattr(check, 'contains'):
                extract_vars(check.contains)
        
        # Check for undefined variables
        undefined = used_vars - defined_vars
        if undefined:
            report.add_issue(
                "error",
                f"Undefined variables: {', '.join(undefined)}",
                suggestion="Define variables in 'variables' section or use 'save' in setup steps",
                doc_link="tests/scenarios/README.md#variables"
            )
    
    def _validate_node_references(self, scenario: TestScenario, report: ValidationReport):
        """Validate node references in steps."""
        node_names = set([node.name for node in scenario.network.nodes])
        
        if not node_names:
            return  # Already warned about no nodes
        
        for step in scenario.setup + scenario.test:
            if hasattr(step, 'node') and step.node:
                if step.node not in node_names:
                    report.add_issue(
                        "error",
                        f"Reference to undefined node: {step.node}",
                        suggestion=f"Available nodes: {', '.join(sorted(node_names))}",
                        doc_link="tests/scenarios/README.md#network-templates"
                    )
    
    def _validate_timeouts(self, scenario: TestScenario, report: ValidationReport):
        """Validate timeout values."""
        for step in scenario.setup + scenario.test:
            if hasattr(step, 'timeout') and step.timeout:
                if step.timeout < 1:
                    report.add_issue(
                        "warning",
                        f"Very short timeout: {step.timeout}s",
                        suggestion="Consider increasing timeout to at least 5s"
                    )
                elif step.timeout > 300:
                    report.add_issue(
                        "warning",
                        f"Very long timeout: {step.timeout}s",
                        suggestion="Consider if 5-minute timeout is really needed"
                    )
    
    def _validate_best_practices(self, scenario: TestScenario, report: ValidationReport):
        """Check best practices."""
        # Check for missing description
        if not scenario.description or len(scenario.description) < 10:
            report.add_issue(
                "warning",
                "Scenario has no or very short description",
                location="description",
                suggestion="Add meaningful description of what this scenario tests"
            )
        
        # Check for missing tags
        if not scenario.tags:
            report.add_issue(
                "info",
                "Scenario has no tags",
                location="tags",
                suggestion="Add tags like [feature, priority, duration] for categorization"
            )
        
        # Check for missing checks
        if not scenario.check:
            report.add_issue(
                "warning",
                "Scenario has no checks",
                location="check",
                suggestion="Add checks to verify test results",
                doc_link="tests/scenarios/README.md#checks"
            )
        
        # Check for wait steps after state changes
        for i, step in enumerate(scenario.setup + scenario.test):
            if hasattr(step, 'cli') and any(cmd in step.cli for cmd in ['token_decl', 'token_emit', 'tx_create']):
                if not hasattr(step, 'wait') or not step.wait:
                    report.add_issue(
                        "info",
                        f"Consider adding 'wait' after state-changing command: {step.cli}",
                        suggestion="Add 'wait: 3s' to ensure operation completes"
                    )
    
    def _get_validation_suggestion(self, error: Dict[str, Any]) -> Optional[str]:
        """Get suggestion based on validation error type."""
        error_type = error.get("type", "")
        
        suggestions = {
            "missing": "This field is required. Check spelling and indentation.",
            "type_error": "Wrong value type. Check expected type in documentation.",
            "value_error": "Invalid value. Check allowed values and format.",
            "extra_forbidden": "Unknown field. Remove it or check spelling.",
        }
        
        for key, suggestion in suggestions.items():
            if key in error_type:
                return suggestion
        
        return None


def validate_scenarios_directory(scenarios_root: Path) -> Dict[str, ValidationReport]:
    """
    Validate all scenarios in directory.
    
    Args:
        scenarios_root: Root scenarios directory
        
    Returns:
        Dictionary of scenario_path -> ValidationReport
    """
    validator = ScenarioValidator(scenarios_root)
    reports = {}
    
    for scenario_file in scenarios_root.rglob("*.yml"):
        if scenario_file.is_file():
            rel_path = scenario_file.relative_to(scenarios_root)
            
            # Skip template/common files (they're meant to be included)
            if "common" in str(rel_path) or "templates" in str(rel_path):
                continue
            
            report = validator.validate_scenario(str(rel_path))
            reports[str(rel_path)] = report
    
    return reports


def print_validation_summary(reports: Dict[str, ValidationReport]):
    """Print summary of all validation reports."""
    total = len(reports)
    passed = sum(1 for r in reports.values() if not r.has_errors())
    failed = total - passed
    warnings = sum(1 for r in reports.values() if r.has_warnings())
    
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Total scenarios: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️  With warnings: {warnings}")
    print("=" * 70 + "\n")
    
    if failed > 0:
        print("Failed scenarios:\n")
        for path, report in reports.items():
            if report.has_errors():
                print(report)
                print()

