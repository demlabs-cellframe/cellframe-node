#!/usr/bin/env python3
"""
Базовый класс для всех команд CLI
Предоставляет общую функциональность и интерфейс

Версия: 2.0.0 (добавлена поддержка JSON контекста)
Обновлено: 2025-01-20
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import argparse


class BaseCommand(ABC):
    """Базовый класс для всех команд CLI"""
    
    def __init__(self):
        self.supports_json_context = False  # Переопределить в команде при необходимости
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Имя команды"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Описание команды"""
        pass
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        """
        Добавить аргументы команды в парсер
        Базовая реализация добавляет JSON контекст, если поддерживается
        """
        if self.supports_json_context:
            parser.add_argument(
                "--json-context",
                action="store_true",
                help="Вывести JSON с контекстом для AI помощника"
            )
            parser.add_argument(
                "--load-content",
                action="store_true",
                help="Загрузить содержимое файлов в JSON вывод"
            )
    
    @abstractmethod
    def execute(self, args: argparse.Namespace) -> int:
        """
        Выполнить команду
        
        Args:
            args: Разобранные аргументы командной строки
            
        Returns:
            Код возврата (0 - успех, не 0 - ошибка)
        """
        pass
    
    def validate_args(self, args: argparse.Namespace) -> bool:
        """
        Валидация аргументов команды
        
        Args:
            args: Аргументы командной строки
            
        Returns:
            True если аргументы валидны, False иначе
        """
        return True
    
    def print_error(self, message: str):
        """Вывести сообщение об ошибке"""
        print(f"❌ {message}")
    
    def print_warning(self, message: str):
        """Вывести предупреждение"""
        print(f"⚠️  {message}")
    
    def print_success(self, message: str):
        """Вывести сообщение об успехе"""
        print(f"✅ {message}")
    
    def print_info(self, message: str):
        """Вывести информационное сообщение"""
        print(f"ℹ️  {message}")
    
    def handle_json_context_output(
        self, 
        args: argparse.Namespace, 
        execution_result: Dict[str, Any],
        context_files: List[str] = None,
        context_summary: str = None,
        recommended_actions: List[str] = None,
        next_commands: List[str] = None
    ) -> None:
        """
        Обработать вывод JSON контекста если запрошен
        
        Args:
            args: Аргументы команды
            execution_result: Результат выполнения команды
            context_files: Файлы для загрузки
            context_summary: Краткое описание результатов
            recommended_actions: Рекомендуемые действия
            next_commands: Предлагаемые следующие команды
        """
        if not self.supports_json_context:
            return
            
        if hasattr(args, 'json_context') and args.json_context:
            try:
                from tools.cli_modules.common.context_output import ContextOutputManager
                
                if hasattr(self, 'base_path'):
                    manager = ContextOutputManager(str(self.base_path))
                    
                    context_output = manager.create_context_output(
                        command_name=self.name,
                        execution_result=execution_result,
                        context_files=context_files or [],
                        context_summary=context_summary,
                        recommended_actions=recommended_actions or [],
                        next_commands=next_commands or [],
                        load_content=getattr(args, 'load_content', False)
                    )
                    
                    manager.print_context_output(context_output)
                    
            except ImportError as e:
                self.print_warning(f"Не удалось загрузить модуль контекста: {e}")
            except Exception as e:
                self.print_error(f"Ошибка вывода JSON контекста: {e}")


class ContextAwareCommand(BaseCommand):
    """
    Расширенный базовый класс для команд с поддержкой контекста
    Автоматически добавляет поддержку JSON вывода
    """
    
    def __init__(self, base_path: str = None):
        super().__init__()
        self.base_path = base_path
        self.supports_json_context = True  # Автоматически включаем поддержку
    
    def output_json_context(self, context_data: Dict[str, Any]):
        """
        Вывод JSON контекста для AI интеграции
        
        Args:
            context_data: Данные контекста для вывода
        """
        import json
        print("\n" + "="*60)
        print("🤖 JSON КОНТЕКСТ ДЛЯ AI:")
        print("="*60)
        print(json.dumps(context_data, indent=2, ensure_ascii=False))
        print("="*60)
        
    def get_default_context_files(self) -> List[str]:
        """
        Получить список файлов контекста по умолчанию для данной команды
        Переопределить в наследниках
        """
        return []
    
    def get_context_summary(self, execution_result: Dict[str, Any]) -> str:
        """
        Получить краткое описание результатов выполнения
        Переопределить в наследниках
        """
        return f"Выполнена команда {self.name}"
    
    def get_recommended_actions(self, execution_result: Dict[str, Any]) -> List[str]:
        """
        Получить рекомендуемые действия на основе результатов
        Переопределить в наследниках
        """
        return []
    
    def get_next_commands(self, execution_result: Dict[str, Any]) -> List[str]:
        """
        Получить предлагаемые следующие команды
        Переопределить в наследниках
        """
        return []
    
    def execute_with_context(self, args: argparse.Namespace) -> Dict[str, Any]:
        """
        Выполнить команду и вернуть результат для контекста
        Переопределить в наследниках вместо execute()
        
        Returns:
            Словарь с результатами выполнения команды
        """
        return {"status": "success", "message": "Команда выполнена"}
    
    def execute(self, args: argparse.Namespace) -> int:
        """
        Базовая реализация execute с автоматическим выводом контекста
        """
        try:
            # Выполняем команду
            execution_result = self.execute_with_context(args)
            
            # Автоматически выводим JSON контекст если запрошен
            self.handle_json_context_output(
                args=args,
                execution_result=execution_result,
                context_files=self.get_default_context_files(),
                context_summary=self.get_context_summary(execution_result),
                recommended_actions=self.get_recommended_actions(execution_result),
                next_commands=self.get_next_commands(execution_result)
            )
            
            return 0
            
        except Exception as e:
            self.print_error(f"Ошибка выполнения команды {self.name}: {e}")
            return 1


class CommandRegistry:
    """Реестр команд CLI"""
    
    def __init__(self):
        self._commands: Dict[str, BaseCommand] = {}
    
    def register(self, command: BaseCommand):
        """
        Регистрация команды
        
        Args:
            command: Экземпляр команды для регистрации
        """
        self._commands[command.name] = command
    
    def get_command(self, name: str) -> BaseCommand:
        """
        Получение команды по имени
        
        Args:
            name: Имя команды
            
        Returns:
            Экземпляр команды или None если не найдена
        """
        return self._commands.get(name)
    
    def get_all_commands(self) -> Dict[str, BaseCommand]:
        """Получение всех зарегистрированных команд"""
        return self._commands.copy()
    
    def list_commands(self) -> list:
        """Получение списка имен команд"""
        return list(self._commands.keys()) 