#!/usr/bin/env python3
"""
Stage Environment CLI - управление тестовым окружением Cellframe Node.

"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.build.builder import BuildManager
from src.certs.generator import CertGenerator
from src.config.loader import ConfigLoader
from src.network.manager import NetworkManager
from src.utils.cli import (
    check_prerequisites,
    confirm,
    format_duration,
    print_error,
    print_info,
    print_panel,
    print_success,
    print_warning,
)
from src.utils.logger import setup_logging, get_logger

# Initialize CLI app
app = typer.Typer(
    name="stage_env",
    help="🚀 Cellframe Node Stage Environment Manager",
    add_completion=False,
)

console = Console()
logger = get_logger(__name__)

# Global state
BASE_PATH = Path(__file__).parent
CONFIG_PATH: Optional[Path] = None


@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    json_logs: bool = typer.Option(False, "--json", help="Output logs as JSON"),
    config: Optional[str] = typer.Option(None, "--config", help="Path to stage-env.cfg"),
):
    """Configure global options."""
    global CONFIG_PATH
    
    # Set config path from option or environment variable
    if config:
        CONFIG_PATH = Path(config).resolve()
    else:
        import os
        env_config = os.environ.get("STAGE_ENV_CONFIG")
        if env_config:
            CONFIG_PATH = Path(env_config).resolve()
    
    # Setup logging with file output
    log_file = None
    if CONFIG_PATH and CONFIG_PATH.exists():
        try:
            from configparser import ConfigParser
            cfg = ConfigParser()
            cfg.read(CONFIG_PATH)
            if cfg.has_section('logging') and cfg.has_option('logging', 'log_dir'):
                log_dir = BASE_PATH / cfg.get('logging', 'log_dir')
                log_dir.mkdir(parents=True, exist_ok=True)
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                log_file = log_dir / f"stage-env_{timestamp}.log"
        except Exception as e:
            print(f"Warning: Failed to setup file logging: {e}", file=sys.stderr)
    
    setup_logging(verbose=verbose, json_output=json_logs, log_file=log_file)
    
    if log_file:
        logger.info("file_logging_enabled", log_file=str(log_file))


@app.command()
def build(
    clean: bool = typer.Option(False, "--clean", help="Clean build (remove build dir)"),
    release: bool = typer.Option(False, "--release", help="Release build (default: debug)"),
    jobs: int = typer.Option(0, "--jobs", "-j", help="Parallel jobs (0 = auto)"),
):
    """🔨 Build cellframe-node artifacts."""
    
    print_info("Building cellframe-node...")
    
    builder = BuildManager(BASE_PATH)
    
    build_type = "release" if release else "debug"
    result = builder.build(
        build_type=build_type,
        clean=clean,
        parallel=jobs,
    )
    
    if result.success:
        print_success(f"Build completed in {format_duration(result.duration_s)}")
        print_info(f"Artifacts: {', '.join(result.artifacts)}")
    else:
        print_error("Build failed!")
        raise typer.Exit(1)


@app.command()
def certs(
    network: str = typer.Option("stagenet", help="Network name"),
    nodes: int = typer.Option(4, help="Number of nodes"),
    validators: int = typer.Option(3, help="Number of validators"),
    force: bool = typer.Option(False, "--force", help="Regenerate even if exist"),
):
    """🔐 Generate certificates for test network."""
    
    # Load config to get correct cache_dir
    config_loader = ConfigLoader(BASE_PATH, CONFIG_PATH)
    paths_config = config_loader.get_paths_config()
    cache_dir_relative = paths_config.get('cache_dir', 'cache')
    cache_dir = (BASE_PATH / cache_dir_relative).resolve()
    certs_dir = cache_dir / "certs"
    
    cert_gen = CertGenerator(BASE_PATH, certs_dir=certs_dir)
    
    if cert_gen.certs_exist() and not force:
        if not confirm("Certificates already exist. Regenerate?", default=False):
            print_info("Keeping existing certificates")
            return
        cert_gen.clean()
    
    print_info(f"Generating certificates for {nodes} nodes + {validators} validators...")
    
    result = cert_gen.generate_all(
        network_name=network,
        node_count=nodes,
        validator_count=validators,
    )
    
    print_success(f"Generated {len(result['nodes'])} node certificates")
    print_success(f"Generated {len(result['validators'])} validator certificates")


@app.command()
def start(
    topology: str = typer.Option("default", "--topology", "-t", help="Topology to use"),
    rebuild: bool = typer.Option(False, "--rebuild", help="Rebuild images before start"),
    clean: bool = typer.Option(False, "--clean", help="Clean all data before start"),
    wait: bool = typer.Option(True, "--wait/--no-wait", help="Wait for nodes to be ready"),
):
    """▶️  Start the test network."""
    
    # Check prerequisites
    if not check_prerequisites():
        raise typer.Exit(1)
    
    # Clean if requested
    if clean:
        if not confirm("This will delete all data. Continue?", default=False):
            print_info("Cancelled")
            return
        
        print_warning("Cleaning all data...")
        # Load config to get correct cache_dir
        config_loader = ConfigLoader(BASE_PATH, CONFIG_PATH)
        paths_config = config_loader.get_paths_config()
        cache_dir_relative = paths_config.get('cache_dir', 'cache')
        cache_dir = (BASE_PATH / cache_dir_relative).resolve()
        certs_dir = cache_dir / "certs"
        
        cert_gen = CertGenerator(BASE_PATH, certs_dir=certs_dir)
        cert_gen.clean()
    
    # Start network
    network_mgr = NetworkManager(BASE_PATH, topology_name=topology, config_path=CONFIG_PATH)
    
    async def _start():
        await network_mgr.start(rebuild=rebuild, wait_ready=wait)
    
    try:
        asyncio.run(_start())
        print_success("Network started successfully!")
        
        # Show status
        _show_status(network_mgr)
        
    except Exception as e:
        print_error(f"Failed to start network: {e}")
        logger.exception("start_failed")
        raise typer.Exit(1)


@app.command()
def stop(
    volumes: bool = typer.Option(False, "--volumes", "-v", help="Remove volumes"),
):
    """⏹️  Stop the test network."""
    
    network_mgr = NetworkManager(BASE_PATH, config_path=CONFIG_PATH)
    
    async def _stop():
        await network_mgr.stop(remove_volumes=volumes)
    
    try:
        asyncio.run(_stop())
        print_success("Network stopped")
    except Exception as e:
        print_error(f"Failed to stop network: {e}")
        raise typer.Exit(1)


@app.command()
def restart(
    node: Optional[str] = typer.Argument(None, help="Node to restart (empty = all)"),
):
    """🔄 Restart network or specific node."""
    
    network_mgr = NetworkManager(BASE_PATH, config_path=CONFIG_PATH)
    
    async def _restart():
        await network_mgr.restart(node_name=node)
    
    try:
        asyncio.run(_restart())
        if node:
            print_success(f"Node {node} restarted")
        else:
            print_success("Network restarted")
    except Exception as e:
        print_error(f"Failed to restart: {e}")
        raise typer.Exit(1)


@app.command()
def status(
    topology: str = typer.Option("default", "--topology", "-t", help="Topology name"),
):
    """📊 Show network status."""
    
    network_mgr = NetworkManager(BASE_PATH, topology_name=topology, config_path=CONFIG_PATH)
    
    # Generate node configs to get info
    network_mgr.generate_node_configs()
    
    _show_status(network_mgr)


def _show_status(network_mgr: NetworkManager):
    """Helper to display network status."""
    
    async def _get_status():
        return await network_mgr.get_status()
    
    try:
        status_data = asyncio.run(_get_status())
    except Exception as e:
        print_warning(f"Could not get full status: {e}")
        return
    
    # Print summary
    print_panel(
        title="📊 Network Status",
        content=f"Network: {status_data['network_name']}\n"
                f"Topology: {status_data['topology']}\n"
                f"Total Nodes: {status_data['total_nodes']}",
        style="blue",
    )
    
    # Print node table
    table = Table(title="Nodes", show_header=True, header_style="bold magenta")
    table.add_column("Node", style="cyan")
    table.add_column("Role", style="yellow")
    table.add_column("Status", style="green")
    table.add_column("Health", style="blue")
    table.add_column("Response", style="white")
    
    nodes_list = network_mgr.list_nodes()
    health_data = status_data.get("health", {})
    
    for node in nodes_list:
        node_name = node["name"]
        health = health_data.get(node_name, {})
        
        status_emoji = "🟢" if health.get("healthy") else "🔴"
        response_time = health.get("response_time_ms", 0)
        
        table.add_row(
            node_name,
            node["role"],
            status_data["containers"].get(node_name, "unknown"),
            status_emoji,
            f"{response_time:.1f}ms" if response_time else "N/A",
        )
    
    console.print(table)


@app.command()
def logs(
    node: str = typer.Argument(..., help="Node name"),
    tail: int = typer.Option(100, "--tail", "-n", help="Number of lines"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output"),
):
    """📜 Show logs for a node."""
    
    network_mgr = NetworkManager(BASE_PATH, config_path=CONFIG_PATH)
    
    try:
        output = network_mgr.get_node_logs(node, tail=tail, follow=follow)
        
        if follow:
            # Stream logs
            for line in output:
                console.print(line.decode("utf-8"), end="")
        else:
            console.print(output)
            
    except Exception as e:
        print_error(f"Failed to get logs: {e}")
        raise typer.Exit(1)


@app.command()
def exec(
    node: str = typer.Argument(..., help="Node name"),
    command: str = typer.Argument(..., help="Command to execute"),
):
    """⚙️  Execute command in node container."""
    
    network_mgr = NetworkManager(BASE_PATH, config_path=CONFIG_PATH)
    
    try:
        exit_code, output = network_mgr.exec_in_node(
            node,
            command.split(),
        )
        
        console.print(output)
        
        if exit_code != 0:
            raise typer.Exit(exit_code)
            
    except Exception as e:
        print_error(f"Failed to execute command: {e}")
        raise typer.Exit(1)


@app.command()
def rebuild(
    skip_confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompts"),
):
    """🔨 Rebuild everything from scratch (cert-generator + cellframe images + network).
    
    This command will:
    1. Stop the network
    2. Rebuild cert-generator Docker image
    3. Rebuild all cellframe-node Docker images
    4. Clean and regenerate certificates
    5. Regenerate configurations
    6. Start the network
    """
    import subprocess
    
    if not skip_confirm:
        print_warning("This will:")
        print_warning("  • Stop the network")
        print_warning("  • Rebuild cert-generator Docker image (may take 5-10 min)")
        print_warning("  • Rebuild all cellframe-node images (no-cache)")
        print_warning("  • Clean and regenerate certificates")
        print_warning("  • Regenerate configurations")
        print_warning("  • Start the network")
        
        if not confirm("Continue?"):
            print_info("Rebuild cancelled")
            raise typer.Exit(0)
    
    # Step 1: Stop network
    print_info("\n📛 Step 1/6: Stopping network...")
    try:
        network_mgr = NetworkManager(BASE_PATH, config_path=CONFIG_PATH)
        
        async def _stop():
            await network_mgr.stop()
        
        asyncio.run(_stop())
        print_success("Network stopped")
    except Exception as e:
        print_warning(f"Network stop failed (maybe not running): {e}")
    
    # Step 2: Rebuild cert-generator image
    print_info("\n🔧 Step 2/6: Rebuilding cert-generator Docker image...")
    print_info("This may take 5-10 minutes...")
    
    try:
        # Remove old image
        subprocess.run(
            ["docker", "rmi", "-f", "cf-cert-generator:latest"],
            capture_output=True,
            check=False
        )
        
        # Find cellframe-node root (parent of tests/)
        root_dir = BASE_PATH.parent.parent
        
        # Build new image
        result = subprocess.run(
            [
                "docker", "build",
                "--no-cache",
                "-f", str(BASE_PATH / "Dockerfile.cert-generator"),
                "-t", "cf-cert-generator:latest",
                str(root_dir)
            ],
            cwd=str(root_dir),
            capture_output=False,  # Show progress
            text=True
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"cert-generator build failed with code {result.returncode}")
        
        print_success("cert-generator image rebuilt")
    except Exception as e:
        print_error(f"Failed to rebuild cert-generator: {e}")
        raise typer.Exit(1)
    
    # Step 3: Clean certificates
    print_info("\n🧹 Step 3/6: Cleaning old certificates...")
    config_loader = ConfigLoader(BASE_PATH, CONFIG_PATH)
    paths_config = config_loader.get_paths_config()
    cache_dir_relative = paths_config.get('cache_dir', 'cache')
    cache_dir = (BASE_PATH / cache_dir_relative).resolve()
    certs_dir = cache_dir / "certs"
    
    cert_gen = CertGenerator(BASE_PATH, certs_dir=certs_dir)
    cert_gen.clean()
    print_success("Certificates cleaned")
    
    # Step 4: Generate new certificates
    print_info("\n🔐 Step 4/6: Generating new certificates...")
    try:
        network_mgr = NetworkManager(BASE_PATH, topology_name="default", config_path=CONFIG_PATH)
        network_mgr.generate_node_configs()  # Generate configs first
        
        # Get node count from topology
        node_count = len(network_mgr.node_configs)
        
        # Generate certificates
        result = cert_gen.generate_all(
            network_name="stagenet",
            node_count=node_count,
            validator_count=3
        )
        
        print_success(f"Generated certificates for {node_count} nodes")
    except Exception as e:
        print_error(f"Failed to generate certificates: {e}")
        raise typer.Exit(1)
    
    # Step 5: Rebuild cellframe images and start network
    print_info("\n🚀 Step 5/6: Rebuilding cellframe images and starting network...")
    print_info("This may take several minutes...")
    
    try:
        async def _start():
            await network_mgr.start(rebuild=True, wait_ready=True)
        
        asyncio.run(_start())
        print_success("Network started with fresh images")
    except Exception as e:
        print_error(f"Failed to start network: {e}")
        raise typer.Exit(1)
    
    # Step 6: Show status
    print_info("\n📊 Step 6/6: Network status...")
    _show_status(network_mgr)
    
    print_success("\n✅ Full rebuild completed successfully!")
    print_info("All images, certificates, and network are now fresh.")


@app.command()
def clean(
    all: bool = typer.Option(False, "--all", help="Clean everything (build + certs + cache)"),
    build: bool = typer.Option(False, "--build", help="Clean build artifacts"),
    certs: bool = typer.Option(False, "--certs", help="Clean certificates"),
):
    """🧹 Clean build artifacts and data."""
    
    if not any([all, build, certs]):
        print_error("Specify what to clean: --all, --build, or --certs")
        raise typer.Exit(1)
    
    if all or build:
        print_info("Cleaning build artifacts...")
        builder = BuildManager(BASE_PATH)
        builder.clean()
    
    if all or certs:
        print_info("Cleaning certificates...")
        # Load config to get correct cache_dir
        config_loader = ConfigLoader(BASE_PATH, CONFIG_PATH)
        paths_config = config_loader.get_paths_config()
        cache_dir_relative = paths_config.get('cache_dir', 'cache')
        cache_dir = (BASE_PATH / cache_dir_relative).resolve()
        certs_dir = cache_dir / "certs"
        
        cert_gen = CertGenerator(BASE_PATH, certs_dir=certs_dir)
        cert_gen.clean()
    
    print_success("Cleanup completed")


@app.command()
def run_tests(
    test_dirs: list[str] = typer.Argument(..., help="Test scenario directories to run"),
    parallel: bool = typer.Option(False, "--parallel", "-p", help="Run tests in parallel (not yet implemented)"),
    filter: Optional[str] = typer.Option(None, "--filter", "-k", help="Filter tests by pattern"),
    start_network: bool = typer.Option(True, "--start-network/--no-start-network", help="Start network before tests"),
    stop_after: bool = typer.Option(True, "--stop-after/--keep-running", help="Stop network after tests"),
):
    """🧪 Run YAML test scenarios from specified directories."""
    
    import asyncio
    from pathlib import Path
    from datetime import datetime
    from src.scenarios.parser import ScenarioParser
    from src.scenarios.executor import ScenarioExecutor, ScenarioExecutionError
    from src.utils.artifacts import ArtifactsManager
    
    print_info(f"Running tests from {len(test_dirs)} director{'y' if len(test_dirs) == 1 else 'ies'}:")
    for test_dir in test_dirs:
        print_info(f"  • {test_dir}")
    
    # Create run directory for this test session (without test_type subdirs yet)
    config_loader = ConfigLoader(BASE_PATH, CONFIG_PATH)
    artifacts_config = config_loader.get_artifacts_config()
    artifacts_manager = ArtifactsManager(BASE_PATH, artifacts_config)
    
    # Create run ID - one timestamp for entire test session
    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    run_id = timestamp_str
    
    # Create base run directory (without test_type - will create subdirs as needed)
    run_dir_base = artifacts_manager.artifacts_root / f"run_{run_id}"
    run_dir_base.mkdir(parents=True, exist_ok=True)
    
    print_info(f"📁 Created run directory: run_{run_id}/")
    
    # Start network if requested
    network_mgr = None
    if start_network:
        print_info("\n🚀 Starting test network...")
        network_mgr = NetworkManager(BASE_PATH, topology_name="default", config_path=CONFIG_PATH)
        
        async def _start_network():
            await network_mgr.start(rebuild=False, wait_ready=True)
        
        try:
            asyncio.run(_start_network())
            print_success("Network started successfully")
        except Exception as e:
            print_error(f"Failed to start network: {e}")
            raise typer.Exit(1)
    
    all_passed = True
    total_scenarios = 0
    passed_scenarios = 0
    failed_scenarios = 0
    
    # Path to CLI binary inside containers
    cli_path = "cellframe-node-cli"
    
    try:
        for test_dir in test_dirs:
            test_path = Path(test_dir).resolve()
            
            if not test_path.exists():
                print_warning(f"Directory not found: {test_path}")
                continue
            
            # Find all YAML scenario files (including suite descriptors)
            yml_files = list(test_path.glob("**/*.yml")) + list(test_path.glob("**/*.yaml"))
            
            if not yml_files:
                print_warning(f"No YAML scenario files found in {test_path.name}")
                continue
            
            # Group files by suite:
            # Suite = directory with matching .yml file at same level
            # Example: wallet/ folder + wallet.yml file = suite "wallet"
            suites = {}  # suite_path -> {'descriptor': file, 'scenarios': [files]}
            standalone_scenarios = []  # scenarios without suite
            
            for yml_file in yml_files:
                parent_dir = yml_file.parent
                file_stem = yml_file.stem
                
                # Check if this is a suite descriptor:
                # File name matches directory name at same level
                matching_dir = parent_dir / file_stem
                if matching_dir.exists() and matching_dir.is_dir():
                    # This is a suite descriptor
                    suite_key = str(matching_dir.relative_to(test_path))
                    if suite_key not in suites:
                        suites[suite_key] = {
                            'descriptor': yml_file,
                            'scenarios': [],
                            'path': matching_dir
                        }
                    # Don't process descriptor as regular scenario
                    continue
                
                # Check if this scenario belongs to a suite
                # (is inside a directory that has a matching descriptor)
                suite_found = False
                for potential_suite_dir in [parent_dir] + list(parent_dir.parents):
                    if potential_suite_dir == test_path:
                        break
                    suite_name = potential_suite_dir.name
                    descriptor_file = potential_suite_dir.parent / f"{suite_name}.yml"
                    if descriptor_file.exists():
                        # This scenario belongs to a suite
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
                    # Standalone scenario (no suite)
                    standalone_scenarios.append(yml_file)
            
            # Process each suite
            for suite_key, suite_info in suites.items():
                suite_path = suite_info['path']
                suite_descriptor = suite_info['descriptor']
                suite_scenarios = suite_info['scenarios']
                
                # Parse suite descriptor to get metadata
                common_root = BASE_PATH / "tests"
                parser = ScenarioParser(scenarios_root=suite_descriptor.parent, common_root=common_root)
                
                try:
                    suite_desc_rel = suite_descriptor.relative_to(suite_descriptor.parent)
                    suite_spec = parser.load_scenario(str(suite_desc_rel))
                    suite_name = suite_spec.name
                    suite_description = suite_spec.description
                except Exception as e:
                    suite_name = suite_path.name
                    suite_description = None
                    print_warning(f"Failed to parse suite descriptor {suite_descriptor.name}: {e}")
                
                # Create suite-specific directory: run_<timestamp>/<relative_path_to_suite>/
                # Example: tests/e2e/wallet/ -> run_XXX/e2e/wallet/
                try:
                    suite_relative_path = suite_path.relative_to(test_path.parent)
                except:
                    suite_relative_path = Path(test_path.name) / suite_path.name
                
                suite_dir = run_dir_base / suite_relative_path
                suite_dir.mkdir(parents=True, exist_ok=True)
                
                # Create artifact subdirectories for this suite
                subdirs = [
                    "node-logs",
                    "core-dumps",
                    "stack-traces",
                    "health-logs",
                    "reports",
                    "scenario-logs",
                ]
                for subdir in subdirs:
                    (suite_dir / subdir).mkdir(exist_ok=True)
                
                print_info(f"\n{'═' * 60}")
                print_info(f"📦 Suite: {suite_name}")
                if suite_description:
                    print_info(f"   {suite_description}")
                print_info(f"   Path: {suite_relative_path}")
                print_info(f"   Scenarios: {len(suite_scenarios)}")
                print_info(f"{'═' * 60}")
                
                # Filter scenarios if needed
                if filter:
                    suite_scenarios = [f for f in suite_scenarios if filter.lower() in f.name.lower()]
                    if not suite_scenarios:
                        print_warning(f"No scenarios match filter '{filter}' in suite {suite_name}")
                        continue
                
                # Execute suite scenarios
                parser = ScenarioParser(scenarios_root=suite_path, common_root=common_root)
                
                for scenario_file in suite_scenarios:
                    total_scenarios += 1
                    print_info(f"\n{'─' * 60}")
                    print_info(f"▶ Running scenario: {scenario_file.name}")
                    
                    # Create scenario-specific log file in suite directory
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    scenario_name_clean = scenario_file.stem.replace(' ', '_')
                    scenario_log_name = f"scenario_{scenario_name_clean}_{timestamp}.log"
                    
                    # Save logs in suite_dir/scenario-logs/
                    scenario_logs_dir = suite_dir / "scenario-logs"
                    scenario_log_file = scenario_logs_dir / scenario_log_name
                    
                    try:
                        # Parse scenario
                        # Convert absolute path to relative path from scenarios_root
                        relative_path = scenario_file.relative_to(suite_path)
                        scenario = parser.load_scenario(str(relative_path))
                        print_info(f"  📋 Name: {scenario.name}")
                        if scenario.description:
                            print_info(f"  📝 Description: {scenario.description}")
                        if scenario.tags:
                            print_info(f"  🏷️  Tags: {', '.join(scenario.tags)}")
                        
                        # Get step counts (handle both list and SectionConfig)
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
                        executor = ScenarioExecutor(node_cli_path=cli_path, log_file=scenario_log_file)
                        
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
                        logger.error("scenario_execution_failed", 
                                   scenario=str(scenario_file),
                                   error=str(e))
                        
                    except Exception as e:
                        failed_scenarios += 1
                        all_passed = False
                        
                        # Write error to scenario log
                        with open(scenario_log_file, 'a', encoding='utf-8') as log_f:
                            log_f.write(f"\n{'=' * 60}\n")
                            log_f.write(f"=== Results ===\n")
                            log_f.write(f"Status: ERROR\n")
                            log_f.write(f"Exception: {str(e)}\n")
                            import traceback
                            log_f.write(f"Traceback:\n{traceback.format_exc()}\n")
                        
                        print_error(f"  ❌ Unexpected error: {str(e)}")
                        logger.exception("scenario_unexpected_error", 
                                       scenario=str(scenario_file))
                
                # Collect node logs and health logs for this specific suite
                if network_mgr:
                    print_info(f"\n📦 Collecting suite artifacts for {suite_relative_path}...")
                    import docker
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
                        
                        # Collect health logs for this suite
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
            # Collect stage-env log to base run directory
            logging_config = config_loader.get_logging_config()
            log_dir_relative = logging_config.get('log_dir', 'logs')
            log_dir = (BASE_PATH / log_dir_relative).resolve()
            
            # Create stage-env-logs in base directory
            stage_env_logs_dir = run_dir_base / "stage-env-logs"
            stage_env_logs_dir.mkdir(exist_ok=True)
            
            if log_dir.exists():
                log_files = sorted(log_dir.glob("stage-env_*.log"), 
                                  key=lambda p: p.stat().st_mtime, 
                                  reverse=True)
                if log_files:
                    artifacts_manager.collect_stage_env_log(run_dir_base, log_files[0])
                    print_success(f"Collected stage-env log")
            
            # Generate summary and reports for the ENTIRE run
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
                # For report compatibility
                'tests_run': total_scenarios,
                'tests_passed': passed_scenarios,
                'tests_failed': failed_scenarios,
                'tests_skipped': 0,
            }
            
            # Save summary to base directory
            artifacts_manager.create_run_summary(run_dir_base, summary_data)
            
            # Generate reports in base directory
            print_info("Generating test reports...")
            from src.utils.report_generator import ReportGenerator
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


@app.command()
def snapshots_list():
    """📦 List all available topology snapshots."""
    from src.snapshots import TopologySnapshotManager
    
    cache_dir = BASE_PATH / "cache"
    snapshot_mgr = TopologySnapshotManager(cache_dir)
    
    snapshots = snapshot_mgr.list_snapshots()
    
    if not snapshots:
        print_info("No snapshots found")
        return
    
    table = Table(title="📦 Topology Snapshots")
    table.add_column("Hash", style="cyan")
    table.add_column("Nodes", justify="right")
    table.add_column("Consensus", style="yellow")
    table.add_column("Size", justify="right", style="green")
    table.add_column("Version")
    table.add_column("Age")
    table.add_column("Status", style="magenta")
    
    for snapshot in snapshots:
        status = "✅ Valid" if snapshot['valid'] else "❌ Invalid"
        
        table.add_row(
            snapshot['topology_hash_short'],
            str(snapshot['node_count']),
            snapshot['consensus_type'],
            snapshot['size'],
            snapshot['version'],
            snapshot['created'].split('T')[0] if 'T' in snapshot['created'] else snapshot['created'],
            status,
        )
    
    console.print(table)
    
    # Show total size
    total_size = snapshot_mgr.get_total_size()
    from src.snapshots.utils import format_size
    print_info(f"Total snapshot size: {format_size(total_size)}")


@app.command()
def snapshots_delete(
    topology_hash: str = typer.Argument(..., help="Topology hash to delete (or 'all' for all snapshots)"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """🗑️  Delete topology snapshot(s)."""
    from src.snapshots import TopologySnapshotManager
    
    cache_dir = BASE_PATH / "cache"
    snapshot_mgr = TopologySnapshotManager(cache_dir)
    
    if topology_hash.lower() == 'all':
        snapshots = snapshot_mgr.list_snapshots()
        if not snapshots:
            print_info("No snapshots to delete")
            return
        
        if not yes and not confirm(f"Delete {len(snapshots)} snapshot(s)?"):
            print_info("Cancelled")
            return
        
        deleted_count = 0
        for snapshot in snapshots:
            if snapshot_mgr.delete(snapshot['topology_hash']):
                deleted_count += 1
        
        print_success(f"Deleted {deleted_count} snapshot(s)")
    else:
        # Find snapshot by prefix
        snapshots = snapshot_mgr.list_snapshots()
        matching = [s for s in snapshots if s['topology_hash'].startswith(topology_hash)]
        
        if not matching:
            print_error(f"Snapshot not found: {topology_hash}")
            raise typer.Exit(1)
        
        if len(matching) > 1:
            print_error(f"Ambiguous hash prefix. Found {len(matching)} matches:")
            for s in matching:
                print_info(f"  {s['topology_hash_short']}")
            raise typer.Exit(1)
        
        snapshot = matching[0]
        full_hash = snapshot['topology_hash']
        
        if not yes and not confirm(f"Delete snapshot {snapshot['topology_hash_short']}?"):
            print_info("Cancelled")
            return
        
        if snapshot_mgr.delete(full_hash):
            print_success(f"Deleted snapshot: {snapshot['topology_hash_short']}")
        else:
            print_error("Failed to delete snapshot")
            raise typer.Exit(1)


@app.command()
def snapshots_info(
    topology_hash: str = typer.Argument(..., help="Topology hash (or prefix)"),
):
    """ℹ️  Show detailed snapshot information."""
    from src.snapshots import TopologySnapshotManager
    import json
    
    cache_dir = BASE_PATH / "cache"
    snapshot_mgr = TopologySnapshotManager(cache_dir)
    
    # Find snapshot by prefix
    snapshots = snapshot_mgr.list_snapshots()
    matching = [s for s in snapshots if s['topology_hash'].startswith(topology_hash)]
    
    if not matching:
        print_error(f"Snapshot not found: {topology_hash}")
        raise typer.Exit(1)
    
    if len(matching) > 1:
        print_error(f"Ambiguous hash prefix. Found {len(matching)} matches:")
        for s in matching:
            print_info(f"  {s['topology_hash_short']}")
        raise typer.Exit(1)
    
    snapshot = matching[0]
    info = snapshot_mgr.get_info(snapshot['topology_hash'])
    
    if not info:
        print_error("Failed to get snapshot info")
        raise typer.Exit(1)
    
    print_panel(title="Snapshot Information", content=f"📦 Snapshot: {info['topology_hash'][:16]}...")
    print_info(f"Path: {info['path']}")
    print_info(f"Size: {info['size']}")
    print_info(f"Nodes: {info['node_count']}")
    print_info(f"Consensus: {info['consensus_type']}")
    print_info(f"Version: {info['version']}")
    print_info(f"Created: {info['created']}")
    print_info(f"Compression: {info['compression_ratio']}x")
    print_info(f"Valid: {'✅ Yes' if info['valid'] else '❌ No'}")
    
    # Show metadata
    print_info("\nMetadata:")
    console.print_json(json.dumps(info['metadata'], indent=2))


@app.command()
def snapshots_clean(
    max_age_days: int = typer.Option(30, "--max-age", help="Maximum age in days"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """🧹 Clean expired snapshots."""
    from src.snapshots import TopologySnapshotManager
    
    cache_dir = BASE_PATH / "cache"
    snapshot_mgr = TopologySnapshotManager(cache_dir)
    
    if not yes and not confirm(f"Delete snapshots older than {max_age_days} days?"):
        print_info("Cancelled")
        return
    
    print_info(f"Cleaning snapshots older than {max_age_days} days...")
    deleted_count = snapshot_mgr.clean_expired(max_age_days)
    
    if deleted_count > 0:
        print_success(f"Deleted {deleted_count} expired snapshot(s)")
    else:
        print_info("No expired snapshots found")


@app.command("collect-artifacts")
def collect_artifacts(
    ctx: typer.Context,
    test_type: str = typer.Argument(..., help="Test type: e2e, functional, or all"),
    exit_code: int = typer.Option(0, help="Test exit code"),
):
    """📦 Collect artifacts and generate reports after test run."""
    import docker
    from datetime import datetime
    from src.utils.artifacts import ArtifactsManager
    from src.utils.report_generator import ReportGenerator
    
    print_info(f"Collecting artifacts for {test_type} tests (exit code: {exit_code})")
    
    # Load configuration
    config_loader = ConfigLoader(BASE_PATH, CONFIG_PATH)
    artifacts_config = config_loader.get_artifacts_config()
    
    # Initialize artifacts manager
    artifacts_manager = ArtifactsManager(BASE_PATH, artifacts_config)
    
    # Create run directory
    run_id = f"{test_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir = artifacts_manager.create_run_directory(run_id)
    
    print_info(f"Created run directory: {run_dir.name}")
    
    # Collect stage-env log (use log_dir from config)
    logging_config = config_loader.get_logging_config()
    log_dir_relative = logging_config.get('log_dir', 'logs')
    log_dir = (BASE_PATH / log_dir_relative).resolve()
    if log_dir.exists():
        log_files = sorted(log_dir.glob("stage-env_*.log"), 
                          key=lambda p: p.stat().st_mtime, 
                          reverse=True)
        if log_files:
            artifacts_manager.collect_stage_env_log(run_dir, log_files[0])
            print_success(f"Collected stage-env log: {log_files[0].name}")
    
    # Collect node logs from Docker containers
    try:
        client = docker.from_env()
        project_name = "cellframe-stage"
        
        containers = client.containers.list(
            all=True,
            filters={"label": f"com.docker.compose.project={project_name}"}
        )
        
        node_logs_dir = run_dir / "node-logs"
        core_dumps_dir = run_dir / "core-dumps"
        
        collected_logs = 0
        collected_dumps = 0
        
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
                    
                    # Check for core dumps
                    crash_dir = f"/crash-artifacts/{node_id}"
                    result = container.exec_run(f"ls {crash_dir}", demux=False)
                    if result.exit_code == 0 and result.output:
                        files = result.output.decode('utf-8').strip().split('\n')
                        for file in files:
                            if file and file != '.':
                                dump_result = container.exec_run(
                                    f"cat {crash_dir}/{file}",
                                    demux=False
                                )
                                if dump_result.exit_code == 0:
                                    dump_file = core_dumps_dir / f"{node_id}_{file}"
                                    dump_file.write_bytes(dump_result.output)
                                    collected_dumps += 1
            except Exception as e:
                logger.warning("failed_to_collect_container_artifacts",
                             container=container.name,
                             error=str(e))
        
        print_success(f"Collected {collected_logs} node logs")
        if collected_dumps > 0:
            print_warning(f"Collected {collected_dumps} core dumps ⚠️")
        
    except Exception as e:
        print_error(f"Failed to collect Docker artifacts: {e}")
    
    # Collect health logs
    artifacts_manager.collect_health_logs(run_dir)
    
    # Build summary data
    summary_data = {
        'run_id': run_id,
        'test_type': test_type,
        'exit_code': exit_code,
        'status': 'passed' if exit_code == 0 else 'failed',
        'timestamp': datetime.now().isoformat(),
        'topology': 'default',
        'network': 'stagenet',
        'total_nodes': 7,
        'artifacts': {
            'node_logs': [str(p.name) for p in (run_dir / "node-logs").glob("*.log")],
            'stage_env_logs': [str(p.name) for p in (run_dir / "stage-env-logs").glob("*.log")],
            'core_dumps': [str(p.name) for p in (run_dir / "core-dumps").glob("*")],
            'stack_traces': [str(p.name) for p in (run_dir / "stack-traces").glob("*")],
        }
    }
    
    # Create summary file
    artifacts_manager.create_run_summary(run_dir, summary_data)
    print_success("Created summary.json")
    
    # Generate reports
    print_info("Generating reports...")
    report_generator = ReportGenerator(run_dir)
    reports = report_generator.generate_full_report(summary_data)
    
    for report_type, report_path in reports.items():
        print_success(f"Generated {report_type} report: {report_path.name}")
    
    # Cleanup old artifacts
    print_info("Cleaning up old artifacts...")
    artifacts_manager.cleanup_old_artifacts()
    
    print_panel(
        title="Artifacts Collection Complete",
        content=f"✅ Artifacts collected: [cyan]{run_dir}[/cyan]\n\n"
        f"📊 Reports:\n"
        + "\n".join([f"  • {t}: {p.relative_to(run_dir)}" for t, p in reports.items()])
    )


if __name__ == "__main__":
    app()

