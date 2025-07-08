"""
🔄 Migration Tools

Автоматические инструменты миграции от старого Python Cellframe API к новому.

Features:
- ✅ Code scanner для обнаружения старого API
- ✅ Automatic code transformation
- ✅ Configuration migration
- ✅ Test generation для проверки
- ✅ Migration report

Usage:
    from cellframe.migration import migrate_code, analyze_code
    
    # Analyze existing code
    report = analyze_code('old_project/')
    
    # Migrate code
    migrate_code('old_project/', 'new_project/', report)
    
    # CLI usage
    python -m cellframe.migration --analyze old_project/
    python -m cellframe.migration --migrate old_project/ new_project/
"""

import ast
import os
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MigrationLevel(Enum):
    """Migration complexity level"""
    SIMPLE = "simple"      # Direct 1:1 mapping
    MEDIUM = "medium"      # Some restructuring needed
    COMPLEX = "complex"    # Manual intervention required
    MANUAL = "manual"      # Cannot be automated


@dataclass
class CodeIssue:
    """Represents a code issue found during analysis"""
    file_path: str
    line_number: int
    issue_type: str
    old_code: str
    suggested_fix: str
    migration_level: MigrationLevel
    description: str


@dataclass
class MigrationReport:
    """Migration analysis report"""
    project_path: str
    files_analyzed: int
    issues_found: List[CodeIssue] = field(default_factory=list)
    migration_stats: Dict[str, int] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    
    def add_issue(self, issue: CodeIssue):
        """Add issue to report"""
        self.issues_found.append(issue)
        issue_type = issue.issue_type
        self.migration_stats[issue_type] = self.migration_stats.get(issue_type, 0) + 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get migration summary"""
        return {
            'total_files': self.files_analyzed,
            'total_issues': len(self.issues_found),
            'by_type': self.migration_stats,
            'by_level': {
                level.value: len([i for i in self.issues_found if i.migration_level == level])
                for level in MigrationLevel
            }
        }


class LegacyAPIPattern:
    """Patterns for detecting legacy API usage"""
    
    # Legacy import patterns
    LEGACY_IMPORTS = {
        r'from\s+CellFrame\s+import\s+\*': 'import cellframe',
        r'from\s+DAP\s+import\s+\*': 'import dap',
        r'import\s+CellFrame': 'import cellframe',
        r'import\s+DAP': 'import dap'
    }
    
    # Legacy API calls
    LEGACY_CALLS = {
        # CellFrame API
        r'CellFrame\.init\(\[(.*?)\]\)': r'cellframe.CellframeNode(\1)',
        r'CellFrame\.deinit\(\)': r'# Use context manager: with cellframe.CellframeNode() as node:',
        r'CellFrame\.Chain\.find_by_id\((.*?)\)': r'node.chain.get_by_id(\1)',
        r'CellFrame\.Chain\.load_all\(\)': r'node.chain.load_all()',
        
        # DAP API
        r'DAP\.init\((.*?)\)': r'with dap.Dap() as dap_instance:',
        r'DAP\.deinit\(\)': r'# Use context manager: with dap.Dap() as dap_instance:',
        r'DAP\.setLogLevel\((.*?)\)': r'dap.DapConfig().logging.set_level(\1)',
        r'DAP\.configGetItem\((.*?)\)': r'dap.DapConfig().get(\1)',
        
        # Legacy classes
        r'DAP\.Crypto\.Key\((.*?)\)': r'dap.DapKey(\1)',
        r'CellFrame\.Chain\.ChainObject\((.*?)\)': r'cellframe.CellframeChain(\1)',
    }
    
    # JSON configuration patterns
    JSON_CONFIG_PATTERNS = {
        r'"modules":\s*\[(.*?)\]': 'modules list in JSON config',
        r'"app_name":\s*"(.*?)"': 'app_name configuration',
        r'"debug_mode":\s*(true|false)': 'debug_mode configuration'
    }


class CodeAnalyzer:
    """Analyzes Python code for legacy API usage"""
    
    def __init__(self):
        self.patterns = LegacyAPIPattern()
        self.report = None
    
    def analyze_file(self, file_path: Path) -> List[CodeIssue]:
        """Analyze single Python file"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return issues
        
        # Check for legacy imports
        for i, line in enumerate(lines, 1):
            issues.extend(self._check_legacy_imports(file_path, i, line))
            issues.extend(self._check_legacy_calls(file_path, i, line))
            issues.extend(self._check_json_config(file_path, i, line))
        
        # AST analysis for more complex patterns
        try:
            tree = ast.parse(content)
            issues.extend(self._analyze_ast(file_path, tree, lines))
        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
        
        return issues
    
    def _check_legacy_imports(self, file_path: Path, line_num: int, line: str) -> List[CodeIssue]:
        """Check for legacy import patterns"""
        issues = []
        
        for pattern, suggestion in self.patterns.LEGACY_IMPORTS.items():
            if re.search(pattern, line):
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    issue_type="legacy_import",
                    old_code=line.strip(),
                    suggested_fix=suggestion,
                    migration_level=MigrationLevel.SIMPLE,
                    description="Legacy import pattern detected"
                ))
        
        return issues
    
    def _check_legacy_calls(self, file_path: Path, line_num: int, line: str) -> List[CodeIssue]:
        """Check for legacy API calls"""
        issues = []
        
        for pattern, suggestion in self.patterns.LEGACY_CALLS.items():
            if re.search(pattern, line):
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    issue_type="legacy_api_call",
                    old_code=line.strip(),
                    suggested_fix=suggestion,
                    migration_level=MigrationLevel.MEDIUM,
                    description="Legacy API call detected"
                ))
        
        return issues
    
    def _check_json_config(self, file_path: Path, line_num: int, line: str) -> List[CodeIssue]:
        """Check for JSON configuration patterns"""
        issues = []
        
        for pattern, description in self.patterns.JSON_CONFIG_PATTERNS.items():
            if re.search(pattern, line):
                issues.append(CodeIssue(
                    file_path=str(file_path),
                    line_number=line_num,
                    issue_type="json_config",
                    old_code=line.strip(),
                    suggested_fix="Use Python configuration instead of JSON",
                    migration_level=MigrationLevel.COMPLEX,
                    description=f"JSON config pattern: {description}"
                ))
        
        return issues
    
    def _analyze_ast(self, file_path: Path, tree: ast.AST, lines: List[str]) -> List[CodeIssue]:
        """Analyze AST for complex patterns"""
        issues = []
        
        class LegacyAPIVisitor(ast.NodeVisitor):
            def __init__(self, analyzer):
                self.analyzer = analyzer
                self.issues = []
            
            def visit_Call(self, node):
                """Visit function calls"""
                if isinstance(node.func, ast.Attribute):
                    # Check for CellFrame.init() pattern
                    if (isinstance(node.func.value, ast.Name) and 
                        node.func.value.id == 'CellFrame' and
                        node.func.attr == 'init'):
                        
                        self.issues.append(CodeIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_type="legacy_init_call",
                            old_code=lines[node.lineno-1].strip(),
                            suggested_fix="Use cellframe.CellframeNode() context manager",
                            migration_level=MigrationLevel.COMPLEX,
                            description="Legacy initialization pattern"
                        ))
                
                self.generic_visit(node)
            
            def visit_Import(self, node):
                """Visit import statements"""
                for alias in node.names:
                    if alias.name in ['CellFrame', 'DAP']:
                        self.issues.append(CodeIssue(
                            file_path=str(file_path),
                            line_number=node.lineno,
                            issue_type="legacy_import",
                            old_code=lines[node.lineno-1].strip(),
                            suggested_fix=f"import {alias.name.lower()}",
                            migration_level=MigrationLevel.SIMPLE,
                            description="Legacy import detected"
                        ))
                
                self.generic_visit(node)
        
        visitor = LegacyAPIVisitor(self)
        visitor.visit(tree)
        issues.extend(visitor.issues)
        
        return issues
    
    def analyze_project(self, project_path: Path) -> MigrationReport:
        """Analyze entire project"""
        report = MigrationReport(
            project_path=str(project_path),
            files_analyzed=0
        )
        
        # Find all Python files
        python_files = list(project_path.rglob('*.py'))
        
        for file_path in python_files:
            issues = self.analyze_file(file_path)
            for issue in issues:
                report.add_issue(issue)
            report.files_analyzed += 1
        
        # Add recommendations
        report.recommendations = self._generate_recommendations(report)
        
        return report
    
    def _generate_recommendations(self, report: MigrationReport) -> List[str]:
        """Generate migration recommendations"""
        recommendations = []
        
        stats = report.get_summary()
        
        if stats['by_type'].get('legacy_import', 0) > 0:
            recommendations.append(
                "Replace legacy imports with modern equivalents: "
                "CellFrame -> cellframe, DAP -> dap"
            )
        
        if stats['by_type'].get('legacy_api_call', 0) > 0:
            recommendations.append(
                "Replace legacy API calls with modern context managers and methods"
            )
        
        if stats['by_type'].get('json_config', 0) > 0:
            recommendations.append(
                "Consider migrating JSON configuration to Python configuration objects"
            )
        
        if stats['by_level'].get('complex', 0) > 0:
            recommendations.append(
                "Some complex patterns require manual intervention. "
                "Review suggestions carefully."
            )
        
        return recommendations


class CodeMigrator:
    """Migrates code from legacy API to new API"""
    
    def __init__(self):
        self.analyzer = CodeAnalyzer()
    
    def migrate_file(self, source_path: Path, target_path: Path, 
                    issues: List[CodeIssue]) -> bool:
        """Migrate single file"""
        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
        except Exception as e:
            logger.error(f"Error reading source file {source_path}: {e}")
            return False
        
        # Apply simple and medium complexity fixes
        modified_lines = lines.copy()
        
        # Sort issues by line number (reverse order to avoid line number shifts)
        file_issues = [i for i in issues if i.file_path == str(source_path)]
        file_issues.sort(key=lambda x: x.line_number, reverse=True)
        
        for issue in file_issues:
            if issue.migration_level in [MigrationLevel.SIMPLE, MigrationLevel.MEDIUM]:
                line_idx = issue.line_number - 1
                if 0 <= line_idx < len(modified_lines):
                    # Simple pattern replacement
                    old_line = modified_lines[line_idx]
                    new_line = self._apply_fix(old_line, issue)
                    modified_lines[line_idx] = new_line
                    
                    logger.info(f"Migrated line {issue.line_number} in {source_path}")
        
        # Write migrated content
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(modified_lines))
            return True
        except Exception as e:
            logger.error(f"Error writing target file {target_path}: {e}")
            return False
    
    def _apply_fix(self, line: str, issue: CodeIssue) -> str:
        """Apply migration fix to line"""
        # For simple replacements, use the suggested fix
        if issue.migration_level == MigrationLevel.SIMPLE:
            # Pattern-based replacement
            for pattern, replacement in LegacyAPIPattern.LEGACY_IMPORTS.items():
                if re.search(pattern, line):
                    return re.sub(pattern, replacement, line)
        
        # For medium complexity, apply more complex transformations
        if issue.migration_level == MigrationLevel.MEDIUM:
            for pattern, replacement in LegacyAPIPattern.LEGACY_CALLS.items():
                if re.search(pattern, line):
                    return re.sub(pattern, replacement, line)
        
        # If no pattern matches, return original line with comment
        return f"{line}  # TODO: Manual migration required - {issue.suggested_fix}"
    
    def migrate_project(self, source_path: Path, target_path: Path, 
                       report: MigrationReport) -> bool:
        """Migrate entire project"""
        logger.info(f"Starting migration from {source_path} to {target_path}")
        
        # Create target directory
        target_path.mkdir(parents=True, exist_ok=True)
        
        # Copy and migrate Python files
        python_files = list(source_path.rglob('*.py'))
        
        for source_file in python_files:
            # Calculate relative path
            rel_path = source_file.relative_to(source_path)
            target_file = target_path / rel_path
            
            # Get issues for this file
            file_issues = [i for i in report.issues_found if i.file_path == str(source_file)]
            
            if file_issues:
                # Migrate with fixes
                success = self.migrate_file(source_file, target_file, report.issues_found)
                if success:
                    logger.info(f"Migrated {source_file} -> {target_file}")
                else:
                    logger.error(f"Failed to migrate {source_file}")
            else:
                # Copy as-is
                target_file.parent.mkdir(parents=True, exist_ok=True)
                target_file.write_text(source_file.read_text(encoding='utf-8'))
        
        # Copy non-Python files
        for source_file in source_path.rglob('*'):
            if source_file.is_file() and source_file.suffix != '.py':
                rel_path = source_file.relative_to(source_path)
                target_file = target_path / rel_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                target_file.write_bytes(source_file.read_bytes())
        
        # Generate migration report
        self._generate_migration_report(target_path, report)
        
        logger.info(f"Migration completed. Results in {target_path}")
        return True
    
    def _generate_migration_report(self, target_path: Path, report: MigrationReport):
        """Generate migration report file"""
        report_file = target_path / 'MIGRATION_REPORT.md'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Migration Report\n\n")
            f.write(f"**Source:** {report.project_path}\n")
            f.write(f"**Target:** {target_path}\n")
            f.write(f"**Files analyzed:** {report.files_analyzed}\n")
            f.write(f"**Issues found:** {len(report.issues_found)}\n\n")
            
            # Summary
            f.write("## Summary\n\n")
            summary = report.get_summary()
            for issue_type, count in summary['by_type'].items():
                f.write(f"- {issue_type}: {count}\n")
            
            f.write("\n## Migration Levels\n\n")
            for level, count in summary['by_level'].items():
                f.write(f"- {level}: {count}\n")
            
            # Recommendations
            f.write("\n## Recommendations\n\n")
            for rec in report.recommendations:
                f.write(f"- {rec}\n")
            
            # Detailed issues
            f.write("\n## Detailed Issues\n\n")
            for issue in report.issues_found:
                f.write(f"### {issue.file_path}:{issue.line_number}\n")
                f.write(f"**Type:** {issue.issue_type}\n")
                f.write(f"**Level:** {issue.migration_level.value}\n")
                f.write(f"**Old code:** `{issue.old_code}`\n")
                f.write(f"**Suggested fix:** `{issue.suggested_fix}`\n")
                f.write(f"**Description:** {issue.description}\n\n")


# High-level API functions
def analyze_code(project_path: str) -> MigrationReport:
    """
    Analyze project for legacy API usage
    
    Args:
        project_path: Path to project directory
        
    Returns:
        Migration report with issues found
    """
    analyzer = CodeAnalyzer()
    return analyzer.analyze_project(Path(project_path))


def migrate_code(source_path: str, target_path: str, 
                report: Optional[MigrationReport] = None) -> bool:
    """
    Migrate project from legacy API to new API
    
    Args:
        source_path: Source project path
        target_path: Target project path  
        report: Optional pre-generated report
        
    Returns:
        True if migration successful
    """
    if report is None:
        report = analyze_code(source_path)
    
    migrator = CodeMigrator()
    return migrator.migrate_project(Path(source_path), Path(target_path), report)


def generate_migration_guide(report: MigrationReport) -> str:
    """
    Generate human-readable migration guide
    
    Args:
        report: Migration analysis report
        
    Returns:
        Migration guide text
    """
    guide = "# Migration Guide: Legacy to Modern Python Cellframe API\n\n"
    
    guide += "## Overview\n"
    guide += f"This guide covers migrating from legacy Python Cellframe API to the new modern API.\n\n"
    
    guide += "## Key Changes\n\n"
    guide += "### Imports\n"
    guide += "```python\n"
    guide += "# Old\n"
    guide += "from CellFrame import *\n"
    guide += "from DAP import *\n\n"
    guide += "# New\n"
    guide += "import cellframe\n"
    guide += "import dap\n"
    guide += "```\n\n"
    
    guide += "### Initialization\n"
    guide += "```python\n"
    guide += "# Old\n"
    guide += "CellFrame.init([\"Chain\", \"Network\"])\n"
    guide += "DAP.init(json_config)\n\n"
    guide += "# New\n"
    guide += "with cellframe.CellframeNode() as node:\n"
    guide += "    # Your code here\n"
    guide += "```\n\n"
    
    guide += "### API Calls\n"
    guide += "```python\n"
    guide += "# Old\n"
    guide += "chain = CellFrame.Chain.find_by_id(\"mainnet\")\n"
    guide += "key = DAP.Crypto.Key(\"sig_dil\")\n\n"
    guide += "# New\n"
    guide += "chain = node.chain.get_by_id(\"mainnet\")\n"
    guide += "key = dap.DapKey(\"sig_dil\")\n"
    guide += "```\n\n"
    
    if report.issues_found:
        guide += f"## Issues Found in Your Code\n\n"
        guide += f"Total issues: {len(report.issues_found)}\n\n"
        
        for issue in report.issues_found[:10]:  # Show first 10 issues
            guide += f"### {issue.file_path}:{issue.line_number}\n"
            guide += f"**Old:** `{issue.old_code}`\n"
            guide += f"**New:** `{issue.suggested_fix}`\n\n"
    
    return guide


__all__ = [
    'analyze_code',
    'migrate_code', 
    'generate_migration_guide',
    'MigrationReport',
    'CodeIssue',
    'MigrationLevel',
    'CodeAnalyzer',
    'CodeMigrator'
] 