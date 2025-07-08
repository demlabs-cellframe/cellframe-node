#!/usr/bin/env python3
"""
СЛК Автоматическая очистка файловой организации

Скрипт для поддержания правильной организации файлов в проекте СЛК.
Автоматически перемещает файлы в соответствующие директории согласно стандартам.

Версия: 1.0.0
Создано: 2025-01-15
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Tuple


class SLCFileOrganizer:
    """Автоматический организатор файлов СЛК"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.rules = self._define_organization_rules()
        self.moved_files = []
        self.deleted_files = []
        
    def _define_organization_rules(self) -> Dict[str, Dict]:
        """Определяет правила организации файлов"""
        return {
            "system_files": {
                "target_dir": ".slc",
                "patterns": [
                    "*.slc_usage_stats.json",
                    "changes.json",
                    "*.cache",
                    "*.tmp",
                    "evolution_state.json"
                ],
                "description": "Системные файлы СЛК"
            },
            
            "documentation": {
                "target_dir": "docs", 
                "patterns": [
                    "MIGRATION_*.md",
                    "REFACTORING_*.md", 
                    "RELEASE_NOTES_*.md",
                    "README_*.md",
                    "*WIKI*.md",
                    "NAVIGATION_*.md",
                    "DEPLOYMENT.md",
                    "*_guide.md",
                    "*_examples.md",
                    "*_methodology_*.md",
                    "profiling_*.md"
                ],
                "description": "Документация и руководства"
            },
            
            "scripts": {
                "target_dir": "tools/scripts",
                "patterns": [
                    "deploy_*.sh",
                    "backup_*.sh", 
                    "test_*.sh",
                    "setup_*.sh",
                    "install_*.sh"
                ],
                "description": "Скрипты развертывания и установки"
            },
            
            "archives": {
                "target_dir": "archives",
                "patterns": [
                    "backup_*.tar.gz",
                    "*.backup",
                    "*.archive",
                    "archive_*.json"
                ],
                "description": "Архивы и backup файлы"
            },
            
            "temp_files_to_delete": {
                "target_dir": None,  # Удалять, не перемещать
                "patterns": [
                    "test_*.md",
                    "test_*.json",
                    "test_*.slc-update",
                    "temp_*.json",
                    "*.temp",
                    ".DS_Store",
                    "Thumbs.db"
                ],
                "description": "Временные файлы для удаления"
            }
        }
    
    def ensure_directories_exist(self):
        """Создаёт необходимые директории если их нет"""
        required_dirs = [
            ".slc", "docs", "archives", 
            "tools/scripts", "tasks/archives"
        ]
        
        for dir_path in required_dirs:
            full_path = self.base_path / dir_path
            if not full_path.exists():
                full_path.mkdir(parents=True, exist_ok=True)
                print(f"📁 Создана директория: {dir_path}")
    
    def scan_and_organize(self, dry_run: bool = False) -> Tuple[int, int]:
        """
        Сканирует корневую директорию и организует файлы
        
        Args:
            dry_run: Если True, только показывает что будет сделано
            
        Returns:
            Tuple of (moved_files_count, deleted_files_count)
        """
        moved_count = 0
        deleted_count = 0
        
        # Получаем список файлов в корне
        root_files = [f for f in self.base_path.iterdir() 
                     if f.is_file() and not f.name.startswith('.git')]
        
        print(f"🔍 Найдено {len(root_files)} файлов в корневой директории")
        
        for file_path in root_files:
            target_action = self._determine_action(file_path)
            
            if target_action["action"] == "move":
                if dry_run:
                    print(f"📦 [DRY RUN] Переместил бы: {file_path.name} → {target_action['target']}")
                else:
                    self._move_file(file_path, target_action["target"])
                    moved_count += 1
                    
            elif target_action["action"] == "delete":
                if dry_run:
                    print(f"🗑️  [DRY RUN] Удалил бы: {file_path.name}")
                else:
                    self._delete_file(file_path)
                    deleted_count += 1
                    
            elif target_action["action"] == "keep":
                print(f"✅ Оставляю в корне: {file_path.name}")
        
        return moved_count, deleted_count
    
    def _determine_action(self, file_path: Path) -> Dict[str, str]:
        """Определяет действие для файла"""
        file_name = file_path.name
        
        # Файлы которые должны остаться в корне
        keep_in_root = {
            "README.md", "VERSION", ".gitignore", 
            "LICENSE", "CHANGELOG.md"
        }
        
        if file_name in keep_in_root:
            return {"action": "keep", "reason": "Should stay in root"}
        
        # Проверяем правила организации
        for rule_name, rule_config in self.rules.items():
            if self._matches_patterns(file_name, rule_config["patterns"]):
                if rule_config["target_dir"] is None:
                    return {"action": "delete", "reason": f"Temp file: {rule_name}"}
                else:
                    return {
                        "action": "move",
                        "target": rule_config["target_dir"],
                        "reason": rule_config["description"]
                    }
        
        # Неизвестный файл - предупреждение
        print(f"⚠️  Неизвестный файл в корне: {file_name}")
        return {"action": "keep", "reason": "Unknown file type"}
    
    def _matches_patterns(self, filename: str, patterns: List[str]) -> bool:
        """Проверяет соответствие файла паттернам"""
        import fnmatch
        return any(fnmatch.fnmatch(filename, pattern) for pattern in patterns)
    
    def _move_file(self, source: Path, target_dir: str):
        """Перемещает файл в целевую директорию"""
        target_path = self.base_path / target_dir / source.name
        
        try:
            # Создаём директорию если нужно
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Перемещаем файл
            shutil.move(str(source), str(target_path))
            self.moved_files.append((str(source), str(target_path)))
            print(f"📦 Перемещён: {source.name} → {target_dir}/")
            
        except Exception as e:
            print(f"❌ Ошибка перемещения {source.name}: {e}")
    
    def _delete_file(self, file_path: Path):
        """Удаляет файл"""
        try:
            file_path.unlink()
            self.deleted_files.append(str(file_path))
            print(f"🗑️  Удалён: {file_path.name}")
        except Exception as e:
            print(f"❌ Ошибка удаления {file_path.name}: {e}")
    
    def generate_report(self) -> Dict:
        """Генерирует отчёт о проделанной работе"""
        return {
            "timestamp": "2025-01-15T21:20:00Z",
            "moved_files": len(self.moved_files),
            "deleted_files": len(self.deleted_files), 
            "moved_details": self.moved_files,
            "deleted_details": self.deleted_files,
            "status": "completed"
        }
    
    def save_report(self, report: Dict):
        """Сохраняет отчёт о работе"""
        report_path = self.base_path / ".slc" / "last_cleanup_report.json"
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"📊 Отчёт сохранён: {report_path}")
        except Exception as e:
            print(f"❌ Ошибка сохранения отчёта: {e}")


def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description="СЛК автоматическая очистка файлов")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Показать что будет сделано без реальных изменений")
    parser.add_argument("--path", default=".", 
                       help="Путь к проекту СЛК (по умолчанию: текущая директория)")
    
    args = parser.parse_args()
    
    print("🧹 СЛК Автоматическая очистка файловой организации")
    print("=" * 50)
    
    organizer = SLCFileOrganizer(args.path)
    
    # Создаём необходимые директории
    organizer.ensure_directories_exist()
    
    # Выполняем организацию
    moved_count, deleted_count = organizer.scan_and_organize(dry_run=args.dry_run)
    
    # Генерируем отчёт
    if not args.dry_run:
        report = organizer.generate_report()
        organizer.save_report(report)
        
        print("\n" + "=" * 50)
        print(f"✅ Очистка завершена!")
        print(f"📦 Перемещено файлов: {moved_count}")
        print(f"🗑️  Удалено файлов: {deleted_count}")
    else:
        print("\n" + "=" * 50)
        print("🔍 DRY RUN - изменения не применены")
        print("Запустите без --dry-run для применения изменений")


if __name__ == "__main__":
    main() 