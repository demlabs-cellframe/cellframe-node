"""
Report generator for test runs.

Generates:
- Markdown reports
- PDF reports (via pandoc or weasyprint)
- Summary statistics
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json
import subprocess

from ..utils.logger import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """Generate test run reports in various formats."""
    
    def __init__(self, run_dir: Path):
        """
        Initialize report generator.
        
        Args:
            run_dir: Directory containing run artifacts
        """
        self.run_dir = run_dir
        self.report_dir = run_dir / "reports"
        self.report_dir.mkdir(exist_ok=True)
        
        logger.info("report_generator_initialized", run_dir=str(run_dir))
    
    def generate_markdown_report(self, summary_data: Dict) -> Path:
        """
        Generate Markdown report.
        
        Args:
            summary_data: Summary data dictionary
            
        Returns:
            Path to generated Markdown file
        """
        logger.info("generating_markdown_report")
        
        md_file = self.report_dir / "report.md"
        
        # Build markdown content
        content = self._build_markdown_content(summary_data)
        
        # Write to file
        md_file.write_text(content)
        
        logger.info("markdown_report_generated", file=str(md_file))
        return md_file
    
    def _build_markdown_content(self, summary_data: Dict) -> str:
        """Build markdown content from summary data."""
        
        run_id = summary_data.get('run_id', 'unknown')
        timestamp = summary_data.get('timestamp', datetime.now().isoformat())
        topology = summary_data.get('topology', 'unknown')
        network = summary_data.get('network', 'unknown')
        total_nodes = summary_data.get('total_nodes', 0)
        
        # Test results
        tests_run = summary_data.get('tests_run', 0)
        tests_passed = summary_data.get('tests_passed', 0)
        tests_failed = summary_data.get('tests_failed', 0)
        tests_skipped = summary_data.get('tests_skipped', 0)
        
        # Timing
        startup_time = summary_data.get('startup_time_seconds', 0)
        test_duration = summary_data.get('test_duration_seconds', 0)
        total_duration = summary_data.get('total_duration_seconds', 0)
        
        # Build markdown
        md = f"""# Test Run Report: {run_id}

## Summary

- **Run ID:** {run_id}
- **Timestamp:** {timestamp}
- **Topology:** {topology}
- **Network:** {network}
- **Total Nodes:** {total_nodes}

## Test Results

| Metric | Value |
|--------|-------|
| Tests Run | {tests_run} |
| Tests Passed | ✅ {tests_passed} |
| Tests Failed | ❌ {tests_failed} |
| Tests Skipped | ⏭️  {tests_skipped} |
| **Success Rate** | **{(tests_passed/tests_run*100) if tests_run > 0 else 0:.1f}%** |

## Performance

| Metric | Duration |
|--------|----------|
| Network Startup | {startup_time:.1f}s |
| Test Execution | {test_duration:.1f}s |
| **Total Duration** | **{total_duration:.1f}s** |

## Network Status

"""
        
        # Node status table
        nodes_status = summary_data.get('nodes_status', {})
        if nodes_status:
            md += "### Nodes\n\n"
            md += "| Node | Status | Links | State |\n"
            md += "|------|--------|-------|-------|\n"
            
            for node_name, status in nodes_status.items():
                state = status.get('state', 'unknown')
                links = status.get('links', 0)
                health = '✅' if status.get('healthy', False) else '❌'
                md += f"| {node_name} | {health} | {links} | {state} |\n"
            
            md += "\n"
        
        # Test scenarios
        scenarios = summary_data.get('scenarios', [])
        if scenarios:
            md += "## Test Scenarios\n\n"
            
            for scenario in scenarios:
                scenario_name = scenario.get('name', 'unknown')
                scenario_status = scenario.get('status', 'unknown')
                scenario_duration = scenario.get('duration', 0)
                
                status_emoji = {
                    'passed': '✅',
                    'failed': '❌',
                    'skipped': '⏭️',
                    'error': '💥'
                }.get(scenario_status, '❓')
                
                md += f"### {status_emoji} {scenario_name}\n\n"
                md += f"- **Status:** {scenario_status}\n"
                md += f"- **Duration:** {scenario_duration:.2f}s\n"
                
                # Add error details if failed
                if scenario_status in ['failed', 'error']:
                    error = scenario.get('error', 'No error details')
                    md += f"\n**Error:**\n```\n{error}\n```\n"
                
                md += "\n"
        
        # Artifacts
        md += "## Collected Artifacts\n\n"
        
        artifacts = summary_data.get('artifacts', {})
        
        if artifacts.get('node_logs'):
            md += f"- **Node Logs:** {len(artifacts['node_logs'])} files\n"
        
        if artifacts.get('stage_env_logs'):
            md += f"- **Stage-env Logs:** {len(artifacts['stage_env_logs'])} files\n"
        
        if artifacts.get('core_dumps'):
            md += f"- **Core Dumps:** {len(artifacts['core_dumps'])} files ⚠️\n"
        
        if artifacts.get('stack_traces'):
            md += f"- **Stack Traces:** {len(artifacts['stack_traces'])} files\n"
        
        md += "\n"
        
        # Logs location
        md += "## Logs Location\n\n"
        md += f"All artifacts are located in: `{self.run_dir}`\n\n"
        md += "```\n"
        md += f"{self.run_dir.name}/\n"
        md += "├── stage-env-logs/    # Stage-env logs\n"
        md += "├── node-logs/         # Node container logs\n"
        md += "├── core-dumps/        # Core dumps (if any)\n"
        md += "├── stack-traces/      # Stack traces\n"
        md += "├── health-logs/       # Health check logs\n"
        md += "├── reports/           # This report\n"
        md += "└── summary.json       # Machine-readable summary\n"
        md += "```\n\n"
        
        # Footer
        md += "---\n\n"
        md += f"*Report generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        return md
    
    def generate_pdf_report(self, md_file: Path) -> Optional[Path]:
        """
        Generate PDF report from Markdown.
        
        Tries multiple methods:
        1. pandoc (if available)
        2. weasyprint (if available)
        3. Falls back to markdown-only
        
        Args:
            md_file: Path to markdown file
            
        Returns:
            Path to generated PDF file or None if failed
        """
        logger.info("generating_pdf_report", markdown=str(md_file))
        
        pdf_file = self.report_dir / "report.pdf"
        
        # Try pandoc first
        if self._try_pandoc(md_file, pdf_file):
            logger.info("pdf_report_generated_with_pandoc", file=str(pdf_file))
            return pdf_file
        
        # Try weasyprint
        if self._try_weasyprint(md_file, pdf_file):
            logger.info("pdf_report_generated_with_weasyprint", file=str(pdf_file))
            return pdf_file
        
        logger.warning("pdf_generation_failed_no_tools_available",
                      tried=['pandoc', 'weasyprint'])
        return None
    
    def _try_pandoc(self, md_file: Path, pdf_file: Path) -> bool:
        """Try to generate PDF using pandoc."""
        try:
            # Check if pandoc is available
            result = subprocess.run(
                ['which', 'pandoc'],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode != 0:
                logger.debug("pandoc_not_available")
                return False
            
            # Generate PDF
            cmd = [
                'pandoc',
                str(md_file),
                '-o', str(pdf_file),
                '--pdf-engine=xelatex',
                '-V', 'geometry:margin=2cm',
                '-V', 'fontsize=11pt',
                '--highlight-style=tango'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=60,
                text=True
            )
            
            if result.returncode == 0 and pdf_file.exists():
                return True
            
            logger.warning("pandoc_failed",
                          returncode=result.returncode,
                          stderr=result.stderr[:500] if result.stderr else '')
            return False
            
        except subprocess.TimeoutExpired:
            logger.warning("pandoc_timeout")
            return False
        except Exception as e:
            logger.warning("pandoc_error", error=str(e))
            return False
    
    def _try_weasyprint(self, md_file: Path, pdf_file: Path) -> bool:
        """Try to generate PDF using weasyprint (via markdown2)."""
        try:
            import markdown2
            from weasyprint import HTML
            
            # Convert markdown to HTML
            md_content = md_file.read_text()
            html_content = markdown2.markdown(
                md_content,
                extras=['tables', 'fenced-code-blocks']
            )
            
            # Add CSS styling
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        max-width: 800px;
                        margin: 40px auto;
                        padding: 0 20px;
                    }}
                    h1, h2, h3 {{ color: #333; }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 20px 0;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }}
                    th {{ background-color: #f2f2f2; }}
                    code {{
                        background-color: #f4f4f4;
                        padding: 2px 5px;
                        border-radius: 3px;
                    }}
                    pre {{
                        background-color: #f4f4f4;
                        padding: 10px;
                        border-radius: 5px;
                        overflow-x: auto;
                    }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            # Generate PDF
            HTML(string=styled_html).write_pdf(str(pdf_file))
            
            if pdf_file.exists():
                return True
            
            return False
            
        except ImportError:
            logger.debug("weasyprint_not_available")
            return False
        except Exception as e:
            logger.warning("weasyprint_error", error=str(e))
            return False
    
    def generate_full_report(self, summary_data: Dict) -> Dict[str, Path]:
        """
        Generate both Markdown and PDF reports.
        
        Args:
            summary_data: Summary data dictionary
            
        Returns:
            Dictionary with paths to generated files
        """
        logger.info("generating_full_report")
        
        results = {}
        
        # Generate Markdown
        try:
            md_file = self.generate_markdown_report(summary_data)
            results['markdown'] = md_file
        except Exception as e:
            logger.error("markdown_generation_failed", error=str(e))
        
        # Generate PDF
        if 'markdown' in results:
            try:
                pdf_file = self.generate_pdf_report(results['markdown'])
                if pdf_file:
                    results['pdf'] = pdf_file
            except Exception as e:
                logger.error("pdf_generation_failed", error=str(e))
        
        logger.info("full_report_generated", files=list(results.keys()))
        return results

