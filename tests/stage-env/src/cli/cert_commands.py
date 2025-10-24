"""
CLI commands for certificate management.
"""
import typer
from pathlib import Path

from .common import print_info, print_success, print_error, confirm


def register_commands(app: typer.Typer, base_path: Path, config_path: Path):
    """Register certificate management commands."""
    
    @app.command()
    def certs(
        network: str = typer.Option("stagenet", help="Network name"),
        nodes: int = typer.Option(4, help="Number of nodes"),
        validators: int = typer.Option(3, help="Number of validators"),
        force: bool = typer.Option(False, "--force", help="Regenerate even if exist"),
    ):
        """🔐 Generate certificates for test network."""
        from ..certs.generator import CertGenerator
        from ..config.loader import ConfigLoader
        
        # Load config to get correct cache_dir
        config_loader = ConfigLoader(base_path, config_path)
        paths_config = config_loader.get_paths_config()
        cache_dir_relative = paths_config.get('cache_dir', 'cache')
        cache_dir = (base_path / cache_dir_relative).resolve()
        certs_dir = cache_dir / "certs"
        
        cert_gen = CertGenerator(base_path, certs_dir=certs_dir)
        
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
        print_info(f"Certificates saved to: {certs_dir}")
    
    @app.command()
    def clean(
        yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
    ):
        """🧹 Clean up generated certificates and cache."""
        from ..certs.generator import CertGenerator
        from ..config.loader import ConfigLoader
        
        if not yes and not confirm("This will delete all generated certificates and cache. Continue?", default=False):
            print_info("Cancelled")
            return
        
        config_loader = ConfigLoader(base_path, config_path)
        paths_config = config_loader.get_paths_config()
        cache_dir_relative = paths_config.get('cache_dir', 'cache')
        cache_dir = (base_path / cache_dir_relative).resolve()
        certs_dir = cache_dir / "certs"
        
        cert_gen = CertGenerator(base_path, certs_dir=certs_dir)
        cert_gen.clean()
        
        print_success("Cleaned certificates and cache")
