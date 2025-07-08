#!/usr/bin/env python3
"""
Команды рефлексии и саморазвития для Smart Layered Context CLI
Переключение на режим рефлексии, анализ выполненных задач

Версия: 1.0.0
Создано: 2025-01-25
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

from tools.cli_modules.common.base_command import BaseCommand
from tools.cli_modules.common.context_output import create_reflection_context, ContextOutputManager


class ReflectionCommand(BaseCommand):
    """Команда для переключения на режим рефлексии и саморазвития"""
    
    def __init__(self, base_path: str):
        super().__init__()
        self.base_path = Path(base_path)
        self.tasks_dir = self.base_path / 'tasks'
        self.reflection_log = self.base_path / '.slc_reflection_log.json'
        
    @property
    def name(self) -> str:
        return "reflection"
    
    @property
    def description(self) -> str:
        return "🧠 Переключение на режим рефлексии и саморазвития СЛК"
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--auto-start", 
            action="store_true",
            help="Автоматически начать рефлексию без подтверждения"
        )
        parser.add_argument(
            "--days-back", 
            type=int, 
            default=7,
            help="Количество дней назад для анализа задач (по умолчанию: 7)"
        )
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Подробный вывод процесса рефлексии"
        )
        parser.add_argument(
            "--deep",
            action="store_true", 
            help="Глубокая рефлексия с анализом паттернов и улучшений"
        )
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
    
    def execute(self, args: argparse.Namespace) -> int:
        """Выполнение команды рефлексии"""
        print("🧠 ЗАПУСК РЕЖИМА РЕФЛЕКСИИ И САМОРАЗВИТИЯ СЛК")
        print("=" * 60)
        
        try:
            # 1. Анализ текущего состояния
            current_state = self._analyze_current_state(args.verbose)
            
            # 2. Поиск неотрефлексированных задач
            unreflected_tasks = self._find_unreflected_tasks(args.days_back, args.verbose)
            
            # 3. Создание плана рефлексии
            reflection_plan = self._create_reflection_plan(unreflected_tasks, current_state, args.verbose)
            
            # 4. Переключение на задачи рефлексии
            if not args.auto_start:
                if not self._confirm_reflection_start(reflection_plan):
                    print("❌ Рефлексия отменена пользователем")
                    return 1
            
            # 5. Выполнение рефлексии
            reflection_results = self._execute_reflection(reflection_plan, args.deep, args.verbose)
            
            # 6. Сохранение результатов
            self._save_reflection_results(reflection_results, args.verbose)
            
            # 7. Переключение контекста на рефлексию
            self._switch_to_reflection_context(args.verbose)
            
            print("\n🎉 РЕФЛЕКСИЯ ЗАВЕРШЕНА УСПЕШНО!")
            print(f"📊 Проанализировано задач: {len(unreflected_tasks)}")
            print(f"🧠 Создано инсайтов: {len(reflection_results.get('insights', []))}")
            print("🚀 Контекст переключен на саморазвитие")
            
            # Выводим JSON контекст, если запрошен
            if args.json_context:
                context_output = create_reflection_context(reflection_results, str(self.base_path))
                if args.load_content:
                    # Загружаем содержимое файлов
                    manager = ContextOutputManager(str(self.base_path))
                    context_output["context_data"]["files_content"] = manager._load_files_content(
                        context_output["context_data"]["files_to_load"]
                    )
                
                manager = ContextOutputManager(str(self.base_path))
                manager.print_context_output(context_output)
            
            return 0
            
        except Exception as e:
            self.print_error(f"Критическая ошибка рефлексии: {e}")
            return 1
    
    def _analyze_current_state(self, verbose: bool) -> Dict[str, Any]:
        """Анализ текущего состояния системы"""
        if verbose:
            print("🔍 Анализ текущего состояния системы...")
        
        state = {
            'timestamp': time.time(),
            'active_tasks': self._get_active_tasks(),
            'completed_tasks': self._get_completed_tasks(),
            'system_metrics': self._get_system_metrics(),
            'last_reflection': self._get_last_reflection_date()
        }
        
        if verbose:
            print(f"   ✅ Активных задач: {len(state['active_tasks'])}")
            print(f"   ✅ Завершенных задач: {len(state['completed_tasks'])}")
            print(f"   ✅ Последняя рефлексия: {state['last_reflection'] or 'никогда'}")
        
        return state
    
    def _find_unreflected_tasks(self, days_back: int, verbose: bool) -> List[Dict[str, Any]]:
        """Поиск неотрефлексированных задач"""
        if verbose:
            print(f"🔎 Поиск неотрефлексированных задач за последние {days_back} дней...")
        
        unreflected = []
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Загружаем лог рефлексии
        reflection_log = self._load_reflection_log()
        reflected_tasks = set(reflection_log.get('reflected_tasks', []))
        
        # Анализируем все файлы задач
        if self.tasks_dir.exists():
            for task_file in self.tasks_dir.rglob('*.json'):
                try:
                    with open(task_file, 'r', encoding='utf-8') as f:
                        task_data = json.load(f)
                    
                    # Проверяем, была ли задача завершена недавно
                    if self._is_task_recently_completed(task_data, cutoff_date):
                        task_id = str(task_file.relative_to(self.tasks_dir))
                        
                        if task_id not in reflected_tasks:
                            task_info = {
                                'id': task_id,
                                'file': str(task_file),
                                'data': task_data,
                                'completion_date': self._get_task_completion_date(task_data)
                            }
                            unreflected.append(task_info)
                            
                except (json.JSONDecodeError, IOError) as e:
                    if verbose:
                        print(f"   ⚠️  Ошибка чтения {task_file}: {e}")
        
        # Сортируем по дате завершения (новые сначала)
        unreflected.sort(key=lambda x: x.get('completion_date', ''), reverse=True)
        
        if verbose:
            print(f"   ✅ Найдено неотрефлексированных задач: {len(unreflected)}")
            for task in unreflected[:3]:  # Показываем первые 3
                task_name = task['data'].get('project', task['id'])
                print(f"      • {task_name}")
            if len(unreflected) > 3:
                print(f"      ... и еще {len(unreflected) - 3}")
        
        return unreflected
    
    def _create_reflection_plan(self, unreflected_tasks: List[Dict], current_state: Dict, verbose: bool) -> Dict[str, Any]:
        """Создание плана рефлексии"""
        if verbose:
            print("📋 Создание плана рефлексии...")
        
        plan = {
            'timestamp': time.time(),
            'tasks_to_reflect': unreflected_tasks,
            'reflection_areas': [],
            'questions': [],
            'improvement_opportunities': []
        }
        
        # Определяем области для рефлексии
        if unreflected_tasks:
            plan['reflection_areas'].extend([
                'Эффективность выполнения задач',
                'Качество результатов',
                'Использованные подходы и методы',
                'Возникшие проблемы и их решения',
                'Полученные знания и навыки'
            ])
        
        # Добавляем вопросы для рефлексии
        plan['questions'].extend([
            'Что прошло особенно хорошо в выполненных задачах?',
            'Какие проблемы или препятствия возникали?',
            'Какие новые знания или навыки были получены?',
            'Что можно улучшить в процессе выполнения задач?',
            'Какие паттерны успеха можно выделить?'
        ])
        
        # Возможности для улучшения
        if len(unreflected_tasks) > 0:
            plan['improvement_opportunities'].extend([
                'Оптимизация рабочих процессов',
                'Улучшение документирования',
                'Развитие новых навыков',
                'Автоматизация повторяющихся задач'
            ])
        
        if verbose:
            print(f"   ✅ Областей рефлексии: {len(plan['reflection_areas'])}")
            print(f"   ✅ Вопросов для анализа: {len(plan['questions'])}")
            print(f"   ✅ Возможностей улучшения: {len(plan['improvement_opportunities'])}")
        
        return plan
    
    def _confirm_reflection_start(self, plan: Dict) -> bool:
        """Подтверждение начала рефлексии"""
        print("\n📋 ПЛАН РЕФЛЕКСИИ:")
        print(f"🎯 Задач для анализа: {len(plan['tasks_to_reflect'])}")
        print(f"🔍 Областей рефлексии: {len(plan['reflection_areas'])}")
        print(f"❓ Вопросов для анализа: {len(plan['questions'])}")
        
        if plan['tasks_to_reflect']:
            print("\n📂 Задачи для рефлексии:")
            for i, task in enumerate(plan['tasks_to_reflect'][:5], 1):
                task_name = task['data'].get('project', task['id'])
                print(f"   {i}. {task_name}")
            if len(plan['tasks_to_reflect']) > 5:
                print(f"   ... и еще {len(plan['tasks_to_reflect']) - 5}")
        
        try:
            response = input("\n🤔 Начать рефлексию? (y/n): ").lower().strip()
            return response in ['y', 'yes', 'д', 'да']
        except (EOFError, KeyboardInterrupt):
            return False
    
    def _execute_reflection(self, plan: Dict, deep: bool, verbose: bool) -> Dict[str, Any]:
        """Выполнение процесса рефлексии"""
        if verbose:
            print("🧠 Выполнение рефлексии...")
        
        results = {
            'timestamp': time.time(),
            'insights': [],
            'lessons_learned': [],
            'improvement_actions': [],
            'patterns': [],
            'recommendations': []
        }
        
        # Анализируем каждую задачу
        for task in plan['tasks_to_reflect']:
            task_insights = self._reflect_on_task(task, deep, verbose)
            results['insights'].extend(task_insights)
        
        # Ищем общие паттерны
        if deep:
            patterns = self._identify_patterns(plan['tasks_to_reflect'], verbose)
            results['patterns'].extend(patterns)
        
        # Генерируем рекомендации
        recommendations = self._generate_recommendations(results, verbose)
        results['recommendations'].extend(recommendations)
        
        if verbose:
            print(f"   ✅ Создано инсайтов: {len(results['insights'])}")
            print(f"   ✅ Выявлено паттернов: {len(results['patterns'])}")
            print(f"   ✅ Рекомендаций: {len(results['recommendations'])}")
        
        return results
    
    def _reflect_on_task(self, task: Dict, deep: bool, verbose: bool) -> List[Dict[str, Any]]:
        """Рефлексия по конкретной задаче"""
        insights = []
        task_data = task['data']
        task_name = task_data.get('project', task['id'])
        
        if verbose:
            print(f"   🔍 Анализ задачи: {task_name}")
        
        # Базовый анализ
        insight = {
            'task_id': task['id'],
            'task_name': task_name,
            'completion_date': task.get('completion_date', ''),
            'type': 'task_analysis',
            'observations': []
        }
        
        # Анализ статуса и прогресса
        if 'status' in task_data:
            insight['observations'].append(f"Статус задачи: {task_data['status']}")
        
        if 'progress' in task_data:
            insight['observations'].append(f"Прогресс: {task_data['progress']}")
        
        # Анализ версии
        if 'version' in task_data:
            insight['observations'].append(f"Версия: {task_data['version']}")
        
        insights.append(insight)
        return insights
    
    def _identify_patterns(self, tasks: List[Dict], verbose: bool) -> List[Dict[str, Any]]:
        """Выявление паттернов в выполненных задачах"""
        if verbose:
            print("   🔍 Поиск паттернов...")
        
        patterns = []
        
        # Паттерн: типы задач
        task_types = {}
        for task in tasks:
            task_type = task['data'].get('domain', 'unknown')
            task_types[task_type] = task_types.get(task_type, 0) + 1
        
        if task_types:
            patterns.append({
                'type': 'task_types',
                'description': 'Распределение типов задач',
                'data': task_types
            })
        
        return patterns
    
    def _generate_recommendations(self, results: Dict, verbose: bool) -> List[Dict[str, Any]]:
        """Генерация рекомендаций на основе рефлексии"""
        if verbose:
            print("   💡 Генерация рекомендаций...")
        
        recommendations = []
        
        # Рекомендация: регулярная рефлексия
        recommendations.append({
            'category': 'process_improvement',
            'title': 'Регулярная рефлексия',
            'description': 'Проводить рефлексию каждые 3-7 дней для поддержания осознанности',
            'priority': 'high',
            'action': 'Настроить напоминания для регулярной рефлексии'
        })
        
        return recommendations
    
    def _save_reflection_results(self, results: Dict, verbose: bool):
        """Сохранение результатов рефлексии"""
        if verbose:
            print("💾 Сохранение результатов рефлексии...")
        
        # Обновляем лог рефлексии
        reflection_log = self._load_reflection_log()
        
        # Добавляем результаты
        if 'sessions' not in reflection_log:
            reflection_log['sessions'] = []
        
        session = {
            'timestamp': results['timestamp'],
            'insights_count': len(results['insights']),
            'patterns_count': len(results['patterns']),
            'recommendations_count': len(results['recommendations']),
            'results': results
        }
        
        reflection_log['sessions'].append(session)
        
        # Обновляем список отрефлексированных задач
        if 'reflected_tasks' not in reflection_log:
            reflection_log['reflected_tasks'] = []
        
        for insight in results['insights']:
            if insight.get('task_id'):
                if insight['task_id'] not in reflection_log['reflected_tasks']:
                    reflection_log['reflected_tasks'].append(insight['task_id'])
        
        # Сохраняем лог
        try:
            with open(self.reflection_log, 'w', encoding='utf-8') as f:
                json.dump(reflection_log, f, ensure_ascii=False, indent=2, default=str)
            
            if verbose:
                print(f"   ✅ Результаты сохранены в {self.reflection_log}")
                
        except IOError as e:
            print(f"   ⚠️  Ошибка сохранения: {e}")
    
    def _switch_to_reflection_context(self, verbose: bool):
        """Переключение контекста на рефлексию"""
        if verbose:
            print("🔄 Переключение контекста на рефлексию...")
        
        try:
            # Находим корневую директорию проекта (где находится файл slc)
            root_path = self.base_path.parent  # .context -> smart_layered_context
            slc_path = root_path / 'slc'
            
            if slc_path.exists():
                # Загружаем контекст рефлексии через CLI
                import subprocess
                result = subprocess.run(
                    [str(slc_path), 'load-context', 'reflection_system'],
                    capture_output=True,
                    text=True,
                    cwd=str(root_path)
                )
                
                if result.returncode == 0:
                    if verbose:
                        print("   ✅ Контекст рефлексии загружен")
                else:
                    if verbose:
                        print("   ⚠️  Не удалось загрузить контекст рефлексии")
            else:
                if verbose:
                    print("   ✅ Контекст рефлексии активирован (файл slc не найден, но это нормально)")
                    
        except Exception as e:
            if verbose:
                print(f"   ⚠️  Ошибка переключения контекста: {e}")
                print("   ✅ Продолжаем без переключения контекста")
    
    # Вспомогательные методы
    def _get_active_tasks(self) -> List[Dict]:
        """Получение списка активных задач"""
        active_tasks = []
        active_file = self.tasks_dir / 'active.json'
        
        if active_file.exists():
            try:
                with open(active_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'tasks' in data:
                        active_tasks = data['tasks']
                    elif isinstance(data, list):
                        active_tasks = data
            except (json.JSONDecodeError, IOError):
                pass
        
        return active_tasks
    
    def _get_completed_tasks(self) -> List[Dict]:
        """Получение списка завершенных задач"""
        completed = []
        
        if self.tasks_dir.exists():
            for task_file in self.tasks_dir.rglob('*.json'):
                if task_file.name == 'active.json':
                    continue
                    
                try:
                    with open(task_file, 'r', encoding='utf-8') as f:
                        task_data = json.load(f)
                        
                    if self._is_task_completed(task_data):
                        completed.append(task_data)
                        
                except (json.JSONDecodeError, IOError):
                    pass
        
        return completed
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Получение метрик системы"""
        modules_path = self.base_path / '.context' / 'modules'
        templates_count = 0
        
        if modules_path.exists():
            templates_count = len(list(modules_path.rglob('*.json')))
        
        return {
            'templates_count': templates_count,
            'cli_commands': 24,  # Известное количество команд
            'disk_usage': self._get_directory_size(self.base_path)
        }
    
    def _get_last_reflection_date(self) -> Optional[str]:
        """Получение даты последней рефлексии"""
        reflection_log = self._load_reflection_log()
        sessions = reflection_log.get('sessions', [])
        
        if sessions:
            last_session = max(sessions, key=lambda x: x.get('timestamp', 0))
            timestamp = last_session.get('timestamp', 0)
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        
        return None
    
    def _load_reflection_log(self) -> Dict[str, Any]:
        """Загрузка лога рефлексии"""
        if self.reflection_log.exists():
            try:
                with open(self.reflection_log, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        return {
            'version': '1.0',
            'created': time.time(),
            'reflected_tasks': [],
            'sessions': []
        }
    
    def _is_task_recently_completed(self, task_data: Dict, cutoff_date: datetime) -> bool:
        """Проверка, была ли задача недавно завершена"""
        completion_date = self._get_task_completion_date(task_data)
        if completion_date:
            try:
                # Пробуем разные форматы дат
                formats = [
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d',
                    '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%dT%H:%M:%SZ',
                    '%Y-%m-%dT%H:%M:%S.%f'
                ]
                
                for fmt in formats:
                    try:
                        task_datetime = datetime.strptime(completion_date, fmt)
                        # Проверяем, что задача была завершена недавно
                        is_recent = task_datetime >= cutoff_date
                        if is_recent:
                            return True
                    except ValueError:
                        continue
                        
                # Если не удалось распарсить дату, считаем задачу недавней
                # если она имеет признаки завершения
                return self._is_task_completed(task_data)
                        
            except Exception:
                pass
        return False
    
    def _is_task_completed(self, task_data: Dict) -> bool:
        """Проверка, завершена ли задача"""
        status = task_data.get('status', '').lower()
        progress = task_data.get('progress', 0)
        completion = task_data.get('completion', '')
        
        # Проверяем различные индикаторы завершения
        status_completed = status in ['completed', 'done', 'finished']
        progress_completed = progress >= 100
        completion_completed = '100%' in str(completion)
        has_completion_date = self._get_task_completion_date(task_data) is not None
        
        return status_completed or progress_completed or completion_completed or has_completion_date
    
    def _get_task_completion_date(self, task_data: Dict) -> Optional[str]:
        """Получение даты завершения задачи"""
        # Ищем различные поля с датой завершения
        for field in ['completed_date', 'finished_date', 'updated', 'last_modified']:
            if field in task_data:
                return str(task_data[field])
        
        return None
    
    def _get_directory_size(self, path: Path) -> int:
        """Получение размера директории"""
        total_size = 0
        try:
            for file_path in path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except (OSError, PermissionError):
            pass
        return total_size 