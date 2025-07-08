"""
Команды работы с задачами

Реализует команды: list

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

from common.base_command import BaseCommand, ContextAwareCommand


class ListCommand(ContextAwareCommand):
    """Команда list - список задач проекта с JSON выводом для AI интеграции"""
    
    def __init__(self, base_path: str):
        super().__init__()
        self.base_path = base_path
        self.tasks_path = Path(base_path) / "tasks"
    
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
        
        # Устанавливаем значения по умолчанию если аргументы отсутствуют
        status = getattr(args, 'status', 'active')
        detailed = getattr(args, 'detailed', False)
        format_type = getattr(args, 'format', 'summary')
        
        # Создаем новый объект args с правильными значениями
        fixed_args = argparse.Namespace()
        fixed_args.status = status
        fixed_args.detailed = detailed
        fixed_args.format = format_type
        
        if fixed_args.status in ["active", "all"]:
            self._show_active_tasks(fixed_args)
        
        if fixed_args.status in ["completed", "all"]:
            self._show_completed_tasks(fixed_args)
        
        if fixed_args.status == "all":
            self._show_summary()
        
        # JSON вывод для AI интеграции
        list_result = self._prepare_json_context(fixed_args)
        self.output_json_context(list_result)
        
        return 0
    
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