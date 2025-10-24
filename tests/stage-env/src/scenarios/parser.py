"""
YAML scenario parser with include support and variable substitution.

Provides loading, validation, and preprocessing of test scenarios
with user-friendly error messages.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import ValidationError

from ..utils.logger import get_logger
from .schema import TestScenario

logger = get_logger(__name__)


class ScenarioParseError(Exception):
    """Error parsing scenario file."""
    
    def __init__(self, message: str, file_path: Optional[Path] = None, line: Optional[int] = None):
        self.file_path = file_path
        self.line = line
        super().__init__(self._format_message(message))
    
    def _format_message(self, message: str) -> str:
        """Format error message with context."""
        parts = []
        if self.file_path:
            parts.append(f"File: {self.file_path}")
        if self.line:
            parts.append(f"Line: {self.line}")
        parts.append(message)
        return "\n".join(parts)


class ScenarioParser:
    """Parse and validate YAML test scenarios."""
    
    def __init__(self, scenarios_root: Path, common_root: Optional[Path] = None):
        """
        Initialize parser.
        
        Args:
            scenarios_root: Root directory for scenario files
            common_root: Optional root directory for common includes (defaults to scenarios_root)
        """
        self.scenarios_root = Path(scenarios_root)
        self.common_root = Path(common_root) if common_root else self.scenarios_root
        self._loaded_files: Dict[Path, Dict[str, Any]] = {}
        self._variable_pattern = re.compile(r'\{\{(\w+)\}\}')
    
    def load_scenario(self, scenario_path: str) -> TestScenario:
        """
        Load and parse scenario from YAML file.
        
        Args:
            scenario_path: Relative path to scenario file
            
        Returns:
            Parsed and validated test scenario
            
        Raises:
            ScenarioParseError: If scenario is invalid
        """
        full_path = self._resolve_path(scenario_path)
        
        if not full_path.exists():
            raise ScenarioParseError(
                f"Scenario file not found: {scenario_path}",
                file_path=full_path
            )
        
        try:
            # Load main scenario file
            raw_data = self._load_yaml_file(full_path)
            
            # Process includes
            if "includes" in raw_data:
                raw_data = self._process_includes(raw_data, full_path.parent)
            
            # Validate with Pydantic
            scenario = TestScenario(**raw_data)
            
            logger.info(f"Loaded scenario: {scenario.name} from {scenario_path}")
            return scenario
            
        except yaml.YAMLError as e:
            raise ScenarioParseError(
                f"Invalid YAML syntax: {str(e)}",
                file_path=full_path
            ) from e
        except ValidationError as e:
            raise ScenarioParseError(
                f"Scenario validation failed:\n{self._format_validation_errors(e)}",
                file_path=full_path
            ) from e
        except Exception as e:
            raise ScenarioParseError(
                f"Unexpected error loading scenario: {str(e)}",
                file_path=full_path
            ) from e
    
    def _resolve_path(self, path_str: str) -> Path:
        """Resolve scenario path relative to scenarios root."""
        path = Path(path_str)
        if path.is_absolute():
            return path
        return (self.scenarios_root / path).resolve()
    
    def _load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML file with caching."""
        if file_path in self._loaded_files:
            return self._loaded_files[file_path].copy()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not isinstance(data, dict):
                raise ScenarioParseError(
                    "Scenario file must contain a YAML dictionary",
                    file_path=file_path
                )
            
            self._loaded_files[file_path] = data
            return data.copy()
            
        except FileNotFoundError as e:
            raise ScenarioParseError(
                f"File not found: {file_path}",
                file_path=file_path
            ) from e
        except PermissionError as e:
            raise ScenarioParseError(
                f"Permission denied: {file_path}",
                file_path=file_path
            ) from e
    
    def _process_includes(self, data: Dict[str, Any], base_dir: Path) -> Dict[str, Any]:
        """
        Process include directives in scenario.
        
        Args:
            data: Scenario data with includes
            base_dir: Base directory for resolving relative paths
            
        Returns:
            Merged scenario data
        """
        includes = data.pop("includes", [])
        
        if not includes:
            return data
        
        # Load all included files
        included_data: List[Dict[str, Any]] = []
        for include_path in includes:
            # Try multiple search paths:
            # 1. Relative to scenario file directory
            # 2. Relative to scenarios_root
            # 3. Relative to common_root (for common includes)
            search_paths = [
                (base_dir / include_path).resolve(),
                (self.scenarios_root / include_path).resolve(),
                (self.common_root / include_path).resolve(),
            ]
            
            include_full = None
            for path in search_paths:
                if path.exists():
                    include_full = path
                    break
            
            if include_full is None:
                raise ScenarioParseError(
                    f"Included file not found: {include_path}\nSearched in:\n" +
                    "\n".join(f"  - {p}" for p in search_paths),
                    file_path=search_paths[0]
                )
            
            included = self._load_yaml_file(include_full)
            included_data.append(included)
        
        # Merge: includes first, then main scenario (main overrides)
        result = {}
        for included in included_data:
            result = self._deep_merge(result, included)
        result = self._deep_merge(result, data)
        
        return result
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        
        Lists are concatenated, dicts are recursively merged.
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result:
                if isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._deep_merge(result[key], value)
                elif isinstance(result[key], list) and isinstance(value, list):
                    result[key] = result[key] + value
                else:
                    result[key] = value
            else:
                result[key] = value
        
        return result
    
    def substitute_variables(self, text: str, variables: Dict[str, Any]) -> str:
        """
        Substitute {{variable}} placeholders in text.
        
        Args:
            text: Text with variable placeholders
            variables: Variable name -> value mapping
            
        Returns:
            Text with variables substituted
        """
        def replace_var(match):
            var_name = match.group(1)
            if var_name not in variables:
                raise ScenarioParseError(f"Undefined variable: {var_name}")
            return str(variables[var_name])
        
        return self._variable_pattern.sub(replace_var, text)
    
    def _format_validation_errors(self, error: ValidationError) -> str:
        """Format Pydantic validation errors for users."""
        lines = []
        for err in error.errors():
            location = " -> ".join(str(loc) for loc in err["loc"])
            message = err["msg"]
            lines.append(f"  • {location}: {message}")
        return "\n".join(lines)


class ScenarioLoader:
    """High-level scenario loader with directory scanning."""
    
    def __init__(self, scenarios_root: Path):
        """
        Initialize loader.
        
        Args:
            scenarios_root: Root directory containing scenarios
        """
        self.scenarios_root = Path(scenarios_root)
        self.parser = ScenarioParser(scenarios_root)
    
    def discover_scenarios(self, pattern: str = "**/*.yml") -> List[Path]:
        """
        Discover all scenario files matching pattern.
        
        Args:
            pattern: Glob pattern for scenario files
            
        Returns:
            List of scenario file paths (relative to scenarios_root)
        """
        if not self.scenarios_root.exists():
            logger.warning(f"Scenarios directory not found: {self.scenarios_root}")
            return []
        
        scenarios = []
        for path in self.scenarios_root.glob(pattern):
            if path.is_file():
                rel_path = path.relative_to(self.scenarios_root)
                scenarios.append(rel_path)
        
        logger.info(f"Discovered {len(scenarios)} scenario files")
        return sorted(scenarios)
    
    def load_all_scenarios(self, pattern: str = "**/*.yml") -> Dict[str, TestScenario]:
        """
        Load all discovered scenarios.
        
        Args:
            pattern: Glob pattern for scenario files
            
        Returns:
            Dictionary of scenario_path -> TestScenario
        """
        scenarios = {}
        discovered = self.discover_scenarios(pattern)
        
        for scenario_path in discovered:
            try:
                scenario = self.parser.load_scenario(str(scenario_path))
                scenarios[str(scenario_path)] = scenario
            except ScenarioParseError as e:
                logger.error(f"Failed to load {scenario_path}: {e}")
                # Continue with other scenarios
        
        return scenarios

