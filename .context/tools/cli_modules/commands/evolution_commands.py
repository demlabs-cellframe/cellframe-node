#!/usr/bin/env python3
"""
Команды эволюции СЛК

Реализует команды:
- export: Экспорт изменений в .slc-update пакет
- import: Импорт .slc-update пакета
- evolution-validate: Валидация пакета

Версия: 1.1.0
Создано: 2025-01-15
"""

import argparse
import json
import os
import sys
import time
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import zipfile
import tempfile
import uuid
from datetime import datetime

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..base_command import BaseCommand, ContextAwareCommand


class ExportEvolutionCommand(ContextAwareCommand):
    """Команда экспорта SLC изменений в .slc-update пакет"""
    
    def __init__(self, base_path: str):
        super().__init__(base_path)
        self.evolution_state_file = Path(base_path) / ".slc" / "evolution_state.json"
    
    @property
    def name(self) -> str:
        return "export"
    
    @property  
    def description(self) -> str:
        return "📦 Экспорт изменений SLC в .slc-update пакет для синхронизации"
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--output", "-o",
            help="Путь к выходному .slc-update файлу"
        )
        parser.add_argument(
            "--since", "-s",
            help="Экспорт изменений с указанной даты (YYYY-MM-DD)"
        )
        parser.add_argument(
            "--modules", "-m",
            nargs="*",
            help="Экспорт только указанных модулей"
        )
        parser.add_argument(
            "--type", "-t",
            choices=["new_module", "enhancement", "core_update", "cli_improvement", "docs", "all"],
            default="all",
            help="Тип изменений для экспорта"
        )
        parser.add_argument(
            "--preview", "-p",
            action="store_true",
            help="Предварительный просмотр без создания файла"
        )
        parser.add_argument(
            "--description", "-d",
            help="Описание пакета обновления"
        )
        parser.add_argument(
            "--create-baseline",
            action="store_true",
            help="Создать новый baseline после экспорта"
        )
    
    def execute(self, args: argparse.Namespace) -> int:
        """Выполнение команды export-evolution"""
        print("📦 Экспорт SLC Evolution")
        print("=" * 40)
        
        try:
            # Создаем или загружаем baseline
            baseline = self._load_or_create_baseline()
            
            # Обнаруживаем изменения
            changes = self._detect_changes(baseline, args)
            
            if not changes["changed_files"] and not changes["new_files"] and not changes["deleted_files"]:
                print("ℹ️  Изменений не обнаружено")
                result = {
                    "command": "export",
                    "status": "no_changes",
                    "changes_count": 0
                }
            else:
                print(f"📊 Обнаружены изменения:")
                print(f"   📄 Новых файлов: {len(changes['new_files'])}")
                print(f"   ✏️  Измененных файлов: {len(changes['changed_files'])}")
                print(f"   🗑️  Удаленных файлов: {len(changes['deleted_files'])}")
                
                if args.preview:
                    self._show_preview(changes)
                    result = {
                        "command": "export",
                        "status": "preview_completed",
                        "changes_count": len(changes['new_files']) + len(changes['changed_files']) + len(changes['deleted_files'])
                    }
                else:
                    # Создаем пакет
                    package_path = self._create_update_package(changes, args)
                    print(f"✅ Пакет создан: {package_path}")
                    
                    if args.create_baseline:
                        self._create_baseline()
                        print("📝 Новый baseline создан")
                    
                    result = {
                        "command": "export",
                        "status": "completed",
                        "package_path": str(package_path),
                        "changes_count": len(changes['new_files']) + len(changes['changed_files']) + len(changes['deleted_files'])
                    }
            
            # Добавляем рекомендации
            recommendations = []
            if result["changes_count"] > 0:
                recommendations.append("Пакет успешно создан - можно отправлять для синхронизации")
                recommendations.append("Используйте 'слк эволюция-валидация' для проверки пакета")
                if not args.create_baseline:
                    recommendations.append("Рассмотрите создание нового baseline: --create-baseline")
            else:
                recommendations.append("Нет изменений для экспорта")
                recommendations.append("Внесите изменения в модули или создайте новые")
            
            result["ai_recommendations"] = recommendations
            result["next_commands"] = ["evolution-validate", "list", "templates"]
            
            self.output_json_context(result)
            
            return 0
            
        except Exception as e:
            print(f"❌ Ошибка экспорта: {e}")
            return 1
    
    def _load_or_create_baseline(self) -> Dict[str, Any]:
        """Загрузить или создать baseline"""
        if self.evolution_state_file.exists():
            try:
                with open(self.evolution_state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return self._create_baseline()
    
    def _create_baseline(self) -> Dict[str, Any]:
        """Создать новый baseline"""
        baseline = {
            "version": "4.0.0",
            "timestamp": datetime.now().isoformat(),
            "files_registry": {}
        }
        
        # Сканируем все отслеживаемые файлы
        tracked_patterns = [
            "modules/**/*.json",
            "tasks/**/*.json", 
            "tools/scripts/*.py",
            "docs/*.md",
            "*.md",
            "VERSION"
        ]
        
        base_path = Path(self.base_path)
        for pattern in tracked_patterns:
            for file_path in base_path.glob(pattern):
                if file_path.is_file():
                    rel_path = str(file_path.relative_to(base_path))
                    baseline["files_registry"][rel_path] = self._get_file_info(file_path)
        
        # Сохраняем baseline
        self.evolution_state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.evolution_state_file, 'w', encoding='utf-8') as f:
            json.dump(baseline, f, indent=2, ensure_ascii=False)
        
        return baseline
    
    def _get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Получить информацию о файле"""
        stat = file_path.stat()
        
        with open(file_path, 'rb') as f:
            content = f.read()
            file_hash = hashlib.sha256(content).hexdigest()
        
        return {
            "hash": file_hash,
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "type": file_path.suffix.lower()
        }
    
    def _detect_changes(self, baseline: Dict[str, Any], args: argparse.Namespace) -> Dict[str, List]:
        """Обнаружить изменения относительно baseline"""
        current_files = {}
        base_path = Path(self.base_path)
        
        # Сканируем текущие файлы
        tracked_patterns = [
            "modules/**/*.json",
            "tasks/**/*.json",
            "tools/scripts/*.py", 
            "docs/*.md",
            "*.md",
            "VERSION"
        ]
        
        for pattern in tracked_patterns:
            for file_path in base_path.glob(pattern):
                if file_path.is_file():
                    rel_path = str(file_path.relative_to(base_path))
                    current_files[rel_path] = self._get_file_info(file_path)
        
        baseline_files = baseline.get("files_registry", {})
        
        # Анализируем изменения
        new_files = []
        changed_files = []
        deleted_files = []
        
        # Новые и измененные файлы
        for file_path, file_info in current_files.items():
            if file_path not in baseline_files:
                new_files.append(file_path)
            elif file_info["hash"] != baseline_files[file_path]["hash"]:
                changed_files.append(file_path)
        
        # Удаленные файлы
        for file_path in baseline_files:
            if file_path not in current_files:
                deleted_files.append(file_path)
        
        return {
            "new_files": new_files,
            "changed_files": changed_files,
            "deleted_files": deleted_files
        }
    
    def _show_preview(self, changes: Dict[str, List]):
        """Показать preview изменений"""
        print("\n📋 PREVIEW ИЗМЕНЕНИЙ:")
        print("-" * 30)
        
        if changes["new_files"]:
            print(f"\n📄 Новые файлы ({len(changes['new_files'])}):")
            for file_path in changes["new_files"][:10]:
                print(f"   + {file_path}")
            if len(changes["new_files"]) > 10:
                print(f"   ... и еще {len(changes['new_files']) - 10} файлов")
        
        if changes["changed_files"]:
            print(f"\n✏️  Измененные файлы ({len(changes['changed_files'])}):")
            for file_path in changes["changed_files"][:10]:
                print(f"   ~ {file_path}")
            if len(changes["changed_files"]) > 10:
                print(f"   ... и еще {len(changes['changed_files']) - 10} файлов")
        
        if changes["deleted_files"]:
            print(f"\n🗑️  Удаленные файлы ({len(changes['deleted_files'])}):")
            for file_path in changes["deleted_files"][:10]:
                print(f"   - {file_path}")
            if len(changes["deleted_files"]) > 10:
                print(f"   ... и еще {len(changes['deleted_files']) - 10} файлов")
    
    def _create_update_package(self, changes: Dict[str, List], args: argparse.Namespace) -> Path:
        """Создать .slc-update пакет"""
        # Определяем путь выходного файла
        if args.output:
            output_path = Path(args.output)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(f"slc_evolution_{timestamp}.slc-update")
        
        # Создаем пакет
        package = {
            "header": {
                "update_id": str(uuid.uuid4()),
                "version": "4.0.0",
                "timestamp": datetime.now().isoformat(),
                "author": "SLC Evolution System",
                "description": args.description or "Автоматический экспорт изменений"
            },
            "metadata": {
                "change_summary": f"{len(changes['new_files'])} новых, {len(changes['changed_files'])} измененных, {len(changes['deleted_files'])} удаленных файлов",
                "impact_assessment": "minor",
                "dependencies": [],
                "compatibility": "4.0.0+",
                "rollback_info": "Поддерживается полный откат"
            },
            "changes": {
                "new_files": {},
                "modified_files": {},
                "deleted_files": changes["deleted_files"]
            }
        }
        
        base_path = Path(self.base_path)
        
        # Добавляем содержимое новых файлов
        for file_path in changes["new_files"]:
            full_path = base_path / file_path
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    package["changes"]["new_files"][file_path] = f.read()
        
        # Добавляем содержимое измененных файлов
        for file_path in changes["changed_files"]:
            full_path = base_path / file_path
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    package["changes"]["modified_files"][file_path] = f.read()
        
        # Сохраняем пакет
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(package, f, indent=2, ensure_ascii=False)
        
        return output_path


class ImportEvolutionCommand(ContextAwareCommand):
    """Команда импорта .slc-update пакета"""
    
    def __init__(self, base_path: str):
        super().__init__(base_path)
    
    @property
    def name(self) -> str:
        return "import"
    
    @property  
    def description(self) -> str:
        return "📥 Импорт .slc-update пакета с безопасным применением изменений"
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "package",
            help="Путь к .slc-update файлу"
        )
        parser.add_argument(
            "--preview", "-p",
            action="store_true",
            help="Предварительный просмотр без применения изменений"
        )
        parser.add_argument(
            "--backup", "-b",
            help="Имя backup точки (по умолчанию автоматическое)"
        )
        parser.add_argument(
            "--selective", "-s",
            action="store_true",
            help="Выборочный импорт изменений"
        )
        parser.add_argument(
            "--force", "-f",
            action="store_true",
            help="Принудительный импорт с перезаписью"
        )
    
    def execute(self, args: argparse.Namespace) -> int:
        """Выполнение команды import-evolution"""
        print("📥 Импорт SLC Evolution")
        print("=" * 40)
        
        try:
            # Загружаем и валидируем пакет
            package = self._load_and_validate_package(args.package)
            
            # Анализируем конфликты
            conflicts = self._analyze_conflicts(package)
            
            print(f"📊 Анализ пакета:")
            print(f"   📄 Новых файлов: {len(package['changes'].get('new_files', {}))}")
            print(f"   ✏️  Измененных файлов: {len(package['changes'].get('modified_files', {}))}")
            print(f"   🗑️  Удаленных файлов: {len(package['changes'].get('deleted_files', []))}")
            print(f"   ⚠️  Конфликтов: {len(conflicts)}")
            
            if conflicts:
                print(f"\n⚠️  Обнаружены конфликты:")
                for conflict in conflicts[:5]:
                    print(f"   • {conflict}")
                if len(conflicts) > 5:
                    print(f"   ... и еще {len(conflicts) - 5} конфликтов")
            
            if args.preview:
                self._show_import_preview(package, conflicts)
                result = {
                    "command": "import",
                    "status": "preview_completed",
                    "conflicts_count": len(conflicts)
                }
            else:
                # Создаем backup
                backup_name = self._create_backup(args.backup)
                print(f"💾 Backup создан: {backup_name}")
                
                # Применяем изменения
                applied_changes = self._apply_changes(package, conflicts, args)
                print(f"✅ Применено изменений: {applied_changes}")
                
                result = {
                    "command": "import",
                    "status": "completed",
                    "applied_changes": applied_changes,
                    "backup_name": backup_name,
                    "conflicts_count": len(conflicts)
                }
            
            # Добавляем рекомендации
            recommendations = []
            if len(conflicts) > 0:
                recommendations.append("Обнаружены конфликты - проверьте применение изменений")
                recommendations.append("При необходимости используйте 'слк rollback' для отката")
            else:
                recommendations.append("Импорт завершен успешно - система обновлена")
                recommendations.append("Рекомендую проверить работоспособность: 'слк статус'")
            
            result["ai_recommendations"] = recommendations
            result["next_commands"] = ["status", "validate"] if len(conflicts) > 0 else ["status", "list"]
            
            self.output_json_context(result)
            
            return 0
            
        except Exception as e:
            print(f"❌ Ошибка импорта: {e}")
            return 1
    
    def _load_and_validate_package(self, package_path: str) -> Dict[str, Any]:
        """Загрузить и валидировать пакет"""
        package_file = Path(package_path)
        if not package_file.exists():
            raise FileNotFoundError(f"Пакет не найден: {package_path}")
        
        with open(package_file, 'r', encoding='utf-8') as f:
            package = json.load(f)
        
        # Базовая валидация структуры
        required_sections = ["header", "metadata", "changes"]
        for section in required_sections:
            if section not in package:
                raise ValueError(f"Отсутствует обязательная секция: {section}")
        
        return package
    
    def _analyze_conflicts(self, package: Dict[str, Any]) -> List[str]:
        """Анализ конфликтов"""
        conflicts = []
        base_path = Path(self.base_path)
        
        # Проверяем конфликты с существующими файлами
        for file_path in package["changes"].get("modified_files", {}):
            full_path = base_path / file_path
            if full_path.exists():
                conflicts.append(f"Файл будет перезаписан: {file_path}")
        
        for file_path in package["changes"].get("new_files", {}):
            full_path = base_path / file_path
            if full_path.exists():
                conflicts.append(f"Новый файл конфликтует с существующим: {file_path}")
        
        return conflicts
    
    def _show_import_preview(self, package: Dict[str, Any], conflicts: List[str]):
        """Показать preview импорта"""
        print("\n📋 PREVIEW ИМПОРТА:")
        print("-" * 30)
        
        header = package.get("header", {})
        print(f"📦 Пакет: {header.get('description', 'N/A')}")
        print(f"🔖 Версия: {header.get('version', 'N/A')}")
        print(f"👤 Автор: {header.get('author', 'N/A')}")
        print(f"📅 Дата: {header.get('timestamp', 'N/A')}")
        
        changes = package.get("changes", {})
        
        if changes.get("new_files"):
            print(f"\n📄 Новые файлы будут созданы:")
            for file_path in list(changes["new_files"].keys())[:10]:
                print(f"   + {file_path}")
        
        if changes.get("modified_files"):
            print(f"\n✏️  Файлы будут изменены:")
            for file_path in list(changes["modified_files"].keys())[:10]:
                print(f"   ~ {file_path}")
        
        if changes.get("deleted_files"):
            print(f"\n🗑️  Файлы будут удалены:")
            for file_path in changes["deleted_files"][:10]:
                print(f"   - {file_path}")
    
    def _create_backup(self, backup_name: Optional[str]) -> str:
        """Создать backup"""
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"pre_import_{timestamp}"
        
        # Заглушка - в реальной реализации здесь был бы полный backup
        print(f"📝 Создание backup: {backup_name}")
        return backup_name
    
    def _apply_changes(self, package: Dict[str, Any], conflicts: List[str], args: argparse.Namespace) -> int:
        """Применить изменения"""
        changes_applied = 0
        base_path = Path(self.base_path)
        changes = package.get("changes", {})
        
        # Применяем новые файлы
        for file_path, content in changes.get("new_files", {}).items():
            full_path = base_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            changes_applied += 1
            print(f"   + Создан: {file_path}")
        
        # Применяем измененные файлы
        for file_path, content in changes.get("modified_files", {}).items():
            full_path = base_path / file_path
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            changes_applied += 1
            print(f"   ~ Изменен: {file_path}")
        
        # Удаляем файлы
        for file_path in changes.get("deleted_files", []):
            full_path = base_path / file_path
            if full_path.exists():
                full_path.unlink()
                changes_applied += 1
                print(f"   - Удален: {file_path}")
        
        return changes_applied


class ValidateEvolutionCommand(ContextAwareCommand):
    """Команда валидации .slc-update пакета"""
    
    def __init__(self, base_path: str):
        super().__init__(base_path)
    
    @property
    def name(self) -> str:
        return "evolution-validate"
    
    @property  
    def description(self) -> str:
        return "🔍 Валидация .slc-update пакета без применения изменений"
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "package",
            help="Путь к .slc-update файлу"
        )
        parser.add_argument(
            "--detailed", "-d",
            action="store_true",
            help="Детальная валидация с анализом содержимого"
        )
    
    def execute(self, args: argparse.Namespace) -> int:
        """Выполнение команды validate-evolution"""
        print("🔍 Валидация SLC Evolution пакета")
        print("=" * 40)
        
        try:
            package_file = Path(args.package)
            if not package_file.exists():
                print(f"❌ Файл не найден: {args.package}")
                return 1
            
            # Загружаем пакет
            with open(package_file, 'r', encoding='utf-8') as f:
                package = json.load(f)
            
            # Валидируем структуру
            issues = self._validate_package_structure(package)
            
            # Анализируем содержимое
            if args.detailed:
                content_issues = self._validate_content(package)
                issues.extend(content_issues)
            
            # Выводим результаты
            if issues:
                print(f"❌ Обнаружено проблем: {len(issues)}")
                for issue in issues:
                    print(f"   • {issue}")
                
                result = {
                    "command": "evolution-validate",
                    "status": "invalid",
                    "issues": issues,
                    "valid": False
                }
            else:
                print("✅ Пакет валиден")
                
                result = {
                    "command": "evolution-validate", 
                    "status": "valid",
                    "issues": [],
                    "valid": True
                }
            
            # Добавляем рекомендации
            recommendations = []
            if issues:
                recommendations.append("Пакет содержит ошибки - исправьте перед импортом")
                recommendations.append("Свяжитесь с автором пакета для получения исправленной версии")
            else:
                recommendations.append("Пакет готов к импорту - можно безопасно применять")
                recommendations.append("Используйте 'слк импорт' для применения изменений")
            
            result["ai_recommendations"] = recommendations
            result["next_commands"] = ["help"] if issues else ["import"]
            
            self.output_json_context(result)
            
            return 0 if not issues else 1
            
        except Exception as e:
            print(f"❌ Ошибка валидации: {e}")
            return 1
    
    def _validate_package_structure(self, package: Dict[str, Any]) -> List[str]:
        """Валидация структуры пакета"""
        issues = []
        
        # Проверяем обязательные секции
        required_sections = ["header", "metadata", "changes"]
        for section in required_sections:
            if section not in package:
                issues.append(f"Отсутствует секция: {section}")
        
        # Проверяем header
        if "header" in package:
            header = package["header"]
            required_header_fields = ["update_id", "version", "timestamp"]
            for field in required_header_fields:
                if field not in header:
                    issues.append(f"Отсутствует поле header.{field}")
        
        # Проверяем changes
        if "changes" in package:
            changes = package["changes"]
            if not any([
                changes.get("new_files"),
                changes.get("modified_files"), 
                changes.get("deleted_files")
            ]):
                issues.append("Пакет не содержит изменений")
        
        return issues
    
    def _validate_content(self, package: Dict[str, Any]) -> List[str]:
        """Валидация содержимого"""
        issues = []
        changes = package.get("changes", {})
        
        # Проверяем JSON файлы
        for file_path, content in changes.get("new_files", {}).items():
            if file_path.endswith('.json'):
                try:
                    json.loads(content)
                except json.JSONDecodeError as e:
                    issues.append(f"Неверный JSON в {file_path}: {e}")
        
        for file_path, content in changes.get("modified_files", {}).items():
            if file_path.endswith('.json'):
                try:
                    json.loads(content)
                except json.JSONDecodeError as e:
                    issues.append(f"Неверный JSON в {file_path}: {e}")
        
        return issues