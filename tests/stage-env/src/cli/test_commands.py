"""
CLI commands for running tests.

This module contains the main test execution command extracted from stage_env.py.
"""
import asyncio
import typer
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Callable

from .common import print_info, print_success, print_error, print_warning


def register_commands(app: typer.Typer, base_path: Path, get_config_path: Callable[[], Optional[Path]]):
    """Register test execution commands."""
    
    @app.command()
    def run_tests(
        test_dirs: List[str] = typer.Argument(..., help="Test scenario directories to run"),
        parallel: bool = typer.Option(False, "--parallel", "-p", help="Run tests in parallel (not yet implemented)"),
        filter: Optional[str] = typer.Option(None, "--filter", "-k", help="Filter tests by pattern"),
        start_network: bool = typer.Option(True, "--start-network/--no-start-network", help="Start network before tests"),
        stop_after: bool = typer.Option(True, "--stop-after/--keep-running", help="Stop network after tests"),
    ):
        """🧪 Run YAML test scenarios from specified directories."""
        
        from ..scenarios.parser import ScenarioParser
        from ..scenarios.executor import ScenarioExecutor, ScenarioExecutionError
        from ..scenarios.schema import SuiteDescriptor
        from ..utils.artifacts import ArtifactsManager
        from ..config.loader import ConfigLoader
        from ..network.manager import NetworkManager
        from ..monitoring.manager import MonitoringManager
        from ..utils.report_generator import ReportGenerator
        from ..scenarios.extractors import set_debug_mode
        import docker
        from ..utils.logger import logger
        
        print_info(f"Running tests from {len(test_dirs)} director{'y' if len(test_dirs) == 1 else 'ies'}:")
        for test_dir in test_dirs:
            print_info(f"  • {test_dir}")
        
        # Load configuration
        config_path = get_config_path()
        config_loader = ConfigLoader(base_path, config_path)
        artifacts_config = config_loader.get_artifacts_config()
        artifacts_manager = ArtifactsManager(base_path, artifacts_config)
        
        # Load scenarios config and set debug mode
        scenarios_config = config_loader.get_scenarios_config()
        debug_mode = scenarios_config.get('debug', False)
        set_debug_mode(debug_mode)
        
        if debug_mode:
            print_info("🐛 Debug mode enabled for scenario extraction")
        
        # Create run ID - one timestamp for entire test session
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        run_id = timestamp_str
        
        # Create base run directory
        run_dir_base = artifacts_manager.artifacts_root / f"run_{run_id}"
        run_dir_base.mkdir(parents=True, exist_ok=True)
        
        print_info(f"📁 Created run directory: run_{run_id}/")
        
        # Start network if requested
        network_mgr = None
        if start_network:
            print_info("\n🚀 Starting test network...")
            config_path = get_config_path()
            network_mgr = NetworkManager(base_path, topology_name="default", config_path=config_path)
            
            async def _start_network():
                await network_mgr.start(rebuild=False, wait_ready=True)
            
            try:
                asyncio.run(_start_network())
                print_success("Network started successfully")
                
                # Initialize CLI parser with help data from node
                print_info("📖 Parsing CLI commands...")
                from ..utils.cli_parser import get_cli_parser
                
                cache_file = base_path / "cache" / "cli_commands.json"
                cli_parser = get_cli_parser(cache_file=cache_file)
                
                # Parse CLI help from first node container
                async def _init_cli_parser():
                    # Use node1 container for parsing
                    container_name = "cellframe-stage-node-1"
                    success = await cli_parser.parse_cli_help(container_name, use_cache=True)
                    return success
                
                parser_success = asyncio.run(_init_cli_parser())
                if parser_success:
                    stats = cli_parser.get_stats()
                    print_success(f"✓ CLI parser initialized: {stats['total_commands']} commands")
                else:
                    print_warning("⚠️  CLI parser initialization failed - defaults will not be applied")
            except Exception as e:
                print_error(f"Failed to start network: {e}")
                raise typer.Exit(1)
        else:
            # Network already running - still need to initialize CLI parser
            print_info("📖 Initializing CLI parser from running network...")
            from ..utils.cli_parser import get_cli_parser
            
            cache_file = base_path / "cache" / "cli_commands.json"
            cli_parser = get_cli_parser(cache_file=cache_file)
            
            async def _init_cli_parser():
                container_name = "cellframe-stage-node-1"
                success = await cli_parser.parse_cli_help(container_name, use_cache=True)
                return success
            
            try:
                parser_success = asyncio.run(_init_cli_parser())
                if parser_success:
                    stats = cli_parser.get_stats()
                    print_success(f"✓ CLI parser initialized: {stats['total_commands']} commands")
                else:
                    print_warning("⚠️  CLI parser initialization failed - defaults will not be applied")
            except Exception as e:
                print_warning(f"CLI parser init failed: {e}")
        
        all_passed = True
        total_scenarios = 0
        passed_scenarios = 0
        failed_scenarios = 0
        scenario_results = []
        
        cli_path = "cellframe-node-cli"
        
        # Start monitoring services ONCE for entire test session
        async def _start_monitoring():
            monitoring = await MonitoringManager.get_instance(
                node_cli_path=cli_path,
                log_file=run_dir_base,
                datum_check_interval=2.0
            )
            await monitoring.start()
            print_info("🔍 Monitoring services started")
        
        try:
            asyncio.run(_start_monitoring())
        except Exception as e:
            print_warning(f"Failed to start monitoring: {e}")
        
        # Main test execution loop
        try:
            for test_dir in test_dirs:
                test_path = Path(test_dir).resolve()
                
                if not test_path.exists():
                    print_warning(f"Directory not found: {test_path}")
                    continue
                
                # Find all YAML scenario files
                yml_files = list(test_path.glob("**/*.yml")) + list(test_path.glob("**/*.yaml"))
                
                if not yml_files:
                    print_warning(f"No YAML scenario files found in {test_path.name}")
                    continue
                
                # Group files by suite
                suites = {}
                standalone_scenarios = []
                
                for yml_file in yml_files:
                    parent_dir = yml_file.parent
                    file_stem = yml_file.stem
                    
                    # Check if this is a suite descriptor
                    matching_dir = parent_dir / file_stem
                    if matching_dir.exists() and matching_dir.is_dir():
                        suite_key = str(matching_dir.relative_to(test_path))
                        if suite_key not in suites:
                            suites[suite_key] = {
                                'descriptor': yml_file,
                                'scenarios': [],
                                'path': matching_dir
                            }
                        continue
                    
                    # Check if this scenario belongs to a suite
                    suite_found = False
                    for potential_suite_dir in [parent_dir] + list(parent_dir.parents):
                        if potential_suite_dir == test_path:
                            break
                        suite_name = potential_suite_dir.name
                        descriptor_file = potential_suite_dir.parent / f"{suite_name}.yml"
                        if descriptor_file.exists():
                            suite_key = str(potential_suite_dir.relative_to(test_path))
                            if suite_key not in suites:
                                suites[suite_key] = {
                                    'descriptor': descriptor_file,
                                    'scenarios': [],
                                    'path': potential_suite_dir
                                }
                            suites[suite_key]['scenarios'].append(yml_file)
                            suite_found = True
                            break
                    
                    if not suite_found:
                        standalone_scenarios.append(yml_file)
                
                # Process each suite
                for suite_key, suite_info in suites.items():
                    suite_path = suite_info['path']
                    suite_descriptor = suite_info['descriptor']
                    suite_scenarios = suite_info['scenarios']
                    
                    # Parse suite descriptor to get metadata
                    common_root = base_path / "tests"
                    parser = ScenarioParser(scenarios_root=suite_descriptor.parent, common_root=common_root)
                    
                    suite_spec = None  # Initialize to None in case of parse failure
                    try:
                        suite_desc_rel = suite_descriptor.relative_to(suite_descriptor.parent)
                        suite_spec = parser.load_scenario(str(suite_desc_rel))
                        if isinstance(suite_spec, SuiteDescriptor):
                            suite_name = suite_spec.name
                            suite_description = suite_spec.description
                        else:
                            suite_name = suite_spec.name
                            suite_description = getattr(suite_spec, 'description', None)
                    except Exception as e:
                        suite_name = suite_path.name
                        suite_description = None
                        print_warning(f"Failed to parse suite descriptor {suite_descriptor.name}: {e}")
                    
                    # Create suite-specific directory
                    test_type = test_path.name
                    suite_relative_path = Path(test_type) / suite_path.name
                    suite_dir = run_dir_base / suite_relative_path
                    suite_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Create artifact subdirectories
                    for subdir in ["node-logs", "core-dumps", "stack-traces", "health-logs", "reports", "scenario-logs"]:
                        (suite_dir / subdir).mkdir(exist_ok=True)
                    
                    print_info(f"\n{'═' * 60}")
                    print_info(f"📦 Suite: {suite_name}")
                    if suite_description:
                        print_info(f"   {suite_description}")
                    print_info(f"   Path: {suite_relative_path}")
                    print_info(f"   Scenarios: {len(suite_scenarios)}")
                    print_info(f"{'═' * 60}")
                    
                    # Clean test data before each suite (if network is running)
                    if network_mgr:
                        print_info("🧹 Restoring clean environment state...")
                        
                        async def _restore_state():
                            await network_mgr.restore_clean_state()
                        
                        try:
                            asyncio.run(_restore_state())
                            print_success("✓ Environment restored from snapshot")
                        except Exception as e:
                            print_warning(f"Failed to restore clean state: {e}")

                    # Execute suite-level setup (if defined)
                    if isinstance(suite_spec, SuiteDescriptor) and (suite_spec.includes or suite_spec.setup):
                        print_info("🔧 Executing suite-level setup...")
                        
                        from ..scenarios.executor import ScenarioExecutor
                        from ..scenarios.schema import SuiteSetupScenario
                        
                        # Create a lightweight scenario for suite setup (no test steps required)
                        suite_setup_data = {
                            "name": f"{suite_name} - Suite Setup",
                            "description": "Suite-level initialization",
                            "network": suite_spec.network.dict() if suite_spec.network else {"topology": "default"},
                            "includes": suite_spec.includes if suite_spec.includes else [],
                            "setup": suite_spec.setup.dict() if suite_spec.setup else [],
                        }
                        
                        try:
                            # Parse suite setup using SuiteSetupScenario (no test steps required)
                            suite_setup_scenario = SuiteSetupScenario(**suite_setup_data)
                            
                            # Execute setup
                            executor = ScenarioExecutor(
                                node_cli_path="cellframe-node-cli",
                                log_file=suite_dir / "suite-setup.log",
                                debug=debug
                            )
                            
                            async def _run_suite_setup():
                                await executor.execute_scenario(suite_setup_scenario)
                            
                            asyncio.run(_run_suite_setup())
                            print_success("✓ Suite setup completed")
                            
                        except Exception as e:
                            print_error(f"Suite setup failed: {e}")
                            print_error(f"❌ Skipping all scenarios in suite: {suite_name}")
                            # Skip all scenarios in this suite
                            continue


                    
                    # Filter scenarios if needed
                    if filter:
                        suite_scenarios = [f for f in suite_scenarios if filter.lower() in f.name.lower()]
                        if not suite_scenarios:
                            print_warning(f"No scenarios match filter '{filter}' in suite {suite_name}")
                            continue
                    
                    # Execute suite scenarios
                    # Create fresh parser for each suite to avoid stale cache
                    parser = ScenarioParser(scenarios_root=suite_path, common_root=common_root)
                    
                    for scenario_file in suite_scenarios:
                        total_scenarios += 1
                        print_info(f"\n{'─' * 60}")
                        print_info(f"▶ Running scenario: {scenario_file.name}")
                        
                        # Create scenario log file
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        scenario_name_clean = scenario_file.stem.replace(' ', '_')
                        scenario_log_name = f"scenario_{scenario_name_clean}_{timestamp}.log"
                        scenario_logs_dir = suite_dir / "scenario-logs"
                        scenario_log_file = scenario_logs_dir / scenario_log_name
                        
                        try:
                            # Parse scenario
                            relative_path = scenario_file.relative_to(suite_path)
                            scenario = parser.load_scenario(str(relative_path))
                            
                            # Skip if it's a SuiteDescriptor
                            if isinstance(scenario, SuiteDescriptor):
                                continue
                            
                            print_info(f"  📋 Name: {scenario.name}")
                            if hasattr(scenario, 'description') and scenario.description:
                                print_info(f"  📝 Description: {scenario.description}")
                            if hasattr(scenario, 'tags') and scenario.tags:
                                print_info(f"  🏷️  Tags: {', '.join(scenario.tags)}")
                            
                            # Get step counts
                            setup_count = len(scenario.setup.steps) if hasattr(scenario.setup, 'steps') else len(scenario.setup or [])
                            test_count = len(scenario.test.steps) if hasattr(scenario.test, 'steps') else len(scenario.test or [])
                            check_count = len(scenario.check.steps) if hasattr(scenario.check, 'steps') else len(scenario.check or [])
                            print_info(f"  📊 Steps: setup={setup_count}, test={test_count}, check={check_count}")
                            print_info(f"  📄 Log: {scenario_log_file.name}")
                            
                            # Setup scenario logging
                            with open(scenario_log_file, 'w', encoding='utf-8') as log_f:
                                log_f.write(f"=== Scenario: {scenario.name} ===\n")
                                log_f.write(f"File: {scenario_file}\n")
                                log_f.write(f"Description: {scenario.description or 'N/A'}\n")
                                log_f.write(f"Tags: {', '.join(scenario.tags) if scenario.tags else 'N/A'}\n")
                                log_f.write(f"Started: {timestamp}\n")
                                log_f.write(f"{'=' * 60}\n\n")
                            
                            # Execute scenario
                            executor = ScenarioExecutor(
                                node_cli_path=cli_path, 
                                log_file=scenario_log_file,
                                debug=debug_mode
                            )
                            
                            async def _execute():
                                return await executor.execute_scenario(scenario)
                            
                            print_info("  ▶️  Executing...")
                            ctx = asyncio.run(_execute())
                            
                            # Get summary
                            summary = ctx.get_summary()
                            
                            # Write results to scenario log
                            with open(scenario_log_file, 'a', encoding='utf-8') as log_f:
                                log_f.write(f"\n{'=' * 60}\n")
                                log_f.write(f"=== Results ===\n")
                                log_f.write(f"Status: PASSED\n")
                                log_f.write(f"Steps: {summary['passed']}/{summary['total_steps']} passed\n")
                                if summary.get('variables'):
                                    log_f.write(f"Variables saved: {len(summary['variables'])}\n")
                                    for var_name, var_value in summary.get('variables', {}).items():
                                        log_f.write(f"  {var_name} = {var_value}\n")
                            
                            print_success(f"  ✅ Scenario passed!")
                            print_info(f"     Steps: {summary['passed']}/{summary['total_steps']} passed")
                            if summary.get('variables'):
                                print_info(f"     Variables: {len(summary['variables'])} saved")
                            
                            passed_scenarios += 1
                            
                            # Record success
                            scenario_results.append({
                                'name': scenario.name,
                                'file': scenario_file.name,
                                'suite': suite_name,
                                'path': str(suite_relative_path / scenario_file.name),
                                'status': 'passed',
                                'duration': summary.get('duration_seconds', 0),
                                'steps_total': summary['total_steps'],
                                'steps_passed': summary['passed'],
                                'log_file': str(scenario_log_file.relative_to(run_dir_base))
                            })
                            
                        except ScenarioExecutionError as e:
                            failed_scenarios += 1
                            all_passed = False
                            
                            # Write error to scenario log
                            with open(scenario_log_file, 'a', encoding='utf-8') as log_f:
                                log_f.write(f"\n{'=' * 60}\n")
                                log_f.write(f"=== Results ===\n")
                                log_f.write(f"Status: FAILED\n")
                                log_f.write(f"Error: {str(e)}\n")
                            
                            print_error(f"  ❌ Scenario failed: {str(e)}")
                            logger.error("scenario_execution_failed", scenario=str(scenario_file), error=str(e))
                            
                            # Extract last 30 lines of log
                            error_log_excerpt = ""
                            try:
                                with open(scenario_log_file, 'r', encoding='utf-8') as log_f:
                                    lines = log_f.readlines()
                                    error_log_excerpt = ''.join(lines[-30:])
                            except:
                                error_log_excerpt = "Failed to read log file"
                            
                            # Record failure
                            scenario_results.append({
                                'name': getattr(scenario, 'name', scenario_file.stem),
                                'file': scenario_file.name,
                                'suite': suite_name,
                                'path': str(suite_relative_path / scenario_file.name),
                                'status': 'failed',
                                'error': str(e),
                                'error_log': error_log_excerpt,
                                'log_file': str(scenario_log_file.relative_to(run_dir_base))
                            })
                            
                        except Exception as e:
                            failed_scenarios += 1
                            all_passed = False
                            
                            # Write error to scenario log
                            import traceback
                            with open(scenario_log_file, 'a', encoding='utf-8') as log_f:
                                log_f.write(f"\n{'=' * 60}\n")
                                log_f.write(f"=== Results ===\n")
                                log_f.write(f"Status: ERROR\n")
                                log_f.write(f"Exception: {str(e)}\n")
                                log_f.write(f"Traceback:\n{traceback.format_exc()}\n")
                            
                            print_error(f"  ❌ Unexpected error: {str(e)}")
                            logger.exception("scenario_unexpected_error", scenario=str(scenario_file))
                            
                            # Extract last 30 lines of log
                            error_log_excerpt = ""
                            try:
                                with open(scenario_log_file, 'r', encoding='utf-8') as log_f:
                                    lines = log_f.readlines()
                                    error_log_excerpt = ''.join(lines[-30:])
                            except:
                                error_log_excerpt = "Failed to read log file"
                            
                            # Record error
                            scenario_results.append({
                                'name': scenario_file.stem,
                                'file': scenario_file.name,
                                'suite': suite_name,
                                'path': str(suite_relative_path / scenario_file.name),
                                'status': 'error',
                                'error': f"Unexpected error: {str(e)}",
                                'error_log': error_log_excerpt,
                                'traceback': traceback.format_exc(),
                                'log_file': str(scenario_log_file.relative_to(run_dir_base))
                            })
                    
                    # Collect artifacts for this suite
                    if network_mgr:
                        print_info(f"\n📦 Collecting suite artifacts for {suite_relative_path}...")
                        try:
                            client = docker.from_env()
                            project_name = "cellframe-stage"
                            
                            containers = client.containers.list(
                                all=True,
                                filters={"label": f"com.docker.compose.project={project_name}"}
                            )
                            
                            node_logs_dir = suite_dir / "node-logs"
                            collected_logs = 0
                            
                            for container in containers:
                                try:
                                    container_name = container.name
                                    if "node-" in container_name:
                                        node_name = container_name.split("node-", 1)[1]
                                        node_id = f"node-{node_name}"
                                        
                                        # Collect logs
                                        logs = container.logs(tail=10000).decode('utf-8', errors='ignore')
                                        log_file = node_logs_dir / f"{node_id}.log"
                                        log_file.write_text(logs)
                                        collected_logs += 1
                                except Exception as e:
                                    logger.warning("failed_to_collect_container_log",
                                                    container=container.name,
                                                    error=str(e))
                            
                            if collected_logs > 0:
                                print_success(f"  Collected {collected_logs} node logs")
                            
                            # Collect health logs
                            artifacts_manager.collect_health_logs(suite_dir)
                            print_success(f"  Health logs collected")
                            
                        except Exception as e:
                            print_warning(f"  Failed to collect suite artifacts: {e}")
            
                # Print summary
                print_info(f"\n{'═' * 60}")
                print_info(f"📊 Scenario Test Summary")
                print_info(f"{'═' * 60}")
                print_info(f"Total scenarios: {total_scenarios}")
                if passed_scenarios > 0:
                    print_success(f"✅ Passed: {passed_scenarios}")
                if failed_scenarios > 0:
                    print_error(f"❌ Failed: {failed_scenarios}")
                print_info(f"{'═' * 60}")
                
        finally:
            # Collect final artifacts
            print_info("\n📦 Finalizing artifacts...")
            
            try:
                # Collect stage-env log
                logging_config = config_loader.get_logging_config()
                log_dir_relative = logging_config.get('log_dir', 'logs')
                log_dir = (base_path / log_dir_relative).resolve()
                
                stage_env_logs_dir = run_dir_base / "stage-env-logs"
                stage_env_logs_dir.mkdir(exist_ok=True)
                
                if log_dir.exists():
                    log_files = sorted(log_dir.glob("stage-env_*.log"), 
                                    key=lambda p: p.stat().st_mtime, 
                                    reverse=True)
                    if log_files:
                        artifacts_manager.collect_stage_env_log(run_dir_base, log_files[0])
                        print_success(f"Collected stage-env log")
                
                # Generate summary and reports
                summary_data = {
                    'run_id': run_id,
                    'test_type': 'mixed' if len(test_dirs) > 1 else 'single_suite',
                    'topology': 'default',
                    'network': 'stagenet',
                    'total_nodes': 7,
                    'exit_code': 0 if all_passed else 1,
                    'status': 'passed' if all_passed else 'failed',
                    'timestamp': datetime.now().isoformat(),
                    'total_scenarios': total_scenarios,
                    'passed_scenarios': passed_scenarios,
                    'failed_scenarios': failed_scenarios,
                    'tests_run': total_scenarios,
                    'tests_passed': passed_scenarios,
                    'tests_failed': failed_scenarios,
                    'tests_skipped': 0,
                    'scenarios': scenario_results,
                }
                
                # Save summary
                artifacts_manager.create_run_summary(run_dir_base, summary_data)
                
                # Generate reports
                print_info("Generating test reports...")
                report_gen = ReportGenerator(run_dir_base)
                try:
                    reports = report_gen.generate_full_report(summary_data)
                    for report_type, report_path in reports.items():
                        print_success(f"Generated {report_type}: {report_path.name}")
                except Exception as e:
                    print_warning(f"Failed to generate some reports: {e}")
                
                print_success(f"✅ All artifacts saved to: run_{run_id}/")
                
            except Exception as e:
                print_warning(f"Failed to collect some artifacts: {e}")
            
            # Stop monitoring services
            print_info("\n🔍 Stopping monitoring services...")
            async def _stop_monitoring():
                try:
                    monitoring = await MonitoringManager.get_instance()
                    await monitoring.stop()
                    print_success("Monitoring services stopped")
                except Exception as e:
                    print_warning(f"Failed to stop monitoring: {e}")
            
            try:
                asyncio.run(_stop_monitoring())
            except Exception as e:
                print_warning(f"Monitoring cleanup failed: {e}")
            
            # Stop network if requested
            if stop_after and network_mgr:
                print_info("\n🛑 Stopping test network...")
                
                async def _stop_network():
                    await network_mgr.stop(remove_volumes=False)
                
                try:
                    asyncio.run(_stop_network())
                    print_success("Network stopped")
                except Exception as e:
                    print_warning(f"Failed to stop network cleanly: {e}")
        
        if not all_passed:
            raise typer.Exit(1)
