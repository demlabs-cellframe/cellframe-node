"""
Artifacts collection and management for stage-env test runs.

This module handles collection of:
- stage-env logs
- Node logs from all containers
- Core dumps and stack traces
- Health check and monitoring logs
"""

from pathlib import Path
from datetime import datetime, timedelta
import shutil
from typing import List, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ArtifactsManager:
    """Manages test artifacts collection and organization."""
    
    def __init__(self, base_path: Path, config: dict):
        """
        Initialize artifacts manager.
        
        Args:
            base_path: Base path for stage-env
            config: Configuration dict with [artifacts] section
        """
        self.base_path = base_path
        self.config = config
        
        # Get artifacts directory from config
        artifacts_dir = config.get('artifacts_dir', '../testing/artifacts')
        self.artifacts_root = (base_path / artifacts_dir).resolve()
        
        # Collection flags (use different names to avoid conflict with methods)
        self.should_collect_node_logs = config.get('collect_node_logs', True)
        self.should_collect_health_logs = config.get('collect_health_logs', True)
        self.should_collect_crash_dumps = config.get('collect_crash_dumps', True)
        self.retain_days = config.get('retain_days', 30)
        
        # Create base structure
        self._create_base_structure()
        
        logger.info("artifacts_manager_initialized",
                   artifacts_dir=str(self.artifacts_root),
                   collect_node_logs=self.should_collect_node_logs,
                   collect_health_logs=self.should_collect_health_logs,
                   collect_crash_dumps=self.should_collect_crash_dumps)
    
    def _create_base_structure(self):
        """Create base artifacts directory structure (only root, subdirs are per-run)."""
        # Only create the root artifacts directory
        # All subdirectories (node-logs, core-dumps, etc.) are created per-run
        self.artifacts_root.mkdir(parents=True, exist_ok=True)
        logger.debug("created_artifacts_directory", path=str(self.artifacts_root))
    
    def create_run_directory(self, run_id: Optional[str] = None, test_type: Optional[str] = None) -> Path:
        """
        Create a directory for a specific test run.
        
        Args:
            run_id: Optional run identifier (defaults to timestamp)
            test_type: Optional test type (e2e, functional, base) to create subdirectories
            
        Returns:
            Path to the run directory (or test_type subdir if specified)
        """
        if run_id is None:
            run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        run_dir = self.artifacts_root / f"run_{run_id}"
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for this run
        subdirs = [
            "stage-env-logs",
            "node-logs",
            "core-dumps",
            "stack-traces",
            "health-logs",
            "reports",
            "scenario-logs",
        ]
        
        # If test_type specified, create only that test type subdirectory
        if test_type:
            test_type_dir = run_dir / test_type
            test_type_dir.mkdir(exist_ok=True)
            
            # Create subdirs under this specific test type
            for subdir in subdirs:
                (test_type_dir / subdir).mkdir(exist_ok=True)
            
            result_dir = test_type_dir
        else:
            # Create subdirs at run_dir level (old behavior)
            for subdir in subdirs:
                (run_dir / subdir).mkdir(exist_ok=True)
            result_dir = run_dir
        
        logger.info("created_run_directory", 
                   run_id=run_id, 
                   test_type=test_type,
                   path=str(result_dir))
        return result_dir
    
    def collect_stage_env_log(self, run_dir: Path, log_file: Path):
        """
        Copy stage-env log to artifacts.
        
        Args:
            run_dir: Run directory
            log_file: Path to stage-env log file
        """
        if not log_file.exists():
            logger.warning("stage_env_log_not_found", log_file=str(log_file))
            return
        
        dest = run_dir / "stage-env-logs" / log_file.name
        try:
            shutil.copy2(log_file, dest)
            logger.info("collected_stage_env_log", 
                       source=str(log_file),
                       dest=str(dest))
        except Exception as e:
            logger.error("failed_to_collect_stage_env_log",
                        log_file=str(log_file),
                        error=str(e))
    
    def collect_node_logs(self, run_dir: Path, docker_client, node_names: List[str]):
        """
        Collect logs from all Docker containers.
        
        Args:
            run_dir: Run directory
            docker_client: Docker client instance
            node_names: List of node names to collect logs from
        """
        if not self.should_collect_node_logs:
            logger.debug("node_logs_collection_disabled")
            return
        
        node_logs_dir = run_dir / "node-logs"
        
        for node_name in node_names:
            try:
                container_name = f"cellframe-stage-{node_name}"
                container = docker_client.containers.get(container_name)
                
                # Get all logs
                logs = container.logs().decode('utf-8', errors='ignore')
                
                # Write to file
                log_file = node_logs_dir / f"{node_name}.log"
                log_file.write_text(logs)
                
                logger.info("collected_node_log",
                           node=node_name,
                           size=len(logs),
                           file=str(log_file))
            except Exception as e:
                logger.error("failed_to_collect_node_log",
                            node=node_name,
                            error=str(e))
    
    def collect_core_dumps(self, run_dir: Path, docker_client, node_names: List[str]):
        """
        Collect core dumps from containers if they exist.
        
        Args:
            run_dir: Run directory
            docker_client: Docker client instance
            node_names: List of node names
        """
        if not self.should_collect_crash_dumps:
            logger.debug("crash_dumps_collection_disabled")
            return
        
        core_dumps_dir = run_dir / "core-dumps"
        stack_traces_dir = run_dir / "stack-traces"
        
        for node_name in node_names:
            try:
                container_name = f"cellframe-stage-{node_name}"
                container = docker_client.containers.get(container_name)
                
                # Check for core dumps in common locations
                core_paths = [
                    "/tmp/core*",
                    "/var/crash/*",
                    "/opt/cellframe-node/var/log/core*"
                ]
                
                for pattern in core_paths:
                    try:
                        # List files matching pattern
                        result = container.exec_run(f"sh -c 'ls -1 {pattern} 2>/dev/null || true'")
                        if result.exit_code == 0 and result.output:
                            files = result.output.decode('utf-8').strip().split('\n')
                            for file_path in files:
                                if file_path:
                                    self._extract_file_from_container(
                                        container, file_path, 
                                        core_dumps_dir / f"{node_name}_{Path(file_path).name}"
                                    )
                                    
                                    # Try to generate stack trace
                                    self._generate_stack_trace(
                                        container, file_path, node_name, stack_traces_dir
                                    )
                    except Exception as e:
                        logger.debug("no_core_dumps_for_pattern",
                                    node=node_name,
                                    pattern=pattern,
                                    error=str(e))
            except Exception as e:
                logger.error("failed_to_check_core_dumps",
                            node=node_name,
                            error=str(e))
    
    def _extract_file_from_container(self, container, src_path: str, dest_path: Path):
        """Extract a file from Docker container."""
        try:
            # Use docker cp via container.get_archive
            stream, stat = container.get_archive(src_path)
            
            # Write to destination
            import tarfile
            import io
            
            tar_stream = io.BytesIO()
            for chunk in stream:
                tar_stream.write(chunk)
            tar_stream.seek(0)
            
            with tarfile.open(fileobj=tar_stream) as tar:
                # Extract the file
                for member in tar.getmembers():
                    if member.isfile():
                        with tar.extractfile(member) as src:
                            dest_path.write_bytes(src.read())
                        logger.info("extracted_file_from_container",
                                   src=src_path,
                                   dest=str(dest_path),
                                   size=dest_path.stat().st_size)
                        break
        except Exception as e:
            logger.error("failed_to_extract_file",
                        src=src_path,
                        dest=str(dest_path),
                        error=str(e))
    
    def _generate_stack_trace(self, container, core_path: str, node_name: str, 
                             stack_traces_dir: Path):
        """Generate stack trace from core dump using gdb."""
        try:
            # Try to use gdb to generate backtrace
            result = container.exec_run(
                f"gdb -batch -ex 'bt' /opt/cellframe-node/bin/cellframe-node {core_path}",
                demux=False
            )
            
            if result.exit_code == 0 and result.output:
                trace_file = stack_traces_dir / f"{node_name}_{Path(core_path).name}.txt"
                trace_file.write_bytes(result.output)
                logger.info("generated_stack_trace",
                           node=node_name,
                           file=str(trace_file))
        except Exception as e:
            logger.debug("failed_to_generate_stack_trace",
                        node=node_name,
                        error=str(e))
    
    def collect_health_logs(self, run_dir: Path):
        """
        Collect health check and monitoring logs from Docker containers.
        
        Args:
            run_dir: Run directory
        """
        if not self.should_collect_health_logs:
            logger.debug("health_logs_collection_disabled")
            return
        
        try:
            import docker
            client = docker.from_env()
            project_name = "cellframe-stage"
            
            containers = client.containers.list(
                all=True,
                filters={"label": f"com.docker.compose.project={project_name}"}
            )
            
            health_logs_dir = run_dir / "health-logs"
            collected = 0
            
            for container in containers:
                try:
                    container_name = container.name
                    if "node-" in container_name:
                        node_name = container_name.split("node-", 1)[1]
                        node_id = f"node-{node_name}"
                        
                        # Get container health status
                        health_info = {
                            "node_id": node_id,
                            "container_name": container_name,
                            "status": container.status,
                            "health": container.attrs.get('State', {}).get('Health', {}),
                            "started_at": container.attrs.get('State', {}).get('StartedAt'),
                            "finished_at": container.attrs.get('State', {}).get('FinishedAt'),
                        }
                        
                        # Try to get cellframe-node CLI health check
                        try:
                            result = container.exec_run("cellframe-node-cli version", demux=False)
                            health_info["cli_available"] = result.exit_code == 0
                            if result.exit_code == 0:
                                health_info["version"] = result.output.decode('utf-8', errors='ignore').strip()
                        except:
                            health_info["cli_available"] = False
                        
                        # Try to get network status
                        try:
                            result = container.exec_run(
                                "cellframe-node-cli net -net stagenet get status",
                                demux=False
                            )
                            if result.exit_code == 0:
                                health_info["network_status"] = result.output.decode('utf-8', errors='ignore').strip()
                        except:
                            pass
                        
                        # Write health info to file
                        import json
                        health_file = health_logs_dir / f"{node_id}_health.json"
                        health_file.write_text(json.dumps(health_info, indent=2, default=str))
                        collected += 1
                        
                except Exception as e:
                    logger.warning("failed_to_collect_health_info",
                                 container=container.name,
                                 error=str(e))
            
            if collected > 0:
                logger.info("collected_health_logs", count=collected)
                
        except Exception as e:
            logger.error("health_logs_collection_failed", error=str(e))
    
    def cleanup_old_artifacts(self):
        """Remove artifacts older than retain_days."""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retain_days)
            removed_count = 0
            
            # Find all run directories
            for run_dir in self.artifacts_root.glob("run_*"):
                if not run_dir.is_dir():
                    continue
                
                # Check directory modification time
                mtime = datetime.fromtimestamp(run_dir.stat().st_mtime)
                if mtime < cutoff_date:
                    shutil.rmtree(run_dir)
                    removed_count += 1
                    logger.info("removed_old_artifacts",
                               run_dir=run_dir.name,
                               age_days=(datetime.now() - mtime).days)
            
            if removed_count > 0:
                logger.info("cleanup_completed", removed=removed_count)
        except Exception as e:
            logger.error("cleanup_failed", error=str(e))
    
    def create_run_summary(self, run_dir: Path, summary_data: dict):
        """
        Create a summary file for the test run.
        
        Args:
            run_dir: Run directory
            summary_data: Dictionary with summary information
        """
        import json
        
        summary_file = run_dir / "summary.json"
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "run_id": run_dir.name,
            **summary_data
        }
        
        summary_file.write_text(json.dumps(summary, indent=2))
        logger.info("created_run_summary", file=str(summary_file))

