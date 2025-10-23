#!/usr/bin/env python3
"""
Helper script to collect artifacts and generate reports after test run.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add stage-env to path
sys.path.insert(0, str(Path(__file__).parent / "stage-env"))

from src.utils.artifacts import ArtifactsManager
from src.utils.report_generator import ReportGenerator
from src.config.loader import ConfigLoader
from src.utils.logger import setup_logging, get_logger

setup_logging(verbose=True, json_output=False)
logger = get_logger(__name__)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: collect_artifacts.py <test_type> [exit_code]", file=sys.stderr)
        print("  test_type: e2e, functional, or all", file=sys.stderr)
        print("  exit_code: optional test exit code (default: 0)", file=sys.stderr)
        sys.exit(1)
    
    test_type = sys.argv[1]
    exit_code = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    
    # Get base paths
    tests_dir = Path(__file__).parent
    stage_env_dir = tests_dir / "stage-env"
    config_file = tests_dir / "stage-env.cfg"
    
    logger.info("collecting_artifacts", 
               test_type=test_type,
               exit_code=exit_code)
    
    # Load configuration
    config_loader = ConfigLoader(stage_env_dir, config_file)
    artifacts_config = config_loader.get_artifacts_config()
    
    # Initialize artifacts manager
    artifacts_manager = ArtifactsManager(stage_env_dir, artifacts_config)
    
    # Create run directory
    run_id = f"{test_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    run_dir = artifacts_manager.create_run_directory(run_id)
    
    logger.info("created_run_directory", run_dir=str(run_dir))
    
    # Collect stage-env log
    log_dir = tests_dir / "logs"
    if log_dir.exists():
        # Find most recent log file
        log_files = sorted(log_dir.glob("stage-env_*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
        if log_files:
            artifacts_manager.collect_stage_env_log(run_dir, log_files[0])
    
    # Collect node logs from Docker containers
    try:
        import docker
        client = docker.from_env()
        project_name = "cellframe-stage"
        
        # Get all running node containers
        containers = client.containers.list(
            all=True,
            filters={"label": f"com.docker.compose.project={project_name}"}
        )
        
        node_logs_dir = run_dir / "node-logs"
        core_dumps_dir = run_dir / "core-dumps"
        
        for container in containers:
            try:
                # Extract node name from container name
                # e.g., "cellframe-stage-node-1" -> "node-1"
                container_name = container.name
                if "node-" in container_name:
                    node_name = container_name.split("node-", 1)[1]
                    node_id = f"node-{node_name}"
                    
                    # Collect logs
                    logger.info("collecting_container_logs", node=node_id)
                    logs = container.logs(tail=10000).decode('utf-8', errors='ignore')
                    log_file = node_logs_dir / f"{node_id}.log"
                    log_file.write_text(logs)
                    
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
                                    logger.info("collected_core_dump", 
                                              node=node_id, 
                                              file=file)
            except Exception as e:
                logger.warning("failed_to_collect_container_artifacts",
                             container=container.name,
                             error=str(e))
        
    except Exception as e:
        logger.error("failed_to_collect_docker_artifacts", error=str(e))
    
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
            'node_logs': list((run_dir / "node-logs").glob("*.log")),
            'stage_env_logs': list((run_dir / "stage-env-logs").glob("*.log")),
            'core_dumps': list((run_dir / "core-dumps").glob("*")),
            'stack_traces': list((run_dir / "stack-traces").glob("*")),
        }
    }
    
    # Convert Path objects to strings for JSON serialization
    for key in summary_data['artifacts']:
        summary_data['artifacts'][key] = [str(p.name) for p in summary_data['artifacts'][key]]
    
    # Create summary file
    artifacts_manager.create_run_summary(run_dir, summary_data)
    
    # Generate reports
    logger.info("generating_reports")
    
    report_generator = ReportGenerator(run_dir)
    reports = report_generator.generate_full_report(summary_data)
    
    # Print results
    print(f"\n✅ Artifacts collected: {run_dir}")
    print(f"\n📊 Reports generated:")
    for report_type, report_path in reports.items():
        print(f"  - {report_type}: {report_path}")
    
    # Cleanup old artifacts
    logger.info("cleaning_up_old_artifacts")
    artifacts_manager.cleanup_old_artifacts()
    
    logger.info("artifacts_collection_completed")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

