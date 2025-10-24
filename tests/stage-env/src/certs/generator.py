"""
Certificate generator for test network.

Python wrapper around C certificate generator utility running in Docker.
Handles generation of:
- Node certificates
- Validator certificates  
- CA certificates

Uses cf-cert-generator utility in Docker container for cross-platform compatibility.
This utility generates proper binary DAP certificates using DAP SDK crypto.
"""

from pathlib import Path
from typing import List, Optional
import json
import subprocess
import shutil
import os

from pydantic import BaseModel

from ..utils.logger import get_logger
from ..utils.cli import run_command, print_info, print_success, print_error

logger = get_logger(__name__)

# Docker image name for certificate generator
CERT_GENERATOR_IMAGE = "cf-cert-generator:latest"


class CertConfig(BaseModel):
    """Certificate configuration."""
    
    name: str
    type: str  # node, validator, ca
    output_dir: Path


class CertGenerator:
    """Generate certificates for test network."""
    
    def __init__(self, base_path: Path, certs_dir: Optional[Path] = None):
        """
        Initialize certificate generator.
        
        Args:
            base_path: Base path to stage-env directory
            certs_dir: Optional path to certificates directory (defaults to base_path/cache/certs)
        """
        self.base_path = base_path
        self.certs_dir = certs_dir if certs_dir is not None else (base_path / "cache" / "certs")
        self.dockerfile = base_path / "Dockerfile.cert-generator"
        
        self.certs_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("cert_generator_initialized",
                   certs_dir=str(self.certs_dir),
                   docker_mode=True)
    
    def build_docker_image(self) -> bool:
        """
        Build Docker image for certificate generator if needed.
        
        Returns:
            True if image is ready
        """
        # Check if image exists
        try:
            result = subprocess.run(
                ["docker", "images", "-q", CERT_GENERATOR_IMAGE],
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout.strip():
                logger.debug("cert_generator_image_exists")
                return True
        except subprocess.CalledProcessError:
            pass
        
        logger.info("building_cert_generator_image")
        print_info("Building certificate generator Docker image...")
        
        try:
            # Build Docker image from project root
            project_root = self.base_path.parent.parent  # Go up from stage-env to project root
            
            result = subprocess.run(
                [
                    "docker", "build",
                    "-f", str(self.dockerfile),
                    "-t", CERT_GENERATOR_IMAGE,
                    str(project_root)
                ],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            if result.returncode != 0:
                logger.error("image_build_failed", 
                           stderr=result.stderr,
                           stdout=result.stdout)
                print_error(f"Failed to build image: {result.stderr}")
                return False
            
            print_success("Certificate generator image built")
            logger.info("cert_generator_image_built")
            return True
            
        except Exception as e:
            logger.error("image_build_exception", error=str(e))
            print_error(f"Exception building image: {e}")
            return False
    
    def generate_node_cert(
        self,
        node_id: int,
        node_name: str,
        output_dir: Optional[Path] = None,
    ) -> Path:
        """
        Generate certificate for a node.
        
        Args:
            node_id: Node ID
            node_name: Node name
            output_dir: Output directory (default: cache/certs/nodeN)
            
        Returns:
            Path to generated certificate
        """
        if output_dir is None:
            output_dir = self.certs_dir / f"node{node_id}"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        cert_file = output_dir / "node-addr.dcert"
        
        logger.info("generating_node_cert",
                   node_id=node_id,
                   node_name=node_name)
        
        # Use cert tool to generate
        # For now, use Python fallback for simple cert generation
        self._generate_simple_cert(
            name=node_name,
            cert_type="node",
            output_file=cert_file,
        )
        
        logger.info("node_cert_generated",
                   node_id=node_id,
                   path=str(cert_file))
        
        return cert_file
    
    def generate_validator_certs(
        self,
        prefix: str,
        count: int,
        output_dir: Optional[Path] = None,
    ) -> List[Path]:
        """
        Generate validator certificates.
        
        Args:
            prefix: Certificate prefix (e.g., "stagenet.master")
            count: Number of certificates to generate
            output_dir: Output directory
            
        Returns:
            List of paths to generated certificates
        """
        if output_dir is None:
            output_dir = self.certs_dir
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("generating_validator_certs",
                   prefix=prefix,
                   count=count)
        
        certs = []
        
        for i in range(count):
            cert_name = f"{prefix}.{i}"
            cert_file = output_dir / f"{cert_name}.dcert"
            
            self._generate_simple_cert(
                name=cert_name,
                cert_type="validator",
                output_file=cert_file,
            )
            
            certs.append(cert_file)
        
        logger.info("validator_certs_generated", count=len(certs))
        
        return certs
    
    def generate_all(
        self,
        network_name: str,
        node_count: int,
        validator_count: int = 3,
    ) -> dict:
        """
        Generate all certificates for network using Docker-based cf-cert-generator.
        
        Args:
            network_name: Network name (e.g., "stagenet")
            node_count: Number of nodes
            validator_count: Number of validators
            
        Returns:
            Dict with generated certificate paths
        """
        logger.info("generating_all_certificates",
                   network=network_name,
                   nodes=node_count,
                   validators=validator_count,
                   method="docker")
        
        print_info(f"Generating {node_count} node certificates using Docker...")
        
        # Ensure Docker image is built
        if not self.build_docker_image():
            raise RuntimeError("Failed to build certificate generator Docker image")
        
        # Network ID for stagenet
        network_id = "0x1234"
        
        # Prepare output directory with correct permissions
        self.certs_dir.mkdir(parents=True, exist_ok=True)
        
        # Run certificate generator in Docker
        # Mount certs directory as /output in container
        try:
            logger.info("calling_docker_cert_generator",
                       image=CERT_GENERATOR_IMAGE,
                       output_dir=str(self.certs_dir),
                       node_count=node_count,
                       network_name=network_name,
                       network_id=network_id)
            
            # Docker command: docker run --rm -v <host_path>:/output <image> /output <count> <network> <id>
            result_proc = subprocess.run(
                [
                    "docker", "run",
                    "--rm",  # Remove container after execution
                    "-v", f"{self.certs_dir.absolute()}:/output",  # Mount certs directory
                    "-u", f"{os.getuid()}:{os.getgid()}",  # Run as current user to avoid permission issues
                    CERT_GENERATOR_IMAGE,
                    "/output",  # output directory inside container
                    str(node_count),  # number of nodes
                    network_name,  # network name
                    network_id  # network ID
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            
            logger.info("cert_generator_docker_output", stdout=result_proc.stdout)
            
            if result_proc.stderr:
                logger.warning("cert_generator_docker_stderr", stderr=result_proc.stderr)
            
        except subprocess.CalledProcessError as e:
            print_error(f"Certificate generation failed: {e}")
            logger.error("cert_generation_docker_failed",
                        returncode=e.returncode,
                        stdout=e.stdout,
                        stderr=e.stderr)
            raise RuntimeError(f"Certificate generation failed: {e.stderr}")
        
        result = {
            "nodes": [],
            "validators": [],
        }
        
        # Collect generated certificates from node1/, node2/, etc.
        for i in range(1, node_count + 1):
            node_dir = self.certs_dir / f"node{i}"
            
            # Main node certificate
            node_cert = node_dir / "node-addr.dcert"
            if node_cert.exists():
                result["nodes"].append(str(node_cert))
            
            # ESBOCS validator certificate
            esbocs_cert = node_dir / "node-addr.esbocs.dcert"
            if esbocs_cert.exists():
                result["validators"].append(str(esbocs_cert))
        
        # Save PKI config
        pki_config = {
            "network": network_name,
            "network_id": network_id,
            "node_count": node_count,
            "validator_count": validator_count,
            "generated_at": self._get_timestamp(),
            "crypto": "Dilithium (post-quantum)",
        }
        
        pki_config_file = self.certs_dir / "pki-config.json"
        with open(pki_config_file, "w") as f:
            json.dump(pki_config, f, indent=2)
        
        print_success(f"Generated {len(result['nodes'])} node + {len(result['validators'])} validator certificates")
        logger.info("all_certificates_generated",
                   nodes=len(result["nodes"]),
                   validators=len(result["validators"]))
        
        return result
    
    def _generate_simple_cert(
        self,
        name: str,
        cert_type: str,
        output_file: Path,
    ) -> None:
        """
        Generate simple certificate (fallback method).
        
        Args:
            name: Certificate name
            cert_type: Certificate type
            output_file: Output file path
        """
        # Simple placeholder implementation
        # In production, this would call the C utility or use proper crypto
        
        cert_data = {
            "name": name,
            "type": cert_type,
            "version": "1.0",
            "created": self._get_timestamp(),
        }
        
        with open(output_file, "w") as f:
            json.dump(cert_data, f, indent=2)
        
        logger.debug("simple_cert_generated",
                    name=name,
                    type=cert_type,
                    file=str(output_file))
    
    def _get_timestamp(self) -> str:
        """Get current ISO timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
    
    def certs_exist(self) -> bool:
        """
        Check if certificates exist.
        
        Returns:
            True if certificate directory has content
        """
        if not self.certs_dir.exists():
            return False
        
        # Check for PKI config
        pki_config = self.certs_dir / "pki-config.json"
        if not pki_config.exists():
            return False
        
        # Check for at least one cert
        certs = list(self.certs_dir.rglob("*.dcert"))
        
        return len(certs) > 0
    
    def clean(self) -> None:
        """Remove all generated certificates."""
        logger.info("cleaning_certificates")
        
        import shutil
        
        if self.certs_dir.exists():
            print_info("Removing certificates...")
            shutil.rmtree(self.certs_dir)
            self.certs_dir.mkdir(parents=True, exist_ok=True)
        
        print_success("Certificates cleaned")
        logger.info("certificates_cleaned")

