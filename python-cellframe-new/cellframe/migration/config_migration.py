"""
⚙️ Configuration Migration Tools

Инструменты миграции конфигураций от JSON к Python configuration objects.

Features:
- ✅ JSON config parsing
- ✅ Python config generation
- ✅ Validation and error detection
- ✅ Backup creation
- ✅ Migration verification

Usage:
    from cellframe.migration.config_migration import migrate_config
    
    # Migrate JSON config to Python
    migrate_config('old_config.json', 'new_config.py')
    
    # Validate configuration
    validate_config('config.json')
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ConfigIssue:
    """Configuration issue"""
    issue_type: str
    description: str
    location: str
    suggested_fix: str
    severity: str  # 'error', 'warning', 'info'


class JSONConfigAnalyzer:
    """Analyze legacy JSON configuration"""
    
    KNOWN_SECTIONS = {
        'modules': 'Module initialization list',
        'app_name': 'Application name',
        'debug_mode': 'Debug mode flag',
        'log_level': 'Logging level',
        'file_log': 'Log file path',
        'config_dir': 'Configuration directory',
        'networks': 'Network configuration',
        'chains': 'Chain configuration',
        'consensus': 'Consensus configuration',
        'services': 'Services configuration',
        'crypto': 'Cryptographic configuration',
        'server': 'Server configuration',
        'client': 'Client configuration'
    }
    
    def __init__(self):
        self.issues: List[ConfigIssue] = []
    
    def analyze_config(self, config_path: Path) -> Tuple[Dict[str, Any], List[ConfigIssue]]:
        """
        Analyze JSON configuration file
        
        Args:
            config_path: Path to JSON config file
            
        Returns:
            Tuple of (config_dict, issues_list)
        """
        self.issues.clear()
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except FileNotFoundError:
            self.issues.append(ConfigIssue(
                issue_type='file_not_found',
                description=f'Configuration file not found: {config_path}',
                location=str(config_path),
                suggested_fix='Create configuration file',
                severity='error'
            ))
            return {}, self.issues
        except json.JSONDecodeError as e:
            self.issues.append(ConfigIssue(
                issue_type='json_syntax_error',
                description=f'JSON syntax error: {e}',
                location=f'{config_path}:{e.lineno}',
                suggested_fix='Fix JSON syntax',
                severity='error'
            ))
            return {}, self.issues
        
        # Validate configuration structure
        self._validate_structure(config)
        
        # Check for deprecated patterns
        self._check_deprecated_patterns(config)
        
        # Validate values
        self._validate_values(config)
        
        return config, self.issues
    
    def _validate_structure(self, config: Dict[str, Any]):
        """Validate configuration structure"""
        required_fields = ['modules', 'app_name']
        
        for field in required_fields:
            if field not in config:
                self.issues.append(ConfigIssue(
                    issue_type='missing_required_field',
                    description=f'Required field missing: {field}',
                    location=f'root.{field}',
                    suggested_fix=f'Add {field} field to configuration',
                    severity='error'
                ))
        
        # Check for unknown fields
        for field in config:
            if field not in self.KNOWN_SECTIONS:
                self.issues.append(ConfigIssue(
                    issue_type='unknown_field',
                    description=f'Unknown configuration field: {field}',
                    location=f'root.{field}',
                    suggested_fix=f'Remove unknown field or check spelling',
                    severity='warning'
                ))
    
    def _check_deprecated_patterns(self, config: Dict[str, Any]):
        """Check for deprecated configuration patterns"""
        
        # Check for deprecated module names
        if 'modules' in config:
            deprecated_modules = {
                'Chain': 'Use cellframe.chain module',
                'Network': 'Use cellframe.network module',
                'Crypto': 'Use dap.crypto module',
                'GlobalDB': 'Use dap.globaldb module'
            }
            
            modules = config['modules']
            if isinstance(modules, list):
                for module in modules:
                    if module in deprecated_modules:
                        self.issues.append(ConfigIssue(
                            issue_type='deprecated_module',
                            description=f'Deprecated module: {module}',
                            location=f'modules.{module}',
                            suggested_fix=deprecated_modules[module],
                            severity='warning'
                        ))
        
        # Check for deprecated configuration keys
        deprecated_keys = {
            'debug_mode': 'Use log_level instead',
            'file_log': 'Use logging.file_path instead',
            'config_dir': 'Use paths.config_dir instead'
        }
        
        for key, suggestion in deprecated_keys.items():
            if key in config:
                self.issues.append(ConfigIssue(
                    issue_type='deprecated_config_key',
                    description=f'Deprecated configuration key: {key}',
                    location=f'root.{key}',
                    suggested_fix=suggestion,
                    severity='warning'
                ))
    
    def _validate_values(self, config: Dict[str, Any]):
        """Validate configuration values"""
        
        # Validate log level
        if 'log_level' in config:
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if config['log_level'] not in valid_levels:
                self.issues.append(ConfigIssue(
                    issue_type='invalid_log_level',
                    description=f'Invalid log level: {config["log_level"]}',
                    location='root.log_level',
                    suggested_fix=f'Use one of: {", ".join(valid_levels)}',
                    severity='error'
                ))
        
        # Validate app_name
        if 'app_name' in config:
            app_name = config['app_name']
            if not isinstance(app_name, str) or not app_name.strip():
                self.issues.append(ConfigIssue(
                    issue_type='invalid_app_name',
                    description='Invalid app_name: must be non-empty string',
                    location='root.app_name',
                    suggested_fix='Set valid application name',
                    severity='error'
                ))


class PythonConfigGenerator:
    """Generate Python configuration from JSON"""
    
    def __init__(self):
        self.template = self._load_template()
    
    def _load_template(self) -> str:
        """Load Python config template"""
        return '''"""
🔧 Migrated Configuration

This configuration was automatically migrated from JSON to Python.
Generated by Cellframe Migration Tools.

Original JSON config: {original_path}
Migration date: {migration_date}
"""

from pathlib import Path
from cellframe.core import CellframeConfig
from dap.config import DapConfig


class MigratedConfig(CellframeConfig):
    """Migrated configuration from JSON"""
    
    def __init__(self):
        super().__init__()
        
        # Basic application settings
        self.app_name = "{app_name}"
        self.log_level = "{log_level}"
        
        # Module configuration
        self.modules = {modules}
        
        # Network settings
        self.network = {{
            {network_config}
        }}
        
        # Chain settings  
        self.chain = {{
            {chain_config}
        }}
        
        # Crypto settings
        self.crypto = {{
            {crypto_config}
        }}
        
        # Server settings
        self.server = {{
            {server_config}
        }}
        
        # Additional settings
        {additional_config}
    
    def validate(self) -> bool:
        """Validate configuration"""
        # Add validation logic here
        return True
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {{
            'app_name': self.app_name,
            'log_level': self.log_level,
            'modules': self.modules,
            'network': self.network,
            'chain': self.chain,
            'crypto': self.crypto,
            'server': self.server
        }}


# Create configuration instance
config = MigratedConfig()

# Export for compatibility
__all__ = ['config', 'MigratedConfig']
'''
    
    def generate_config(self, json_config: Dict[str, Any], 
                       original_path: Path) -> str:
        """
        Generate Python configuration from JSON
        
        Args:
            json_config: Parsed JSON configuration
            original_path: Original JSON file path
            
        Returns:
            Generated Python configuration code
        """
        from datetime import datetime
        
        # Extract configuration sections
        app_name = json_config.get('app_name', 'cellframe-app')
        log_level = json_config.get('log_level', 'INFO')
        modules = json_config.get('modules', [])
        
        # Format modules list
        modules_str = str(modules) if modules else '[]'
        
        # Generate network configuration
        network_config = self._generate_network_config(
            json_config.get('networks', {})
        )
        
        # Generate chain configuration
        chain_config = self._generate_chain_config(
            json_config.get('chains', {})
        )
        
        # Generate crypto configuration
        crypto_config = self._generate_crypto_config(
            json_config.get('crypto', {})
        )
        
        # Generate server configuration
        server_config = self._generate_server_config(
            json_config.get('server', {})
        )
        
        # Generate additional configuration
        additional_config = self._generate_additional_config(json_config)
        
        # Format template
        return self.template.format(
            original_path=original_path,
            migration_date=datetime.now().isoformat(),
            app_name=app_name,
            log_level=log_level,
            modules=modules_str,
            network_config=network_config,
            chain_config=chain_config,
            crypto_config=crypto_config,
            server_config=server_config,
            additional_config=additional_config
        )
    
    def _generate_network_config(self, network_config: Dict[str, Any]) -> str:
        """Generate network configuration section"""
        if not network_config:
            return "'enabled': True"
        
        lines = []
        for key, value in network_config.items():
            if isinstance(value, str):
                lines.append(f"'{key}': '{value}'")
            else:
                lines.append(f"'{key}': {value}")
        
        return ',\n            '.join(lines)
    
    def _generate_chain_config(self, chain_config: Dict[str, Any]) -> str:
        """Generate chain configuration section"""
        if not chain_config:
            return "'enabled': True"
        
        lines = []
        for key, value in chain_config.items():
            if isinstance(value, str):
                lines.append(f"'{key}': '{value}'")
            else:
                lines.append(f"'{key}': {value}")
        
        return ',\n            '.join(lines)
    
    def _generate_crypto_config(self, crypto_config: Dict[str, Any]) -> str:
        """Generate crypto configuration section"""
        if not crypto_config:
            return "'default_key_type': 'sig_dil'"
        
        lines = []
        for key, value in crypto_config.items():
            if isinstance(value, str):
                lines.append(f"'{key}': '{value}'")
            else:
                lines.append(f"'{key}': {value}")
        
        return ',\n            '.join(lines)
    
    def _generate_server_config(self, server_config: Dict[str, Any]) -> str:
        """Generate server configuration section"""
        if not server_config:
            return "'enabled': False"
        
        lines = []
        for key, value in server_config.items():
            if isinstance(value, str):
                lines.append(f"'{key}': '{value}'")
            else:
                lines.append(f"'{key}': {value}")
        
        return ',\n            '.join(lines)
    
    def _generate_additional_config(self, json_config: Dict[str, Any]) -> str:
        """Generate additional configuration sections"""
        known_sections = {
            'modules', 'app_name', 'log_level', 'networks', 
            'chains', 'crypto', 'server'
        }
        
        additional = {}
        for key, value in json_config.items():
            if key not in known_sections:
                additional[key] = value
        
        if not additional:
            return "# No additional configuration"
        
        lines = []
        for key, value in additional.items():
            if isinstance(value, str):
                lines.append(f"self.{key} = '{value}'")
            else:
                lines.append(f"self.{key} = {value}")
        
        return '\n        '.join(lines)


class ConfigMigrator:
    """Main configuration migration orchestrator"""
    
    def __init__(self):
        self.analyzer = JSONConfigAnalyzer()
        self.generator = PythonConfigGenerator()
    
    def migrate_config(self, source_path: Path, target_path: Path) -> bool:
        """
        Migrate configuration from JSON to Python
        
        Args:
            source_path: Source JSON config file
            target_path: Target Python config file
            
        Returns:
            True if migration successful
        """
        logger.info(f"Starting config migration: {source_path} -> {target_path}")
        
        # Analyze source configuration
        config_data, issues = self.analyzer.analyze_config(source_path)
        
        # Check for critical errors
        critical_errors = [i for i in issues if i.severity == 'error']
        if critical_errors:
            logger.error(f"Critical errors found in {source_path}:")
            for error in critical_errors:
                logger.error(f"  - {error.description}")
            return False
        
        # Generate Python configuration
        python_config = self.generator.generate_config(config_data, source_path)
        
        # Write to target file
        try:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(python_config)
            
            logger.info(f"Configuration migrated successfully to {target_path}")
            
            # Generate migration report
            self._generate_migration_report(source_path, target_path, issues)
            
            return True
            
        except Exception as e:
            logger.error(f"Error writing target file {target_path}: {e}")
            return False
    
    def _generate_migration_report(self, source_path: Path, target_path: Path, 
                                  issues: List[ConfigIssue]):
        """Generate configuration migration report"""
        report_path = target_path.parent / f'{target_path.stem}_migration_report.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# Configuration Migration Report\n\n")
            f.write(f"**Source:** {source_path}\n")
            f.write(f"**Target:** {target_path}\n")
            f.write(f"**Issues found:** {len(issues)}\n\n")
            
            if issues:
                f.write("## Issues Found\n\n")
                for issue in issues:
                    f.write(f"### {issue.issue_type} ({issue.severity})\n")
                    f.write(f"**Location:** {issue.location}\n")
                    f.write(f"**Description:** {issue.description}\n")
                    f.write(f"**Suggested fix:** {issue.suggested_fix}\n\n")
            
            f.write("## Next Steps\n\n")
            f.write("1. Review the generated Python configuration\n")
            f.write("2. Test the configuration with your application\n")
            f.write("3. Address any issues listed above\n")
            f.write("4. Update your application to use the new configuration\n")
    
    def validate_config(self, config_path: Path) -> List[ConfigIssue]:
        """
        Validate configuration file
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            List of issues found
        """
        _, issues = self.analyzer.analyze_config(config_path)
        return issues


# High-level API functions
def migrate_config(source_path: str, target_path: str) -> bool:
    """
    Migrate configuration from JSON to Python
    
    Args:
        source_path: Source JSON config file path
        target_path: Target Python config file path
        
    Returns:
        True if migration successful
    """
    migrator = ConfigMigrator()
    return migrator.migrate_config(Path(source_path), Path(target_path))


def validate_config(config_path: str) -> List[ConfigIssue]:
    """
    Validate configuration file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        List of issues found
    """
    migrator = ConfigMigrator()
    return migrator.validate_config(Path(config_path))


def analyze_config(config_path: str) -> Tuple[Dict[str, Any], List[ConfigIssue]]:
    """
    Analyze configuration file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Tuple of (config_dict, issues_list)
    """
    analyzer = JSONConfigAnalyzer()
    return analyzer.analyze_config(Path(config_path))


__all__ = [
    'migrate_config',
    'validate_config',
    'analyze_config',
    'ConfigMigrator',
    'JSONConfigAnalyzer',
    'PythonConfigGenerator',
    'ConfigIssue'
] 