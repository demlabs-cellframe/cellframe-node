#!/usr/bin/env python3
"""
Команды организации файлов СЛК

Реализует команды:
- organize: Автоматическая организация файлов
- cleanup: Очистка временных файлов
- create-rule: Создание правил организации
- monitor: Мониторинг файловой системы
- org-stats: Статистика организации

Версия: 1.1.0
Создано: 2025-01-15
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import threading
import hashlib

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..base_command import BaseCommand, ContextAwareCommand
from ..core.file_organization_engine import FileOrganizationEngine, AutoCleanupSystem, quick_organize, cleanup_project


class OrganizeCommand(ContextAwareCommand):
    """Команда автоматической организации файлов с JSON выводом для AI интеграции"""
    
    @property
    def name(self) -> str:
        return "organize"
    
    @property
    def description(self) -> str:
        return "🗂️  Автоматическая интеллектуальная организация файлов проекта"
    
    def __init__(self, base_path: str):
        super().__init__(base_path)
        self.engine = FileOrganizationEngine(base_path) if FileOrganizationEngine else None
    
    def add_arguments(self, parser):
        """Добавляет аргументы команды"""
        parser.add_argument(
            "paths",
            nargs="*",
            help="Пути для организации (по умолчанию: весь проект)"
        )
        
        parser.add_argument(
            "--dry-run", "-n",
            action="store_true",
            help="Только анализ без реальных изменений"
        )
        
        parser.add_argument(
            "--rules", "-r",
            help="Путь к файлу с пользовательскими правилами"
        )
        
        parser.add_argument(
            "--exclude", "-e",
            action="append",
            help="Исключить пути из организации (можно указать несколько раз)"
        )
        
        parser.add_argument(
            "--type", "-t",
            choices=["documentation", "code", "template", "temporary", "archive", "all"],
            default="all",
            help="Организовать только файлы определённого типа"
        )
        
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Подробный вывод операций"
        )
        
        parser.add_argument(
            "--save-report",
            help="Сохранить отчёт о выполненных операциях в файл"
        )
    
    def validate_args(self, args) -> bool:
        """Валидация аргументов"""
        if not self.engine:
            print("❌ Ошибка: File Organization Engine недоступен")
            return False
        
        # Проверяем существование путей
        for path in args.paths:
            if not Path(path).exists():
                print(f"❌ Ошибка: Путь не существует: {path}")
                return False
        
        return True
    
    def execute(self, args) -> int:
        """Выполнение команды"""
        try:
            print("🗂️  Запуск автоматической организации файлов...")
            print("=" * 60)
            
            if args.dry_run:
                print("🔍 РЕЖИМ АНАЛИЗА - реальные изменения не выполняются")
            
            # Выполняем организацию
            target_paths = args.paths if args.paths else None
            result = self.engine.organize_files(target_paths, dry_run=args.dry_run)
            
            # Выводим результаты
            self._print_results(result, args.verbose)
            
            # Сохраняем отчёт если требуется
            if args.save_report:
                self._save_report(result, args.save_report)
            
            # JSON вывод для AI интеграции
            organize_result = {
                "command": "organize",
                "status": "completed" if not result.errors else "completed_with_errors",
                "mode": "dry_run" if args.dry_run else "execute",
                "summary": {
                    "processed_files": result.processed_files,
                    "moved_files": result.moved_files,
                    "deleted_files": result.deleted_files,
                    "archived_files": result.archived_files,
                    "space_freed": result.space_freed,
                    "execution_time": result.execution_time
                },
                "errors_count": len(result.errors),
                "warnings_count": len(result.warnings)
            }
            
            # Добавляем рекомендации на основе результатов
            recommendations = []
            if args.dry_run:
                if result.moved_files > 0 or result.deleted_files > 0:
                    recommendations.append("Анализ показал возможности для организации - запустите './slc organize' для применения")
                else:
                    recommendations.append("Проект уже хорошо организован - изменений не требуется")
            else:
                if result.moved_files > 0:
                    recommendations.append(f"Организовано {result.moved_files} файлов - структура проекта улучшена")
                if result.space_freed > 1024 * 1024:  # > 1MB
                    recommendations.append(f"Освобождено {self._format_size(result.space_freed)} дискового пространства")
                if not result.errors:
                    recommendations.append("Организация завершена успешно - можно продолжать работу")
                else:
                    recommendations.append("Есть ошибки - проверьте вывод и при необходимости запустите 'слк validate'")
            
            organize_result["ai_recommendations"] = recommendations
            organize_result["next_commands"] = ["status", "validate"] if result.errors else ["status", "templates"]
            
            self.output_json_context(organize_result)
            
            # Возвращаем код в зависимости от результата
            if result.errors:
                print(f"\n⚠️  Выполнено с ошибками: {len(result.errors)} ошибок")
                return 1
            else:
                print(f"\n✅ Успешно завершено за {result.execution_time:.2f}с")
                return 0
                
        except Exception as e:
            print(f"❌ Произошла ошибка: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    def _print_results(self, result, verbose: bool):
        """Выводит результаты организации"""
        print(f"\n📊 Результаты организации:")
        print(f"   📁 Обработано файлов: {result.processed_files}")
        print(f"   📂 Перемещено файлов: {result.moved_files}")
        print(f"   🗑️  Удалено файлов: {result.deleted_files}")
        print(f"   📦 Архивировано файлов: {result.archived_files}")
        print(f"   💾 Освобождено места: {self._format_size(result.space_freed)}")
        print(f"   ⏱️  Время выполнения: {result.execution_time:.2f}с")
        
        if result.rules_applied:
            print(f"\n📋 Применённые правила:")
            for rule in set(result.rules_applied):
                count = result.rules_applied.count(rule)
                print(f"   • {rule} ({count} раз)")
        
        if result.errors and verbose:
            print(f"\n❌ Ошибки ({len(result.errors)}):")
            for error in result.errors[:5]:  # Показываем первые 5
                print(f"   • {error}")
            if len(result.errors) > 5:
                print(f"   ... и ещё {len(result.errors) - 5} ошибок")
        
        if result.warnings and verbose:
            print(f"\n⚠️  Предупреждения ({len(result.warnings)}):")
            for warning in result.warnings[:3]:
                print(f"   • {warning}")
    
    def _format_size(self, size_bytes: int) -> str:
        """Форматирует размер в человекочитаемый вид"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"
    
    def _save_report(self, result, file_path: str):
        """Сохраняет отчёт о выполненных операциях"""
        try:
            report = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "summary": {
                    "processed_files": result.processed_files,
                    "moved_files": result.moved_files,
                    "deleted_files": result.deleted_files,
                    "archived_files": result.archived_files,
                    "space_freed": result.space_freed,
                    "execution_time": result.execution_time
                },
                "rules_applied": result.rules_applied,
                "errors": result.errors,
                "warnings": result.warnings
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Отчёт сохранён: {file_path}")
            
        except Exception as e:
            print(f"❌ Ошибка сохранения отчёта: {e}")


class CleanupCommand(BaseCommand):
    """Команда очистки временных файлов"""
    
    name = "cleanup"
    description = "🧹 Автоматическая очистка временных и ненужных файлов"
    
    def __init__(self, base_path: str):
        super().__init__()
        self.base_path = base_path
    
    def add_arguments(self, parser):
        """Добавляет аргументы команды"""
        parser.add_argument(
            "--dry-run", "-n",
            action="store_true",
            help="Только анализ без реального удаления"
        )
        
        parser.add_argument(
            "--aggressive", "-a",
            action="store_true",
            help="Агрессивная очистка (включая старые backup файлы)"
        )
        
        parser.add_argument(
            "--older-than",
            type=int,
            default=7,
            help="Удалять файлы старше указанного количества дней (по умолчанию: 7)"
        )
        
        parser.add_argument(
            "--patterns",
            nargs="+",
            help="Дополнительные паттерны файлов для удаления"
        )
        
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Подробный вывод удаляемых файлов"
        )
    
    def execute(self, args) -> int:
        """Выполнение команды"""
        try:
            print("🧹 Запуск автоматической очистки...")
            print("=" * 50)
            
            if args.dry_run:
                print("🔍 РЕЖИМ АНАЛИЗА - файлы не будут удалены")
            
            # Выполняем очистку
            result = cleanup_project(dry_run=args.dry_run)
            
            # Выводим результаты
            print(f"\n📊 Результаты очистки:")
            print(f"   📁 Обработано файлов: {result.processed_files}")
            print(f"   🗑️  Удалено файлов: {result.deleted_files}")
            print(f"   💾 Освобождено места: {self._format_size(result.space_freed)}")
            
            if result.errors and args.verbose:
                print(f"\n❌ Ошибки ({len(result.errors)}):")
                for error in result.errors:
                    print(f"   • {error}")
            
            if result.deleted_files > 0:
                print(f"\n✅ Очистка завершена успешно")
            else:
                print(f"\n💡 Файлы для очистки не найдены")
            
            return 0
            
        except Exception as e:
            print(f"❌ Произошла ошибка: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
    def _format_size(self, size_bytes: int) -> str:
        """Форматирует размер в человекочитаемый вид"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"


class MonitorCommand(BaseCommand):
    """Команда мониторинга файловой системы"""
    
    name = "monitor"
    description = "👁️  Мониторинг файловой системы в реальном времени"
    
    def __init__(self, base_path: str):
        super().__init__()
        self.base_path = base_path
    
    def add_arguments(self, parser):
        """Добавляет аргументы команды"""
        parser.add_argument(
            "--auto-organize",
            action="store_true",
            help="Автоматически организовывать новые файлы"
        )
        
        parser.add_argument(
            "--watch-paths",
            nargs="+",
            help="Пути для мониторинга (по умолчанию: корень проекта)"
        )
        
        parser.add_argument(
            "--interval", "-i",
            type=int,
            default=30,
            help="Интервал проверки в секундах (по умолчанию: 30)"
        )
    
    def execute(self, args) -> int:
        """Выполнение команды"""
        print("👁️  Мониторинг файловой системы (функция в разработке)")
        print("📝 Планируется реализация в следующих версиях:")
        print("   • Real-time мониторинг изменений файлов")
        print("   • Автоматическая организация новых файлов")
        print("   • Уведомления о подозрительных изменениях")
        print("   • Интеграция с системой backup'а")
        return 0


class OrganizationStatsCommand(BaseCommand):
    """Команда получения статистики организации"""
    
    name = "org-stats"
    description = "📊 Статистика автоматической организации файлов"
    
    def __init__(self, base_path: str):
        super().__init__()
        self.base_path = base_path
        self.engine = FileOrganizationEngine(base_path) if FileOrganizationEngine else None
    
    def add_arguments(self, parser):
        """Добавляет аргументы команды"""
        parser.add_argument(
            "--format", "-f",
            choices=["table", "json"],
            default="table",
            help="Формат вывода статистики"
        )
        
        parser.add_argument(
            "--history",
            action="store_true",
            help="Показать историю операций"
        )
        
        parser.add_argument(
            "--rules",
            action="store_true",
            help="Показать активные правила организации"
        )
    
    def execute(self, args) -> int:
        """Выполнение команды"""
        try:
            if not self.engine:
                print("❌ Ошибка: File Organization Engine недоступен")
                return 1
            
            print("📊 Статистика автоматической организации файлов")
            print("=" * 55)
            
            # Получаем статистику
            stats = self.engine.get_organization_stats()
            
            if args.format == "json":
                print(json.dumps(stats, indent=2, ensure_ascii=False))
            else:
                self._print_table_stats(stats)
            
            if args.rules:
                self._print_rules_info()
            
            if args.history:
                self._print_history()
            
            return 0
            
        except Exception as e:
            print(f"❌ Произошла ошибка: {e}")
            return 1
    
    def _print_table_stats(self, stats: Dict):
        """Выводит статистику в табличном формате"""
        print(f"📈 Общая статистика:")
        print(f"   Всего операций:     {stats['total_operations']}")
        print(f"   Файлов организовано: {stats['files_organized']}")
        print(f"   Места освобождено:   {stats['space_freed']}")
        print(f"   Последняя очистка:   {stats['last_cleanup'] or 'Никогда'}")
        print(f"   Всего правил:       {stats['rules_count']}")
        print(f"   Активных правил:    {stats['enabled_rules']}")
    
    def _print_rules_info(self):
        """Выводит информацию о правилах"""
        print(f"\n📋 Активные правила организации:")
        
        if not self.engine.rules:
            print("   Правила не загружены")
            return
        
        for i, rule in enumerate(self.engine.rules, 1):
            status = "✅" if rule.enabled else "❌"
            print(f"   {i}. {status} {rule.name}")
            print(f"      Приоритет: {rule.priority}")
            print(f"      Действие: {rule.action.value}")
            print(f"      Паттерн: {rule.pattern}")
    
    def _print_history(self):
        """Выводит историю операций"""
        print(f"\n📜 История операций (последние 5):")
        
        log_file = Path(self.base_path) / ".slc" / "organization_log.json"
        if not log_file.exists():
            print("   История не найдена")
            return
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_entries = json.load(f)
            
            for entry in log_entries[-5:]:
                timestamp = entry['timestamp']
                result = entry['result']
                dry_run = entry.get('dry_run', False)
                mode = " [DRY RUN]" if dry_run else ""
                
                print(f"   📅 {timestamp}{mode}")
                print(f"      Файлов: {result['processed_files']}, "
                      f"Перемещено: {result['moved_files']}, "
                      f"Удалено: {result['deleted_files']}")
                
        except Exception as e:
            print(f"   Ошибка чтения истории: {e}")


class CreateRuleCommand(BaseCommand):
    """Команда создания пользовательского правила организации"""
    
    name = "create-rule"
    description = "📝 Создание пользовательского правила организации файлов"
    
    def __init__(self, base_path: str):
        super().__init__()
        self.base_path = base_path
    
    def add_arguments(self, parser):
        """Добавляет аргументы команды"""
        parser.add_argument(
            "name",
            help="Название правила"
        )
        
        parser.add_argument(
            "--pattern", "-p",
            required=True,
            help="Регулярное выражение для имён файлов"
        )
        
        parser.add_argument(
            "--target", "-t",
            required=True,
            help="Целевая директория"
        )
        
        parser.add_argument(
            "--action", "-a",
            choices=["move", "copy", "delete", "archive"],
            default="move",
            help="Действие для файлов"
        )
        
        parser.add_argument(
            "--priority",
            type=int,
            default=50,
            help="Приоритет правила (0-100)"
        )
        
        parser.add_argument(
            "--enable",
            action="store_true",
            help="Сразу включить правило"
        )
    
    def execute(self, args) -> int:
        """Выполнение команды"""
        print(f"📝 Создание правила '{args.name}' (функция в разработке)")
        print(f"   Паттерн: {args.pattern}")
        print(f"   Цель: {args.target}")
        print(f"   Действие: {args.action}")
        print(f"   Приоритет: {args.priority}")
        print(f"   Включено: {'Да' if args.enable else 'Нет'}")
        
        print("\n💡 Функция будет реализована в следующих версиях")
        return 0 