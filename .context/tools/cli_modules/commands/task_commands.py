"""
Команды работы с задачами

Реализует команды: list, create

Версия: 1.0.0
Создано: 2025-01-16
"""

import json
import argparse
from typing import Dict, List, Any
from pathlib import Path
import sys

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..base_command import BaseCommand, ContextAwareCommand


class ListCommand(BaseCommand):
    """Команда list - список задач проекта с JSON выводом для AI интеграции"""
    
    def __init__(self, base_path: str):
        super().__init__()
        # Если base_path уже включает .context, то tasks прямо в нем
        # Иначе добавляем .context
        base = Path(base_path)
        if base.name == ".context":
            self.tasks_path = base / "tasks"
        else:
            self.tasks_path = base / ".context" / "tasks"
    
    @property
    def name(self) -> str:
        return "list"
    
    @property
    def description(self) -> str:
        return "Показать список задач проекта"
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--status", "-s",
            choices=["active", "completed", "all"],
            default="active",
            help="Статус задач для показа"
        )
        parser.add_argument(
            "--format", "-f",
            choices=["table", "json", "summary"],
            default="summary",
            help="Формат вывода"
        )
        parser.add_argument(
            "--detailed", "-d",
            action="store_true",
            help="Показать подробную информацию"
        )
    
    def execute(self, args: argparse.Namespace) -> int:
        """Выполнение команды list"""
        print("📋 Задачи Smart Layered Context")
        print("=" * 50)
        
        if not self.tasks_path.exists():
            self.print_warning("Папка задач не найдена")
            return 1
        
        # Получаем все задачи
        all_tasks = self._get_all_tasks_data()
        
        # Устанавливаем значения по умолчанию если аргументы отсутствуют
        status = getattr(args, 'status', 'active')
        detailed = getattr(args, 'detailed', False)
        format_type = getattr(args, 'format', 'summary')
        
        # Показываем задачи в зависимости от статуса
        if status in ["active", "all"]:
            self._show_tasks_by_status(all_tasks["active"], "🚀 АКТИВНЫЕ ЗАДАЧИ", format_type, detailed)
        
        if status in ["active", "all"] and all_tasks["pending"]:
            self._show_tasks_by_status(all_tasks["pending"], "📋 ОЖИДАЮЩИЕ ЗАДАЧИ", format_type, detailed)
        
        if status in ["deferred", "all"] and all_tasks["deferred"]:
            self._show_tasks_by_status(all_tasks["deferred"], "⏳ ОТЛОЖЕННЫЕ ЗАДАЧИ", format_type, detailed)
        
        if status in ["completed", "all"]:
            completed_count = len(all_tasks["completed"])
            if completed_count > 0:
                if detailed:
                    self._show_tasks_by_status(all_tasks["completed"], "✅ ЗАВЕРШЕННЫЕ ЗАДАЧИ", format_type, detailed)
                else:
                    print(f"\n✅ ЗАВЕРШЕННЫЕ ЗАДАЧИ: {completed_count} задач")
        
        # Статистика
        if status == "all":
            self._show_tasks_summary(all_tasks)
        
        # JSON вывод для AI интеграции
        list_result = self._prepare_json_context_v2(all_tasks, status)
        self._output_json_context(list_result)
        
        return 0
    
    def _output_json_context(self, data: dict):
        """Выводит JSON контекст для AI интеграции"""
        print("\n" + "=" * 60)
        print("🤖 JSON КОНТЕКСТ ДЛЯ AI:")
        print("=" * 60)
        print(json.dumps(data, ensure_ascii=False, indent=2))
        print("=" * 60)
    
    def _prepare_json_context(self, args: argparse.Namespace) -> dict:
        """Подготовка JSON контекста для AI"""
        active_tasks = self._get_active_tasks_data()
        completed_tasks = self._get_completed_tasks_data()
        
        # Генерируем рекомендации на основе состояния задач
        recommendations = []
        if active_tasks:
            completion = active_tasks.get('completion', '0%')
            if completion == '0%':
                recommendations.append("Есть неначатые задачи - сфокусируйтесь на текущем проекте")
            elif '100%' in completion:
                recommendations.append("Текущий проект завершен - можно начинать новую задачу")
            else:
                recommendations.append("Есть активная задача в процессе - продолжайте работу")
                
            current_focus = active_tasks.get('current_focus', {})
            if current_focus:
                title = current_focus.get('title', '')
                if title:
                    recommendations.append(f"Текущий фокус: {title}")
        else:
            recommendations.append("Нет активных задач - используйте 'слк шаблоны' для начала нового проекта")
        
        next_commands = []
        if active_tasks:
            if active_tasks.get('completion', '0%') == '0%':
                next_commands = ["templates", "intelligent-recommend", "load-context"]
            else:
                next_commands = ["status", "templates", "help"]
        else:
            next_commands = ["templates", "create", "intelligent-recommend"]
        
        # Файлы для загрузки в AI контекст
        suggested_files = []
        if active_tasks:
            suggested_files.append("tasks/active.json")
        if completed_tasks:
            suggested_files.append("tasks/completed/")
        suggested_files.extend(["manifest.json", "modules/core/project.json"])
        
        return {
            "command": "list",
            "status": "completed",
            "tasks_summary": {
                "active_count": 1 if active_tasks else 0,
                "completed_count": len(completed_tasks),
                "total_count": (1 if active_tasks else 0) + len(completed_tasks)
            },
            "active_project": active_tasks.get('project', None) if active_tasks else None,
            "current_focus": active_tasks.get('current_focus', {}).get('title', None) if active_tasks else None,
            "project_phase": active_tasks.get('phase', None) if active_tasks else None,
            "completion": active_tasks.get('completion', None) if active_tasks else None,
            "ai_recommendations": recommendations,
            "next_commands": next_commands,
            "suggested_files_to_load": suggested_files
        }
    
    def _get_active_tasks_data(self) -> dict:
        """Получить данные активных задач"""
        active_file = self.tasks_path / "active.json"
        if not active_file.exists():
            return {}
        
        try:
            with open(active_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _get_completed_tasks_data(self) -> list:
        """Получить данные завершенных задач"""
        completed_path = self.tasks_path / "completed"
        if not completed_path.exists():
            return []
        
        completed_files = list(completed_path.glob("*.json"))
        completed_data = []
        
        for task_file in completed_files:
            try:
                with open(task_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    completed_data.append({
                        "file": task_file.name,
                        "title": data.get('task', {}).get('title', task_file.stem),
                        "status": data.get('task', {}).get('status', 'completed')
                    })
            except Exception:
                continue
        
        return completed_data
    
    def _show_active_tasks(self, args: argparse.Namespace):
        """Показать активные задачи"""
        active_file = self.tasks_path / "active.json"
        
        if not active_file.exists():
            print("\n📋 Активные задачи: не найдены")
            return
        
        try:
            with open(active_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if args.format == "json":
                print(json.dumps(data, indent=2, ensure_ascii=False))
                return
            
            print(f"\n🎯 АКТИВНЫЙ ПРОЕКТ: {data.get('project', 'Unknown')}")
            print(f"📊 Версия: {data.get('version', 'Unknown')}")
            print(f"🏗️ Фаза: {data.get('phase', 'Unknown')}")
            print(f"✅ Завершенность: {data.get('completion', '0%')}")
            print(f"📝 Статус: {data.get('status', 'Unknown')}")
            
            # Текущий фокус
            current_focus = data.get('current_focus', {})
            if current_focus:
                print(f"\n🎯 ТЕКУЩИЙ ФОКУС:")
                print(f"   📋 {current_focus.get('title', 'Unknown')}")
                
                if args.detailed:
                    objectives = current_focus.get('completed_objectives', [])
                    if objectives:
                        print(f"\n✅ Завершенные цели:")
                        for obj in objectives:
                            print(f"   {obj}")
                    
                    new_tasks = current_focus.get('new_tasks_created', [])
                    if new_tasks:
                        print(f"\n📝 Созданные задачи:")
                        for task in new_tasks:
                            print(f"   {task}")
            
            # Фазы проекта
            phases = data.get('phases_completed', [])
            if phases and (args.detailed or args.format == "table"):
                print(f"\n📊 ФАЗЫ ПРОЕКТА:")
                for phase in phases:
                    print(f"   {phase}")
            
        except json.JSONDecodeError:
            self.print_error("Ошибка чтения файла активных задач")
        except Exception as e:
            self.print_error(f"Ошибка: {e}")
    
    def _show_completed_tasks(self, args: argparse.Namespace):
        """Показать завершенные задачи"""
        completed_path = self.tasks_path / "completed"
        
        if not completed_path.exists():
            print("\n📋 Завершенные задачи: не найдены")
            return
        
        completed_files = list(completed_path.glob("*.json"))
        if not completed_files:
            print("\n📋 Завершенные задачи: нет файлов")
            return
        
        print(f"\n✅ ЗАВЕРШЕННЫЕ ЗАДАЧИ ({len(completed_files)}):")
        
        for task_file in sorted(completed_files):
            try:
                with open(task_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                task_name = task_file.stem.replace('_completed', '').replace('_', ' ')
                task_title = data.get('task', {}).get('title', task_name)
                status = data.get('task', {}).get('status', 'Unknown')
                
                print(f"   📄 {task_title}")
                
                if args.detailed:
                    completion = data.get('task', {}).get('completion', 'Unknown')
                    print(f"      📊 Статус: {status}")
                    print(f"      ✅ Завершенность: {completion}")
                    
                    objectives = data.get('task', {}).get('objectives', [])
                    if objectives:
                        completed_count = sum(1 for obj in objectives if obj.startswith('✅'))
                        print(f"      🎯 Цели: {completed_count}/{len(objectives)}")
                
            except Exception as e:
                print(f"   ❌ Ошибка чтения {task_file.name}: {e}")
    
    def _show_summary(self):
        """Показать общую сводку"""
        active_count = 1 if (self.tasks_path / "active.json").exists() else 0
        
        completed_path = self.tasks_path / "completed"
        completed_count = len(list(completed_path.glob("*.json"))) if completed_path.exists() else 0
        
        print(f"\n📊 ОБЩАЯ СВОДКА:")
        print(f"   🎯 Активных задач: {active_count}")
        print(f"   ✅ Завершенных задач: {completed_count}")
        print(f"   📁 Всего задач: {active_count + completed_count}")
        
        print(f"\n💡 Команды:")
        print(f"   ./slc list --detailed - подробная информация")
        print(f"   ./slc list --status completed - показать завершенные")
        print(f"   ./slc list --status all - показать все задачи")
    
    def _get_all_tasks_data(self) -> dict:
        """Получить данные всех задач из папки tasks"""
        all_tasks = {
            "active": [],
            "pending": [],
            "completed": [],
            "deferred": []
        }
        
        if not self.tasks_path.exists():
            return all_tasks
        
        # Сканируем все JSON файлы в корне tasks/
        for task_file in self.tasks_path.glob("*.json"):
            if task_file.name in ["active.json", "history.json"]:
                continue
                
            try:
                with open(task_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Определяем статус задачи
                # Поддерживаем оба формата: task_info и task_data
                task_info = data.get('task_info', {}) or data.get('task_data', {})
                status = task_info.get('status', 'НОВАЯ').upper()
                priority = task_info.get('priority', 'СРЕДНИЙ')
                completion = task_info.get('completion', str(task_info.get('progress', 0)) + '%')
                
                task_data = {
                    "file": task_file.name,
                    "title": task_info.get('title', task_file.stem),
                    "status": status,
                    "priority": priority,
                    "completion": completion,
                    "category": task_info.get('category', 'general'),
                    "created": task_info.get('created', data.get('created', '')),
                    "estimated_time": task_info.get('estimated_time', task_info.get('metadata', {}).get('estimated_duration', 'неизвестно'))
                }
                
                # Классифицируем по статусу
                if status in ['ЗАВЕРШЕНА', 'COMPLETED', 'УСПЕШНО ЗАВЕРШЕНА']:
                    all_tasks["completed"].append(task_data)
                elif status in ['В_ПРОЦЕССЕ', 'АКТИВНАЯ', 'ACTIVE', 'IN_PROGRESS']:
                    all_tasks["active"].append(task_data)
                elif status in ['ОТЛОЖЕНА', 'DEFERRED']:
                    all_tasks["deferred"].append(task_data)
                else:
                    all_tasks["pending"].append(task_data)
                    
            except Exception as e:
                print(f"⚠️ Ошибка чтения {task_file.name}: {e}")
                continue
        
        # Добавляем задачи из completed/
        completed_path = self.tasks_path / "completed"
        if completed_path.exists():
            for task_file in completed_path.glob("*.json"):
                try:
                    with open(task_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    task_info = data.get('task', {}) or data.get('task_info', {})
                    task_data = {
                        "file": f"completed/{task_file.name}",
                        "title": task_info.get('title', task_file.stem),
                        "status": "ЗАВЕРШЕНА",
                        "priority": task_info.get('priority', 'СРЕДНИЙ'),
                        "completion": "100%",
                        "category": task_info.get('category', 'completed'),
                        "created": task_info.get('created', ''),
                        "estimated_time": task_info.get('estimated_time', '')
                    }
                    all_tasks["completed"].append(task_data)
                except Exception:
                    continue
        
        # Добавляем задачи из deferred/
        deferred_path = self.tasks_path / "deferred"
        if deferred_path.exists():
            for task_file in deferred_path.glob("*.json"):
                try:
                    with open(task_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    task_info = data.get('task_info', {})
                    task_data = {
                        "file": f"deferred/{task_file.name}",
                        "title": task_info.get('title', task_file.stem),
                        "status": "ОТЛОЖЕНА",
                        "priority": task_info.get('priority', 'НИЗКИЙ'),
                        "completion": task_info.get('completion', '0%'),
                        "category": task_info.get('category', 'deferred'),
                        "created": task_info.get('created', ''),
                        "estimated_time": task_info.get('estimated_time', '')
                    }
                    all_tasks["deferred"].append(task_data)
                except Exception:
                    continue
        
        return all_tasks 
    
    def _show_tasks_by_status(self, tasks: list, title: str, format_type: str, detailed: bool):
        """Показать задачи определенного статуса"""
        if not tasks:
            return
        
        print(f"\n{title} ({len(tasks)})")
        print("-" * 50)
        
        if format_type == "json":
            print(json.dumps(tasks, indent=2, ensure_ascii=False))
            return
        
        for task in tasks:
            priority_emoji = {
                'КРИТИЧЕСКИЙ': '🔴',
                'ВЫСОКИЙ': '🟠', 
                'СРЕДНИЙ': '🟡',
                'НИЗКИЙ': '🟢'
            }.get(task['priority'], '⚪')
            
            completion = task['completion']
            completion_emoji = '✅' if completion == '100%' else '🔄' if '0%' not in completion else '⏸️'
            
            print(f"  {priority_emoji} {completion_emoji} {task['title']}")
            
            if detailed:
                print(f"     📁 {task['file']}")
                print(f"     📊 {task['completion']} | 🏷️ {task['category']}")
                if task['estimated_time'] != 'неизвестно':
                    print(f"     ⏱️ {task['estimated_time']}")
                print()
    
    def _show_tasks_summary(self, all_tasks: dict):
        """Показать общую статистику задач"""
        active_count = len(all_tasks["active"])
        pending_count = len(all_tasks["pending"]) 
        deferred_count = len(all_tasks["deferred"])
        completed_count = len(all_tasks["completed"])
        total_count = active_count + pending_count + deferred_count + completed_count
        
        print("\n" + "=" * 50)
        print("📊 СТАТИСТИКА ЗАДАЧ")
        print("=" * 50)
        print(f"🚀 Активные:     {active_count}")
        print(f"📋 Ожидающие:    {pending_count}")
        print(f"⏳ Отложенные:   {deferred_count}")
        print(f"✅ Завершенные:  {completed_count}")
        print(f"📊 Всего:        {total_count}")
        
        if total_count > 0:
            completion_rate = (completed_count / total_count) * 100
            print(f"📈 Завершенность: {completion_rate:.1f}%")
    
    def _prepare_json_context_v2(self, all_tasks: dict, status: str) -> dict:
        """Подготовка улучшенного JSON контекста для AI"""
        active_count = len(all_tasks["active"])
        pending_count = len(all_tasks["pending"])
        deferred_count = len(all_tasks["deferred"])
        completed_count = len(all_tasks["completed"])
        total_count = active_count + pending_count + deferred_count + completed_count
        
        # Генерируем рекомендации на основе состояния задач
        recommendations = []
        current_focus = None
        
        if active_count > 0:
            active_task = all_tasks["active"][0]
            recommendations.append(f"Есть активная задача: {active_task['title']}")
            current_focus = active_task['title']
            
            if active_task['completion'] == '0%':
                recommendations.append("Сфокусируйтесь на активной задаче")
            elif active_task['completion'] == '100%':
                recommendations.append("Активная задача завершена - обновите статус")
        
        if pending_count > 0:
            recommendations.append(f"Есть {pending_count} ожидающих задач - выберите следующую для работы")
        
        if active_count == 0 and pending_count == 0:
            recommendations.append("Нет активных задач - используйте 'слк шаблоны' для создания новой")
        
        # Следующие команды
        next_commands = []
        if active_count > 0:
            next_commands = ["load-context", "status", "templates"]
        elif pending_count > 0:
            next_commands = ["load-context", "templates", "intelligent-recommend"]
        else:
            next_commands = ["templates", "create", "help"]
        
        # Файлы для загрузки
        suggested_files = ["tasks/active.json", "manifest.json", "modules/core/project.json"]
        if active_count > 0:
            active_file = all_tasks["active"][0]["file"]
            suggested_files.insert(0, f"tasks/{active_file}")
        
        return {
            "command": "list",
            "status": "completed",
            "tasks_summary": {
                "active_count": active_count,
                "pending_count": pending_count,
                "deferred_count": deferred_count,
                "completed_count": completed_count,
                "total_count": total_count
            },
            "current_focus": current_focus,
            "top_priority_tasks": [
                task["title"] for task in (all_tasks["active"] + all_tasks["pending"])[:3]
            ],
            "ai_recommendations": recommendations,
            "next_commands": next_commands,
            "suggested_files_to_load": suggested_files,
            "task_details": {
                "active": all_tasks["active"][:3],  # Топ 3 активные
                "pending": all_tasks["pending"][:5]  # Топ 5 ожидающие
            }
        }


class CreateCommand(ContextAwareCommand):
    """Команда create - создание новой задачи"""
    
    def __init__(self, base_path: str):
        super().__init__(base_path)
        # Если base_path уже включает .context, то tasks прямо в нем
        # Иначе добавляем .context
        base = Path(base_path)
        if base.name == ".context":
            self.tasks_path = base / "tasks"
        else:
            self.tasks_path = base / ".context" / "tasks"
        self.template_path = self.tasks_path / "templates" / "task_template.json"
        self.active_file = self.tasks_path / "active.json"
    
    @property
    def name(self) -> str:
        return "create"
    
    @property
    def description(self) -> str:
        return "Создать новую задачу"
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "title",
            help="Название задачи"
        )
        parser.add_argument(
            "--category", "-c",
            choices=["ai_development", "refactoring", "optimization", "testing", "documentation", "infrastructure"],
            default="ai_development",
            help="Категория задачи"
        )
        parser.add_argument(
            "--priority", "-p",
            choices=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
            default="MEDIUM",
            help="Приоритет задачи"
        )
        parser.add_argument(
            "--archive", "-a",
            action="store_true",
            default=True,
            help="Архивировать текущую активную задачу перед созданием новой (по умолчанию: True)"
        )
        parser.add_argument(
            "--no-archive",
            action="store_true",
            help="НЕ архивировать текущую задачу"
        )
        parser.add_argument(
            "--force", "-f",
            action="store_true",
            help="Принудительно создать задачу, перезаписав активную"
        )
        parser.add_argument(
            "--description", "-d",
            help="Подробное описание задачи"
        )
        parser.add_argument(
            "--estimated-time", "-t",
            help="Оценочное время выполнения (например: '2 недели', '3 дня')"
        )
    
    def execute(self, args: argparse.Namespace) -> int:
        """Выполнение команды create"""
        print(f"🆕 Создание новой задачи: {args.title}")
        print("=" * 60)
        
        # Проверяем существование шаблона
        if not self.template_path.exists():
            self.print_error(f"Шаблон задачи не найден: {self.template_path}")
            return 1
        
        # Определяем нужно ли архивировать (по умолчанию True, если не указан --no-archive)
        should_archive = not getattr(args, 'no_archive', False)
        
        # Проверяем активную задачу
        if self.active_file.exists() and not args.force and not should_archive:
            self.print_error("Активная задача уже существует")
            print("💡 Используйте:")
            print("   --archive (-a) для архивирования текущей задачи")
            print("   --force (-f) для принудительной перезаписи")
            print("   --no-archive для создания без архивирования")
            return 1
        
        # Архивируем текущую задачу если нужно
        if should_archive and self.active_file.exists():
            if not self._archive_current_task():
                return 1
        
        # Создаем новую задачу
        return self._create_new_task(args)
    
    def _archive_current_task(self) -> bool:
        """Архивирует текущую активную задачу"""
        try:
            print("📦 Архивирование текущей активной задачи...")
            
            # Читаем текущую задачу
            with open(self.active_file, 'r', encoding='utf-8') as f:
                current_task = json.load(f)
            
            # Добавляем информацию о завершении
            from datetime import datetime
            current_task["completion_date"] = datetime.now().isoformat()
            current_task["status"] = "ARCHIVED"
            
            # Создаем имя файла для архива
            completed_dir = self.tasks_path / "completed"
            completed_dir.mkdir(exist_ok=True)
            
            # Генерируем уникальное имя файла
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            task_ref = current_task.get("active_task_reference", {})
            
            # Безопасное получение названия задачи
            task_title = "unknown_task"
            if task_ref and isinstance(task_ref, dict):
                metadata = task_ref.get("metadata", {})
                if metadata and isinstance(metadata, dict):
                    task_title = metadata.get("title", "unknown_task")
            
            # Очищаем название для файла
            safe_title = "".join(c for c in str(task_title) if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_').lower()[:30] if safe_title else "unknown_task"
            
            archive_file = completed_dir / f"{safe_title}_{timestamp}.json"
            
            # Сохраняем в архив
            with open(archive_file, 'w', encoding='utf-8') as f:
                json.dump(current_task, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Задача заархивирована: {archive_file.name}")
            return True
            
        except Exception as e:
            self.print_error(f"Ошибка архивирования: {e}")
            return False
    
    def _create_new_task(self, args: argparse.Namespace) -> bool:
        """Создает новую задачу из шаблона"""
        try:
            # Читаем шаблон
            with open(self.template_path, 'r', encoding='utf-8') as f:
                template = json.load(f)
            
            # Генерируем уникальные идентификаторы
            from datetime import datetime
            timestamp = datetime.now()
            task_id = f"TASK_{timestamp.strftime('%Y%m%d_%H%M%S')}"
            iso_timestamp = timestamp.isoformat()
            
            # Создаем имя файла для новой задачи
            safe_title = "".join(c for c in args.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title.replace(' ', '_').lower()[:40]
            task_filename = f"{safe_title}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            task_file_path = self.tasks_path / task_filename
            
            # Заполняем шаблон данными
            task_data = template.copy()
            
            # Обновляем основную информацию о задаче
            if "task_template" in task_data:
                task_info = task_data["task_template"]
                task_info["id"] = task_id
                task_info["title"] = args.title
                task_info["category"] = args.category
                task_info["priority"] = args.priority
                task_info["status"] = "ACTIVE"
                task_info["progress"] = 0
                
                # Обновляем метаданные
                if "metadata" in task_info:
                    task_info["metadata"]["created"] = iso_timestamp
                    task_info["metadata"]["updated"] = iso_timestamp
                    task_info["metadata"]["estimated_duration"] = args.estimated_time or "не указано"
                
                # Добавляем описание если указано
                if args.description:
                    task_info["description"] = args.description
                
                # Обновляем навигационную систему
                if "navigation_system" in task_data:
                    task_data["navigation_system"]["current_file"] = f".context/tasks/{task_filename}"
                    task_data["navigation_system"]["purpose"] = f"Задача: {args.title}"
                    task_data["navigation_system"]["ai_context"] = f"Активная задача СЛК: {args.title}"
                
                # Автоматически заполняем context_loading_policy.auto_load в зависимости от категории
                if "context" in task_info and "context_loading_policy" in task_info["context"]:
                    base_files = [
                        "modules/core/manifest.json",
                        "modules/core/standards.json", 
                        "modules/core/development_standards.json",
                        "modules/core/project.json"
                    ]
                    
                    # Добавляем специфичные для категории файлы
                    category_files = {
                        "ai_development": [
                            "modules/ai_ml/prompt_engineering.json",
                            "modules/ai_ml/ai_agent_development.json"
                        ],
                        "refactoring": [
                            "modules/languages/python/python_development.json",
                            "modules/core/development_standards.json"
                        ],
                        "testing": [
                            "modules/languages/python/python_development.json",
                            "modules/core/development_standards.json"
                        ],
                        "documentation": [
                            "modules/methodologies/documentation_systems.json",
                            "modules/methodologies/obsidian_workflow.json"
                        ],
                        "infrastructure": [
                            "modules/core/development_standards.json"
                        ],
                        "optimization": [
                            "modules/languages/python/python_development.json"
                        ]
                    }
                    
                    # Автоматическое определение Python/DAP задач по ключевым словам
                    title_lower = args.title.lower()
                    if any(keyword in title_lower for keyword in ["python", "dap", "биндинг", "binding"]):
                        category_files["python_dap"] = [
                            "modules/projects/dap_sdk_project.json",
                            "modules/languages/python/python_development.json",
                            "modules/languages/python/knowledge_base/dap_sdk_binding_standards.json"
                        ]
                        args.category = "python_dap"  # Обновляем категорию
                    
                    # Объединяем базовые и категорийные файлы
                    auto_load_files = base_files[:]
                    if args.category in category_files:
                        auto_load_files.extend(category_files[args.category])
                    
                    # Убираем дубликаты
                    auto_load_files = list(dict.fromkeys(auto_load_files))
                    
                    # Обновляем auto_load в задаче
                    task_info["context"]["context_loading_policy"]["auto_load"] = auto_load_files
                    
                    print(f"🔗 Автоматически добавлено {len(auto_load_files)} файлов в auto_load для категории '{args.category}'")
            
            # Сохраняем файл задачи
            with open(task_file_path, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, indent=2, ensure_ascii=False)
            
            # Создаем/обновляем active.json со ссылкой на новую задачу
            active_data = {
                "active_task_reference": {
                    "$ref": f".context/tasks/{task_filename}",
                    "task_type": "custom_task",
                    "priority": args.priority,
                    "status": "ACTIVE",
                    "activated_at": iso_timestamp
                },
                "metadata": {
                    "title": args.title,
                    "task_id": task_id,
                    "category": args.category,
                    "description": args.description or "Новая задача",
                    "estimated_duration": args.estimated_time or "не указано",
                    "current_focus": args.title
                },
                "execution_status": {
                    "phase": "НАЧАЛЬНАЯ",
                    "current_task": "Настройка и планирование",
                    "progress": "0%",
                    "next_action": "Определить детальный план выполнения задачи",
                    "last_update": iso_timestamp,
                    "completed_steps": [
                        f"✅ Создана задача: {args.title}",
                        f"✅ Установлен приоритет: {args.priority}",
                        f"✅ Категория: {args.category}"
                    ]
                }
            }
            
            # Сохраняем active.json
            with open(self.active_file, 'w', encoding='utf-8') as f:
                json.dump(active_data, f, indent=2, ensure_ascii=False)
            
            # Выводим результат
            print(f"✅ Задача успешно создана!")
            print(f"📋 Название: {args.title}")
            print(f"🆔 ID: {task_id}")
            print(f"🏷️ Категория: {args.category}")
            print(f"📊 Приоритет: {args.priority}")
            print(f"📁 Файл задачи: {task_filename}")
            
            if args.description:
                print(f"📝 Описание: {args.description}")
            
            if args.estimated_time:
                print(f"⏱️ Оценочное время: {args.estimated_time}")
            
            print(f"\n🚀 Следующие шаги:")
            print(f"   ./slc load-context \"{args.title}\" - загрузить контекст задачи")
            print(f"   ./slc list - посмотреть статус задач")
            print(f"   ./slc status - проверить состояние системы")
            
            # JSON контекст для AI
            create_result = {
                "command": "create",
                "status": "completed",
                "task_created": {
                    "id": task_id,
                    "title": args.title,
                    "category": args.category,
                    "priority": args.priority,
                    "file": task_filename,
                    "created_at": iso_timestamp
                },
                "ai_recommendations": [
                    f"Новая задача '{args.title}' создана и активирована",
                    "Используйте 'слк контекст' для загрузки контекста задачи",
                    "Определите детальный план выполнения задачи"
                ],
                "next_commands": ["load-context", "list", "status"],
                "suggested_files_to_load": [
                    f"tasks/{task_filename}",
                    "tasks/active.json",
                    "manifest.json"
                ]
            }
            
            self.output_json_context(create_result)
            
            return 0
            
        except Exception as e:
            self.print_error(f"Ошибка создания задачи: {e}")
            return 1 