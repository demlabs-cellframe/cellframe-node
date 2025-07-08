#!/usr/bin/env python3
"""
Модуль для унифицированного вывода контекста в JSON формате
Smart Context Switching для СЛК команд

Версия: 1.0.0
Создано: 2025-01-20
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class ContextOutputManager:
    """Менеджер для создания JSON вывода с контекстной информацией"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        
    def create_context_output(
        self,
        command_name: str,
        execution_result: Dict[str, Any],
        context_files: List[str] = None,
        context_summary: str = None,
        recommended_actions: List[str] = None,
        next_commands: List[str] = None,
        load_content: bool = False
    ) -> Dict[str, Any]:
        """
        Создать стандартизированный JSON вывод с контекстом
        
        Args:
            command_name: Имя выполненной команды
            execution_result: Результат выполнения команды
            context_files: Список файлов для загрузки в AI
            context_summary: Краткое резюме для AI
            recommended_actions: Рекомендуемые действия
            next_commands: Предлагаемые следующие команды
            load_content: Загружать ли содержимое файлов
        """
        
        output = {
            "slc_context_output": True,
            "timestamp": datetime.now().isoformat(),
            "command": command_name,
            "execution_result": execution_result,
            "context_data": {
                "files_to_load": context_files or [],
                "context_summary": context_summary or f"Результаты выполнения команды {command_name}",
                "recommended_actions": recommended_actions or [],
                "next_commands": next_commands or []
            }
        }
        
        # Опционально загружаем содержимое файлов
        if load_content and context_files:
            output["context_data"]["files_content"] = self._load_files_content(context_files)
            
        return output
    
    def _load_files_content(self, file_paths: List[str]) -> Dict[str, Any]:
        """Загрузить содержимое указанных файлов"""
        files_content = {}
        
        for file_path in file_paths:
            try:
                full_path = self.base_path / file_path.lstrip('/')
                if full_path.exists():
                    with open(full_path, 'r', encoding='utf-8') as f:
                        if file_path.endswith('.json'):
                            files_content[file_path] = json.load(f)
                        else:
                            files_content[file_path] = f.read()
                else:
                    files_content[file_path] = {"error": "Файл не найден"}
            except Exception as e:
                files_content[file_path] = {"error": str(e)}
                
        return files_content
    
    def print_context_output(self, context_output: Dict[str, Any]):
        """Вывести JSON контекст в консоль"""
        print("\n" + "="*80)
        print("📊 SLC CONTEXT OUTPUT (JSON)")
        print("="*80)
        print(json.dumps(context_output, ensure_ascii=False, indent=2))
        print("="*80)


# Декоратор для автоматического добавления JSON контекста
def with_context_output(context_files: List[str] = None, 
                       context_summary: str = None,
                       recommended_actions: List[str] = None,
                       next_commands: List[str] = None):
    """
    Декоратор для автоматического создания JSON контекста
    
    Использование:
    @with_context_output(
        context_files=[".slc_reflection_log.json"],
        context_summary="Рефлексия завершена",
        next_commands=["слк анализ", "слк статус"]
    )
    def reflection_command(self, args):
        ...
    """
    def decorator(func):
        def wrapper(self, args):
            # Выполняем исходную команду
            result = func(self, args)
            
            # Если запрошен JSON вывод контекста
            if hasattr(args, 'json_context') and args.json_context:
                if hasattr(self, 'base_path'):
                    manager = ContextOutputManager(str(self.base_path))
                    context_output = manager.create_context_output(
                        command_name=getattr(self, 'name', func.__name__),
                        execution_result={"status": "success", "return_code": result},
                        context_files=context_files,
                        context_summary=context_summary,
                        recommended_actions=recommended_actions,
                        next_commands=next_commands,
                        load_content=getattr(args, 'load_content', False)
                    )
                    manager.print_context_output(context_output)
            
            return result
        return wrapper
    return decorator


# Вспомогательные функции для создания контекста для разных типов команд

def create_reflection_context(reflection_results: Dict[str, Any], base_path: str) -> Dict[str, Any]:
    """Создать контекст для команды рефлексии"""
    manager = ContextOutputManager(base_path)
    
    context_files = [
        ".slc_reflection_log.json",
        "tasks/active.json"
    ]
    
    insights_count = len(reflection_results.get('insights', []))
    tasks_count = len(reflection_results.get('analyzed_tasks', []))
    
    context_summary = f"""
    Завершена рефлексия СЛК системы:
    - Проанализировано задач: {tasks_count}
    - Создано инсайтов: {insights_count}
    - Выявлены паттерны успеха и области для улучшения
    - Система готова к оптимизации на основе полученных данных
    """
    
    recommended_actions = [
        "Проанализировать выявленные паттерны",
        "Создать план улучшений на основе инсайтов",
        "Применить рекомендации к текущим процессам",
        "Настроить мониторинг ключевых метрик"
    ]
    
    next_commands = [
        "слк анализ",
        "слк intelligence-stats", 
        "слк статус",
        "слк подумай [план улучшений]"
    ]
    
    return manager.create_context_output(
        command_name="reflection",
        execution_result=reflection_results,
        context_files=context_files,
        context_summary=context_summary.strip(),
        recommended_actions=recommended_actions,
        next_commands=next_commands
    )


def create_intelligence_context(stats: Dict[str, Any], base_path: str) -> Dict[str, Any]:
    """Создать контекст для команды intelligence-stats"""
    manager = ContextOutputManager(base_path)
    
    context_files = [
        ".slc_usage_stats.json",
        "modules/ai_ml/machine_learning.json",
        "tools/template_intelligence/"
    ]
    
    context_summary = f"""
    Статистика Template Intelligence системы:
    - Успешных рекомендаций: {stats.get('successful_recommendations', 0)}
    - Активных паттернов: {stats.get('active_patterns', 0)}
    - Средняя успешность: {stats.get('average_success_rate', 0):.1f}%
    """
    
    return manager.create_context_output(
        command_name="intelligence-stats",
        execution_result=stats,
        context_files=context_files,
        context_summary=context_summary.strip(),
        recommended_actions=[
            "Проанализировать наиболее успешные паттерны",
            "Оптимизировать слабые места в рекомендациях",
            "Обучить систему на новых данных"
        ],
        next_commands=[
            "слк record-usage [шаблон]",
            "слк generate-adaptive",
            "слк template-evolution [шаблон]"
        ]
    )


def create_status_context(status_data: Dict[str, Any], base_path: str) -> Dict[str, Any]:
    """Создать контекст для команды status"""
    manager = ContextOutputManager(base_path)
    
    context_files = [
        "VERSION",
        "manifest.json",
        ".slc_usage_stats.json"
    ]
    
    system_health = status_data.get('health', 'unknown')
    templates_count = status_data.get('templates_count', 0)
    
    context_summary = f"""
    Статус системы СЛК:
    - Состояние: {system_health}
    - Доступно шаблонов: {templates_count}
    - Версия: {status_data.get('version', 'unknown')}
    """
    
    next_actions = []
    if system_health != 'HEALTHY':
        next_actions.extend([
            "слк валидация",
            "слк оптимизация"
        ])
    else:
        next_actions.extend([
            "слк рефлексия",
            "слк анализ"
        ])
    
    return manager.create_context_output(
        command_name="status",
        execution_result=status_data,
        context_files=context_files,
        context_summary=context_summary.strip(),
        next_commands=next_actions
    ) 