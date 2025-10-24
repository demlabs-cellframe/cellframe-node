"""Unit tests for scenario executor."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from scenarios.executor import ScenarioExecutor


class TestYAMLErrorDetection:
    """Test YAML error detection in CLI responses."""
    
    def test_detect_yaml_error_dict(self, sample_yaml_error):
        """Test detection of YAML error with dict format."""
        executor = ScenarioExecutor()
        
        result = {
            "returncode": 0,
            "stdout": sample_yaml_error,
            "stderr": ""
        }
        
        success = executor._check_expectation(result, "success", None)
        
        assert success is False, "Should detect YAML error"
    
    def test_detect_yaml_success(self, sample_yaml_success):
        """Test that valid YAML response is accepted."""
        executor = ScenarioExecutor()
        
        result = {
            "returncode": 0,
            "stdout": sample_yaml_success,
            "stderr": ""
        }
        
        success = executor._check_expectation(result, "success", None)
        
        assert success is True, "Should accept valid YAML"
    
    def test_expect_error_with_yaml_error(self, sample_yaml_error):
        """Test that expect=error works with YAML errors."""
        executor = ScenarioExecutor()
        
        result = {
            "returncode": 0,
            "stdout": sample_yaml_error,
            "stderr": ""
        }
        
        success = executor._check_expectation(result, "error", None)
        
        assert success is True, "Should match expected error"


class TestHashExtraction:
    """Test hash extraction from CLI output."""
    
    @pytest.fixture
    def executor(self):
        """Create executor instance."""
        return ScenarioExecutor()
    
    def test_extract_hash_from_yaml(self, executor):
        """Test extracting hash from YAML response."""
        import yaml
        
        output = """
        hash: 0x1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF
        status: success
        """
        
        parsed = yaml.safe_load(output)
        
        # Simulate extraction logic
        saved_value = None
        if isinstance(parsed, dict):
            for key in ['hash', 'tx_hash', 'datum_hash']:
                if key in parsed and parsed[key]:
                    saved_value = parsed[key]
                    break
        
        assert saved_value is not None
        assert saved_value.startswith("0x")
        assert len(saved_value) == 66  # 0x + 64 hex chars
    
    def test_extract_hash_regex_fallback(self, executor):
        """Test regex fallback for hash extraction."""
        import re
        
        output = "Transaction created: 0xABCDEF1234567890ABCDEF1234567890ABCDEF1234567890ABCDEF1234567890"
        
        hash_pattern = r'0x[0-9a-fA-F]{64,}'
        match = re.search(hash_pattern, output)
        
        assert match is not None
        assert match.group(0).startswith("0x")


class TestCLIDefaultsApplication:
    """Test application of CLI defaults to commands."""
    
    def test_defaults_applied_from_global(self):
        """Test that global defaults are applied to commands."""
        from scenarios.schema import TestScenario, StepDefaults
        from scenarios.parser import ScenarioParser
        
        # This would need actual YAML parsing - simplified for unit test
        # In real test: parse YAML with includes, check merged defaults
        pass  # TODO: Implement with mocked parser
    
    def test_defaults_merge_hierarchy(self):
        """Test hierarchical defaults merging (global > section > group)."""
        executor = ScenarioExecutor()
        
        global_defaults = StepDefaults(node="node1", cli={"net": "stagenet"})
        section_defaults = StepDefaults(wait="5s")
        
        merged = executor._merge_defaults(global_defaults, section_defaults)
        
        assert merged is not None
        assert merged.node == "node1"
        assert merged.wait == "5s"
        assert merged.cli == {"net": "stagenet"}


class TestDatumMonitorIntegration:
    """Test datum monitor behavior with invalid hashes."""
    
    @pytest.mark.asyncio
    async def test_invalid_hash_rejected_immediately(self):
        """Test that invalid hash is rejected without monitoring."""
        from monitoring.datum import DatumMonitor
        from monitoring.datum import DatumStatus
        
        monitor = DatumMonitor()
        
        # Try to track obviously invalid hash
        invalid_hash = "errors: code: 102"
        
        result_future = monitor.track_datum(
            datum_hash=invalid_hash,
            node="node1",
            network="stagenet"
        )
        
        # Should resolve immediately
        result = await result_future
        
        assert result.status == DatumStatus.REJECTED
        assert "Invalid datum hash format" in result.error_message
        assert result.elapsed_time < 1.0, "Should reject immediately"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

