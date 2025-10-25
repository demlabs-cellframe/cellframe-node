"""
Команды работы с шаблонами

Реализует команды: templates, search, info, create, recommend

Версия: 1.0.0
Создано: 2025-01-16
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..base_command import BaseCommand
from core.template_manager import TemplateManager


class TemplatesCommand(BaseCommand):
    """Команда templates - список доступных шаблонов"""
    
    def __init__(self, base_path: str):
        super().__init__()
        self.template_manager = TemplateManager(base_path)
    
    @property
    def name(self) -> str:
        return "templates"
    
    @property
    def description(self) -> str:
        return "Показать список доступных шаблонов"
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--category", "-c",
            help="Показать шаблоны только указанной категории"
        )
        parser.add_argument(
            "--format", "-f",
            choices=["table", "json"],
            default="table",
            help="Формат вывода"
        )
    
    def execute(self, args: argparse.Namespace) -> int:
        """Выполнение команды templates"""
        print("📋 Доступные шаблоны Smart Layered Context")
        print("=" * 50)
        
        templates = self.template_manager.list_templates(args.category)
        
        if args.format == "json":
            print(json.dumps(templates, indent=2, ensure_ascii=False))
            return 0
        
        if not any(templates.values()):
            self.print_warning("Шаблоны не найдены")
            return 1
        
        total_templates = 0
        for category, template_list in templates.items():
            if template_list:
                print(f"\n📂 {category.upper()}:")
                for template in template_list:
                    print(f"   📄 {template}")
                    total_templates += 1
        
        print(f"\n📊 Всего найдено шаблонов: {total_templates}")
        return 0


class SearchCommand(BaseCommand):
    """Команда search - поиск шаблонов по ключевым словам"""
    
    def __init__(self, base_path: str):
        super().__init__()
        self.template_manager = TemplateManager(base_path)
    
    @property
    def name(self) -> str:
        return "search"
    
    @property
    def description(self) -> str:
        return "Поиск шаблонов по ключевым словам"
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "query",
            help="Поисковый запрос"
        )
        parser.add_argument(
            "--format", "-f",
            choices=["table", "json"],
            default="table",
            help="Формат вывода"
        )
    
    def execute(self, args: argparse.Namespace) -> int:
        """Выполнение команды search"""
        print(f"🔍 Поиск шаблонов: '{args.query}'")
        print("=" * 50)
        
        results = self.template_manager.search_templates(args.query)
        
        if args.format == "json":
            print(json.dumps(results, indent=2, ensure_ascii=False))
            return 0
        
        if not any(results.values()):
            self.print_warning(f"По запросу '{args.query}' ничего не найдено")
            print("\n💡 Попробуйте:")
            print("   • Более общий запрос")
            print("   • Другие ключевые слова")
            print("   • python3 tools/scripts/slc_cli.py list - для просмотра всех шаблонов")
            return 1
        
        total_found = 0
        for category, template_list in results.items():
            print(f"\n📂 {category.upper()}:")
            for template in template_list:
                print(f"   📄 {template}")
                total_found += 1
        
        print(f"\n🎯 Найдено совпадений: {total_found}")
        return 0


class InfoCommand(BaseCommand):
    """Команда info - подробная информация о шаблоне"""
    
    def __init__(self, base_path: str):
        super().__init__()
        self.template_manager = TemplateManager(base_path)
    
    @property
    def name(self) -> str:
        return "info"
    
    @property
    def description(self) -> str:
        return "Показать подробную информацию о шаблоне"
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "template_path",
            help="Путь к шаблону (например: ai_ml/prompt_engineering.json)"
        )
        parser.add_argument(
            "--format", "-f",
            choices=["table", "json"],
            default="table",
            help="Формат вывода"
        )
    
    def execute(self, args: argparse.Namespace) -> int:
        """Выполнение команды info"""
        template_info = self.template_manager.get_template_info(args.template_path)
        
        if not template_info:
            self.print_error(f"Шаблон не найден: {args.template_path}")
            return 1
        
        if template_info.get("error"):
            self.print_error(f"Ошибка чтения шаблона: {template_info['error']}")
            return 1
        
        if args.format == "json":
            print(json.dumps(template_info, indent=2, ensure_ascii=False))
            return 0
        
        print(f"📋 Информация о шаблоне: {args.template_path}")
        print("=" * 60)
        print(f"📄 Название: {template_info.get('name', 'Unknown')}")
        print(f"📝 Описание: {template_info.get('description', 'No description')}")
        print(f"🏷️  Версия: {template_info.get('version', '1.0.0')}")
        print(f"🎯 Домен: {template_info.get('domain', 'unknown')}")
        print(f"📊 Применимость: {template_info.get('applicability', 'Unknown')}")
        
        target_projects = template_info.get('target_projects', [])
        if target_projects:
            print(f"\n🎯 Целевые проекты:")
            for project in target_projects:
                print(f"   • {project}")
        
        print(f"\n💡 Создание проекта:")
        print(f"   python3 tools/scripts/slc_cli.py create {args.template_path} my-project")
        
        return 0


class TplCreateCommand(BaseCommand):
    """Команда tpl-create - создание проекта из шаблона"""
    
    def __init__(self, base_path: str):
        super().__init__()
        self.template_manager = TemplateManager(base_path)
        # Импортируем ProjectGenerator здесь чтобы избежать циклических импортов
        from ..core.project_generator import ProjectGenerator
        self.project_generator = ProjectGenerator(base_path)
    
    @property
    def name(self) -> str:
        return "tpl-create"
    
    @property
    def description(self) -> str:
        return "Создать проект на основе шаблона"
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "template_path",
            help="Путь к шаблону (например: ai_ml/prompt_engineering.json)"
        )
        parser.add_argument(
            "project_name",
            help="Имя создаваемого проекта"
        )
        parser.add_argument(
            "--output-dir", "-o",
            default=".",
            help="Директория для создания проекта (по умолчанию: текущая)"
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Перезаписать существующий проект"
        )
    
    def validate_args(self, args: argparse.Namespace) -> bool:
        """Валидация аргументов команды create"""
        # Проверка имени проекта
        if not args.project_name.strip():
            self.print_error("Имя проекта не может быть пустым")
            return False
        
        # Проверка на недопустимые символы
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in args.project_name for char in invalid_chars):
            self.print_error(f"Имя проекта содержит недопустимые символы: {', '.join(invalid_chars)}")
            return False
        
        return True
    
    def execute(self, args: argparse.Namespace) -> int:
        """Выполнение команды create"""
        if not self.validate_args(args):
            return 1
        
        print(f"🚀 Создание проекта '{args.project_name}' из шаблона {args.template_path}")
        print("=" * 70)
        
        # Проверяем существование шаблона
        template_info = self.template_manager.get_template_info(args.template_path)
        if not template_info or template_info.get("error"):
            self.print_error(f"Шаблон не найден или недоступен: {args.template_path}")
            return 1
        
        # Проверяем существование целевой директории
        from pathlib import Path
        output_path = Path(args.output_dir) / args.project_name
        
        if output_path.exists() and not args.force:
            self.print_error(f"Директория уже существует: {output_path}")
            print("💡 Используйте --force для перезаписи")
            return 1
        
        # Создаем проект с помощью ProjectGenerator
        print(f"📋 Шаблон: {template_info.get('name', 'Unknown')}")
        print(f"📁 Целевая директория: {output_path}")
        
        result = self.project_generator.create_project(
            args.template_path,
            args.project_name, 
            args.output_dir,
            args.force
        )
        
        if result["success"]:
            self.print_success(f"Проект '{args.project_name}' успешно создан!")
            print(f"📁 Расположение: {result['project_path']}")
            print(f"📋 Шаблон: {result['template_name']}")
            print(f"📄 Создано файлов: {result['files_created']}")
            
            print(f"\n🚀 Следующие шаги:")
            print(f"   cd {result['project_path']}")
            print(f"   # Следуйте инструкциям в README.md")
            return 0
        else:
            self.print_error(f"Ошибка создания проекта: {result['error']}")
            return 1 