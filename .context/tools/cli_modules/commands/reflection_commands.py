#!/usr/bin/env python3
"""
Команды рефлексии для Smart Layered Context CLI
Создание фазы рефлексии с субфазами для наведения порядка в проекте

Версия: 2.0.0
Создано: 2025-01-16
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

from tools.cli_modules.common.base_command import BaseCommand


class ReflectionCommand(BaseCommand):
    """Команда для создания фазы рефлексии с субфазами наведения порядка"""
    
    def __init__(self, base_path: str):
        super().__init__()
        self.base_path = Path(base_path)
        self.tasks_dir = self.base_path / 'tasks'
        
    @property
    def name(self) -> str:
        return "рефлексия"
    
    @property
    def description(self) -> str:
        return "🔧 Создание фазы рефлексии с субфазами наведения порядка в проекте"
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--project-name", 
            type=str,
            help="Название проекта для рефлексии (по умолчанию: текущий проект)"
        )
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Подробный вывод процесса создания фазы"
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Только показать план фазы без создания"
        )
    
    def execute(self, args: argparse.Namespace) -> int:
        """Выполнение команды создания фазы рефлексии"""
        print("🔧 СОЗДАНИЕ ФАЗЫ РЕФЛЕКСИИ")
        print("=" * 50)
        
        try:
            # 1. Определяем проект
            project_name = args.project_name or self._detect_current_project()
            
            # 2. Создаем структуру фазы рефлексии
            reflection_phase = self._create_reflection_phase(project_name, args.verbose)
            
            # 3. Показываем план
            self._display_phase_plan(reflection_phase, args.verbose)
            
            # 4. Создаем фазу (если не dry-run)
            if not args.dry_run:
                task_id = self._create_phase_task(reflection_phase, args.verbose)
                self._update_active_tasks(task_id, reflection_phase, args.verbose)
                self._reload_context(args.verbose)
                
                print(f"\n✅ ФАЗА РЕФЛЕКСИИ СОЗДАНА!")
                print(f"📋 ID задачи: {task_id}")
                print(f"🔧 Субфаз создано: {len(reflection_phase['subphases'])}")
                print("🚀 Контекст обновлен")
                
            else:
                print("\n🔍 РЕЖИМ ПРОСМОТРА (--dry-run)")
                print("Фаза не была создана")
            
            return 0
            
        except Exception as e:
            self.print_error(f"Ошибка создания фазы рефлексии: {e}")
            return 1
    
    def _detect_current_project(self) -> str:
        """Автоматическое определение текущего проекта"""
        # Ищем в активных задачах
        active_tasks_file = self.tasks_dir / 'active.json'
        if active_tasks_file.exists():
            try:
                with open(active_tasks_file, 'r', encoding='utf-8') as f:
                    active_data = json.load(f)
                    tasks = active_data.get('tasks', [])
                    if tasks:
                        # Берем последнюю активную задачу
                        latest_task = max(tasks, key=lambda t: t.get('created_at', 0))
                        return latest_task.get('project', 'unknown_project')
            except:
                pass
        
        # Определяем по директории
        current_dir = Path.cwd().name
        return current_dir if current_dir else 'current_project'
    
    def _create_reflection_phase(self, project_name: str, verbose: bool) -> Dict[str, Any]:
        """Создание структуры фазы рефлексии"""
        if verbose:
            print("📋 Создание структуры фазы рефлексии...")
        
        timestamp = time.time()
        
        reflection_phase = {
            'project': project_name,
            'phase_name': 'рефлексия',
            'created_at': timestamp,
            'description': 'Наведение порядка в проекте и исправление технических долгов',
            'priority': 'high',
            'estimated_duration': '4-8 часов',
            'subphases': [
                {
                    'id': 'cleanup_fallbacks',
                    'name': 'Удаление фоллбэков',
                    'description': 'Удаление всех временных решений и fallback кода',
                    'tasks': [
                        'Найти все TODO, FIXME, HACK комментарии',
                        'Удалить устаревшие fallback функции',
                        'Заменить временные решения на постоянные',
                        'Очистить условный код для старых версий'
                    ],
                    'priority': 'high',
                    'estimated_time': '1-2 часа'
                },
                {
                    'id': 'complete_todos',
                    'name': 'Доделка TODO пунктов',
                    'description': 'Завершение всех незавершенных задач и TODO элементов',
                    'tasks': [
                        'Составить список всех TODO в коде',
                        'Приоритизировать TODO по важности',
                        'Реализовать критичные TODO',
                        'Удалить неактуальные TODO',
                        'Задокументировать отложенные TODO'
                    ],
                    'priority': 'high',
                    'estimated_time': '2-3 часа'
                },
                {
                    'id': 'fix_weakened_functionality',
                    'name': 'Исправление ослабленной функциональности',
                    'description': 'Восстановление полной функциональности компонентов',
                    'tasks': [
                        'Найти функции с урезанным функционалом',
                        'Восстановить отключенные проверки',
                        'Исправить временно упрощенную логику',
                        'Восстановить полную валидацию данных'
                    ],
                    'priority': 'high',
                    'estimated_time': '1-2 часа'
                },
                {
                    'id': 'fix_disconnected_functionality',
                    'name': 'Подключение отвалившегося функционала',
                    'description': 'Исправление точек где функционал есть но не используется',
                    'tasks': [
                        'Найти неиспользуемые функции и классы',
                        'Проверить корректность вызовов API',
                        'Исправить несоответствие сигнатур функций',
                        'Подключить отключенные модули',
                        'Исправить игнорирование исключений'
                    ],
                    'priority': 'critical',
                    'estimated_time': '1-2 часа'
                },
                {
                    'id': 'fix_weak_tests',
                    'name': 'Исправление ослабленных тестов',
                    'description': 'Восстановление полноценного тестирования',
                    'tasks': [
                        'Найти заглушенные/пропущенные тесты',
                        'Восстановить отключенные проверки в тестах',
                        'Добавить недостающие тест-кейсы',
                        'Исправить тесты с неполными проверками'
                    ],
                    'priority': 'medium',
                    'estimated_time': '1 час'
                },
                {
                    'id': 'organize_tests',
                    'name': 'Организация тестов',
                    'description': 'Приведение тестов к принятой структуре проекта',
                    'tasks': [
                        'Переместить тесты в папку tests/',
                        'Привести к единому стилю именования',
                        'Организовать тесты по модулям',
                        'Удалить дублирующиеся тесты',
                        'Создать общие фикстуры'
                    ],
                    'priority': 'medium',
                    'estimated_time': '30-60 минут'
                },
                {
                    'id': 'fix_development_issues',
                    'name': 'Исправление некорректной разработки',
                    'description': 'Исправление нарушений практик разработки',
                    'tasks': [
                        'Исправить нарушения code style',
                        'Удалить дублированный код',
                        'Исправить неконсистентное именование',
                        'Привести к единым паттернам проектирования',
                        'Исправить нарушения SOLID принципов'
                    ],
                    'priority': 'medium',
                    'estimated_time': '1 час'
                },
                {
                    'id': 'organize_files',
                    'name': 'Наведение порядка в файлах',
                    'description': 'Организация файловой структуры проекта',
                    'tasks': [
                        'Переместить файлы в правильные папки',
                        'Удалить временные и дублирующие файлы',
                        'Организовать ресурсы по категориям',
                        'Очистить корневую директорию от лишних файлов',
                        'Привести к единой структуре проекта'
                    ],
                    'priority': 'low',
                    'estimated_time': '30 минут'
                },
                {
                    'id': 'update_progress',
                    'name': 'Обновление прогресса и контекста',
                    'description': 'Финализация рефлексии и обновление состояния',
                    'tasks': [
                        'Обновить прогресс выполнения в задачах',
                        'Задокументировать внесенные изменения',
                        'Перезагрузить контекст СЛК системы',
                        'Создать отчет о выполненной рефлексии',
                        'Планировать следующую итерацию рефлексии'
                    ],
                    'priority': 'high',
                    'estimated_time': '30 минут'
                }
            ],
            'success_criteria': [
                'Удалены все fallback решения',
                'Завершены все критичные TODO',
                'Восстановлена полная функциональность',
                'Исправлены все отвалившиеся связи',
                'Тесты приведены в порядок',
                'Файловая структура организована',
                'Контекст обновлен'
            ]
        }
        
        if verbose:
            print(f"   ✅ Создана фаза с {len(reflection_phase['subphases'])} субфазами")
        
        return reflection_phase
    
    def _display_phase_plan(self, phase: Dict[str, Any], verbose: bool):
        """Отображение плана фазы рефлексии"""
        print(f"\n📋 ПЛАН ФАЗЫ РЕФЛЕКСИИ: {phase['project']}")
        print(f"📝 Описание: {phase['description']}")
        print(f"⏱️  Ожидаемая длительность: {phase['estimated_duration']}")
        print(f"🎯 Субфаз: {len(phase['subphases'])}")
        
        print("\n🔧 СУБФАЗЫ:")
        for i, subphase in enumerate(phase['subphases'], 1):
            priority_icon = {
                'critical': '🔥',
                'high': '🔴', 
                'medium': '🟡',
                'low': '🟢'
            }.get(subphase['priority'], '⚪')
            
            print(f"\n{i:2d}. {priority_icon} {subphase['name']}")
            print(f"     📝 {subphase['description']}")
            print(f"     ⏱️  {subphase['estimated_time']}")
            
            if verbose:
                print(f"     📋 Задачи ({len(subphase['tasks'])}):")
                for task in subphase['tasks']:
                    print(f"        • {task}")
        
        print(f"\n🎯 КРИТЕРИИ УСПЕХА:")
        for criterion in phase['success_criteria']:
            print(f"   ✅ {criterion}")
    
    def _create_phase_task(self, phase: Dict[str, Any], verbose: bool) -> str:
        """Создание файла задачи для фазы рефлексии"""
        if verbose:
            print("💾 Создание файла задачи...")
        
        timestamp = time.time()
        task_id = f"reflection_phase_{int(timestamp)}"
        
        task_data = {
            'id': task_id,
            'project': phase['project'],
            'type': 'reflection_phase',
            'title': f"Фаза рефлексии: {phase['project']}",
            'description': phase['description'],
            'status': 'active',
            'priority': phase['priority'],
            'created_at': timestamp,
            'estimated_duration': phase['estimated_duration'],
            'phase_data': phase,
            'current_subphase': 0,
            'completed_subphases': [],
            'notes': []
        }
        
        # Создаем файл задачи
        task_file = self.tasks_dir / f"{task_id}.json"
        self.tasks_dir.mkdir(exist_ok=True)
        
        with open(task_file, 'w', encoding='utf-8') as f:
            json.dump(task_data, f, ensure_ascii=False, indent=2, default=str)
        
        if verbose:
            print(f"   ✅ Создан файл задачи: {task_file}")
        
        return task_id
    
    def _update_active_tasks(self, task_id: str, phase: Dict[str, Any], verbose: bool):
        """Обновление списка активных задач"""
        if verbose:
            print("📝 Обновление активных задач...")
        
        active_tasks_file = self.tasks_dir / 'active.json'
        
        # Загружаем существующие активные задачи
        active_data = {}
        if active_tasks_file.exists():
            try:
                with open(active_tasks_file, 'r', encoding='utf-8') as f:
                    active_data = json.load(f)
            except:
                pass
        
        # Создаем новую структуру для фазы рефлексии
        reflection_task = {
            "active_task_reference": {
                "$ref": f".context/tasks/{task_id}.json",
                "task_type": "reflection_phase",
                "priority": "HIGH",
                "status": "ACTIVE",
                "activated_at": datetime.now().isoformat()
            },
            "metadata": {
                "title": f"Рефлексия: {phase['project']}",
                "task_id": task_id,
                "category": "maintenance",
                "description": phase['description'],
                "estimated_duration": phase['estimated_duration'],
                "current_focus": "Фаза рефлексии и наведение порядка"
            },
            "execution_status": {
                "phase": "РЕФЛЕКСИЯ",
                "current_task": "Подготовка к выполнению субфаз",
                "progress": "0%",
                "subphases_total": len(phase['subphases']),
                "subphases_completed": 0,
                "current_subphase": 1,
                "next_action": phase['subphases'][0]['name']
            },
            "reflection_data": {
                "project_name": phase['project'],
                "total_subphases": len(phase['subphases']),
                "priority_subphases": [s['name'] for s in phase['subphases'] if s['priority'] in ['critical', 'high']],
                "estimated_completion": datetime.now().isoformat()
            }
        }
        
        # Сохраняем
        with open(active_tasks_file, 'w', encoding='utf-8') as f:
            json.dump(reflection_task, f, ensure_ascii=False, indent=2, default=str)
        
        if verbose:
            print(f"   ✅ Фаза рефлексии активирована в {active_tasks_file}")
            print(f"   📋 Текущий фокус: {reflection_task['metadata']['current_focus']}")
            print(f"   🎯 Следующее действие: {reflection_task['execution_status']['next_action']}")
    
    def _reload_context(self, verbose: bool):
        """Перезагрузка контекста СЛК"""
        if verbose:
            print("🔄 Перезагрузка контекста...")
        
        try:
            # Находим корневую директорию проекта
            root_path = self.base_path.parent
            slc_path = root_path / 'slc'
            
            if slc_path.exists():
                # Перезагружаем контекст через CLI
                import subprocess
                result = subprocess.run(
                    [str(slc_path), 'reload-context'],
                    capture_output=True,
                    text=True,
                    cwd=str(root_path)
                )
                
                if result.returncode == 0:
                    if verbose:
                        print("   ✅ Контекст перезагружен")
                else:
                    if verbose:
                        print("   ⚠️  Не удалось перезагрузить контекст")
            else:
                if verbose:
                    print("   ✅ Контекст обновлен локально")
                    
        except Exception as e:
            if verbose:
                print(f"   ⚠️  Ошибка перезагрузки контекста: {e}")
                print("   ✅ Продолжаем без перезагрузки") 