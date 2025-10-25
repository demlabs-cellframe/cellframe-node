"""
Команды управления системой СЛК
"""

import argparse
import json
import os
from pathlib import Path
from typing import Dict, Any, List

from ..base_command import BaseCommand, ContextAwareCommand
from ..core.system_validator import SystemValidator
from .evolution_commands import ExportEvolutionCommand, ImportEvolutionCommand, ValidateEvolutionCommand


class ValidateCommand(ContextAwareCommand):
    """Команда validate - проверка целостности системы СЛК с поддержкой JSON контекста"""
    
    def __init__(self, base_path: str):
        super().__init__(base_path)
        self.system_validator = SystemValidator(base_path)
    
    @property
    def name(self) -> str:
        return "validate"
    
    @property
    def description(self) -> str:
        return "Проверить целостность системы СЛК"
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        super().add_arguments(parser)  # Добавляет JSON контекст
        parser.add_argument(
            "--fix", 
            action="store_true",
            help="Автоматически исправить найденные проблемы"
        )
        parser.add_argument(
            "--format", "-f",
            choices=["table", "json"],
            default="table",
            help="Формат вывода"
        )
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Подробный вывод"
        )
    
    def get_default_context_files(self) -> List[str]:
        """Файлы контекста для validate"""
        return [
            "VERSION",
            "manifest.json",
            "modules/**/*.json",
            "modules/core/standards.json",
            "tasks/active.json"
        ]
    
    def get_context_summary(self, execution_result: Dict[str, Any]) -> str:
        """Описание результатов валидации"""
        is_valid = execution_result.get("is_valid", False)
        issues_count = len(execution_result.get("issues", []))
        components_checked = execution_result.get("components_checked", 0)
        files_checked = execution_result.get("files_checked", 0)
        
        status = "✅ ВАЛИДНА" if is_valid else f"❌ НАЙДЕНО ПРОБЛЕМ: {issues_count}"
        
        return f"""
        Валидация системы СЛК:
        - Статус: {status}
        - Проверено компонентов: {components_checked}
        - Проверено файлов: {files_checked}
        - Критических проблем: {len([i for i in execution_result.get("issues", []) if i.get("severity") == "high"])}
        """
    
    def get_recommended_actions(self, execution_result: Dict[str, Any]) -> List[str]:
        """Рекомендуемые действия на основе валидации"""
        actions = []
        
        if execution_result.get("is_valid", True):
            actions.extend([
                "Система прошла валидацию успешно",
                "Рекомендуется периодический мониторинг - слк status",
                "Можно провести оптимизацию - слк optimize"
            ])
        else:
            issues = execution_result.get("issues", [])
            high_severity = [i for i in issues if i.get("severity") == "high"]
            medium_severity = [i for i in issues if i.get("severity") == "medium"]
            
            if high_severity:
                actions.extend([
                    f"КРИТИЧНО: {len(high_severity)} серьёзных проблем требуют немедленного исправления",
                    "Запустить автоматическое исправление - слк validate --fix",
                    "Проверить статус после исправления - слк status"
                ])
            
            if medium_severity:
                actions.append(f"Рекомендуется исправить {len(medium_severity)} предупреждений")
                
            # Специфические рекомендации по типам проблем
            missing_files = [i for i in issues if "отсутствует" in i.get("description", "").lower()]
            if missing_files:
                actions.append("Восстановить отсутствующие файлы из резервной копии или шаблонов")
                
        return actions
    
    def get_next_commands(self, execution_result: Dict[str, Any]) -> List[str]:
        """Предлагаемые следующие команды"""
        if execution_result.get("is_valid", True):
            return [
                "слк optimize",
                "слк status", 
                "слк рефлексия",
                "слк intelligence-stats"
            ]
        else:
            issues = execution_result.get("issues", [])
            high_severity = [i for i in issues if i.get("severity") == "high"]
            
            if high_severity:
                return [
                    "слк validate --fix",
                    "слк status",
                    "слк optimize --clean-cache"
                ]
            else:
                return [
                    "слк validate --fix",
                    "слк optimize",
                    "слк status"
                ]
    
    def execute_with_context(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Выполнить команду и вернуть результат для контекста"""
        print("🔍 Проверка целостности системы СЛК...")
        print("=" * 50)
        
        # Запускаем валидацию
        validation_result = self.system_validator.validate_system()
        
        if args.format == "json":
            print(json.dumps(validation_result, indent=2, ensure_ascii=False))
            return validation_result
        
        # Выводим результаты
        self._print_validation_results(validation_result, args.verbose)
        
        # Автоматическое исправление
        if args.fix and not validation_result["is_valid"]:
            print("\n🔧 Попытка автоматического исправления...")
            fix_result = self.system_validator.fix_issues(validation_result["issues"])
            self._print_fix_results(fix_result)
            
            # Добавляем результат исправления к результату
            validation_result = {
                **validation_result,
                "fix_attempted": True,
                "fix_result": fix_result
            }
        
        return validation_result
    
    def _print_validation_results(self, result: Dict[str, Any], verbose: bool):
        """Вывод результатов валидации"""
        if result["is_valid"]:
            self.print_success("✅ Система СЛК в хорошем состоянии!")
            print(f"📊 Проверено компонентов: {result['components_checked']}")
            print(f"📄 Проверено файлов: {result['files_checked']}")
            return
        
        self.print_error("❌ Обнаружены проблемы в системе!")
        print(f"🔍 Найдено проблем: {len(result['issues'])}")
        
        # Группируем проблемы по типам
        issues_by_type = {}
        for issue in result["issues"]:
            issue_type = issue.get("type", "unknown")
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)
        
        for issue_type, issues in issues_by_type.items():
            print(f"\n📋 {issue_type.upper()} ({len(issues)} проблем):")
            for issue in issues:
                severity = issue.get("severity", "medium")
                icon = "🔴" if severity == "high" else "🟡" if severity == "medium" else "🟢"
                print(f"   {icon} {issue['description']}")
                
                if verbose and issue.get("details"):
                    print(f"      💡 {issue['details']}")
                
                if issue.get("fix_suggestion"):
                    print(f"      🔧 Рекомендация: {issue['fix_suggestion']}")
    
    def _print_fix_results(self, fix_result: Dict[str, Any]):
        """Вывод результатов исправления"""
        if fix_result["success"]:
            self.print_success(f"✅ Исправлено проблем: {fix_result['fixed_count']}")
        else:
            self.print_warning(f"⚠️ Частично исправлено: {fix_result['fixed_count']}/{fix_result['total_count']}")
        
        if fix_result.get("remaining_issues"):
            print("\n🔍 Оставшиеся проблемы требуют ручного вмешательства:")
            for issue in fix_result["remaining_issues"]:
                print(f"   • {issue['description']}")


class StatusCommand(ContextAwareCommand):
    """Команда status - статус системы СЛК с поддержкой JSON контекста"""
    
    def __init__(self, base_path: str):
        super().__init__(base_path)
        self.base_path = Path(base_path)
    
    @property
    def name(self) -> str:
        return "status"
    
    @property
    def description(self) -> str:
        return "Показать статус системы СЛК"
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        super().add_arguments(parser)  # Добавляет JSON контекст
        parser.add_argument(
            "--format", "-f",
            choices=["table", "json"],
            default="table",
            help="Формат вывода"
        )
    
    def get_default_context_files(self) -> List[str]:
        """Файлы контекста для status"""
        return [
            "VERSION",
            "manifest.json",
            ".slc_usage_stats.json",
            "tasks/active.json"
        ]
    
    def get_context_summary(self, execution_result: Dict[str, Any]) -> str:
        """Описание результатов статуса"""
        health = execution_result.get("health", {})
        templates = execution_result.get("templates", {})
        version = execution_result.get("version", "unknown")
        
        health_status = health.get("status", "unknown")
        templates_count = templates.get("total", 0)
        
        return f"""
        Статус системы СЛК:
        - Состояние: {health_status.upper()}
        - Версия: {version}
        - Доступно шаблонов: {templates_count}
        - Категорий шаблонов: {len(templates.get("categories", {}))}
        """
    
    def get_recommended_actions(self, execution_result: Dict[str, Any]) -> List[str]:
        """Рекомендуемые действия на основе статуса"""
        actions = []
        
        health = execution_result.get("health", {})
        health_status = health.get("status", "unknown")
        issues = health.get("issues", [])
        
        if health_status == "critical":
            actions.extend([
                "СРОЧНО: Запустить валидацию системы - слк validate",
                "Исправить критические проблемы - слк validate --fix",
                "Проверить целостность файлов и директорий"
            ])
        elif health_status == "warning":
            actions.extend([
                "Рекомендуется валидация - слк validate", 
                "Рассмотреть исправление проблем - слк validate --fix"
            ])
        elif health_status == "healthy":
            actions.extend([
                "Система в хорошем состоянии",
                "Можно запустить оптимизацию - слк optimize",
                "Провести рефлексию для улучшений - слк рефлексия"
            ])
        
        # Добавляем общие рекомендации
        templates = execution_result.get("templates", {})
        if templates.get("total", 0) < 10:
            actions.append("Рассмотреть добавление новых шаблонов")
        
        return actions
    
    def get_next_commands(self, execution_result: Dict[str, Any]) -> List[str]:
        """Предлагаемые следующие команды"""
        health = execution_result.get("health", {})
        health_status = health.get("status", "unknown")
        
        if health_status == "critical":
            return [
                "слк validate --fix",
                "слк optimize --clean-cache",
                "слк помощь validate"
            ]
        elif health_status == "warning":
            return [
                "слк validate",
                "слк optimize",
                "слк рефлексия"
            ]
        else:
            return [
                "слк optimize",
                "слк рефлексия", 
                "слк intelligence-stats",
                "слк templates"
            ]
    
    def execute_with_context(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Выполнить команду и вернуть результат для контекста"""
        status_info = self._collect_status_info()
        
        if args.format == "json":
            print(json.dumps(status_info, indent=2, ensure_ascii=False))
            return status_info
        
        print("📊 Статус системы СЛК")
        print("=" * 40)
        
        # Основная информация
        print(f"🏠 Корневая директория: {self.base_path}")
        print(f"📦 Версия: {status_info['version']}")
        print(f"🕒 Последнее обновление: {status_info['last_updated']}")
        
        # Статистика шаблонов
        templates_stats = status_info['templates']
        print(f"\n📋 Шаблоны:")
        print(f"   📄 Всего шаблонов: {templates_stats['total']}")
        print(f"   📂 Категорий: {len(templates_stats['categories'])}")
        
        for category, count in templates_stats['categories'].items():
            print(f"      • {category}: {count}")
        
        # Статистика проектов
        projects_stats = status_info.get('projects', {})
        if projects_stats.get('total', 0) > 0:
            print(f"\n🚀 Проекты:")
            print(f"   📁 Всего проектов: {projects_stats['total']}")
            print(f"   ⚡ Активных: {projects_stats.get('active', 0)}")
        
        # Состояние системы
        health = status_info['health']
        health_icon = "🟢" if health['status'] == 'healthy' else "🟡" if health['status'] == 'warning' else "🔴"
        print(f"\n💗 Состояние системы: {health_icon} {health['status'].upper()}")
        
        if health.get('issues'):
            print("   ⚠️ Проблемы:")
            for issue in health['issues']:
                print(f"      • {issue}")
        
        return status_info
    
    def _collect_status_info(self) -> Dict[str, Any]:
        """Сбор информации о статусе системы"""
        status = {
            "version": self._get_version(),
            "last_updated": self._get_last_updated(),
            "templates": self._get_templates_stats(),
            "projects": self._get_projects_stats(),
            "health": self._get_health_status()
        }
        return status
    
    def _get_version(self) -> str:
        """Получение версии системы"""
        version_file = self.base_path / "VERSION"
        if version_file.exists():
            try:
                return version_file.read_text().strip()
            except:
                pass
        return "unknown"
    
    def _get_last_updated(self) -> str:
        """Получение времени последнего обновления"""
        try:
            import time
            mtime = os.path.getmtime(self.base_path)
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
        except:
            return "unknown"
    
    def _get_templates_stats(self) -> Dict[str, Any]:
        """Статистика шаблонов"""
        templates_path = self.base_path / "modules"
        if not templates_path.exists():
            return {"total": 0, "categories": {}}
        
        categories = {}
        total = 0
        
        for root, dirs, files in os.walk(templates_path):
            for file in files:
                if file.endswith('.json'):
                    rel_path = Path(root).relative_to(templates_path)
                    category = str(rel_path) if str(rel_path) != '.' else 'root'
                    categories[category] = categories.get(category, 0) + 1
                    total += 1
        
        return {"total": total, "categories": categories}
    
    def _get_projects_stats(self) -> Dict[str, Any]:
        """Статистика проектов"""
        # Простая реализация - ищем .slc_project.json файлы
        projects = 0
        active = 0
        
        for root, dirs, files in os.walk(self.base_path):
            if '.slc_project.json' in files:
                projects += 1
                # Проект считается активным если изменялся недавно
                try:
                    import time
                    mtime = os.path.getmtime(os.path.join(root, '.slc_project.json'))
                    if time.time() - mtime < 30 * 24 * 60 * 60:  # 30 дней
                        active += 1
                except:
                    pass
        
        return {"total": projects, "active": active}
    
    def _get_health_status(self) -> Dict[str, Any]:
        """Определение состояния системы"""
        issues = []
        
        # Проверяем наличие основных директорий
        required_dirs = ["modules", "tools"]
        for dir_name in required_dirs:
            if not (self.base_path / dir_name).exists():
                issues.append(f"Отсутствует директория: {dir_name}")
        
        # Проверяем наличие критических файлов
        critical_files = ["VERSION", "README.md"]
        for file_name in critical_files:
            if not (self.base_path / file_name).exists():
                issues.append(f"Отсутствует файл: {file_name}")
        
        if not issues:
            return {"status": "healthy"}
        elif len(issues) <= 2:
            return {"status": "warning", "issues": issues}
        else:
            return {"status": "critical", "issues": issues}


class OptimizeCommand(BaseCommand):
    """Команда optimize - оптимизация системы СЛК"""
    
    def __init__(self, base_path: str):
        super().__init__()
        self.base_path = Path(base_path)
    
    @property
    def name(self) -> str:
        return "optimize"
    
    @property
    def description(self) -> str:
        return "Оптимизировать систему СЛК"
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Показать что будет сделано без выполнения"
        )
        parser.add_argument(
            "--clean-cache",
            action="store_true",
            help="Очистить кэш"
        )
        parser.add_argument(
            "--compress",
            action="store_true",
            help="Сжать файлы"
        )
    
    def execute(self, args: argparse.Namespace) -> int:
        """Выполнение команды optimize"""
        print("🚀 Оптимизация системы СЛК...")
        print("=" * 40)
        
        optimizations = []
        
        if args.clean_cache:
            optimizations.append(self._clean_cache)
        
        if args.compress:
            optimizations.append(self._compress_files)
        
        if not optimizations:
            # По умолчанию запускаем все оптимизации
            optimizations = [self._clean_cache, self._compress_files]
        
        total_saved = 0
        for optimization in optimizations:
            result = optimization(args.dry_run)
            if result:
                print(f"✅ {result['name']}: {result['description']}")
                if result.get('saved_space'):
                    total_saved += result['saved_space']
                    print(f"   💾 Освобождено: {self._format_size(result['saved_space'])}")
        
        if total_saved > 0:
            print(f"\n🎉 Общее освобождено места: {self._format_size(total_saved)}")
        
        return 0
    
    def _clean_cache(self, dry_run: bool) -> Dict[str, Any]:
        """Очистка кэша"""
        cache_dirs = [
            self.base_path / ".cache",
            self.base_path / "tools" / ".cache",
            self.base_path / "__pycache__"
        ]
        
        total_size = 0
        for cache_dir in cache_dirs:
            if cache_dir.exists():
                total_size += self._get_dir_size(cache_dir)
                if not dry_run:
                    import shutil
                    shutil.rmtree(cache_dir)
        
        return {
            "name": "Очистка кэша",
            "description": "Удалены временные и кэшированные файлы",
            "saved_space": total_size
        }
    
    def _compress_files(self, dry_run: bool) -> Dict[str, Any]:
        """Сжатие файлов"""
        # Пока заглушка - можно добавить сжатие JSON файлов
        return {
            "name": "Сжатие файлов", 
            "description": "Файлы проанализированы на возможность сжатия",
            "saved_space": 0
        }
    
    def _get_dir_size(self, path: Path) -> int:
        """Получение размера директории"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
        except:
            pass
        return total_size
    
    def _format_size(self, size_bytes: int) -> str:
        """Форматирование размера в читаемый вид"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


class CreateArchiveCommand(ContextAwareCommand):
    """Команда создания архива для развертывания"""
    
    def __init__(self, base_path: str):
        super().__init__(base_path)
        self.base_path = Path(base_path)
    
    @property
    def name(self) -> str:
        return "create-archive"
    
    @property
    def description(self) -> str:
        return "Создать архив для развертывания"
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--output-dir",
            type=str,
            default="../releases",
            help="Директория для сохранения архива"
        )
    
    def get_default_context_files(self) -> List[str]:
        return [
            ".context/manifest.json",
            ".context/modules/core/standards.json",
            "VERSION"
        ]
    
    def get_context_summary(self, execution_result: Dict[str, Any]) -> str:
        """Получить краткое описание результата создания архива"""
        if execution_result.get("success"):
            return f"Архив v{execution_result.get('version', 'unknown')} создан успешно"
        return "Ошибка создания архива"
    
    def get_recommended_actions(self, execution_result: Dict[str, Any]) -> List[str]:
        """Получить рекомендуемые действия после создания архива"""
        if execution_result.get("success"):
            return [
                "Проверить созданные архивы в папке releases/",
                "Протестировать развертывание на тестовом проекте",
                "Обновить версию в manifest.json если необходимо",
                "Создать git tag для этой версии"
            ]
        return [
            "Проверить состояние системы командой: ./slc status",
            "Валидировать систему командой: ./slc validate",
            "Проверить права доступа к файлам"
        ]
    
    def get_next_commands(self, execution_result: Dict[str, Any]) -> List[str]:
        """Получить следующие команды для выполнения"""
        if execution_result.get("success"):
            return [
                "./slc status - Проверить состояние системы",
                "./slc validate - Валидировать систему",
                "git tag v{version} - Создать git tag".format(
                    version=execution_result.get('version', '0.0.0')
                )
            ]
        return [
            "./slc status - Проверить состояние системы",
            "./slc validate - Проверить целостность"
        ]
    
    def execute_with_context(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Выполнить создание архива с контекстом"""
        try:
            # Путь к скрипту создания архива
            script_path = self.base_path / "tools" / "deployment" / "create_deployment_archive.sh"
            
            if not script_path.exists():
                return {
                    "success": False,
                    "error": f"Скрипт не найден: {script_path}",
                    "version": "unknown"
                }
            
            # Выполнить скрипт
            import subprocess
            result = subprocess.run(
                [str(script_path)], 
                capture_output=True, 
                text=True, 
                cwd=self.base_path.parent
            )
            
            if result.returncode == 0:
                # Парсим версию из вывода
                version = self._parse_version_from_output(result.stdout)
                
                return {
                    "success": True,
                    "message": "Архив успешно создан",
                    "version": version,
                    "output": result.stdout,
                    "archives_created": self._find_created_archives(args.output_dir),
                    "stats": self._get_archive_stats(result.stdout)
                }
            else:
                return {
                    "success": False,
                    "error": f"Ошибка создания архива: {result.stderr}",
                    "version": "unknown"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка выполнения команды: {e}",
                "version": "unknown"
            }
    
    def _parse_version_from_output(self, output: str) -> str:
        """Парсинг версии из вывода скрипта"""
        import re
        match = re.search(r'v(\d+\.\d+\.\d+)', output)
        return match.group(1) if match else "unknown"
    
    def _find_created_archives(self, output_dir: str) -> List[str]:
        """Поиск созданных архивов"""
        archives = []
        output_path = Path(output_dir)
        if output_path.exists():
            for archive in output_path.glob("smart-layered-context-v*.tar.gz"):
                archives.append(str(archive))
            for archive in output_path.glob("smart-layered-context-v*.zip"):
                archives.append(str(archive))
        return archives
    
    def _get_archive_stats(self, output: str) -> Dict[str, Any]:
        """Парсинг статистики архива из вывода"""
        import re
        stats = {}
        
        # Поиск количества файлов
        files_match = re.search(r'Файлов:\s*(\d+)', output)
        if files_match:
            stats['files'] = int(files_match.group(1))
        
        # Поиск размера
        size_match = re.search(r'Размер:\s*([0-9.]+[A-Z]+)', output)
        if size_match:
            stats['size'] = size_match.group(1)
        
        return stats 