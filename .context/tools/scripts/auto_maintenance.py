#!/usr/bin/env python3
"""
Auto Maintenance Script - Автоматическое поддержание порядка в СЛК

Выполняет регулярные задачи:
- Организация файлов по правилам
- Очистка временных файлов
- Архивирование старых backup'ов
- Мониторинг размера проекта
- Генерация отчётов

Версия: 1.0.0
Создано: 2025-01-15
"""

import sys
import time
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

# Добавляем путь к модулям
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.cli_modules.core.file_organization_engine import FileOrganizationEngine, AutoCleanupSystem
    from tools.cli_modules.core.unified_context_engine import UnifiedContextEngine
except ImportError as e:
    print(f"❌ Ошибка импорта модулей: {e}")
    FileOrganizationEngine = None
    UnifiedContextEngine = None


class AutoMaintenanceSystem:
    """Система автоматического поддержания порядка"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.config_file = self.base_path / ".slc" / "maintenance_config.json"
        self.log_file = self.base_path / ".slc" / "maintenance_log.json"
        
        # Инициализируем системы
        self.file_org = FileOrganizationEngine(base_path) if FileOrganizationEngine else None
        self.cleanup_system = AutoCleanupSystem(base_path) if AutoCleanupSystem else None
        
        # Загружаем конфигурацию
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Загружает конфигурацию автоматического обслуживания"""
        default_config = {
            "auto_organize_enabled": True,
            "auto_cleanup_enabled": True,
            "organization_interval_hours": 6,
            "cleanup_interval_hours": 24,
            "max_project_size_mb": 1024,  # 1GB
            "backup_retention_days": 30,
            "generate_reports": True,
            "verbose_logging": False
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return {**default_config, **json.load(f)}
            except Exception:
                pass
        
        return default_config
    
    def run_full_maintenance(self, dry_run: bool = False) -> Dict:
        """Запускает полное автоматическое обслуживание"""
        start_time = time.time()
        
        print("🔧 Запуск полного автоматического обслуживания...")
        print("=" * 60)
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "tasks": {}
        }
        
        # 1. Организация файлов
        if self.config["auto_organize_enabled"] and self.file_org:
            print("\n🗂️  Шаг 1: Автоматическая организация файлов")
            org_result = self.file_org.organize_files(dry_run=dry_run)
            results["tasks"]["file_organization"] = {
                "processed_files": org_result.processed_files,
                "moved_files": org_result.moved_files,
                "execution_time": org_result.execution_time,
                "errors": len(org_result.errors)
            }
            print(f"   ✅ Файлов обработано: {org_result.processed_files}")
            print(f"   📂 Файлов перемещено: {org_result.moved_files}")
        
        # 2. Очистка временных файлов
        if self.config["auto_cleanup_enabled"] and self.cleanup_system:
            print("\n🧹 Шаг 2: Очистка временных файлов")
            cleanup_result = self.cleanup_system.perform_cleanup(dry_run=dry_run)
            results["tasks"]["cleanup"] = {
                "processed_files": cleanup_result.processed_files,
                "deleted_files": cleanup_result.deleted_files,
                "space_freed": cleanup_result.space_freed,
                "errors": len(cleanup_result.errors)
            }
            print(f"   ✅ Файлов обработано: {cleanup_result.processed_files}")
            print(f"   🗑️  Файлов удалено: {cleanup_result.deleted_files}")
            print(f"   💾 Места освобождено: {self._format_size(cleanup_result.space_freed)}")
        
        # 3. Анализ размера проекта
        print("\n📊 Шаг 3: Анализ размера проекта")
        size_analysis = self._analyze_project_size()
        results["tasks"]["size_analysis"] = size_analysis
        print(f"   📏 Общий размер: {self._format_size(size_analysis['total_size'])}")
        print(f"   📁 Файлов всего: {size_analysis['file_count']}")
        print(f"   📂 Директорий: {size_analysis['dir_count']}")
        
        # 4. Проверка старых backup'ов
        print("\n📦 Шаг 4: Управление backup файлами")
        backup_analysis = self._manage_backups(dry_run=dry_run)
        results["tasks"]["backup_management"] = backup_analysis
        print(f"   📦 Backup файлов найдено: {backup_analysis['found_backups']}")
        print(f"   🗑️  Старых backup удалено: {backup_analysis['deleted_backups']}")
        
        # 5. Генерация отчёта
        if self.config["generate_reports"]:
            print("\n📋 Шаг 5: Генерация отчёта")
            report_path = self._generate_maintenance_report(results)
            print(f"   📄 Отчёт создан: {report_path}")
        
        total_time = time.time() - start_time
        results["total_execution_time"] = total_time
        
        print(f"\n🎉 Автоматическое обслуживание завершено за {total_time:.2f}с")
        
        # Логируем результат
        self._log_maintenance_run(results)
        
        return results
    
    def _analyze_project_size(self) -> Dict:
        """Анализирует размер проекта"""
        total_size = 0
        file_count = 0
        dir_count = 0
        largest_files = []
        
        for path in self.base_path.rglob("*"):
            if path.is_file():
                try:
                    size = path.stat().st_size
                    total_size += size
                    file_count += 1
                    
                    # Сохраняем информацию о крупных файлах
                    largest_files.append((str(path.relative_to(self.base_path)), size))
                    
                except Exception:
                    pass
            elif path.is_dir():
                dir_count += 1
        
        # Сортируем по размеру
        largest_files.sort(key=lambda x: x[1], reverse=True)
        largest_files = largest_files[:10]  # Топ 10
        
        return {
            "total_size": total_size,
            "file_count": file_count,
            "dir_count": dir_count,
            "largest_files": largest_files,
            "size_warning": total_size > (self.config["max_project_size_mb"] * 1024 * 1024)
        }
    
    def _manage_backups(self, dry_run: bool = False) -> Dict:
        """Управляет backup файлами"""
        cutoff_date = datetime.now() - timedelta(days=self.config["backup_retention_days"])
        
        backup_patterns = ["backup_*.tar.gz", "*.backup", "*.bak", "*.old"]
        found_backups = 0
        deleted_backups = 0
        
        for pattern in backup_patterns:
            for backup_file in self.base_path.rglob(pattern):
                if backup_file.is_file():
                    found_backups += 1
                    
                    try:
                        file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                        
                        if file_time < cutoff_date:
                            if not dry_run:
                                backup_file.unlink()
                                print(f"   🗑️  Удалён старый backup: {backup_file}")
                            else:
                                print(f"   [DRY RUN] Удалить старый backup: {backup_file}")
                            
                            deleted_backups += 1
                            
                    except Exception as e:
                        print(f"   ⚠️  Ошибка обработки {backup_file}: {e}")
        
        return {
            "found_backups": found_backups,
            "deleted_backups": deleted_backups,
            "retention_days": self.config["backup_retention_days"]
        }
    
    def _generate_maintenance_report(self, results: Dict) -> str:
        """Генерирует отчёт об обслуживании"""
        report_dir = self.base_path / ".slc" / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"maintenance_report_{timestamp}.json"
        
        # Добавляем дополнительную информацию
        enhanced_report = {
            **results,
            "config": self.config,
            "recommendations": self._generate_recommendations(results)
        }
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(enhanced_report, f, indent=2, ensure_ascii=False)
            
            return str(report_file.relative_to(self.base_path))
            
        except Exception as e:
            print(f"   ❌ Ошибка создания отчёта: {e}")
            return ""
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Генерирует рекомендации на основе результатов"""
        recommendations = []
        
        # Анализ размера проекта
        size_analysis = results["tasks"].get("size_analysis", {})
        if size_analysis.get("size_warning"):
            recommendations.append(
                f"⚠️  Размер проекта превышает {self.config['max_project_size_mb']}MB. "
                "Рекомендуется очистка или архивирование."
            )
        
        # Анализ файловой организации
        org_task = results["tasks"].get("file_organization", {})
        if org_task.get("moved_files", 0) > 10:
            recommendations.append(
                "📂 Обнаружено много неорганизованных файлов. "
                "Рассмотрите возможность настройки автоматических правил."
            )
        
        # Анализ backup'ов
        backup_task = results["tasks"].get("backup_management", {})
        if backup_task.get("found_backups", 0) > 5:
            recommendations.append(
                "📦 Найдено много backup файлов. "
                "Рекомендуется настройка автоматической архивации."
            )
        
        if not recommendations:
            recommendations.append("✅ Проект в хорошем состоянии. Дополнительных действий не требуется.")
        
        return recommendations
    
    def _log_maintenance_run(self, results: Dict):
        """Логирует результат обслуживания"""
        log_entries = []
        
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    log_entries = json.load(f)
            except Exception:
                pass
        
        log_entries.append(results)
        
        # Оставляем только последние 50 записей
        log_entries = log_entries[-50:]
        
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
    
    def check_maintenance_needed(self) -> Dict:
        """Проверяет, нужно ли автоматическое обслуживание"""
        
        # Проверяем последний запуск
        last_run = self._get_last_maintenance_run()
        
        if not last_run:
            return {
                "maintenance_needed": True,
                "reason": "Автоматическое обслуживание никогда не запускалось",
                "priority": "high"
            }
        
        last_run_time = datetime.fromisoformat(last_run["timestamp"])
        time_since_last = datetime.now() - last_run_time
        
        # Проверяем интервалы
        org_interval = timedelta(hours=self.config["organization_interval_hours"])
        cleanup_interval = timedelta(hours=self.config["cleanup_interval_hours"])
        
        if time_since_last > cleanup_interval:
            return {
                "maintenance_needed": True,
                "reason": f"Прошло {time_since_last.days} дней с последней очистки",
                "priority": "medium"
            }
        
        if time_since_last > org_interval:
            return {
                "maintenance_needed": True,
                "reason": f"Прошло {time_since_last.total_seconds()/3600:.1f} часов с последней организации",
                "priority": "low"
            }
        
        return {
            "maintenance_needed": False,
            "reason": "Автоматическое обслуживание не требуется",
            "next_run": str(last_run_time + cleanup_interval)
        }
    
    def _get_last_maintenance_run(self) -> Dict:
        """Получает информацию о последнем запуске обслуживания"""
        if not self.log_file.exists():
            return None
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                log_entries = json.load(f)
            
            if log_entries:
                return log_entries[-1]
        except Exception:
            pass
        
        return None


def main():
    """Основная функция CLI"""
    parser = argparse.ArgumentParser(
        description="🔧 Автоматическое поддержание порядка в СЛК",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Только анализ без реальных изменений"
    )
    
    parser.add_argument(
        "--check-only", "-c",
        action="store_true",
        help="Только проверить, нужно ли обслуживание"
    )
    
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Принудительно запустить обслуживание"
    )
    
    parser.add_argument(
        "--config",
        help="Путь к файлу конфигурации"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Подробный вывод"
    )
    
    args = parser.parse_args()
    
    # Инициализируем систему
    maintenance = AutoMaintenanceSystem()
    
    if args.check_only:
        # Только проверка
        check_result = maintenance.check_maintenance_needed()
        
        if check_result["maintenance_needed"]:
            print(f"🔧 Обслуживание требуется: {check_result['reason']}")
            print(f"📊 Приоритет: {check_result['priority']}")
            return 1
        else:
            print(f"✅ {check_result['reason']}")
            if "next_run" in check_result:
                print(f"📅 Следующий запуск: {check_result['next_run']}")
            return 0
    
    else:
        # Запуск обслуживания
        if not args.force:
            check_result = maintenance.check_maintenance_needed()
            if not check_result["maintenance_needed"]:
                print(f"💡 {check_result['reason']}")
                print("   Используйте --force для принудительного запуска")
                return 0
        
        # Выполняем обслуживание
        results = maintenance.run_full_maintenance(dry_run=args.dry_run)
        
        # Выводим рекомендации
        recommendations = results.get("recommendations", [])
        if recommendations:
            print(f"\n💡 Рекомендации:")
            for rec in recommendations:
                print(f"   • {rec}")
        
        return 0


if __name__ == "__main__":
    exit(main()) 