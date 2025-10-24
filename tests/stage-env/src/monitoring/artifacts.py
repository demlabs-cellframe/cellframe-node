"""
Test artifacts collector.

Собирает артефакты после выполнения тестов:
- Core dumps (coredump)
- Stack traces (backtrace)
- Application logs
- Monitoring metrics
- Container logs
- System info (при падении)
"""

import gzip
import shutil
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel

from ..utils.logger import get_logger
from ..utils.cli import run_command, print_info, print_success, print_warning

logger = get_logger(__name__)


class ArtifactMetadata(BaseModel):
    """Metadata for collected artifact."""
    
    artifact_type: str  # coredump, log, trace, metric
    node_id: Optional[str] = None
    timestamp: str
    size_bytes: int
    compressed: bool = False
    source_path: str
    description: str


class ArtifactsCollector:
    """Collect test execution artifacts for debugging."""
    
    def __init__(self, base_path: Path):
        """
        Initialize artifacts collector.
        
        Args:
            base_path: Base path to stage-env directory
        """
        self.base_path = base_path
        self.artifacts_dir = base_path / "cache" / "crash-artifacts"
        self.logs_dir = base_path / "cache" / "logs"
        self.monitoring_dir = base_path / "cache" / "monitoring"
        
        # Create directories
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.monitoring_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("artifacts_collector_initialized",
                   artifacts_dir=str(self.artifacts_dir))
    
    def collect_on_crash(
        self,
        node_id: str,
        container_name: str,
        test_name: Optional[str] = None,
    ) -> Dict[str, any]:
        """
        Collect all artifacts when node crashes.
        
        Args:
            node_id: Node identifier
            container_name: Docker container name
            test_name: Test that was running
            
        Returns:
            Dict with collected artifacts info
        """
        timestamp = self._get_timestamp()
        session_dir = self.artifacts_dir / f"{node_id}_{timestamp}"
        session_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("collecting_crash_artifacts",
                   node_id=node_id,
                   test=test_name,
                   session=session_dir.name)
        
        print_info(f"Collecting crash artifacts for {node_id}...")
        
        collected = {
            "node_id": node_id,
            "container": container_name,
            "test_name": test_name,
            "timestamp": timestamp,
            "session_dir": str(session_dir),
            "artifacts": [],
        }
        
        # 1. Collect core dumps
        coredumps = self._collect_coredumps(container_name, session_dir, node_id)
        collected["artifacts"].extend(coredumps)
        
        # 2. Collect application logs
        app_logs = self._collect_app_logs(container_name, session_dir, node_id)
        collected["artifacts"].extend(app_logs)
        
        # 3. Collect backtrace (if available)
        backtrace = self._collect_backtrace(container_name, session_dir, node_id)
        if backtrace:
            collected["artifacts"].append(backtrace)
        
        # 4. Collect system info
        sysinfo = self._collect_system_info(container_name, session_dir, node_id)
        if sysinfo:
            collected["artifacts"].append(sysinfo)
        
        # 5. Collect monitoring data
        metrics = self._collect_monitoring_metrics(node_id, session_dir)
        collected["artifacts"].extend(metrics)
        
        # 6. Create summary
        self._create_summary(collected, session_dir)
        
        print_success(f"Collected {len(collected['artifacts'])} artifacts to {session_dir.name}")
        logger.info("crash_artifacts_collected",
                   count=len(collected['artifacts']),
                   session=session_dir.name)
        
        return collected
    
    def collect_all_logs(self, test_name: str) -> Path:
        """
        Collect logs from all containers for a test.
        
        Args:
            test_name: Name of the test
            
        Returns:
            Path to archive with logs
        """
        timestamp = self._get_timestamp()
        logs_session = self.logs_dir / f"{test_name}_{timestamp}"
        logs_session.mkdir(parents=True, exist_ok=True)
        
        logger.info("collecting_all_logs", test=test_name)
        
        # This will be called after test execution
        # Docker compose logs collection
        
        # Create tarball
        archive_path = self.logs_dir / f"{test_name}_{timestamp}.tar.gz"
        
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(logs_session, arcname=logs_session.name)
        
        # Remove temp dir
        shutil.rmtree(logs_session)
        
        logger.info("logs_archived", archive=str(archive_path))
        
        return archive_path
    
    def _collect_coredumps(
        self,
        container_name: str,
        output_dir: Path,
        node_id: str,
    ) -> List[ArtifactMetadata]:
        """Collect core dumps from container."""
        
        logger.debug("collecting_coredumps", container=container_name)
        
        artifacts = []
        
        # Try to find core dumps in container
        # Common locations: /tmp/cores, /var/crash, current dir
        core_locations = ["/tmp/cores", "/var/crash", "/core"]
        
        for location in core_locations:
            try:
                # Check if location exists and has cores
                exit_code, output = self._exec_in_container(
                    container_name,
                    ["find", location, "-name", "core*", "-type", "f"],
                )
                
                if exit_code == 0 and output.strip():
                    core_files = output.strip().split("\n")
                    
                    for core_file in core_files:
                        if not core_file:
                            continue
                        
                        # Copy core dump from container
                        local_path = output_dir / f"coredump_{Path(core_file).name}"
                        
                        self._copy_from_container(
                            container_name,
                            core_file,
                            local_path,
                        )
                        
                        if local_path.exists():
                            # Compress core dump
                            compressed_path = self._compress_file(local_path)
                            
                            artifacts.append(ArtifactMetadata(
                                artifact_type="coredump",
                                node_id=node_id,
                                timestamp=self._get_timestamp(),
                                size_bytes=compressed_path.stat().st_size,
                                compressed=True,
                                source_path=core_file,
                                description=f"Core dump from {location}",
                            ))
                            
                            logger.info("coredump_collected",
                                      node_id=node_id,
                                      source=core_file,
                                      size_mb=compressed_path.stat().st_size / 1024 / 1024)
            
            except Exception as e:
                logger.warning("coredump_collection_failed",
                             location=location,
                             error=str(e))
        
        return artifacts
    
    def _collect_app_logs(
        self,
        container_name: str,
        output_dir: Path,
        node_id: str,
    ) -> List[ArtifactMetadata]:
        """Collect application logs from container."""
        
        logger.debug("collecting_app_logs", container=container_name)
        
        artifacts = []
        
        # Common log locations for cellframe-node
        log_locations = [
            "/opt/cellframe-node/var/log",
            "/var/log/cellframe-node",
            "/tmp/cellframe-node.log",
        ]
        
        for location in log_locations:
            try:
                exit_code, output = self._exec_in_container(
                    container_name,
                    ["find", location, "-name", "*.log", "-type", "f"],
                )
                
                if exit_code == 0 and output.strip():
                    log_files = output.strip().split("\n")
                    
                    for log_file in log_files:
                        if not log_file:
                            continue
                        
                        local_path = output_dir / f"log_{Path(log_file).name}"
                        
                        self._copy_from_container(
                            container_name,
                            log_file,
                            local_path,
                        )
                        
                        if local_path.exists():
                            # Compress log
                            compressed_path = self._compress_file(local_path)
                            
                            artifacts.append(ArtifactMetadata(
                                artifact_type="log",
                                node_id=node_id,
                                timestamp=self._get_timestamp(),
                                size_bytes=compressed_path.stat().st_size,
                                compressed=True,
                                source_path=log_file,
                                description=f"Application log: {Path(log_file).name}",
                            ))
            
            except Exception as e:
                logger.debug("log_collection_skipped",
                           location=location,
                           error=str(e))
        
        return artifacts
    
    def _collect_backtrace(
        self,
        container_name: str,
        output_dir: Path,
        node_id: str,
    ) -> Optional[ArtifactMetadata]:
        """Collect backtrace if available."""
        
        logger.debug("collecting_backtrace", container=container_name)
        
        # Try to generate backtrace from core dump using gdb
        # This requires gdb in container
        
        try:
            # Check if gdb is available
            exit_code, _ = self._exec_in_container(
                container_name,
                ["which", "gdb"],
            )
            
            if exit_code != 0:
                logger.debug("gdb_not_available")
                return None
            
            # Find binary and core
            # This is placeholder - real implementation would need proper paths
            
            logger.debug("backtrace_generation_not_implemented")
            return None
        
        except Exception as e:
            logger.debug("backtrace_collection_failed", error=str(e))
            return None
    
    def _collect_system_info(
        self,
        container_name: str,
        output_dir: Path,
        node_id: str,
    ) -> Optional[ArtifactMetadata]:
        """Collect system information at crash time."""
        
        logger.debug("collecting_system_info", container=container_name)
        
        try:
            sysinfo = []
            
            # Collect various system info
            commands = [
                ("uname", ["uname", "-a"]),
                ("memory", ["free", "-h"]),
                ("disk", ["df", "-h"]),
                ("processes", ["ps", "aux"]),
                ("network", ["ip", "addr"]),
            ]
            
            for name, cmd in commands:
                try:
                    exit_code, output = self._exec_in_container(container_name, cmd)
                    if exit_code == 0:
                        sysinfo.append(f"=== {name.upper()} ===\n{output}\n")
                except Exception:
                    pass
            
            if sysinfo:
                sysinfo_file = output_dir / "system_info.txt"
                sysinfo_file.write_text("\n".join(sysinfo))
                
                return ArtifactMetadata(
                    artifact_type="sysinfo",
                    node_id=node_id,
                    timestamp=self._get_timestamp(),
                    size_bytes=sysinfo_file.stat().st_size,
                    compressed=False,
                    source_path="system",
                    description="System information at crash time",
                )
        
        except Exception as e:
            logger.debug("sysinfo_collection_failed", error=str(e))
        
        return None
    
    def _collect_monitoring_metrics(
        self,
        node_id: str,
        output_dir: Path,
    ) -> List[ArtifactMetadata]:
        """Collect monitoring metrics for the node."""
        
        logger.debug("collecting_monitoring_metrics", node_id=node_id)
        
        artifacts = []
        
        # Look for monitoring data in cache/monitoring/
        node_metrics = self.monitoring_dir / f"{node_id}_metrics.json"
        
        if node_metrics.exists():
            # Copy to artifacts
            shutil.copy(node_metrics, output_dir / "metrics.json")
            
            artifacts.append(ArtifactMetadata(
                artifact_type="metric",
                node_id=node_id,
                timestamp=self._get_timestamp(),
                size_bytes=node_metrics.stat().st_size,
                compressed=False,
                source_path=str(node_metrics),
                description="Monitoring metrics",
            ))
        
        return artifacts
    
    def _create_summary(self, collected: Dict, output_dir: Path) -> None:
        """Create summary report for collected artifacts."""
        
        import json
        
        summary_file = output_dir / "SUMMARY.json"
        
        with open(summary_file, "w") as f:
            json.dump(collected, f, indent=2, default=str)
        
        # Also create human-readable summary
        readme = output_dir / "README.txt"
        
        content = f"""
Crash Artifacts Collection
===========================

Node ID: {collected['node_id']}
Container: {collected['container']}
Test: {collected.get('test_name', 'N/A')}
Timestamp: {collected['timestamp']}

Collected Artifacts ({len(collected['artifacts'])} total):
"""
        
        for i, artifact in enumerate(collected['artifacts'], 1):
            if isinstance(artifact, ArtifactMetadata):
                content += f"\n{i}. {artifact.artifact_type.upper()}: {artifact.description}"
                content += f"\n   Size: {artifact.size_bytes / 1024:.1f} KB"
                content += f"\n   Source: {artifact.source_path}\n"
        
        readme.write_text(content)
    
    def _exec_in_container(
        self,
        container_name: str,
        command: List[str],
    ) -> tuple[int, str]:
        """Execute command in container."""
        
        cmd = ["docker", "exec", container_name] + command
        
        try:
            exit_code, stdout, stderr = run_command(cmd, check=False)
            return exit_code, stdout + stderr
        except Exception as e:
            logger.debug("exec_failed", error=str(e))
            return 1, ""
    
    def _copy_from_container(
        self,
        container_name: str,
        source_path: str,
        dest_path: Path,
    ) -> None:
        """Copy file from container to host."""
        
        cmd = ["docker", "cp", f"{container_name}:{source_path}", str(dest_path)]
        
        try:
            run_command(cmd, check=False)
        except Exception as e:
            logger.warning("copy_from_container_failed",
                         source=source_path,
                         error=str(e))
    
    def _compress_file(self, file_path: Path) -> Path:
        """Compress file with gzip."""
        
        compressed_path = file_path.with_suffix(file_path.suffix + ".gz")
        
        with open(file_path, "rb") as f_in:
            with gzip.open(compressed_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remove original
        file_path.unlink()
        
        return compressed_path
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        return datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    def list_artifacts(self) -> List[Dict[str, any]]:
        """
        List all collected artifact sessions.
        
        Returns:
            List of session info dicts
        """
        sessions = []
        
        for session_dir in sorted(self.artifacts_dir.iterdir(), reverse=True):
            if not session_dir.is_dir():
                continue
            
            summary_file = session_dir / "SUMMARY.json"
            
            if summary_file.exists():
                import json
                with open(summary_file) as f:
                    summary = json.load(f)
                    sessions.append({
                        "session": session_dir.name,
                        "node_id": summary.get("node_id"),
                        "timestamp": summary.get("timestamp"),
                        "artifacts_count": len(summary.get("artifacts", [])),
                        "path": str(session_dir),
                    })
        
        return sessions
    
    def clean_old_artifacts(self, keep_last: int = 10) -> None:
        """
        Clean old artifact sessions, keeping only recent ones.
        
        Args:
            keep_last: Number of recent sessions to keep
        """
        sessions = sorted(self.artifacts_dir.iterdir(), reverse=True)
        
        removed = 0
        for session_dir in sessions[keep_last:]:
            if session_dir.is_dir():
                shutil.rmtree(session_dir)
                removed += 1
        
        if removed > 0:
            print_info(f"Removed {removed} old artifact sessions")
            logger.info("old_artifacts_cleaned", removed=removed)

