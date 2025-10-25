#!/usr/bin/env python3
"""
🏗️ Автоматическое поддержание архитектурных правил SLC Agent
Следит за чистотой корневой директории и автоматически перемещает нарушающие файлы
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class ArchitectureEnforcer:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path).resolve()
        self.context_path = self.root_path / ".context"
        self.temp_path = self.context_path / "temp"
        self.docs_path = self.context_path / "docs"
        self.archives_path = self.context_path / "archives"
        
        # Архитектурные правила
        self.allowed_in_root = {
            ".cursorrules",
            "slc", 
            ".context",
            ".git",
            ".gitignore",
            "README.md",
            "VERSION",
            # Системные директории (допустимы)
            ".cursor",
            "slc-agent",
            ".pytest_cache",
            ".benchmarks",
            "venv",
            ".venv"
        }
        
        self.forbidden_patterns = {
            "*.json": self.temp_path,
            "*.md": self.docs_path,
            "*.txt": self.temp_path,
            "*.log": self.temp_path,
            "*.backup": self.archives_path,
            "*.tar.gz": self.archives_path,
            "test_*": self.temp_path,
            "deploy_*": self.context_path / "tools" / "scripts",
            "*_REPORT.md": self.docs_path / "reports"
        }
        
        self.violations = []
        self.actions_taken = []
        
    def ensure_directories(self):
        """Создает необходимые директории если их нет"""
        for path in [self.temp_path, self.docs_path, self.archives_path]:
            path.mkdir(parents=True, exist_ok=True)
            
    def scan_violations(self) -> List[Dict[str, Any]]:
        """Сканирует корневую директорию на нарушения"""
        violations = []
        
        for item in self.root_path.iterdir():
            if item.name.startswith('.') and item.name not in self.allowed_in_root:
                if item.name not in [".cursor", ".pytest_cache", ".benchmarks", ".venv", "venv"]:
                    violations.append({
                        "path": item,
                        "name": item.name,
                        "type": "hidden_file_or_dir",
                        "target": self.temp_path,
                        "reason": "Скрытые файлы должны быть в .context/temp/"
                    })
                    
            elif item.name not in self.allowed_in_root:
                # Проверяем паттерны
                target = self._get_target_for_item(item)
                if target:
                    violations.append({
                        "path": item,
                        "name": item.name,
                        "type": "misplaced_file",
                        "target": target,
                        "reason": f"Файл должен быть в {target.relative_to(self.root_path)}"
                    })
                    
        return violations
        
    def _get_target_for_item(self, item: Path) -> Path:
        """Определяет целевую директорию для файла"""
        name = item.name.lower()
        
        if name.endswith('.json'):
            return self.temp_path
        elif name.endswith('.md') and name != 'readme.md':
            if 'report' in name:
                return self.docs_path / "reports"
            return self.docs_path
        elif name.endswith(('.txt', '.log')):
            return self.temp_path
        elif name.endswith(('.backup', '.tar.gz', '.zip')):
            return self.archives_path
        elif name.startswith('test_'):
            return self.temp_path
        elif name.startswith('deploy_'):
            return self.context_path / "tools" / "scripts"
            
        return None
        
    def fix_violations(self, violations: List[Dict[str, Any]], dry_run: bool = False) -> List[str]:
        """Исправляет нарушения архитектурных правил"""
        actions = []
        
        for violation in violations:
            source = violation["path"]
            target_dir = violation["target"]
            target_path = target_dir / source.name
            
            # Избегаем конфликтов имен
            if target_path.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                stem = target_path.stem
                suffix = target_path.suffix
                target_path = target_dir / f"{stem}_{timestamp}{suffix}"
                
            action = f"MOVE: {source.relative_to(self.root_path)} → {target_path.relative_to(self.root_path)}"
            actions.append(action)
            
            if not dry_run:
                target_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source), str(target_path))
                
        return actions
        
    def generate_report(self, violations: List[Dict[str, Any]], actions: List[str]) -> Dict[str, Any]:
        """Генерирует отчет о проведенной работе"""
        return {
            "timestamp": datetime.now().isoformat(),
            "root_directory": str(self.root_path),
            "scan_results": {
                "total_items": len(list(self.root_path.iterdir())),
                "violations_found": len(violations),
                "actions_taken": len(actions)
            },
            "violations": [
                {
                    "file": v["name"],
                    "type": v["type"],
                    "reason": v["reason"],
                    "target": str(v["target"].relative_to(self.root_path))
                }
                for v in violations
            ],
            "actions": actions,
            "architecture_compliance": {
                "allowed_items": list(self.allowed_in_root),
                "current_status": "COMPLIANT" if len(violations) == 0 else "VIOLATIONS_FOUND"
            }
        }
        
    def run(self, dry_run: bool = False, verbose: bool = False) -> Dict[str, Any]:
        """Основная функция - запуск проверки и исправления"""
        if verbose:
            print("🏗️ Проверка архитектурных правил SLC Agent...")
            
        self.ensure_directories()
        violations = self.scan_violations()
        
        if verbose:
            print(f"📊 Найдено нарушений: {len(violations)}")
            
        actions = []
        if violations:
            actions = self.fix_violations(violations, dry_run=dry_run)
            if verbose:
                print(f"🔧 Действий выполнено: {len(actions)}")
                for action in actions:
                    print(f"   {action}")
                    
        report = self.generate_report(violations, actions)
        
        if verbose:
            status = "✅ СООТВЕТСТВУЕТ" if len(violations) == 0 else "⚠️ ИСПРАВЛЕНО"
            print(f"🎯 Статус: {status}")
            
        return report

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Поддержание архитектурных правил SLC Agent")
    parser.add_argument("--dry-run", action="store_true", help="Только показать что будет сделано")
    parser.add_argument("--verbose", "-v", action="store_true", help="Подробный вывод")
    parser.add_argument("--json", action="store_true", help="JSON вывод для AI интеграции")
    
    args = parser.parse_args()
    
    enforcer = ArchitectureEnforcer()
    report = enforcer.run(dry_run=args.dry_run, verbose=args.verbose)
    
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif not args.verbose:
        violations = len(report["violations"])
        actions = len(report["actions"])
        if violations == 0:
            print("✅ Архитектурные правила соблюдены")
        else:
            print(f"⚠️ Найдено {violations} нарушений, выполнено {actions} действий")

if __name__ == "__main__":
    main() 