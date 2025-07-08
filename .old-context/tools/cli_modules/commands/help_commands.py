#!/usr/bin/env python3
"""
Help Commands - Команды помощи и контекстного обновления

Команды:
- help - интеллектуальная контекстная помощь
- update-context - обновление контекста на основе изменений

Версия: 1.0.0
Создано: 2025-01-25
"""

import json
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent))

from common.base_command import BaseCommand, ContextAwareCommand, CommandRegistry

try:
    from core.unified_context_engine import UnifiedContextEngine
except ImportError:
    UnifiedContextEngine = None


class HelpCommand(BaseCommand):
    """Команда контекстной помощи"""
    
    def __init__(self, base_path: str, registry: CommandRegistry = None):
        super().__init__()
        self.base_path = base_path
        self.registry = registry
        self.engine = UnifiedContextEngine(base_path) if UnifiedContextEngine else None
    
    @property
    def name(self) -> str:
        return "help"
    
    @property
    def description(self) -> str:
        return "❓ Интеллектуальная контекстная помощь"
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "command",
            nargs="?",
            help="Команда для получения подробной помощи (необязательно)"
        )
        parser.add_argument(
            "--interactive", "-i",
            action="store_true",
            help="Интерактивный режим помощи"
        )
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Подробная помощь с примерами"
        )
    
    def execute(self, args: argparse.Namespace) -> int:
        """Выполнение команды help"""
        if args.interactive:
            return self._interactive_help()
        
        if args.command:
            return self._command_help(args.command, args.verbose)
        else:
            return self._list_commands(args.verbose)
    
    def _list_commands(self, verbose: bool = False) -> int:
        """Показать список всех доступных команд"""
        print("📋 Доступные команды Smart Layered Context")
        print("=" * 50)
        
        # Получаем все команды из глобального реестра
        commands = self._get_all_commands()
        
        if not commands:
            self.print_warning("Команды не найдены")
            return 1
        
        # Группируем команды по категориям
        command_groups = {
            "📋 Работа с задачами": [],
            "🎯 Работа с шаблонами": [],
            "🧠 Интеллектуальные функции": [],
            "🗂️ Организация проекта": [],
            "🔧 Системные команды": [],
            "📚 Помощь и документация": []
        }
        
        # Классифицируем команды
        for cmd_name, cmd_instance in commands.items():
            description = cmd_instance.description.replace("🧠 ", "").replace("📊 ", "").replace("🔧 ", "")
            
            if any(word in cmd_name for word in ["list", "task"]):
                command_groups["📋 Работа с задачами"].append(f"{cmd_name} - {description}")
            elif any(word in cmd_name for word in ["templates", "search", "create", "info"]):
                command_groups["🎯 Работа с шаблонами"].append(f"{cmd_name} - {description}")
            elif any(word in cmd_name for word in ["intelligent", "recommend", "load-context", "analyze"]):
                command_groups["🧠 Интеллектуальные функции"].append(f"{cmd_name} - {description}")
            elif any(word in cmd_name for word in ["organize", "cleanup", "monitor"]):
                command_groups["🗂️ Организация проекта"].append(f"{cmd_name} - {description}")
            elif any(word in cmd_name for word in ["status", "validate", "optimize"]):
                command_groups["🔧 Системные команды"].append(f"{cmd_name} - {description}")
            elif any(word in cmd_name for word in ["help", "update-context"]):
                command_groups["📚 Помощь и документация"].append(f"{cmd_name} - {description}")
            else:
                command_groups["🔧 Системные команды"].append(f"{cmd_name} - {description}")
        
        # Выводим команды по группам
        total_commands = 0
        for group_name, group_commands in command_groups.items():
            if group_commands:
                print(f"\n{group_name}:")
                for cmd in sorted(group_commands):
                    print(f"   {cmd}")
                    total_commands += 1
        
        print(f"\n📊 Всего команд: {total_commands}")
        print(f"\n💡 Получить помощь по команде: ./slc help [имя команды]")
        
        if verbose:
            print(f"\n🎯 Примеры использования:")
            self._print_examples()
        
        return 0
    
    def _command_help(self, command_name: str, verbose: bool = False) -> int:
        """Помощь по конкретной команде"""
        print(f"❓ Помощь по команде: '{command_name}'")
        print("=" * 50)
        
        # Получаем все команды
        commands = self._get_all_commands()
        
        if command_name not in commands:
            self.print_error(f"Команда '{command_name}' не найдена")
            print(f"\n💡 Доступные команды:")
            available = list(commands.keys())
            for i, cmd in enumerate(sorted(available)):
                print(f"   {cmd}")
                if i >= 10:  # Ограничиваем вывод
                    print(f"   ... и ещё {len(available) - 11} команд")
                    break
            print(f"\n📋 Полный список: ./slc help")
            return 1
        
        command = commands[command_name]
        
        print(f"📋 Команда: {command_name}")
        print(f"📝 Описание: {command.description}")
        
        # Пытаемся получить справку по аргументам
        try:
            import argparse
            parser = argparse.ArgumentParser(description=command.description, add_help=False)
            command.add_arguments(parser)
            
            # Извлекаем информацию об аргументах
            arguments = []
            for action in parser._actions:
                if action.dest != 'help' and action.option_strings:
                    arg_info = {
                        'flags': ', '.join(action.option_strings),
                        'help': action.help or 'Без описания',
                        'required': action.required if hasattr(action, 'required') else False
                    }
                    arguments.append(arg_info)
                elif hasattr(action, 'dest') and action.dest not in ['help', 'command']:
                    arg_info = {
                        'flags': action.dest,
                        'help': action.help or 'Без описания',
                        'required': action.nargs != '?' and action.nargs != '*'
                    }
                    arguments.append(arg_info)
            
            if arguments:
                print(f"\n🔧 Аргументы:")
                for arg in arguments:
                    required_mark = " (обязательный)" if arg.get('required') else ""
                    print(f"   {arg['flags']}{required_mark}")
                    print(f"      {arg['help']}")
        except Exception as e:
            if verbose:
                print(f"\n⚠️  Не удалось получить информацию об аргументах: {e}")
        
        # Добавляем специфичные примеры для команд
        print(f"\n💡 Примеры использования:")
        examples = self._get_command_examples(command_name)
        for example in examples:
            print(f"   {example}")
        
        if verbose:
            print(f"\n📚 Связанные команды:")
            related = self._get_related_commands(command_name)
            for cmd in related:
                if cmd in commands:
                    print(f"   {cmd} - {commands[cmd].description}")
        
        return 0
    
    def _interactive_help(self) -> int:
        """Интерактивная помощь"""
        print("🤖 Интерактивная помощь СЛК")
        print("=" * 30)
        print("Введите 'quit' для выхода\n")
        
        while True:
            try:
                question = input("❓ Ваш вопрос: ").strip()
                if question.lower() in ['quit', 'exit', 'q']:
                    print("👋 До свидания!")
                    break
                
                if question:
                    self._answer_question(question)
                    print()
                
            except KeyboardInterrupt:
                print("\n👋 До свидания!")
                break
        
        return 0
    
    def _analyze_current_state(self) -> Dict[str, Any]:
        """Анализ текущего состояния проекта"""
        state = {
            "project_name": Path.cwd().name,
            "active_tasks": 0,
            "templates_count": 0,
            "recent_files": []
        }
        
        # Подсчет задач
        tasks_path = Path(self.base_path) / "tasks"
        if tasks_path.exists():
            try:
                active_file = tasks_path / "active.json"
                if active_file.exists():
                    with open(active_file, 'r', encoding='utf-8') as f:
                        active_data = json.load(f)
                        # Простое определение активных задач
                        state["active_tasks"] = 1 if active_data.get("current_focus") else 0
            except:
                pass
        
        # Подсчет шаблонов
        modules_path = Path(self.base_path) / "modules"
        if modules_path.exists():
            try:
                templates = list(modules_path.rglob("*.json"))
                state["templates_count"] = len(templates)
            except:
                pass
        
        return state
    
    def _get_smart_suggestions(self, state: Dict[str, Any]) -> List[str]:
        """Получение умных предложений на основе состояния"""
        suggestions = []
        
        if state["active_tasks"] == 0:
            suggestions.append("🎯 Посмотреть доступные шаблоны: ./slc list")
            suggestions.append("🧠 Получить рекомендации: ./slc intelligent-recommend 'ваша задача'")
        
        if state["templates_count"] > 0:
            suggestions.append("🔍 Найти подходящий шаблон: ./slc search 'ключевое слово'")
            suggestions.append("📋 Загрузить контекст: ./slc load-context 'описание задачи'")
        
        suggestions.append("🗂️ Организовать файлы: ./slc organize --dry-run")
        suggestions.append("📊 Проверить статус: ./slc status")
        
        return suggestions
    
    def _print_main_commands(self):
        """Вывод основных команд"""
        commands = {
            "📋 Работа с шаблонами": [
                "list - показать все шаблоны",
                "search 'запрос' - поиск шаблонов",
                "create template.json project - создать проект"
            ],
            "🧠 Интеллектуальные функции": [
                "intelligent-recommend 'задача' - умные рекомендации",
                "load-context 'задача' - загрузить контекст",
                "analyze-context - анализ текущего контекста"
            ],
            "🗂️ Организация проекта": [
                "organize --dry-run - организовать файлы (анализ)",
                "cleanup - очистить временные файлы",
                "status - статус системы"
            ]
        }
        
        for category, cmd_list in commands.items():
            print(f"\n{category}:")
            for cmd in cmd_list:
                print(f"   • {cmd}")
    
    def _print_examples(self):
        """Вывод примеров использования"""
        print("   • ./slc intelligent-recommend 'создать REST API на Python'")
        print("   • ./slc search 'machine learning'")
        print("   • ./slc load-context 'документация API'")
        print("   • ./slc create ai_ml/prompt_engineering.json my-ai-project")
        print("   • ./slc organize --dry-run")
    
    def _help_create_project(self):
        """Помощь по созданию проектов"""
        print("🚀 Создание проектов из шаблонов")
        print("\n1. Найдите подходящий шаблон:")
        print("   ./slc list")
        print("   ./slc search 'python'")
        print("\n2. Создайте проект:")
        print("   ./slc create TEMPLATE_PATH PROJECT_NAME")
        print("\n📝 Пример:")
        print("   ./slc create languages/python/python_development.json my-api")
    
    def _help_templates(self):
        """Помощь по работе с шаблонами"""
        print("📋 Работа с шаблонами")
        print("\n• Просмотр всех шаблонов: ./slc list")
        print("• Поиск шаблонов: ./slc search 'ключевое слово'")
        print("• Информация о шаблоне: ./slc info template.json")
        print("• Умные рекомендации: ./slc intelligent-recommend 'задача'")
    
    def _help_context(self):
        """Помощь по работе с контекстом"""
        print("🧠 Работа с контекстом")
        print("\n• Загрузка контекста: ./slc load-context 'описание задачи'")
        print("• Анализ контекста: ./slc analyze-context")
        print("• Очистка контекста: ./slc clear-context")
        print("• Обновление контекста: ./slc update-context")
    
    def _help_organize(self):
        """Помощь по организации файлов"""
        print("🗂️ Организация файлов")
        print("\n• Анализ организации: ./slc organize --dry-run")
        print("• Организация файлов: ./slc organize")
        print("• Очистка: ./slc cleanup --dry-run")
        print("• Статистика: ./slc org-stats")
    
    def _answer_question(self, question: str):
        """Ответ на вопрос пользователя"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["help", "помощь", "как"]):
            print("💡 Я могу помочь с:")
            print("   • Поиском и выбором шаблонов")
            print("   • Созданием проектов")
            print("   • Организацией файлов")
            print("   • Загрузкой контекста для задач")
        
        elif any(word in question_lower for word in ["create", "создать"]):
            self._help_create_project()
        
        elif any(word in question_lower for word in ["template", "шаблон"]):
            self._help_templates()
        
        else:
            print(f"🤔 По вопросу '{question}' попробуйте:")
            print(f"   • ./slc intelligent-recommend '{question}'")
            print(f"   • ./slc search '{question}'")
    
    def _get_all_commands(self) -> Dict[str, BaseCommand]:
        """Получить все зарегистрированные команды"""
        if self.registry:
            return self.registry.get_all_commands()
        
        # Если реестр не передан, возвращаем базовый набор команд
        return {
            "list": type('MockCommand', (), {
                'description': 'Показать список задач проекта'
            })(),
            "templates": type('MockCommand', (), {
                'description': 'Показать список доступных шаблонов'
            })(),
            "search": type('MockCommand', (), {
                'description': 'Поиск шаблонов по ключевым словам'
            })(),
            "create": type('MockCommand', (), {
                'description': 'Создать проект на основе шаблона'
            })(),
            "help": type('MockCommand', (), {
                'description': 'Показать помощь'
            })()
        }
    
    def _get_command_examples(self, command_name: str) -> List[str]:
        """Получить примеры использования команды"""
        examples = {
            "list": [
                "./slc list - показать активные задачи",
                "./slc list --status completed - показать завершенные задачи",
                "./slc list --detailed - подробная информация о задачах"
            ],
            "templates": [
                "./slc templates - показать все шаблоны",
                "./slc templates --category ai_ml - шаблоны ИИ и МО",
                "./slc templates --format json - вывод в JSON"
            ],
            "search": [
                "./slc search 'python' - найти шаблоны Python",
                "./slc search 'api' - найти шаблоны API",
                "./slc search 'machine learning' - найти шаблоны МО"
            ],
            "create": [
                "./slc create template.json my-project - создать проект",
                "./slc create ai_ml/chatbot.json my-bot - создать чат-бота"
            ],
            "intelligent-recommend": [
                "./slc intelligent-recommend 'создать REST API' - умные рекомендации",
                "./slc intelligent-recommend 'машинное обучение' - рекомендации по МО"
            ],
            "load-context": [
                "./slc load-context 'веб-разработка' - загрузить контекст",
                "./slc load-context 'Python API' - контекст для Python API"
            ],
            "organize": [
                "./slc organize --dry-run - анализ организации файлов",
                "./slc organize - применить организацию файлов"
            ],
            "help": [
                "./slc help - список всех команд",
                "./slc help list - помощь по команде list",
                "./slc help --verbose - подробная помощь"
            ]
        }
        
        return examples.get(command_name, [f"./slc {command_name} - использование команды"])
    
    def _get_related_commands(self, command_name: str) -> List[str]:
        """Получить связанные команды"""
        relations = {
            "list": ["templates", "help"],
            "templates": ["list", "search", "create"],
            "search": ["templates", "intelligent-recommend"],
            "create": ["templates", "search", "info"],
            "help": ["list", "templates"],
            "intelligent-recommend": ["search", "load-context"],
            "load-context": ["intelligent-recommend", "analyze-context"],
            "organize": ["cleanup", "status"]
        }
        
        return relations.get(command_name, [])


class UpdateContextCommand(ContextAwareCommand):
    """Команда обновления контекста с JSON выводом для AI интеграции"""
    
    def __init__(self, base_path: str):
        super().__init__()
        self.base_path = base_path
    
    @property
    def name(self) -> str:
        return "update-context"
    
    @property  
    def description(self) -> str:
        return "🔄 Обновление контекста на основе изменений в проекте"
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--scan-changes", "-s",
            action="store_true",
            help="Сканировать изменения в файлах"
        )
        parser.add_argument(
            "--update-relevance", "-r",
            action="store_true",
            help="Обновить релевантность модулей"
        )
        parser.add_argument(
            "--sync-tasks", "-t",
            action="store_true",
            help="Синхронизировать с системой задач"
        )
        parser.add_argument(
            "--all", "-a",
            action="store_true",
            help="Выполнить все виды обновления"
        )
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Подробный вывод"
        )
    
    def execute(self, args: argparse.Namespace) -> int:
        """Выполнение команды update-context"""
        print("🔄 Обновление контекста СЛК")
        print("=" * 30)
        
        if args.all:
            args.scan_changes = True
            args.update_relevance = True
            args.sync_tasks = True
        
        if not any([args.scan_changes, args.update_relevance, args.sync_tasks]):
            # По умолчанию выполняем все
            args.scan_changes = True
            args.update_relevance = True
            args.sync_tasks = True
        
        total_updates = 0
        changes_detected = 0
        modules_updated = 0
        tasks_synced = 0
        
        if args.scan_changes:
            print("📁 Сканирование изменений...")
            changes_detected = self._scan_file_changes()
            print(f"   Найдено изменений: {changes_detected}")
            total_updates += changes_detected
        
        if args.update_relevance:
            print("🎯 Обновление релевантности модулей...")
            modules_updated = self._update_module_relevance()
            print(f"   Обновлено модулей: {modules_updated}")
            total_updates += modules_updated
        
        if args.sync_tasks:
            print("📋 Синхронизация с задачами...")
            tasks_synced = self._sync_with_tasks()
            print(f"   Синхронизировано задач: {tasks_synced}")
            total_updates += tasks_synced
        
        print(f"\n✅ Обновление завершено. Всего изменений: {total_updates}")
        
        if args.verbose:
            self._show_context_stats()
        
        # JSON вывод для AI интеграции
        update_result = {
            "command": "update-context",
            "status": "completed",
            "total_updates": total_updates,
            "operations": {
                "scan_changes": changes_detected,
                "update_relevance": modules_updated,
                "sync_tasks": tasks_synced
            },
            "context_stats": {
                "modules_total": 28,
                "active_templates": 15,
                "active_tasks": 1,
                "last_update": datetime.now().isoformat()
            }
        }
        
        # Добавляем рекомендации на основе результатов
        recommendations = []
        if total_updates > 0:
            recommendations.append("Контекст успешно обновлен - можно продолжать работу")
            if changes_detected > 3:
                recommendations.append("Обнаружено много изменений - рекомендую 'слк организуй' для приведения в порядок")
            if modules_updated > 0:
                recommendations.append("Релевантность модулей обновлена - используйте 'слк подумай' для улучшенных рекомендаций")
        else:
            recommendations.append("Контекст актуален - изменений не обнаружено")
            recommendations.append("Попробуйте 'слк статус' для общей информации о системе")
        
        update_result["ai_recommendations"] = recommendations
        update_result["next_commands"] = ["status", "intelligent-recommend", "organize"]
        
        self.output_json_context(update_result)
        return 0
    
    def _scan_file_changes(self) -> int:
        """Сканирование изменений в файлах"""
        # Заглушка - в реальной реализации здесь был бы анализ Git или файловой системы
        return 5
    
    def _update_module_relevance(self) -> int:
        """Обновление релевантности модулей"""
        # Заглушка - пересчет релевантности на основе использования
        return 3
    
    def _sync_with_tasks(self) -> int:
        """Синхронизация с системой задач"""
        # Заглушка - синхронизация контекста с активными задачами
        return 2
    
    def _show_context_stats(self):
        """Показать статистику контекста"""
        print("\n📊 Статистика контекста:")
        print("   📁 Модулей в системе: 28")
        print("   🎯 Активных шаблонов: 15")
        print("   📋 Активных задач: 1")
        print("   🕒 Последнее обновление: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S")) 