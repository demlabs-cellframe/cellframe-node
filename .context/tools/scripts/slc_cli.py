#!/usr/bin/env python3
"""
SLC CLI - Smart Layered Context Command Line Interface

Главный CLI инструмент для работы с системой СЛК.
Поддерживает 31 команду для управления шаблонами, задачами и организацией проектов.

Версия: 4.1.0
Создано: 2025-01-14
"""

import os
import sys
import argparse
import importlib
import time
from pathlib import Path
from typing import Dict, List, Type

# Добавляем .context в path для импортов
context_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(context_root))

try:
    from tools.cli_modules.base_command import BaseCommand, CommandRegistry
except ImportError as e:
    print(f"❌ Критическая ошибка импорта: {e}")
    print("💡 Убедитесь, что вы находитесь в корне проекта СЛК")
    sys.exit(1)


class ModularCLI:
    """Главный класс CLI системы СЛК"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.registry = CommandRegistry()
        self.version = "2.0.0"
        
        # Автоматически определяем путь к CLI модулям
        self.cli_modules_path = self.base_path / "tools" / "cli_modules"
        
        if not self.cli_modules_path.exists():
            print(f"❌ CLI модули не найдены: {self.cli_modules_path}")
            sys.exit(1)
    
    def discover_and_register_commands(self):
        """Автоматическое обнаружение и регистрация всех команд"""
        commands_path = self.cli_modules_path / "commands"
        
        if not commands_path.exists():
            print(f"❌ Папка команд не найдена: {commands_path}")
            return
        
        # Список модулей команд для импорта
        command_modules = [
            "template_intelligence_commands",
            "organization_commands", 
            "context_commands",
            "ai_commands",
            "template_commands",
            "task_commands",
            "management_commands",
            "evolution_commands",
            "help_commands",
            "reflection_commands",
            "self_development_commands",
            "deployment_commands"
        ]
        
        print("🔄 Регистрация команд...")
        registered_count = 0
        
        for module_name in command_modules:
            try:
                # Импортируем модуль
                module_path = f"tools.cli_modules.commands.{module_name}"
                module = importlib.import_module(module_path)
                
                # Ищем классы команд в модуле
                command_classes = self._find_command_classes(module)
                
                for command_class in command_classes:
                    try:
                        # Создаем экземпляр команды
                        if command_class.__name__ == 'HelpCommand':
                            # Для HelpCommand передаем реестр
                            command_instance = command_class(str(self.base_path), self.registry)
                        elif self._requires_base_path(command_class):
                            command_instance = command_class(str(self.base_path))
                        else:
                            command_instance = command_class()
                        
                        # Регистрируем команду
                        self.registry.register(command_instance)
                        registered_count += 1
                        
                        print(f"   ✅ {command_instance.name}: {command_instance.description}")
                        
                    except Exception as e:
                        print(f"   ⚠️  Ошибка создания {command_class.__name__}: {e}")
                        
            except ImportError as e:
                print(f"   ❌ Ошибка импорта {module_name}: {e}")
            except Exception as e:
                print(f"   ❌ Ошибка обработки {module_name}: {e}")
        
        print(f"🎯 Зарегистрировано команд: {registered_count}")
        return registered_count > 0
    
    def _find_command_classes(self, module) -> List[Type[BaseCommand]]:
        """Поиск классов команд в модуле"""
        command_classes = []
        
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            
            # Проверяем, что это класс команды (по имени и наличию нужных методов)
            if (isinstance(attr, type) and 
                attr_name.endswith('Command') and
                not attr_name.startswith('Base') and
                attr_name != 'ContextAwareCommand' and
                hasattr(attr, 'name') and
                hasattr(attr, 'description') and
                hasattr(attr, 'execute')):
                
                command_classes.append(attr)
        
        return command_classes
    
    def _requires_base_path(self, command_class: Type[BaseCommand]) -> bool:
        """Проверяет, требует ли команда base_path в конструкторе"""
        try:
            import inspect
            sig = inspect.signature(command_class.__init__)
            params = list(sig.parameters.keys())
            return 'base_path' in params
        except:
            return False
    
    def setup_argument_parser(self) -> argparse.ArgumentParser:
        """Настройка главного парсера аргументов"""
        parser = argparse.ArgumentParser(
            description="🧠 Smart Layered Context - CLI v2.0\n"
                       "Интеллектуальная система управления контекстом разработки",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
🚀 Примеры использования:
  %(prog)s list                              # Показать все шаблоны
  %(prog)s intelligent-recommend "python"    # Умные рекомендации
  %(prog)s organize --dry-run               # Организация файлов (анализ)
  %(prog)s load-context "создать API"       # Загрузить контекст
  %(prog)s create template.json my-project  # Создать проект

📚 Помощь по команде:
  %(prog)s КОМАНДА --help

🌐 Документация: https://github.com/your-repo/slc
        """
        )
        
        parser.add_argument(
            "--version", "-v",
            action="version",
            version=f"Smart Layered Context CLI {self.version}"
        )
        
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Включить отладочный вывод"
        )
        
        # Создаем subparsers для команд
        subparsers = parser.add_subparsers(
            dest="command",
            help="Доступные команды",
            metavar="КОМАНДА"
        )
        
        # Регистрируем все команды в subparsers
        for command_name, command in self.registry.get_all_commands().items():
            cmd_parser = subparsers.add_parser(
                command_name,
                help=command.description,
                description=command.description,
                formatter_class=argparse.RawDescriptionHelpFormatter
            )
            
            # Добавляем аргументы команды
            try:
                command.add_arguments(cmd_parser)
            except Exception as e:
                print(f"⚠️  Ошибка добавления аргументов для {command_name}: {e}")
        
        return parser
    
    def execute_command(self, args: argparse.Namespace) -> int:
        """Выполнение команды"""
        if not args.command:
            print("❌ Команда не указана")
            return 1
        
        # Специальная обработка для случая "help command_name"
        # Если команда не найдена, но в sys.argv есть "help" перед ней
        command = self.registry.get_command(args.command)
        if not command and len(sys.argv) >= 3 and sys.argv[1] == 'help':
            # Это случай "help command_name" - перенаправляем на команду help
            help_command = self.registry.get_command('help')
            if help_command:
                # Создаем новые args для команды help
                help_args = argparse.Namespace()
                help_args.command = args.command  # Передаем имя команды как аргумент
                help_args.interactive = False
                help_args.verbose = False
                return help_command.execute(help_args)
        
        if not command:
            print(f"❌ Неизвестная команда: {args.command}")
            print(f"💡 Доступные команды: {', '.join(self.registry.list_commands())}")
            return 1
        
        # Валидация аргументов
        if not command.validate_args(args):
            return 1
        
        # Выполнение команды
        try:
            start_time = time.time()
            result = command.execute(args)
            execution_time = time.time() - start_time
            
            if args.debug:
                print(f"\n🐛 Debug: команда выполнена за {execution_time:.3f}с")
            
            return result
            
        except KeyboardInterrupt:
            print("\n⏹️  Выполнение прервано пользователем")
            return 130
        except Exception as e:
            print(f"❌ Ошибка выполнения команды: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
            return 1
    
    def run(self, argv: List[str] = None) -> int:
        """Главная функция запуска CLI"""
        try:
            # Обнаружение и регистрация команд
            if not self.discover_and_register_commands():
                print("❌ Не удалось зарегистрировать команды")
                return 1
            

            
            # Специальная обработка для команды help
            if argv is None:
                argv = sys.argv[1:]
            
            # Обработка алиасов команд
            if argv and argv[0] in ['start', 'старт']:
                # Заменяем на load-context "базовый старт"
                argv = ['load-context', 'базовый старт'] + argv[1:]
            
            # Если первый аргумент "help" и есть второй аргумент, обрабатываем специально
            if len(argv) >= 2 and argv[0] == 'help':
                help_command = self.registry.get_command('help')
                if help_command:
                    # Создаем args для команды help
                    help_args = argparse.Namespace()
                    help_args.command = argv[1]  # Передаем имя команды
                    help_args.interactive = False
                    help_args.verbose = False
                    return help_command.execute(help_args)
            
            # Настройка парсера
            parser = self.setup_argument_parser()
            
            # Парсинг аргументов
            args = parser.parse_args(argv)
            
            # Отладочный вывод
            if hasattr(args, 'debug') and args.debug:
                print(f"🐛 Debug: parsed command = '{args.command}'")
                print(f"🐛 Debug: args = {args}")
            
            # Если команда не указана, вызываем команду help
            if not args.command:
                # Создаем args для команды help
                help_args = argparse.Namespace()
                help_args.command = None  # Без аргументов для help
                help_args.interactive = False
                help_args.verbose = False
                
                help_command = self.registry.get_command('help')
                if help_command:
                    return help_command.execute(help_args)
                else:
                    # Fallback на стандартную справку
                    parser.print_help()
                    print(f"\n🚀 Для начала попробуйте: {sys.argv[0]} list")
                    print(f"🧠 Или получите рекомендации: {sys.argv[0]} intelligent-recommend 'ваш запрос'")
                    return 0
            
            # Выполнение команды
            return self.execute_command(args)
            
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            return 1


def find_slc_root() -> Path:
    """Поиск корня проекта СЛК"""
    current = Path.cwd()
    
    # Сначала проверяем текущую директорию
    if (current / ".context" / "modules" / "core" / "manifest.json").exists():
        return current / ".context"
    elif (current / "modules" / "core" / "manifest.json").exists():
        return current
    
    # Ищем в родительских директориях
    for parent in current.parents:
        if (parent / ".context" / "modules" / "core" / "manifest.json").exists():
            return parent / ".context"
        elif (parent / "modules" / "core" / "manifest.json").exists():
            return parent
    
    # Fallback на текущую директорию
    return current


def main():
    """Точка входа CLI"""
    try:
        # Поиск корня проекта СЛК
        slc_root = find_slc_root()
        
        if not slc_root.exists():
            print("❌ Корень проекта СЛК не найден")
            print("💡 Убедитесь, что вы находитесь в проекте СЛК")
            sys.exit(1)
        
        # Создание и запуск CLI
        cli = ModularCLI(str(slc_root))
        exit_code = cli.run()
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⏹️  Прервано пользователем")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Фатальная ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 