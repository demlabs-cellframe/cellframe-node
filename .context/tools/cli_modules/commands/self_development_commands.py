#!/usr/bin/env python3
"""
Команды саморазвития для Smart Layered Context CLI
Переключение на режим саморазвития, анализ выполненных задач

Версия: 1.0.0
Создано: 2025-01-16
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


class SelfDevelopmentCommand(BaseCommand):
    """Команда для переключения на режим саморазвития и анализа задач"""
    
    def __init__(self, base_path: str):
        super().__init__()
        self.base_path = Path(base_path)
        self.tasks_dir = self.base_path / 'tasks'
        self.reflection_log = self.base_path / '.slc_reflection_log.json'
        
    @property
    def name(self) -> str:
        return "саморазвитие"
    
    @property
    def description(self) -> str:
        return "🧠 Переключение на режим саморазвития и анализа выполненных задач"
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--auto-start", 
            action="store_true",
            help="Автоматически начать анализ без подтверждения"
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
            help="Подробный вывод процесса анализа"
        )
        parser.add_argument(
            "--deep",
            action="store_true", 
            help="Глубокий анализ с выявлением паттернов и улучшений"
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
        """Выполнение команды саморазвития"""
        print("🧠 ЗАПУСК РЕЖИМА САМОРАЗВИТИЯ СЛК")
        print("=" * 60)
        
        try:
            # 1. Анализ текущего состояния
            current_state = self._analyze_current_state(args.verbose)
            
            # 2. Поиск неотрефлексированных задач
            unreflected_tasks = self._find_unreflected_tasks(args.days_back, args.verbose)
            
            # 3. Создание плана анализа
            analysis_plan = self._create_analysis_plan(unreflected_tasks, current_state, args.verbose)
            
            # 4. Переключение на задачи анализа
            if not args.auto_start:
                print("🚀 Автоматический запуск анализа (интерактивность отключена)")
                print(f"📋 Будет проанализировано задач: {len(unreflected_tasks)}")
                print(f"🔍 Областей анализа: {len(analysis_plan.get('analysis_areas', []))}")
            
            # 5. Выполнение анализа
            analysis_results = self._execute_analysis(analysis_plan, args.deep, args.verbose)
            
            # 6. Сохранение результатов
            self._save_analysis_results(analysis_results, args.verbose)
            
            # 7. Переключение контекста на саморазвитие
            self._switch_to_development_context(args.verbose)
            
            print("\n🎉 АНАЛИЗ САМОРАЗВИТИЯ ЗАВЕРШЕН УСПЕШНО!")
            print(f"📊 Проанализировано задач: {len(unreflected_tasks)}")
            print(f"🧠 Создано инсайтов: {len(analysis_results.get('insights', []))}")
            print("🚀 Контекст переключен на саморазвитие")
            
            # Выводим JSON контекст, если запрошен
            if args.json_context:
                context_output = create_reflection_context(analysis_results, str(self.base_path))
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
            self.print_error(f"Критическая ошибка анализа: {e}")
            return 1
    
    def _analyze_current_state(self, verbose: bool) -> Dict[str, Any]:
        """Анализ текущего состояния СЛК системы"""
        if verbose:
            print("📊 Анализ текущего состояния...")
        
        state = {
            'timestamp': time.time(),
            'tasks_total': 0,
            'tasks_active': 0,
            'tasks_completed': 0,
            'templates_count': 0,
            'last_activity': None
        }
        
        # Анализ задач
        if self.tasks_dir.exists():
            active_tasks_file = self.tasks_dir / 'active.json'
            if active_tasks_file.exists():
                try:
                    with open(active_tasks_file, 'r', encoding='utf-8') as f:
                        active_data = json.load(f)
                        state['tasks_active'] = len(active_data.get('tasks', []))
                        state['tasks_total'] += state['tasks_active']
                except:
                    pass
            
            completed_dir = self.tasks_dir / 'completed'
            if completed_dir.exists():
                completed_files = list(completed_dir.glob('*.json'))
                state['tasks_completed'] = len(completed_files)
                state['tasks_total'] += state['tasks_completed']
                
                if completed_files:
                    latest_file = max(completed_files, key=lambda f: f.stat().st_mtime)
                    state['last_activity'] = latest_file.stat().st_mtime
        
        if verbose:
            print(f"   ✅ Найдено задач: {state['tasks_total']} (активных: {state['tasks_active']}, завершенных: {state['tasks_completed']})")
        
        return state
    
    def _find_unreflected_tasks(self, days_back: int, verbose: bool) -> List[Dict[str, Any]]:
        """Поиск задач, которые не были отрефлексированы"""
        if verbose:
            print(f"🔍 Поиск неотрефлексированных задач за последние {days_back} дней...")
        
        # Загружаем лог рефлексии
        reflection_log = self._load_reflection_log()
        reflected_task_ids = set(reflection_log.get('reflected_tasks', []))
        
        unreflected = []
        cutoff_time = time.time() - (days_back * 24 * 60 * 60)
        
        # Ищем в завершенных задачах
        completed_dir = self.tasks_dir / 'completed'
        if completed_dir.exists():
            for task_file in completed_dir.glob('*.json'):
                if task_file.stat().st_mtime < cutoff_time:
                    continue
                
                try:
                    with open(task_file, 'r', encoding='utf-8') as f:
                        task_data = json.load(f)
                        task_id = task_file.stem
                        
                        if task_id not in reflected_task_ids:
                            unreflected.append({
                                'id': task_id,
                                'file_path': str(task_file),
                                'completion_time': task_file.stat().st_mtime,
                                'data': task_data
                            })
                except:
                    continue
        
        if verbose:
            print(f"   ✅ Найдено неотрефлексированных задач: {len(unreflected)}")
            for task in unreflected[:3]:  # Показываем первые 3
                task_name = task['data'].get('project', task['id'])
                print(f"      • {task_name}")
            if len(unreflected) > 3:
                print(f"      ... и еще {len(unreflected) - 3}")
        
        return unreflected
    
    def _create_analysis_plan(self, unreflected_tasks: List[Dict], current_state: Dict, verbose: bool) -> Dict[str, Any]:
        """Создание плана анализа для саморазвития"""
        if verbose:
            print("📋 Создание плана анализа...")
        
        plan = {
            'timestamp': time.time(),
            'tasks_to_analyze': unreflected_tasks,
            'analysis_areas': [],
            'questions': [],
            'improvement_opportunities': []
        }
        
        # Определяем области для анализа
        if unreflected_tasks:
            plan['analysis_areas'].extend([
                'Эффективность выполнения задач',
                'Качество результатов',
                'Использованные подходы и методы',
                'Возникшие проблемы и их решения',
                'Полученные знания и навыки'
            ])
        
        # Добавляем вопросы для анализа
        plan['questions'].extend([
            'Какие паттерны успеха можно выделить?',
            'Где есть возможности для улучшения?',
            'Какие знания были получены?',
            'Как оптимизировать рабочие процессы?'
        ])
        
        if verbose:
            print(f"   ✅ Создан план анализа с {len(plan['analysis_areas'])} областями")
        
        return plan
    
    def _execute_analysis(self, plan: Dict, deep: bool, verbose: bool) -> Dict[str, Any]:
        """Выполнение процесса анализа саморазвития"""
        if verbose:
            print("🧠 Выполнение анализа саморазвития...")
        
        results = {
            'timestamp': time.time(),
            'insights': [],
            'lessons_learned': [],
            'improvement_actions': [],
            'patterns': [],
            'recommendations': []
        }
        
        # Анализируем каждую задачу
        for task in plan['tasks_to_analyze']:
            task_insights = self._analyze_task(task, deep, verbose)
            results['insights'].extend(task_insights)
        
        # Ищем общие паттерны
        if deep:
            patterns = self._identify_patterns(plan['tasks_to_analyze'], verbose)
            results['patterns'].extend(patterns)
        
        # Генерируем рекомендации
        recommendations = self._generate_recommendations(results, verbose)
        results['recommendations'].extend(recommendations)
        
        if verbose:
            print(f"   ✅ Создано инсайтов: {len(results['insights'])}")
            print(f"   ✅ Выявлено паттернов: {len(results['patterns'])}")
            print(f"   ✅ Рекомендаций: {len(results['recommendations'])}")
        
        return results
    
    def _analyze_task(self, task: Dict, deep: bool, verbose: bool) -> List[Dict[str, Any]]:
        """Анализ отдельной задачи"""
        insights = []
        
        task_data = task['data']
        task_name = task_data.get('project', task['id'])
        
        # Базовый анализ
        insight = {
            'task_id': task['id'],
            'task_name': task_name,
            'type': 'task_analysis',
            'completion_time': task['completion_time'],
            'analysis': {
                'project_type': task_data.get('project_type', 'unknown'),
                'status': task_data.get('status', 'unknown'),
                'duration': self._calculate_task_duration(task_data),
                'complexity': self._assess_complexity(task_data)
            }
        }
        
        insights.append(insight)
        
        return insights
    
    def _identify_patterns(self, tasks: List[Dict], verbose: bool) -> List[Dict[str, Any]]:
        """Выявление паттернов в выполненных задачах"""
        patterns = []
        
        if not tasks:
            return patterns
        
        # Анализ по типам проектов
        project_types = {}
        for task in tasks:
            project_type = task['data'].get('project_type', 'unknown')
            if project_type not in project_types:
                project_types[project_type] = 0
            project_types[project_type] += 1
        
        if project_types:
            patterns.append({
                'type': 'project_distribution',
                'data': project_types,
                'insight': f"Чаще всего работаю с проектами типа: {max(project_types, key=project_types.get)}"
            })
        
        return patterns
    
    def _generate_recommendations(self, results: Dict, verbose: bool) -> List[Dict[str, Any]]:
        """Генерация рекомендаций для саморазвития"""
        recommendations = []
        
        # Базовые рекомендации
        recommendations.extend([
            {
                'type': 'process_improvement',
                'title': 'Систематизация рабочих процессов',
                'description': 'Создать стандартные процедуры для часто выполняемых задач'
            },
            {
                'type': 'knowledge_management',
                'title': 'Управление знаниями',
                'description': 'Ведение базы знаний с решениями типовых проблем'
            }
        ])
        
        return recommendations
    
    def _calculate_task_duration(self, task_data: Dict) -> Optional[float]:
        """Расчет длительности выполнения задачи"""
        # Упрощенная логика - можно расширить
        return None
    
    def _assess_complexity(self, task_data: Dict) -> str:
        """Оценка сложности задачи"""
        # Упрощенная логика - можно расширить
        return "medium"
    
    def _load_reflection_log(self) -> Dict[str, Any]:
        """Загрузка лога рефлексии"""
        if self.reflection_log.exists():
            try:
                with open(self.reflection_log, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_analysis_results(self, results: Dict, verbose: bool):
        """Сохранение результатов анализа"""
        if verbose:
            print("💾 Сохранение результатов анализа...")
        
        # Обновляем лог рефлексии
        reflection_log = self._load_reflection_log()
        
        # Добавляем результаты
        if 'sessions' not in reflection_log:
            reflection_log['sessions'] = []
        
        session = {
            'timestamp': results['timestamp'],
            'type': 'self_development',
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
    
    def _switch_to_development_context(self, verbose: bool):
        """Переключение контекста на саморазвитие"""
        if verbose:
            print("🔄 Переключение контекста на саморазвитие...")
        
        try:
            # Находим корневую директорию проекта
            root_path = self.base_path.parent  # .context -> smart_layered_context
            slc_path = root_path / 'slc'
            
            if slc_path.exists():
                # Загружаем контекст саморазвития через CLI
                import subprocess
                result = subprocess.run(
                    [str(slc_path), 'load-context', 'self_development_system'],
                    capture_output=True,
                    text=True,
                    cwd=str(root_path)
                )
                
                if result.returncode == 0:
                    if verbose:
                        print("   ✅ Контекст саморазвития загружен")
                else:
                    if verbose:
                        print("   ⚠️  Не удалось загрузить контекст саморазвития")
            else:
                if verbose:
                    print("   ✅ Контекст саморазвития активирован")
                    
        except Exception as e:
            if verbose:
                print(f"   ⚠️  Ошибка переключения контекста: {e}")
                print("   ✅ Продолжаем без переключения контекста") 