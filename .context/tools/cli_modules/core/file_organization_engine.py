#!/usr/bin/env python3
"""
File Organization Engine - Движок автоматической организации файлов СЛК

Обеспечивает:
- Smart file placement - интеллектуальное размещение файлов
- Real-time monitoring - мониторинг в реальном времени
- Automatic cleanup - автоматическая очистка
- Rule-based organization - организация на основе правил

Версия: 1.0.0
Создано: 2025-01-15
"""

import os
import shutil
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import re
import mimetypes


class FileType(Enum):
    """Типы файлов для организации"""
    DOCUMENTATION = "documentation"
    CODE = "code"
    TEMPLATE = "template"
    CONFIGURATION = "configuration"
    TEMPORARY = "temporary"
    ARCHIVE = "archive"
    SYSTEM = "system"
    MEDIA = "media"
    UNKNOWN = "unknown"


class OrganizationAction(Enum):
    """Действия организации"""
    MOVE = "move"
    COPY = "copy"
    DELETE = "delete"
    RENAME = "rename"
    IGNORE = "ignore"
    ARCHIVE = "archive"


@dataclass
class FileInfo:
    """Информация о файле для анализа"""
    path: Path
    name: str
    extension: str
    size: int
    created_time: float
    modified_time: float
    file_type: FileType
    mime_type: Optional[str]
    content_hash: Optional[str]
    is_temporary: bool
    is_backup: bool
    parent_directory: str


@dataclass
class OrganizationRule:
    """Правило организации файлов"""
    name: str
    pattern: str
    file_types: List[FileType]
    target_directory: str
    action: OrganizationAction
    conditions: Dict[str, Any]
    priority: int
    enabled: bool


@dataclass
class OrganizationResult:
    """Результат операции организации"""
    processed_files: int
    moved_files: int
    deleted_files: int
    archived_files: int
    errors: List[str]
    warnings: List[str]
    execution_time: float
    rules_applied: List[str]
    space_freed: int


class FileOrganizationEngine:
    """Движок автоматической организации файлов"""
    
    def __init__(self, base_path: str = "."):
        """
        Инициализация движка
        
        Args:
            base_path: Путь к корню проекта СЛК
        """
        self.base_path = Path(base_path)
        self.config_file = self.base_path / ".slc" / "organization_config.json"
        self.log_file = self.base_path / ".slc" / "organization_log.json"
        
        # Загружаем конфигурацию и правила
        self.config = self._load_config()
        self.rules = self._load_organization_rules()
        
        # Инициализируем системы
        self.file_monitor = FileSystemMonitor(self.base_path)
        self.cleanup_system = AutoCleanupSystem(self.base_path)
        
        # Статистика
        self.stats = {
            "total_operations": 0,
            "files_organized": 0,
            "space_freed": 0,
            "last_cleanup": None
        }
    
    def organize_files(self, target_paths: List[str] = None, dry_run: bool = False) -> OrganizationResult:
        """
        Основной метод организации файлов
        
        Args:
            target_paths: Список путей для организации (None = весь проект)
            dry_run: Только анализ без реальных изменений
            
        Returns:
            Результат операции организации
        """
        start_time = time.time()
        result = OrganizationResult(
            processed_files=0,
            moved_files=0,
            deleted_files=0,
            archived_files=0,
            errors=[],
            warnings=[],
            execution_time=0,
            rules_applied=[],
            space_freed=0
        )
        
        try:
            print("🗂️  Запуск автоматической организации файлов...")
            
            # Определяем пути для обработки
            if target_paths is None:
                target_paths = [str(self.base_path)]
            
            # Сканируем файлы
            files_to_process = self._scan_files(target_paths)
            result.processed_files = len(files_to_process)
            
            print(f"📁 Найдено {len(files_to_process)} файлов для анализа")
            
            # Применяем правила организации
            for file_info in files_to_process:
                try:
                    action_result = self._apply_organization_rules(file_info, dry_run)
                    
                    if action_result:
                        rule_name, action, target_path = action_result
                        result.rules_applied.append(rule_name)
                        
                        if not dry_run:
                            success = self._execute_action(file_info, action, target_path)
                            if success:
                                self._update_counters(result, action, file_info.size)
                        else:
                            print(f"[DRY RUN] {action.value}: {file_info.path} -> {target_path}")
                            
                except Exception as e:
                    error_msg = f"Ошибка обработки {file_info.path}: {str(e)}"
                    result.errors.append(error_msg)
                    print(f"❌ {error_msg}")
            
            # Выполняем очистку
            cleanup_result = self.cleanup_system.perform_cleanup(dry_run=dry_run)
            result.deleted_files += cleanup_result.deleted_files
            result.space_freed += cleanup_result.space_freed
            
            result.execution_time = time.time() - start_time
            
            # Логируем результат
            self._log_operation(result, dry_run)
            
            print(f"✅ Организация завершена за {result.execution_time:.2f}с")
            print(f"   📊 Обработано: {result.processed_files} файлов")
            print(f"   📂 Перемещено: {result.moved_files} файлов")
            print(f"   🗑️  Удалено: {result.deleted_files} файлов")
            print(f"   💾 Освобождено: {self._format_size(result.space_freed)}")
            
            return result
            
        except Exception as e:
            result.errors.append(f"Критическая ошибка: {str(e)}")
            result.execution_time = time.time() - start_time
            return result
    
    def _scan_files(self, target_paths: List[str]) -> List[FileInfo]:
        """Сканирует файлы в указанных путях"""
        files = []
        
        for path_str in target_paths:
            path = Path(path_str)
            
            if path.is_file():
                file_info = self._analyze_file(path)
                if file_info:
                    files.append(file_info)
            elif path.is_dir():
                # Рекурсивно сканируем директорию
                for file_path in path.rglob("*"):
                    if file_path.is_file() and not self._should_ignore_file(file_path):
                        file_info = self._analyze_file(file_path)
                        if file_info:
                            files.append(file_info)
        
        return files
    
    def _analyze_file(self, file_path: Path) -> Optional[FileInfo]:
        """Анализирует отдельный файл"""
        try:
            stat = file_path.stat()
            mime_type = mimetypes.guess_type(str(file_path))[0]
            
            # Определяем тип файла
            file_type = self._classify_file_type(file_path, mime_type)
            
            # Генерируем хеш для небольших файлов
            content_hash = None
            if stat.st_size < 1024 * 1024:  # Файлы менее 1MB
                try:
                    with open(file_path, 'rb') as f:
                        content_hash = hashlib.md5(f.read()).hexdigest()
                except Exception:
                    pass
            
            return FileInfo(
                path=file_path,
                name=file_path.name,
                extension=file_path.suffix.lower(),
                size=stat.st_size,
                created_time=stat.st_ctime,
                modified_time=stat.st_mtime,
                file_type=file_type,
                mime_type=mime_type,
                content_hash=content_hash,
                is_temporary=self._is_temporary_file(file_path),
                is_backup=self._is_backup_file(file_path),
                parent_directory=str(file_path.parent.relative_to(self.base_path))
            )
            
        except Exception as e:
            print(f"⚠️  Ошибка анализа файла {file_path}: {e}")
            return None
    
    def _classify_file_type(self, file_path: Path, mime_type: Optional[str]) -> FileType:
        """Классифицирует тип файла"""
        name = file_path.name.lower()
        extension = file_path.suffix.lower()
        
        # Документация
        if extension in ['.md', '.txt', '.rst', '.textile'] or 'readme' in name:
            return FileType.DOCUMENTATION
        
        # Код
        if extension in ['.py', '.js', '.ts', '.json', '.yaml', '.yml', '.sh', '.bash']:
            return FileType.CODE
        
        # Шаблоны
        if 'template' in name or file_path.parent.name == 'templates':
            return FileType.TEMPLATE
        
        # Конфигурационные файлы
        if extension in ['.conf', '.cfg', '.ini', '.env'] or name.startswith('.'):
            return FileType.CONFIGURATION
        
        # Временные файлы
        if self._is_temporary_file(file_path):
            return FileType.TEMPORARY
        
        # Архивы
        if extension in ['.tar', '.gz', '.zip', '.rar', '.7z']:
            return FileType.ARCHIVE
        
        # Системные файлы
        if name.startswith('.') or extension in ['.log', '.pid', '.lock']:
            return FileType.SYSTEM
        
        # Медиа файлы
        if mime_type and mime_type.startswith(('image/', 'video/', 'audio/')):
            return FileType.MEDIA
        
        return FileType.UNKNOWN
    
    def _is_temporary_file(self, file_path: Path) -> bool:
        """Проверяет, является ли файл временным"""
        name = file_path.name.lower()
        
        temporary_patterns = [
            r'^temp_.*',
            r'^tmp_.*',
            r'^test_.*',
            r'.*\.tmp$',
            r'.*\.temp$',
            r'.*~$',
            r'^\.#.*',
            r'.*\.bak$',
            r'.*\.backup$'
        ]
        
        for pattern in temporary_patterns:
            if re.match(pattern, name):
                return True
        
        return False
    
    def _is_backup_file(self, file_path: Path) -> bool:
        """Проверяет, является ли файл backup'ом"""
        name = file_path.name.lower()
        
        backup_patterns = [
            r'^backup_.*',
            r'.*\.backup$',
            r'.*\.bak$',
            r'.*_backup\.',
            r'.*\.old$',
            r'.*\.orig$'
        ]
        
        for pattern in backup_patterns:
            if re.match(pattern, name):
                return True
        
        return False
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Проверяет, нужно ли игнорировать файл"""
        # Игнорируем файлы в .git, __pycache__, node_modules и т.д.
        ignore_dirs = {'.git', '__pycache__', 'node_modules', '.vscode', '.idea'}
        
        for parent in file_path.parents:
            if parent.name in ignore_dirs:
                return True
        
        # Игнорируем уже организованные системные директории
        if str(file_path).startswith('.slc/'):
            return True
        
        return False
    
    def _apply_organization_rules(self, file_info: FileInfo, dry_run: bool) -> Optional[Tuple[str, OrganizationAction, str]]:
        """Применяет правила организации к файлу"""
        
        # Сортируем правила по приоритету
        sorted_rules = sorted(self.rules, key=lambda r: r.priority, reverse=True)
        
        for rule in sorted_rules:
            if not rule.enabled:
                continue
            
            if self._rule_matches(rule, file_info):
                target_path = self._resolve_target_path(rule.target_directory, file_info)
                return rule.name, rule.action, target_path
        
        return None
    
    def _rule_matches(self, rule: OrganizationRule, file_info: FileInfo) -> bool:
        """Проверяет, соответствует ли файл правилу"""
        
        # Проверяем тип файла
        if file_info.file_type not in rule.file_types:
            return False
        
        # Проверяем паттерн имени
        if not re.match(rule.pattern, file_info.name):
            return False
        
        # Проверяем дополнительные условия
        for condition, value in rule.conditions.items():
            if condition == "min_size" and file_info.size < value:
                return False
            elif condition == "max_size" and file_info.size > value:
                return False
            elif condition == "extension" and file_info.extension not in value:
                return False
            elif condition == "max_age_days":
                age_days = (time.time() - file_info.modified_time) / (24 * 3600)
                if age_days < value:
                    return False
        
        return True
    
    def _resolve_target_path(self, target_template: str, file_info: FileInfo) -> str:
        """Разрешает целевой путь на основе шаблона"""
        
        # Подстановки
        replacements = {
            "{extension}": file_info.extension.lstrip('.'),
            "{file_type}": file_info.file_type.value,
            "{parent_dir}": file_info.parent_directory,
            "{year}": str(datetime.now().year),
            "{month}": str(datetime.now().month).zfill(2),
            "{day}": str(datetime.now().day).zfill(2)
        }
        
        target_path = target_template
        for placeholder, value in replacements.items():
            target_path = target_path.replace(placeholder, value)
        
        return target_path
    
    def _execute_action(self, file_info: FileInfo, action: OrganizationAction, target_path: str) -> bool:
        """Выполняет действие организации"""
        try:
            source_path = file_info.path
            target_full_path = self.base_path / target_path / file_info.name
            
            # Создаём целевую директорию если нужно
            target_full_path.parent.mkdir(parents=True, exist_ok=True)
            
            if action == OrganizationAction.MOVE:
                shutil.move(str(source_path), str(target_full_path))
                print(f"📂 Перемещён: {source_path} -> {target_full_path}")
                
            elif action == OrganizationAction.COPY:
                shutil.copy2(str(source_path), str(target_full_path))
                print(f"📄 Скопирован: {source_path} -> {target_full_path}")
                
            elif action == OrganizationAction.DELETE:
                source_path.unlink()
                print(f"🗑️  Удалён: {source_path}")
                
            elif action == OrganizationAction.ARCHIVE:
                archive_path = self.base_path / "archives" / f"{datetime.now().strftime('%Y-%m')}"
                archive_path.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source_path), str(archive_path / file_info.name))
                print(f"📦 Архивирован: {source_path} -> {archive_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка выполнения {action.value} для {file_info.path}: {e}")
            return False
    
    def _update_counters(self, result: OrganizationResult, action: OrganizationAction, file_size: int):
        """Обновляет счётчики результата"""
        if action == OrganizationAction.MOVE:
            result.moved_files += 1
        elif action == OrganizationAction.DELETE:
            result.deleted_files += 1
            result.space_freed += file_size
        elif action == OrganizationAction.ARCHIVE:
            result.archived_files += 1
    
    def _load_config(self) -> Dict:
        """Загружает конфигурацию системы организации"""
        default_config = {
            "auto_cleanup_enabled": True,
            "cleanup_interval_hours": 24,
            "backup_before_delete": True,
            "max_file_age_days": 30,
            "verbose_logging": True
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return {**default_config, **json.load(f)}
            except Exception:
                pass
        
        return default_config
    
    def _load_organization_rules(self) -> List[OrganizationRule]:
        """Загружает правила организации файлов"""
        
        # Базовые правила организации СЛК
        default_rules = [
            OrganizationRule(
                name="Move Documentation to docs/",
                pattern=r".*\.(md|txt|rst|textile)$",
                file_types=[FileType.DOCUMENTATION],
                target_directory="docs",
                action=OrganizationAction.MOVE,
                conditions={"extension": [".md", ".txt", ".rst", ".textile"]},
                priority=80,
                enabled=True
            ),
            OrganizationRule(
                name="Move temporary files to .slc/temp/",
                pattern=r"(temp_|tmp_|test_).*",
                file_types=[FileType.TEMPORARY],
                target_directory=".slc/temp",
                action=OrganizationAction.MOVE,
                conditions={},
                priority=90,
                enabled=True
            ),
            OrganizationRule(
                name="Archive old backup files",
                pattern=r".*(backup|\.bak|\.old).*",
                file_types=[FileType.ARCHIVE],
                target_directory="archives/backups",
                action=OrganizationAction.ARCHIVE,
                conditions={"max_age_days": 7},
                priority=85,
                enabled=True
            ),
            OrganizationRule(
                name="Delete ancient temporary files",
                pattern=r".*\.(tmp|temp)$",
                file_types=[FileType.TEMPORARY],
                target_directory="",
                action=OrganizationAction.DELETE,
                conditions={"max_age_days": 1},
                priority=95,
                enabled=True
            ),
            OrganizationRule(
                name="Move scripts to tools/scripts/",
                pattern=r".*\.(sh|bash|py)$",
                file_types=[FileType.CODE],
                target_directory="tools/scripts",
                action=OrganizationAction.MOVE,
                conditions={"extension": [".sh", ".bash", ".py"]},
                priority=70,
                enabled=False  # Disabled by default to avoid moving core files
            )
        ]
        
        return default_rules
    
    def _log_operation(self, result: OrganizationResult, dry_run: bool):
        """Логирует операцию организации"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "result": {
                "processed_files": result.processed_files,
                "moved_files": result.moved_files,
                "deleted_files": result.deleted_files,
                "archived_files": result.archived_files,
                "space_freed": result.space_freed,
                "execution_time": result.execution_time,
                "rules_applied": result.rules_applied,
                "errors": result.errors,
                "warnings": result.warnings
            }
        }
        
        # Записываем в лог файл
        log_entries = []
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    log_entries = json.load(f)
            except Exception:
                pass
        
        log_entries.append(log_entry)
        
        # Оставляем только последние 100 записей
        log_entries = log_entries[-100:]
        
        try:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(log_entries, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  Ошибка записи лога: {e}")
    
    def _format_size(self, size_bytes: int) -> str:
        """Форматирует размер в человекочитаемый вид"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def get_organization_stats(self) -> Dict:
        """Возвращает статистику организации"""
        return {
            "total_operations": self.stats["total_operations"],
            "files_organized": self.stats["files_organized"],
            "space_freed": self._format_size(self.stats["space_freed"]),
            "last_cleanup": self.stats["last_cleanup"],
            "rules_count": len(self.rules),
            "enabled_rules": len([r for r in self.rules if r.enabled])
        }


class FileSystemMonitor:
    """Мониторинг файловой системы в реальном времени"""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.watched_paths = set()
        self.callbacks = []
    
    def start_monitoring(self):
        """Запускает мониторинг (placeholder для будущего развития)"""
        print("🔍 Мониторинг файловой системы запущен")
    
    def stop_monitoring(self):
        """Останавливает мониторинг"""
        print("⏹️  Мониторинг файловой системы остановлен")


class AutoCleanupSystem:
    """Система автоматической очистки"""
    
    def __init__(self, base_path):
        self.base_path = Path(base_path) if isinstance(base_path, str) else base_path
    
    def perform_cleanup(self, dry_run: bool = False) -> OrganizationResult:
        """Выполняет автоматическую очистку"""
        
        result = OrganizationResult(
            processed_files=0,
            moved_files=0,
            deleted_files=0,
            archived_files=0,
            errors=[],
            warnings=[],
            execution_time=0,
            rules_applied=["auto_cleanup"],
            space_freed=0
        )
        
        # Находим временные файлы для удаления
        temp_files = []
        for pattern in ["*.tmp", "*.temp", ".*~", "test_*", "temp_*"]:
            temp_files.extend(self.base_path.glob(pattern))
        
        for temp_file in temp_files:
            if temp_file.is_file():
                try:
                    file_size = temp_file.stat().st_size
                    if not dry_run:
                        temp_file.unlink()
                        print(f"🧹 Удалён временный файл: {temp_file}")
                    else:
                        print(f"[DRY RUN] Удалить: {temp_file}")
                    
                    result.deleted_files += 1
                    result.space_freed += file_size
                    
                except Exception as e:
                    result.errors.append(f"Ошибка удаления {temp_file}: {str(e)}")
        
        result.processed_files = len(temp_files)
        return result


# Удобные функции для быстрого использования
def quick_organize(target_paths: List[str] = None, dry_run: bool = False) -> OrganizationResult:
    """Быстрая организация файлов"""
    engine = FileOrganizationEngine()
    return engine.organize_files(target_paths, dry_run)


def cleanup_project(dry_run: bool = False) -> OrganizationResult:
    """Быстрая очистка проекта"""
    engine = FileOrganizationEngine()
    cleanup = AutoCleanupSystem(engine.base_path)
    return cleanup.perform_cleanup(dry_run)


if __name__ == "__main__":
    # Простой CLI для тестирования
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        dry_run = "--dry-run" in sys.argv
        
        if command == "organize":
            result = quick_organize(dry_run=dry_run)
            print(f"\n✅ Организация завершена: {result.moved_files} файлов перемещено")
            
        elif command == "cleanup":
            result = cleanup_project(dry_run=dry_run)
            print(f"\n🧹 Очистка завершена: {result.deleted_files} файлов удалено")
            
        else:
            print("Использование: python file_organization_engine.py [organize|cleanup] [--dry-run]")
    else:
        # Запуск полной организации
        result = quick_organize(dry_run=True)
        print(f"\n📊 Анализ завершён: {result.processed_files} файлов проанализировано") 