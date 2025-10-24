"""
YAML scenario executor with runtime context and error handling.

Executes test scenarios step-by-step with variable substitution,
CLI command execution, and result validation.
"""

import asyncio
import re
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..utils.logger import get_logger
from ..monitoring import MonitoringManager, DatumMonitorResult
from .parser import ScenarioParser
from .schema import (
    CLIStep, RPCStep, WaitStep, WaitForDatumStep, PythonStep, BashStep, LoopStep, StepGroup,
    CLICheck, RPCCheck, PythonCheck, BashCheck,
    TestScenario, TestStep, CheckSpec, StepDefaults, SectionConfig, DatumStatus
)

logger = get_logger(__name__)


class ScenarioExecutionError(Exception):
    """Error during scenario execution."""
    
    def __init__(self, message: str, step: Optional[Any] = None, context: Optional[Dict] = None):
        self.step = step
        self.context = context
        super().__init__(self._format_message(message))
    
    def _format_message(self, message: str) -> str:
        """Format error with context."""
        parts = [message]
        if self.step:
            parts.append(f"Step: {self.step}")
        if self.context:
            parts.append(f"Context: {self.context}")
        return "\n".join(parts)


class RuntimeContext:
    """Runtime context for scenario execution."""
    
    def __init__(self, scenario: TestScenario):
        """Initialize runtime context."""
        self.scenario = scenario
        self.variables: Dict[str, Any] = scenario.variables.copy()
        
        # Add network_name from network configuration
        if hasattr(scenario, 'network') and scenario.network:
            if hasattr(scenario.network, 'name') and scenario.network.name:
                self.variables['network_name'] = scenario.network.name
                logger.debug(f"Set network_name from scenario.network.name: {scenario.network.name}")
            else:
                logger.warning(f"scenario.network exists but has no 'name' attribute or it's None")
        else:
            logger.warning(f"scenario has no 'network' attribute or it's None")
        
        self.step_results: List[Dict[str, Any]] = []
        self.start_time = time.time()
        self.parser = ScenarioParser(Path.cwd())
    
    def set_variable(self, name: str, value: Any):
        """Set runtime variable."""
        self.variables[name] = value
        logger.debug(f"Set variable: {name} = {value}")
    
    def get_variable(self, name: str) -> Any:
        """Get runtime variable."""
        if name not in self.variables:
            raise ScenarioExecutionError(f"Undefined variable: {name}")
        return self.variables[name]
    
    def substitute(self, text: str) -> str:
        """Substitute variables in text."""
        return self.parser.substitute_variables(text, self.variables)
    
    def add_result(self, step_type: str, success: bool, details: Dict[str, Any]):
        """Record step execution result."""
        result = {
            "type": step_type,
            "success": success,
            "timestamp": time.time() - self.start_time,
            **details
        }
        self.step_results.append(result)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get execution summary."""
        total = len(self.step_results)
        passed = sum(1 for r in self.step_results if r["success"])
        failed = total - passed
        duration = time.time() - self.start_time
        
        return {
            "scenario": self.scenario.name,
            "total_steps": total,
            "passed": passed,
            "failed": failed,
            "duration_seconds": round(duration, 2),
            "success_rate": round(passed / total * 100, 1) if total > 0 else 0
        }


class ScenarioExecutor:
    """Execute test scenarios with full lifecycle management."""
    
    def __init__(self, node_cli_path: str = "cellframe-node-cli", log_file: Optional[Path] = None, debug: bool = False):
        """
        Initialize executor.
        
        Args:
            node_cli_path: Path to cellframe-node-cli binary
            log_file: Optional path to detailed log file
            debug: Enable debug logging
        """
        self.node_cli_path = node_cli_path
        self.log_file = log_file
        self.debug = debug
        self._running = False
        # Monitoring manager будет получен через синглтон при старте сценария
    
    def _log_to_file(self, message: str):
        """Write message to log file if enabled."""
        if self.log_file:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(message + '\n')
    
    def _merge_defaults(
        self,
        *defaults_list: Optional[StepDefaults]
    ) -> Optional[StepDefaults]:
        """
        Merge multiple StepDefaults objects with priority (last wins).
        
        Args:
            *defaults_list: List of StepDefaults to merge (global → section → group → step)
            
        Returns:
            Merged StepDefaults or None
        """
        merged = {}
        merged_cli = {}
        
        for defaults in defaults_list:
            if defaults:
                if defaults.node is not None:
                    merged['node'] = defaults.node
                if defaults.wait is not None:
                    merged['wait'] = defaults.wait
                if defaults.expect is not None:
                    merged['expect'] = defaults.expect
                if defaults.timeout is not None:
                    merged['timeout'] = defaults.timeout
                if defaults.cli is not None:
                    # Merge CLI defaults (later overrides earlier)
                    merged_cli.update(defaults.cli)
        
        if merged_cli:
            merged['cli'] = merged_cli
        
        return StepDefaults(**merged) if merged else None
    
    def _apply_defaults(self, step: TestStep, defaults: Optional[StepDefaults]) -> TestStep:
        """
        Apply defaults to a step if not already set.
        
        Args:
            step: Original step
            defaults: Defaults to apply
            
        Returns:
            Step with defaults applied
        """
        if not defaults:
            return step
        
        # Universal approach: apply all defaults to all steps that have these attributes
        # No type checking - just check if attribute exists and has default value
        
        # node
        if defaults.node and hasattr(step, 'node'):
            if step.node == "node1":  # Default value
                step.node = defaults.node
        
        # wait
        if defaults.wait and hasattr(step, 'wait'):
            if not step.wait:  # None or empty
                step.wait = defaults.wait
        
        # expect
        if defaults.expect and hasattr(step, 'expect'):
            if step.expect == "success":  # Default value
                step.expect = defaults.expect
        
        # timeout
        if defaults.timeout and hasattr(step, 'timeout'):
            if step.timeout == 30:  # Default value
                step.timeout = defaults.timeout
        
        # Special handling for WaitForDatumStep timeouts
        if isinstance(step, WaitForDatumStep) and defaults.timeout:
            # Apply timeout to all WaitForDatumStep timeout fields if they have default values
            if step.timeout_total == 300:
                step.timeout_total = defaults.timeout
            if step.timeout_mempool == 60:
                step.timeout_mempool = defaults.timeout
            if step.timeout_verification == 120:
                step.timeout_verification = defaults.timeout
            if step.timeout_in_blocks == 180:
                step.timeout_in_blocks = defaults.timeout
        
        return step
    
    async def execute_scenario(self, scenario: TestScenario) -> RuntimeContext:
        """
        Execute complete test scenario.
        
        Args:
            scenario: Parsed test scenario
            
        Returns:
            Runtime context with results
            
        Raises:
            ScenarioExecutionError: If execution fails
        """
        logger.info(f"Starting scenario: {scenario.name}")
        if scenario.description:
            logger.info(f"Description: {scenario.description}")
        
        ctx = RuntimeContext(scenario)
        self._running = True
        
        try:
            # Global defaults (applied to all phases)
            global_defaults = scenario.defaults
            
            # Setup phase
            if scenario.setup:
                logger.info("Executing setup phase...")
                section_defaults = self._merge_defaults(global_defaults, scenario.setup.defaults)
                await self._execute_steps(scenario.setup.steps, ctx, section_defaults)
            
            # Test phase
            logger.info("Executing test phase...")
            section_defaults = self._merge_defaults(global_defaults, scenario.test.defaults)
            await self._execute_steps(scenario.test.steps, ctx, section_defaults)
            
            # Check phase
            if scenario.check:
                logger.info("Executing check phase...")
                section_defaults = self._merge_defaults(global_defaults, scenario.check.defaults)
                await self._execute_checks(scenario.check.steps, ctx, section_defaults)
            
            summary = ctx.get_summary()
            logger.info(f"Scenario completed: {summary['passed']}/{summary['total_steps']} steps passed")
            
            if summary['failed'] > 0:
                raise ScenarioExecutionError(
                    f"Scenario failed: {summary['failed']} step(s) failed",
                    context=summary
                )
            
            return ctx
            
        except KeyboardInterrupt:
            logger.warning("Scenario execution interrupted by user")
            raise
        except ScenarioExecutionError:
            raise
        except Exception as e:
            raise ScenarioExecutionError(
                f"Unexpected error during execution: {str(e)}",
                context=ctx.get_summary()
            ) from e
        finally:
            self._running = False
    
    async def _execute_steps(
        self,
        steps: List[TestStep],
        ctx: RuntimeContext,
        defaults: Optional[StepDefaults] = None
    ):
        """
        Execute list of test steps with defaults.
        
        Args:
            steps: List of steps to execute
            ctx: Runtime context
            defaults: Default parameters to apply
        """
        for i, step in enumerate(steps, 1):
            # Generate step description for logging
            step_type = type(step).__name__
            step_desc = step_type
            
            # Add details for specific step types
            if isinstance(step, WaitForDatumStep):
                datum_count = len(step.wait_for_datum) if isinstance(step.wait_for_datum, list) else 1
                step_desc = f"WaitForDatumStep ({datum_count} datum{'s' if datum_count > 1 else ''})"
            elif isinstance(step, StepGroup) and step.name:
                step_desc = f"StepGroup: {step.name}"
            
            logger.info(f"Step {i}/{len(steps)}: {step_desc}")
            
            # Handle StepGroup
            if isinstance(step, StepGroup):
                # Merge group defaults with section defaults
                group_defaults = self._merge_defaults(defaults, step.defaults)
                
                # Recursively execute group steps
                await self._execute_steps(step.steps, ctx, group_defaults)
                
                if step.name:
                    logger.info(f"Exited group: {step.name}")
                continue
            
            # Apply defaults to step
            step = self._apply_defaults(step, defaults)
            
            if isinstance(step, CLIStep):
                await self._execute_cli_step(step, ctx, defaults)
            elif isinstance(step, RPCStep):
                await self._execute_rpc_step(step, ctx)
            elif isinstance(step, WaitStep):
                await self._execute_wait_step(step, ctx)
            elif isinstance(step, WaitForDatumStep):
                await self._execute_wait_for_datum_step(step, ctx)
            elif isinstance(step, PythonStep):
                await self._execute_python_step(step, ctx)
            elif isinstance(step, BashStep):
                await self._execute_bash_step(step, ctx)
            elif isinstance(step, LoopStep):
                await self._execute_loop_step(step, ctx, defaults)
            else:
                raise ScenarioExecutionError(f"Unknown step type: {type(step)}")
    
    async def _execute_cli_step(self, step: CLIStep, ctx: RuntimeContext, defaults: Optional[StepDefaults] = None):
        """Execute CLI command step."""
        # Substitute variables in command
        cmd = ctx.substitute(step.cli)
        
        # Apply CLI defaults if present
        if defaults and defaults.cli:
            from ..utils.cli_parser import get_cli_parser
            cli_parser = get_cli_parser()
            
            # Substitute variables in CLI defaults
            cli_defaults = {
                key: ctx.substitute(value) 
                for key, value in defaults.cli.items()
            }
            
            # Apply defaults to command
            cmd_with_defaults = cli_parser.apply_cli_defaults(cmd, cli_defaults)
            
            # Ensure result is a string
            if cmd_with_defaults and isinstance(cmd_with_defaults, str):
                cmd = cmd_with_defaults
            else:
                if self.debug:
                    logger.warning(f"apply_cli_defaults returned invalid result: {type(cmd_with_defaults)}")
        
        logger.debug(f"Executing CLI: {cmd} on {step.node}")
        
        # Log to file
        self._log_to_file(f"\n{'=' * 70}")
        self._log_to_file(f"CLI COMMAND")
        self._log_to_file(f"{'=' * 70}")
        self._log_to_file(f"Node: {step.node}")
        self._log_to_file(f"Command: {cmd}")
        self._log_to_file(f"Timeout: {step.timeout}s")
        self._log_to_file(f"Expected: {step.expect}")
        self._log_to_file("")
        
        try:
            # Execute command
            result = await self._run_cli_command(cmd, step.node, step.timeout)
            
            # Log response
            self._log_to_file(f"--- Node Response ---")
            self._log_to_file(f"Exit Code: {result['returncode']}")
            if result["stdout"]:
                self._log_to_file(f"\nStdout:")
                self._log_to_file(result["stdout"])
            if result["stderr"]:
                self._log_to_file(f"\nStderr:")
                self._log_to_file(result["stderr"])
            self._log_to_file(f"{'=' * 70}\n")
            
            # Special handling for wallet new - "already exists" is OK
            is_wallet_new = 'wallet' in cmd.lower() and 'new' in cmd.lower()
            wallet_already_exists = False
            
            if is_wallet_new:
                import yaml
                try:
                    parsed = yaml.safe_load(result["stdout"].strip())
                    if isinstance(parsed, dict) and 'errors' in parsed:
                        errors = parsed['errors']
                        if isinstance(errors, dict) and 'message' in errors:
                            if 'already exists' in errors['message'].lower():
                                wallet_already_exists = True
                                self._log_to_file("ℹ Wallet already exists - will extract address")
                except:
                    pass
            
            # Check expected result (skip check if wallet already exists)
            if wallet_already_exists:
                success = True  # Treat "wallet exists" as success
            else:
                success = self._check_expectation(result, step.expect, step.contains)
            
            if not success:
                ctx.add_result("cli", False, {
                    "command": cmd,
                    "node": step.node,
                    "output": result["stdout"],
                    "error": result["stderr"],
                    "exit_code": result["returncode"]
                })
                raise ScenarioExecutionError(
                    f"CLI command failed: {cmd}\n"
                    f"Expected: {step.expect}\n"
                    f"Got: exit code {result['returncode']}"
                )
            
            # Save result to variable if requested
            if step.save:
                output = result["stdout"].strip()
                
                # Special case: wallet new when wallet already exists
                # Need to get wallet address via wallet info
                if is_wallet_new and wallet_already_exists:
                    import re
                    # Extract wallet name from command
                    # Ensure cmd is a string
                    if not isinstance(cmd, str):
                        if self.debug:
                            self._log_to_file(f"⚠️  Command is not a string: {type(cmd)}")
                        cmd = str(cmd)
                    
                    wallet_match = re.search(r'-w\s+(\S+)', cmd)
                    if wallet_match:
                        wallet_name = wallet_match.group(1)
                        self._log_to_file(f"Getting address for existing wallet: {wallet_name}")
                        
                        # Execute wallet info to get address
                        info_cmd = f"wallet info -w {wallet_name}"
                        info_result = await self._run_cli_command(info_cmd, step.node, step.timeout)
                        
                        if info_result["returncode"] == 0:
                            # Try to extract address from wallet info
                            from .extractors import DataExtractor
                            
                            # Ensure output is a string
                            wallet_info_output = info_result.get("stdout", "")
                            if not isinstance(wallet_info_output, str):
                                if self.debug:
                                    self._log_to_file(f"⚠️  wallet info output is not string: {type(wallet_info_output)}")
                                wallet_info_output = str(wallet_info_output) if wallet_info_output else ""
                            
                            if self.debug:
                                self._log_to_file(f"wallet info output (first 200 chars): {wallet_info_output[:200]}")
                            
                            addr, error = DataExtractor.extract_and_validate(
                                output=wallet_info_output,
                                pattern=None,  # Use default wallet address pattern
                                extract_type="wallet_address",
                                required=False
                            )
                            
                            if addr:
                                ctx.set_variable(step.save, addr)
                                self._log_to_file(f"✓ Extracted wallet address: {addr[:20]}...")
                                # Continue to next step
                                ctx.add_result("cli", True, {
                                    "command": cmd,
                                    "node": step.node,
                                    "note": "Wallet already exists, address extracted"
                                })
                                
                                if step.wait:
                                    await self._wait_duration(step.wait)
                                
                                return
                
                # Try to extract hash from output for common commands
                # token_decl, token_emit, tx_create, etc. return hash
                saved_value = output
                
                # Check if this looks like a command that returns a hash
                hash_commands = ['token_decl', 'token_emit', 'token_update', 'tx_create', 
                                'tx_send', 'wallet_new', 'cert_create']
                cmd_lower = step.cli.lower()
                
                if any(cmd in cmd_lower for cmd in hash_commands):
                    # Try to parse output and extract hash
                    try:
                        import yaml
                        parsed = yaml.safe_load(output)
                        
                        # Look for common hash field names
                        if isinstance(parsed, dict):
                            for key in ['hash', 'tx_hash', 'datum_hash', 'token_hash', 
                                       'emission_hash', 'cert_hash', 'wallet_addr']:
                                if key in parsed and parsed[key]:
                                    saved_value = parsed[key]
                                    self._log_to_file(f"✓ Extracted {key}: {saved_value}")
                                    break
                    except:
                        # Fallback: look for hash pattern in output (0x[hex])
                        import re
                        hash_pattern = r'0x[0-9a-fA-F]{64,}'
                        
                        # Ensure output is a string
                        if isinstance(output, str):
                            match = re.search(hash_pattern, output)
                            if match:
                                saved_value = match.group(0)
                                self._log_to_file(f"✓ Extracted hash from output: {saved_value}")
                
                ctx.set_variable(step.save, saved_value)
                self._log_to_file(f"✓ Saved to variable: {step.save}")
            
            # Extract and validate specific values if requested
            if step.extract_to:
                from .extractors import DataExtractor, ExtractionError
                
                self._log_to_file(f"\n--- Extracting Values ---")
                for var_name, extract_spec in step.extract_to.items():
                    try:
                        # Use default pattern for type if not specified
                        pattern = extract_spec.pattern
                        if not pattern:
                            pattern = DataExtractor.get_default_pattern(extract_spec.type)
                            self._log_to_file(f"Using default pattern for {extract_spec.type}: {pattern}")
                        
                        extracted_value, error = DataExtractor.extract_and_validate(
                            output=result["stdout"],
                            pattern=pattern,
                            extract_type=extract_spec.type,
                            group=extract_spec.group,
                            required=extract_spec.required,
                            default=extract_spec.default
                        )
                        
                        if extracted_value is not None:
                            ctx.set_variable(var_name, extracted_value)
                            self._log_to_file(f"✓ Extracted '{var_name}': {extracted_value[:50]}{'...' if len(extracted_value) > 50 else ''}")
                            self._log_to_file(f"  Type: {extract_spec.type}")
                        elif error:
                            self._log_to_file(f"✗ Extraction warning for '{var_name}': {error}")
                            if extract_spec.required:
                                raise ExtractionError(error)
                    
                    except ExtractionError as e:
                        self._log_to_file(f"✗ Extraction failed for '{var_name}': {e}")
                        ctx.add_result("extraction", False, {
                            "variable": var_name,
                            "error": str(e),
                            "output": result["stdout"][:200]
                        })
                        raise ScenarioExecutionError(f"Failed to extract '{var_name}': {e}")
            
            ctx.add_result("cli", True, {
                "command": cmd,
                "node": step.node,
                "saved_to": step.save
            })
            
            # Wait if specified
            if step.wait:
                await self._wait_duration(step.wait)
                
        except subprocess.TimeoutExpired:
            self._log_to_file(f"✗ TIMEOUT after {step.timeout}s")
            self._log_to_file(f"{'=' * 70}\n")
            ctx.add_result("cli", False, {
                "command": cmd,
                "error": f"Command timeout after {step.timeout}s"
            })
            raise ScenarioExecutionError(f"CLI command timeout: {cmd}")
    
    async def _execute_rpc_step(self, step: RPCStep, ctx: RuntimeContext):
        """Execute JSON-RPC call step."""
        # Substitute variables in method and params
        method = ctx.substitute(step.rpc)
        params = [ctx.substitute(str(p)) if isinstance(p, str) else p for p in step.params]
        
        logger.debug(f"Executing RPC: {method}({params}) on {step.node}")
        
        # Log to file
        self._log_to_file(f"\n{'=' * 70}")
        self._log_to_file(f"RPC CALL")
        self._log_to_file(f"{'=' * 70}")
        self._log_to_file(f"Node: {step.node}")
        self._log_to_file(f"Method: {method}")
        self._log_to_file(f"Params: {params}")
        self._log_to_file(f"Timeout: {step.timeout}s")
        self._log_to_file(f"Expected: {step.expect}")
        self._log_to_file("")
        
        try:
            # Execute RPC call
            result = await self._call_rpc(method, params, step.node, step.timeout)
            
            # Log response
            self._log_to_file(f"--- Node Response ---")
            import json
            self._log_to_file(json.dumps(result, indent=2, ensure_ascii=False))
            self._log_to_file(f"{'=' * 70}\n")
            
            # Check expected result
            if step.expect == "error" and "error" not in result:
                raise ScenarioExecutionError(f"Expected RPC error, got success: {method}")
            if step.expect == "success" and "error" in result:
                raise ScenarioExecutionError(f"RPC call failed: {method}\nError: {result['error']}")
            
            # Save result to variable if requested
            if step.save:
                value = result.get("result", result)
                ctx.set_variable(step.save, value)
                self._log_to_file(f"✓ Saved to variable: {step.save}")
            
            ctx.add_result("rpc", True, {
                "method": method,
                "node": step.node,
                "saved_to": step.save
            })
            
            # Wait if specified
            if step.wait:
                await self._wait_duration(step.wait)
                
        except asyncio.TimeoutError:
            self._log_to_file(f"✗ TIMEOUT after {step.timeout}s")
            self._log_to_file(f"{'=' * 70}\n")
            ctx.add_result("rpc", False, {
                "method": method,
                "error": f"RPC timeout after {step.timeout}s"
            })
            raise ScenarioExecutionError(f"RPC call timeout: {method}")
    
    async def _execute_wait_step(self, step: WaitStep, ctx: RuntimeContext):
        """Execute wait step."""
        logger.debug(f"Waiting: {step.wait}")
        await self._wait_duration(step.wait)
        ctx.add_result("wait", True, {"duration": step.wait})
    
    async def _execute_wait_for_datum_step(self, step: WaitForDatumStep, ctx: RuntimeContext):
        """Execute wait-for-datum step - register datum with background monitor."""
        # Support both single hash and list of hashes
        datum_hashes = step.wait_for_datum if isinstance(step.wait_for_datum, list) else [step.wait_for_datum]
        
        # Substitute variables in hashes
        datum_hashes = [ctx.substitute(h) for h in datum_hashes]
        
        logger.info(f"Registering {len(datum_hashes)} datum(s) for monitoring")
        
        # Get monitoring manager singleton
        monitoring = await MonitoringManager.get_instance()
        
        # Register and wait for each datum
        results = []
        for datum_hash in datum_hashes:
            logger.debug(f"Monitoring datum: {datum_hash[:16]}...")
            
            # Register datum for tracking (returns Future)
            result_future = monitoring.datum.track_datum(
                datum_hash=datum_hash,
                node=step.node,
                network=step.network,
                chain=step.chain,
                check_master_nodes=step.check_master_nodes,
                timeout_total=step.timeout_total,
                timeout_mempool=step.timeout_mempool,
                timeout_verification=step.timeout_verification,
                timeout_in_blocks=step.timeout_in_blocks
            )
            
            # Wait for result
            result = await result_future
            results.append(result)
            
            # Check if monitoring failed
            if result.status not in [DatumStatus.PROPAGATED, DatumStatus.IN_BLOCKS]:
                error_msg = f"Datum monitoring failed: {result.error_message}"
                logger.error(error_msg)
                
                # Log to scenario file
                if self.log_file:
                    self._log_to_file(f"\n{'=' * 80}\n")
                    self._log_to_file(f"❌ WAIT_FOR_DATUM FAILED\n")
                    self._log_to_file(f"Datum: {datum_hash}\n")
                    self._log_to_file(f"Status: {result.status.value}\n")
                    self._log_to_file(f"Error: {result.error_message}\n")
                    self._log_to_file(f"Elapsed: {result.elapsed_time:.1f}s\n")
                    self._log_to_file(f"Details: {result.details}\n")
                    self._log_to_file(f"{'=' * 80}\n\n")
                
                raise ScenarioExecutionError(
                    error_msg,
                    step=step,
                    context={
                        "datum_hash": datum_hash,
                        "status": result.status.value,
                        "elapsed_time": result.elapsed_time,
                        "details": result.details
                    }
                )
            
            logger.info(f"✅ Datum {datum_hash[:16]}... monitored successfully: {result.status.value} in {result.elapsed_time:.1f}s")
        
        # Save status to variable if requested
        if step.save_status:
            if len(results) == 1:
                ctx.set_variable(step.save_status, results[0].status.value)
            else:
                ctx.set_variable(step.save_status, [r.status.value for r in results])
        
        # Add to context results
        ctx.add_result(
            "wait_for_datum",
            True,
            {
                "datum_count": len(datum_hashes),
                "results": [
                    {
                        "hash": r.datum_hash,
                        "status": r.status.value,
                        "elapsed": r.elapsed_time,
                        "details": r.details
                    }
                    for r in results
                ]
            }
        )
    
    async def _execute_loop_step(
        self,
        step: LoopStep,
        ctx: RuntimeContext,
        defaults: Optional[StepDefaults] = None
    ):
        """Execute loop step."""
        logger.info(f"Starting loop: {step.loop} iterations")
        
        for i in range(step.loop):
            logger.debug(f"Loop iteration {i+1}/{step.loop}")
            ctx.set_variable("i", i)
            ctx.set_variable("iteration", i + 1)
            
            await self._execute_steps(step.steps, ctx, defaults)
        
        ctx.add_result("loop", True, {"iterations": step.loop})
    
    async def _execute_checks(
        self,
        checks: List[CheckSpec],
        ctx: RuntimeContext,
        defaults: Optional[StepDefaults] = None
    ):
        """Execute assertion checks with defaults."""
        for i, check in enumerate(checks, 1):
            logger.info(f"Check {i}/{len(checks)}: {type(check).__name__}")
            
            # Apply defaults universally - check if attribute exists
            if defaults:
                # node
                if defaults.node and hasattr(check, 'node'):
                    if check.node == "node1":  # Default value
                        check.node = defaults.node
                
                # timeout
                if defaults.timeout and hasattr(check, 'timeout'):
                    if check.timeout == 30:  # Default value
                        check.timeout = defaults.timeout
            
            if isinstance(check, CLICheck):
                await self._execute_cli_check(check, ctx)
            elif isinstance(check, RPCCheck):
                await self._execute_rpc_check(check, ctx)
            elif isinstance(check, PythonCheck):
                await self._execute_python_check(check, ctx)
            elif isinstance(check, BashCheck):
                await self._execute_bash_check(check, ctx)
            else:
                raise ScenarioExecutionError(f"Unknown check type: {type(check)}")
    
    async def _execute_cli_check(self, check: CLICheck, ctx: RuntimeContext):
        """Execute CLI assertion."""
        cmd = ctx.substitute(check.cli)
        logger.debug(f"Checking CLI: {cmd}")
        
        try:
            result = await self._run_cli_command(cmd, check.node, check.timeout)
            output = result["stdout"]
            
            # Check conditions
            if check.contains and check.contains not in output:
                raise ScenarioExecutionError(
                    f"CLI check failed: expected '{check.contains}' in output\n"
                    f"Got: {output}"
                )
            
            if check.not_contains and check.not_contains in output:
                raise ScenarioExecutionError(
                    f"CLI check failed: '{check.not_contains}' should not be in output\n"
                    f"Got: {output}"
                )
            
            if check.equals and output.strip() != check.equals:
                raise ScenarioExecutionError(
                    f"CLI check failed: expected exact match\n"
                    f"Expected: {check.equals}\n"
                    f"Got: {output}"
                )
            
            ctx.add_result("check_cli", True, {"command": cmd})
            
        except subprocess.TimeoutExpired:
            ctx.add_result("check_cli", False, {"command": cmd, "error": "timeout"})
            raise ScenarioExecutionError(f"CLI check timeout: {cmd}")
    
    async def _execute_rpc_check(self, check: RPCCheck, ctx: RuntimeContext):
        """Execute RPC assertion."""
        method = ctx.substitute(check.rpc)
        params = [ctx.substitute(str(p)) if isinstance(p, str) else p for p in check.params]
        
        logger.debug(f"Checking RPC: {method}")
        
        try:
            result = await self._call_rpc(method, params, check.node, check.timeout)
            
            if "error" in result:
                raise ScenarioExecutionError(f"RPC check failed: {method}\nError: {result['error']}")
            
            rpc_result = result.get("result")
            
            # Check conditions
            if check.result_contains is not None:
                if check.result_contains not in str(rpc_result):
                    raise ScenarioExecutionError(
                        f"RPC check failed: expected '{check.result_contains}' in result\n"
                        f"Got: {rpc_result}"
                    )
            
            if check.result_equals is not None:
                if rpc_result != check.result_equals:
                    raise ScenarioExecutionError(
                        f"RPC check failed: expected exact match\n"
                        f"Expected: {check.result_equals}\n"
                        f"Got: {rpc_result}"
                    )
            
            ctx.add_result("check_rpc", True, {"method": method})
            
        except asyncio.TimeoutError:
            ctx.add_result("check_rpc", False, {"method": method, "error": "timeout"})
            raise ScenarioExecutionError(f"RPC check timeout: {method}")
    
    async def _execute_python_check(self, check: PythonCheck, ctx: RuntimeContext):
        """Execute Python assertion."""
        logger.debug("Executing Python check")
        
        try:
            # Create execution namespace with context
            namespace = {
                'ctx': ctx,
                '__builtins__': __builtins__,
            }
            
            # Execute Python code - should raise AssertionError if check fails
            exec(check.python, namespace)
            
            ctx.add_result("check_python", True, {"check": "Python check"})
            
        except AssertionError as e:
            ctx.add_result("check_python", False, {"error": str(e)})
            raise ScenarioExecutionError(
                f"Python check failed: {str(e)}",
                step=check.python[:100]
            )
        except Exception as e:
            ctx.add_result("check_python", False, {"error": str(e)})
            raise ScenarioExecutionError(
                f"Python check error: {str(e)}",
                step=check.python[:100]
            )
    
    async def _execute_bash_check(self, check: BashCheck, ctx: RuntimeContext):
        """Execute Bash script assertion."""
        # Substitute variables in bash script
        script = ctx.substitute(check.bash)
        
        logger.debug(f"Executing Bash check on {check.node}")
        
        # Convert node ID to container name
        if not check.node.startswith("cellframe-stage-"):
            if check.node.startswith("node"):
                node_num = check.node[4:]
                container_name = f"cellframe-stage-node-{node_num}"
            else:
                container_name = f"cellframe-stage-{check.node}"
        else:
            container_name = check.node
        
        # Build docker exec command
        full_cmd = [
            "docker", "exec", container_name,
            "bash", "-c", script
        ]
        
        process = await asyncio.create_subprocess_exec(
            *full_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=check.timeout
            )
            
            result = {
                "stdout": stdout.decode('utf-8', errors='replace'),
                "stderr": stderr.decode('utf-8', errors='replace'),
                "returncode": process.returncode
            }
            
            if result["returncode"] != 0:
                ctx.add_result("check_bash", False, {
                    "error": f"Exit code {result['returncode']}",
                    "stdout": result["stdout"],
                    "stderr": result["stderr"]
                })
                raise ScenarioExecutionError(
                    f"Bash check failed: exit code {result['returncode']}\n"
                    f"stdout: {result['stdout']}\n"
                    f"stderr: {result['stderr']}",
                    step=script[:100]
                )
            
            ctx.add_result("check_bash", True, {"check": "Bash check"})
            
        except asyncio.TimeoutError:
            process.kill()
            ctx.add_result("check_bash", False, {"error": "timeout"})
            raise ScenarioExecutionError(
                f"Bash check timeout after {check.timeout}s",
                step=script[:100]
            )
    
    async def _run_cli_command(
        self, command: str, node: str, timeout: Optional[int] = 30
    ) -> Dict[str, Any]:
        """Run CLI command via docker exec."""
        # Convert node ID to container name
        # node1 -> cellframe-stage-node-1
        if not node.startswith("cellframe-stage-"):
            # Extract number from node ID (node1 -> 1, node2 -> 2, etc.)
            if node.startswith("node"):
                node_num = node[4:]  # Remove "node" prefix
                container_name = f"cellframe-stage-node-{node_num}"
            else:
                container_name = f"cellframe-stage-{node}"
        else:
            container_name = node
        
        # Build docker exec command
        full_cmd = [
            "docker", "exec", container_name,
            self.node_cli_path, *command.split()
        ]
        
        process = await asyncio.create_subprocess_exec(
            *full_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            return {
                "stdout": stdout.decode('utf-8', errors='replace'),
                "stderr": stderr.decode('utf-8', errors='replace'),
                "returncode": process.returncode
            }
        except asyncio.TimeoutError:
            process.kill()
            raise
    
    async def _call_rpc(
        self, method: str, params: List[Any], node: str, timeout: Optional[int] = 30
    ) -> Dict[str, Any]:
        """Call JSON-RPC method via HTTP."""
        import httpx
        
        # Assuming RPC endpoint is at http://node:8545
        url = f"http://{node}:8545"
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload)
            return response.json()
    
    async def _execute_python_step(self, step: PythonStep, ctx: RuntimeContext):
        """Execute Python code with access to context."""
        try:
            # Create execution namespace with context
            namespace = {
                'ctx': ctx,
                '__builtins__': __builtins__,
            }
            
            # Execute Python code
            exec(step.python, namespace)
            
            # If save is specified and result is in namespace
            if step.save and 'result' in namespace:
                ctx.set_variable(step.save, namespace['result'])
                logger.debug("python_step_saved", variable=step.save, value=namespace['result'])
                
        except Exception as e:
            raise ScenarioExecutionError(
                f"Python step failed: {str(e)}",
                step=step.python[:100],
                context={'error': str(e)}
            )
    
    async def _execute_bash_step(self, step: BashStep, ctx: RuntimeContext):
        """Execute Bash script on specified node."""
        # Substitute variables in bash script
        script = ctx.substitute(step.bash)
        
        # Convert node ID to container name
        if not step.node.startswith("cellframe-stage-"):
            if step.node.startswith("node"):
                node_num = step.node[4:]
                container_name = f"cellframe-stage-node-{node_num}"
            else:
                container_name = f"cellframe-stage-{step.node}"
        else:
            container_name = step.node
        
        # Build docker exec command
        full_cmd = [
            "docker", "exec", container_name,
            "bash", "-c", script
        ]
        
        process = await asyncio.create_subprocess_exec(
            *full_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=step.timeout
            )
            
            result = {
                "stdout": stdout.decode('utf-8', errors='replace'),
                "stderr": stderr.decode('utf-8', errors='replace'),
                "returncode": process.returncode
            }
            
            # Save result if requested
            if step.save:
                ctx.set_variable(step.save, result["stdout"])
                logger.debug("bash_step_saved", variable=step.save)
            
            # Check expectation
            if step.expect == "success" and result["returncode"] != 0:
                raise ScenarioExecutionError(
                    f"Bash step failed: Expected success but got exit code {result['returncode']}",
                    step=script[:100],
                    context=result
                )
            elif step.expect == "error" and result["returncode"] == 0:
                raise ScenarioExecutionError(
                    f"Bash step failed: Expected error but got success",
                    step=script[:100],
                    context=result
                )
                
        except asyncio.TimeoutError:
            process.kill()
            raise ScenarioExecutionError(
                f"Bash step timed out after {step.timeout}s",
                step=script[:100]
            )
    
    async def _wait_duration(self, duration_str: str):
        """Parse and wait for duration (e.g., '5s', '100ms')."""
        match = re.match(r'(\d+)(s|ms|m)', duration_str)
        if not match:
            raise ScenarioExecutionError(f"Invalid duration format: {duration_str}")
        
        value = int(match.group(1))
        unit = match.group(2)
        
        if unit == 's':
            seconds = value
        elif unit == 'ms':
            seconds = value / 1000
        elif unit == 'm':
            seconds = value * 60
        else:
            raise ScenarioExecutionError(f"Unknown time unit: {unit}")
        
        await asyncio.sleep(seconds)
    
    def _check_expectation(
        self, result: Dict[str, Any], expect: str, contains: Optional[str]
    ) -> bool:
        """Check if result matches expectation."""
        import json
        import yaml
        
        # Cellframe CLI always returns exit code 0, but puts errors in output
        # Output can be JSON or YAML format
        has_error = False
        stdout = result["stdout"].strip()
        
        if stdout:
            # Try to parse as YAML first (Cellframe CLI default format)
            try:
                yaml_response = yaml.safe_load(stdout)
                
                if self.debug:
                    logger.debug(f"YAML parsed: type={type(yaml_response)}, value={yaml_response}")
                
                if isinstance(yaml_response, dict):
                    # Check for 'errors' key
                    if "errors" in yaml_response:
                        errors = yaml_response["errors"]
                        if self.debug:
                            logger.debug(f"Found 'errors' in YAML: type={type(errors)}, value={errors}")
                        # Consider it an error if errors field is not empty
                        if errors:
                            if isinstance(errors, dict) and errors:
                                has_error = True
                                if self.debug:
                                    logger.debug("Detected error: errors is non-empty dict")
                            elif isinstance(errors, list) and len(errors) > 0:
                                has_error = True
                                if self.debug:
                                    logger.debug("Detected error: errors is non-empty list")
            except (yaml.YAMLError, ValueError, AttributeError) as e:
                # Try JSON format
                try:
                    json_response = json.loads(stdout)
                    
                    if isinstance(json_response, dict):
                        # Check for 'errors' key (can be dict or list)
                        if "errors" in json_response:
                            errors = json_response["errors"]
                            # Consider it an error if errors field is not empty
                            if errors:
                                if isinstance(errors, dict) and errors:
                                    has_error = True
                                elif isinstance(errors, list) and len(errors) > 0:
                                    has_error = True
                except (json.JSONDecodeError, ValueError):
                    # Not JSON or YAML - check for text error patterns
                    error_patterns = ["error:", "Error:", "ERROR:", "failed", "Failed"]
                    if any(pattern in stdout for pattern in error_patterns):
                        has_error = True
        
        # Check expectation
        if expect == "success":
            # Success means: returncode 0 AND no errors
            if result["returncode"] != 0:
                return False
            if has_error:
                return False
        elif expect == "error":
            # Error means: returncode != 0 OR has errors
            if result["returncode"] == 0 and not has_error:
                return False
        
        # Check contains if specified
        if contains:
            if contains not in stdout:
                return False
        
        return True

