"""
CLI commands for network management.
"""
import asyncio
import typer
from pathlib import Path
from typing import Callable, Optional

from .common import print_info, print_success, print_error, print_warning


def register_commands(app: typer.Typer, base_path: Path, get_config_path: Callable[[], Optional[Path]]):
    """Register network management commands."""
    
    @app.command()
    def build(
        clean: bool = typer.Option(False, "--clean", help="Clean build"),
        release: bool = typer.Option(False, "--release", help="Release build"),
        jobs: int = typer.Option(0, "--jobs", "-j", help="Parallel jobs"),
    ):
        """🔨 Build cellframe-node artifacts."""
        from ..build.manager import BuildManager
        
        print_info("Building cellframe-node...")
        builder = BuildManager(base_path)
        build_type = "release" if release else "debug"
        result = builder.build(build_type=build_type, clean=clean, parallel=jobs)
        
        if result.success:
            # Format duration inline
            duration = result.duration_s
            if duration < 1:
                duration_str = f"{duration * 1000:.0f}ms"
            elif duration < 60:
                duration_str = f"{duration:.1f}s"
            else:
                minutes = int(duration // 60)
                secs = int(duration % 60)
                duration_str = f"{minutes}m {secs}s"
            
            print_success(f"Build completed in {duration_str}")
            print_info(f"Artifacts: {', '.join(result.artifacts)}")
        else:
            print_error("Build failed!")
            raise typer.Exit(1)
    
    @app.command()
    def start(
        topology: str = typer.Option("default", "--topology", "-t", help="Topology to use"),
        rebuild: bool = typer.Option(False, "--rebuild", help="Rebuild images"),
        clean: bool = typer.Option(False, "--clean", help="Clean all data"),
        wait: bool = typer.Option(True, "--wait/--no-wait", help="Wait for nodes"),
    ):
        """▶️  Start the test network."""
        from ..network.manager import NetworkManager
        from ..config.loader import ConfigLoader
        from ..certs.generator import CertGenerator
        
        # Check prerequisites inline
        import shutil
        import subprocess
        
        # Check for docker
        if not shutil.which("docker"):
            print_error("Missing required tool: docker")
            print_info("Please install Docker")
            raise typer.Exit(1)
        
        # Check for docker compose (V2) or docker-compose (V1)
        has_compose = False
        if shutil.which("docker"):
            # Try docker compose (V2)
            result = subprocess.run(["docker", "compose", "version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                has_compose = True
            # Fallback to docker-compose (V1)
            elif shutil.which("docker-compose"):
                has_compose = True
        
        if not has_compose:
            print_error("Missing Docker Compose")
            print_info("Please install Docker Compose (either V1 or V2)")
            raise typer.Exit(1)
        
        if clean:
            from rich.prompt import Confirm
            if not Confirm.ask("This will delete all data. Continue?", default=False):
                print_info("Cancelled")
                return
            
            print_warning("Cleaning all data...")
            config_path = get_config_path()
            config_loader = ConfigLoader(base_path, config_path)
            paths_config = config_loader.get_paths_config()
            cache_dir_relative = paths_config.get('cache_dir', 'cache')
            cache_dir = (base_path / cache_dir_relative).resolve()
            certs_dir = cache_dir / "certs"
            
            cert_gen = CertGenerator(base_path, certs_dir=certs_dir)
            cert_gen.clean()
        
        config_path = get_config_path()
        network_mgr = NetworkManager(base_path, topology_name=topology, config_path=config_path)
        
        async def _start():
            await network_mgr.start(rebuild=rebuild, wait_ready=wait)
        
        try:
            asyncio.run(_start())
            print_success("Network started successfully!")
            _show_status(network_mgr)
        except Exception as e:
            print_error(f"Failed to start network: {e}")
            raise typer.Exit(1)
    
    @app.command()
    def stop(
        volumes: bool = typer.Option(False, "--volumes", "-v", help="Remove volumes"),
    ):
        """⏹️  Stop the test network."""
        from ..network.manager import NetworkManager
        
        config_path = get_config_path()
        network_mgr = NetworkManager(base_path, config_path=config_path)
        
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
        wait: bool = typer.Option(True, "--wait/--no-wait", help="Wait for nodes"),
    ):
        """🔄 Restart the test network."""
        from ..network.manager import NetworkManager
        
        config_path = get_config_path()
        network_mgr = NetworkManager(base_path, config_path=config_path)
        
        async def _restart():
            await network_mgr.restart(wait_ready=wait)
        
        try:
            asyncio.run(_restart())
            print_success("Network restarted")
            _show_status(network_mgr)
        except Exception as e:
            print_error(f"Failed to restart network: {e}")
            raise typer.Exit(1)
    
    @app.command()
    def status():
        """📊 Show network status."""
        from ..network.manager import NetworkManager
        
        config_path = get_config_path()
        network_mgr = NetworkManager(base_path, config_path=config_path)
        
        async def _get_status():
            return await network_mgr.get_status()
        
        try:
            status_data = asyncio.run(_get_status())
        except Exception as e:
            print_warning(f"Could not get full status: {e}")
            return
        
        _print_status_table(status_data)
    
    @app.command()
    def logs(
        node: str = typer.Argument(..., help="Node ID (e.g., node1)"),
        follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output"),
        tail: int = typer.Option(100, "--tail", "-n", help="Number of lines"),
    ):
        """📜 Show logs from a specific node."""
        import subprocess
        
        container_name = f"cellframe-stage-{node}"
        cmd = ["docker", "logs"]
        if follow:
            cmd.append("-f")
        cmd.extend(["--tail", str(tail), container_name])
        
        try:
            subprocess.run(cmd)
        except KeyboardInterrupt:
            pass
        except Exception as e:
            print_error(f"Failed to get logs: {e}")
            raise typer.Exit(1)
    
    @app.command()
    def exec(
        node: str = typer.Argument(..., help="Node ID (e.g., node1)"),
        command: str = typer.Argument(..., help="Command to execute"),
    ):
        """⚡ Execute command on a node."""
        import subprocess
        
        container_name = f"cellframe-stage-{node}"
        cmd = ["docker", "exec", "-it", container_name, "sh", "-c", command]
        
        try:
            subprocess.run(cmd)
        except Exception as e:
            print_error(f"Failed to execute command: {e}")
            raise typer.Exit(1)
    
    @app.command()
    def rebuild():
        """🔧 Rebuild all Docker images and restart network."""
        from ..network.manager import NetworkManager
        from ..config.loader import ConfigLoader
        from ..certs.generator import CertGenerator
        
        print_info("Starting full environment rebuild...")
        
        # Stop network
        print_info("\n🛑 Stopping network...")
        config_path = get_config_path()
        network_mgr = NetworkManager(base_path, config_path=config_path)
        
        async def _stop():
            await network_mgr.stop(remove_volumes=False)
        
        try:
            asyncio.run(_stop())
            print_success("Network stopped")
        except Exception as e:
            print_warning(f"Network was not running: {e}")
        
        # Rebuild cert-generator
        print_info("\n🔨 Rebuilding cert-generator image...")
        import subprocess
        cert_gen_dir = base_path / "cellframe-sdk" / "dap-sdk" / "crypto" / "tools" / "cert-generator"
        if cert_gen_dir.exists():
            result = subprocess.run(
                ["docker", "build", "-t", "demlabs-cellframe-cert-generator", "."],
                cwd=cert_gen_dir,
                capture_output=True
            )
            if result.returncode == 0:
                print_success("Cert-generator rebuilt")
            else:
                print_warning("Failed to rebuild cert-generator")
        
        # Clean and regenerate certs
        print_info("\n🔐 Regenerating certificates...")
        config_path = get_config_path()
        config_loader = ConfigLoader(base_path, config_path)
        cache_config = config_loader.get_cache_config()
        cache_dir_relative = cache_config.get('cache_dir', 'cache')
        cache_dir = (base_path / cache_dir_relative).resolve()
        certs_dir = cache_dir / "certs"
        
        cert_gen = CertGenerator(base_path, certs_dir=certs_dir)
        cert_gen.clean()
        
        try:
            cert_gen.generate_all()
            print_success("Certificates regenerated")
        except Exception as e:
            print_error(f"Failed to regenerate certificates: {e}")
            raise typer.Exit(1)
        
        # Rebuild cellframe images
        print_info("\n🔨 Rebuilding cellframe-node images...")
        
        async def _start():
            await network_mgr.start(rebuild=True, wait_ready=True)
        
        try:
            asyncio.run(_start())
            print_success("Network rebuilt and started")
        except Exception as e:
            print_error(f"Failed to rebuild network: {e}")
            raise typer.Exit(1)
        
        # Show status
        print_info("\n📊 Network Status:")
        _show_status(network_mgr)
        
        print_success("\n✅ Full rebuild completed!")


def _show_status(network_mgr):
    """Show network status (helper function)."""
    async def _get_status():
        return await network_mgr.get_status()
    
    try:
        status_data = asyncio.run(_get_status())
        _print_status_table(status_data)
    except Exception as e:
        print_warning(f"Could not get status: {e}")


def _print_status_table(status_data):
    """Print status table (helper function)."""
    from rich.table import Table
    from rich.console import Console
    from .common import print_panel
    
    console = Console()
    
    print_panel(
        title="📊 Network Status",
        content=f"Network: {status_data['network_name']}\n"
                f"Topology: {status_data['topology']}\n"
                f"Total Nodes: {status_data['total_nodes']}",
        style="cyan"
    )
    
    table = Table(title="🖥️  Nodes")
    table.add_column("Node", style="cyan", no_wrap=True)
    table.add_column("Role", style="yellow")
    table.add_column("Container", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Response", style="blue")
    
    for node in status_data['nodes']:
        status_emoji = "🟢" if node['is_master'] else "🔵"
        status_text = f"{status_emoji} {node['status']}"
        
        table.add_row(
            node['node_id'],
            "Master" if node['is_master'] else "Regular",
            node['container'],
            status_text,
            node['response']
        )
    
    console.print(table)

