#!/usr/bin/env python3
"""
🔄 Cellframe Migration CLI

Command-line interface for migrating from legacy to modern Python Cellframe API.

Usage:
    python -m cellframe.migration analyze /path/to/project
    python -m cellframe.migration migrate /path/to/old_project /path/to/new_project
    python -m cellframe.migration config /path/to/config.json /path/to/config.py
    python -m cellframe.migration guide /path/to/project

Examples:
    # Analyze legacy code
    python -m cellframe.migration analyze my_old_project/
    
    # Migrate project
    python -m cellframe.migration migrate my_old_project/ my_new_project/
    
    # Migrate configuration
    python -m cellframe.migration config old_config.json new_config.py
    
    # Generate migration guide
    python -m cellframe.migration guide my_old_project/ > migration_guide.md
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from . import analyze_code, migrate_code, generate_migration_guide
    from .config_migration import migrate_config, validate_config, analyze_config
except ImportError:
    # Fallback for direct execution
    from cellframe.migration import analyze_code, migrate_code, generate_migration_guide
    from cellframe.migration.config_migration import migrate_config, validate_config, analyze_config


def cmd_analyze(args):
    """Analyze project for legacy API usage"""
    project_path = Path(args.project_path)
    
    if not project_path.exists():
        logger.error(f"Project path does not exist: {project_path}")
        return 1
    
    if not project_path.is_dir():
        logger.error(f"Project path is not a directory: {project_path}")
        return 1
    
    logger.info(f"Analyzing project: {project_path}")
    
    try:
        report = analyze_code(str(project_path))
        
        # Print summary
        print(f"\n🔍 Analysis Results for: {project_path}")
        print("=" * 60)
        print(f"Files analyzed: {report.files_analyzed}")
        print(f"Issues found: {len(report.issues_found)}")
        
        if report.issues_found:
            print("\n📊 Issues by Type:")
            summary = report.get_summary()
            for issue_type, count in summary['by_type'].items():
                print(f"  {issue_type}: {count}")
            
            print("\n📊 Issues by Migration Level:")
            for level, count in summary['by_level'].items():
                print(f"  {level}: {count}")
            
            print("\n💡 Recommendations:")
            for rec in report.recommendations:
                print(f"  • {rec}")
            
            if args.detailed:
                print("\n📋 Detailed Issues:")
                for issue in report.issues_found:
                    print(f"\n  {issue.file_path}:{issue.line_number}")
                    print(f"    Type: {issue.issue_type}")
                    print(f"    Level: {issue.migration_level.value}")
                    print(f"    Old: {issue.old_code}")
                    print(f"    Fix: {issue.suggested_fix}")
        else:
            print("\n✅ No legacy API usage found! Your code is already modern.")
        
        # Save report if requested
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w') as f:
                f.write(f"# Analysis Report for {project_path}\n\n")
                f.write(f"Files analyzed: {report.files_analyzed}\n")
                f.write(f"Issues found: {len(report.issues_found)}\n\n")
                
                if report.issues_found:
                    f.write("## Issues by Type\n\n")
                    for issue_type, count in summary['by_type'].items():
                        f.write(f"- {issue_type}: {count}\n")
                    
                    f.write("\n## Detailed Issues\n\n")
                    for issue in report.issues_found:
                        f.write(f"### {issue.file_path}:{issue.line_number}\n")
                        f.write(f"- **Type:** {issue.issue_type}\n")
                        f.write(f"- **Level:** {issue.migration_level.value}\n")
                        f.write(f"- **Old:** `{issue.old_code}`\n")
                        f.write(f"- **Fix:** `{issue.suggested_fix}`\n\n")
            
            print(f"\n📄 Report saved to: {output_path}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return 1


def cmd_migrate(args):
    """Migrate project from legacy to modern API"""
    source_path = Path(args.source_path)
    target_path = Path(args.target_path)
    
    if not source_path.exists():
        logger.error(f"Source path does not exist: {source_path}")
        return 1
    
    if not source_path.is_dir():
        logger.error(f"Source path is not a directory: {source_path}")
        return 1
    
    if target_path.exists() and not args.force:
        logger.error(f"Target path already exists: {target_path}")
        logger.error("Use --force to overwrite")
        return 1
    
    logger.info(f"Migrating project: {source_path} -> {target_path}")
    
    try:
        # First analyze
        report = analyze_code(str(source_path))
        
        if not report.issues_found and not args.force:
            print("✅ No legacy API usage found. Migration not needed.")
            return 0
        
        # Perform migration
        success = migrate_code(str(source_path), str(target_path), report)
        
        if success:
            print(f"\n🎉 Migration completed successfully!")
            print(f"📁 Target project: {target_path}")
            print(f"📄 Migration report: {target_path}/MIGRATION_REPORT.md")
            
            # Show migration summary
            summary = report.get_summary()
            print(f"\n📊 Migration Summary:")
            print(f"  Files processed: {report.files_analyzed}")
            print(f"  Issues migrated: {len(report.issues_found)}")
            
            for level, count in summary['by_level'].items():
                if count > 0:
                    print(f"  {level} level fixes: {count}")
            
            print(f"\n💡 Next Steps:")
            print(f"  1. Review migrated code in {target_path}")
            print(f"  2. Test the migrated application")
            print(f"  3. Address any manual migration items")
            print(f"  4. Update documentation and dependencies")
            
            return 0
        else:
            logger.error("Migration failed")
            return 1
            
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return 1


def cmd_config(args):
    """Migrate configuration from JSON to Python"""
    source_path = Path(args.source_config)
    target_path = Path(args.target_config)
    
    if not source_path.exists():
        logger.error(f"Source config does not exist: {source_path}")
        return 1
    
    if target_path.exists() and not args.force:
        logger.error(f"Target config already exists: {target_path}")
        logger.error("Use --force to overwrite")
        return 1
    
    logger.info(f"Migrating configuration: {source_path} -> {target_path}")
    
    try:
        # Validate source config first
        issues = validate_config(str(source_path))
        
        if issues:
            critical_errors = [i for i in issues if i.severity == 'error']
            if critical_errors:
                print(f"❌ Critical errors in source configuration:")
                for error in critical_errors:
                    print(f"  • {error.description}")
                return 1
            
            warnings = [i for i in issues if i.severity == 'warning']
            if warnings:
                print(f"⚠️  Warnings in source configuration:")
                for warning in warnings:
                    print(f"  • {warning.description}")
        
        # Perform migration
        success = migrate_config(str(source_path), str(target_path))
        
        if success:
            print(f"\n🎉 Configuration migrated successfully!")
            print(f"📁 Target config: {target_path}")
            print(f"📄 Migration report: {target_path.parent}/{target_path.stem}_migration_report.md")
            
            print(f"\n💡 Next Steps:")
            print(f"  1. Review migrated configuration")
            print(f"  2. Test with your application")
            print(f"  3. Update your code to use new config")
            
            return 0
        else:
            logger.error("Configuration migration failed")
            return 1
            
    except Exception as e:
        logger.error(f"Configuration migration failed: {e}")
        return 1


def cmd_guide(args):
    """Generate migration guide"""
    project_path = Path(args.project_path)
    
    if not project_path.exists():
        logger.error(f"Project path does not exist: {project_path}")
        return 1
    
    if not project_path.is_dir():
        logger.error(f"Project path is not a directory: {project_path}")
        return 1
    
    logger.info(f"Generating migration guide for: {project_path}")
    
    try:
        report = analyze_code(str(project_path))
        guide = generate_migration_guide(report)
        
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w') as f:
                f.write(guide)
            print(f"📄 Migration guide saved to: {output_path}")
        else:
            print(guide)
        
        return 0
        
    except Exception as e:
        logger.error(f"Guide generation failed: {e}")
        return 1


def cmd_validate(args):
    """Validate configuration file"""
    config_path = Path(args.config_path)
    
    if not config_path.exists():
        logger.error(f"Config file does not exist: {config_path}")
        return 1
    
    logger.info(f"Validating configuration: {config_path}")
    
    try:
        issues = validate_config(str(config_path))
        
        if not issues:
            print(f"✅ Configuration is valid: {config_path}")
            return 0
        
        print(f"❌ Configuration issues found: {config_path}")
        
        errors = [i for i in issues if i.severity == 'error']
        warnings = [i for i in issues if i.severity == 'warning']
        
        if errors:
            print(f"\n🚨 Errors ({len(errors)}):")
            for error in errors:
                print(f"  • {error.description}")
                print(f"    Location: {error.location}")
                print(f"    Fix: {error.suggested_fix}")
        
        if warnings:
            print(f"\n⚠️  Warnings ({len(warnings)}):")
            for warning in warnings:
                print(f"  • {warning.description}")
                print(f"    Location: {warning.location}")
                print(f"    Fix: {warning.suggested_fix}")
        
        return 1 if errors else 0
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Cellframe Migration Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '-v', '--verbose', 
        action='store_true',
        help='Enable verbose logging'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser(
        'analyze', 
        help='Analyze project for legacy API usage'
    )
    analyze_parser.add_argument(
        'project_path', 
        help='Path to project directory'
    )
    analyze_parser.add_argument(
        '-d', '--detailed',
        action='store_true',
        help='Show detailed issue list'
    )
    analyze_parser.add_argument(
        '-o', '--output',
        help='Save report to file'
    )
    analyze_parser.set_defaults(func=cmd_analyze)
    
    # Migrate command
    migrate_parser = subparsers.add_parser(
        'migrate',
        help='Migrate project from legacy to modern API'
    )
    migrate_parser.add_argument(
        'source_path',
        help='Source project directory'
    )
    migrate_parser.add_argument(
        'target_path', 
        help='Target project directory'
    )
    migrate_parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite target directory if exists'
    )
    migrate_parser.set_defaults(func=cmd_migrate)
    
    # Config command
    config_parser = subparsers.add_parser(
        'config',
        help='Migrate configuration from JSON to Python'
    )
    config_parser.add_argument(
        'source_config',
        help='Source JSON configuration file'
    )
    config_parser.add_argument(
        'target_config',
        help='Target Python configuration file'
    )
    config_parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite target file if exists'
    )
    config_parser.set_defaults(func=cmd_config)
    
    # Guide command
    guide_parser = subparsers.add_parser(
        'guide',
        help='Generate migration guide'
    )
    guide_parser.add_argument(
        'project_path',
        help='Path to project directory'
    )
    guide_parser.add_argument(
        '-o', '--output',
        help='Save guide to file'
    )
    guide_parser.set_defaults(func=cmd_guide)
    
    # Validate command
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate configuration file'
    )
    validate_parser.add_argument(
        'config_path',
        help='Path to configuration file'
    )
    validate_parser.set_defaults(func=cmd_validate)
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if args.verbose:
            raise
        return 1


if __name__ == '__main__':
    sys.exit(main()) 