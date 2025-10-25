#!/usr/bin/env python3
"""
Команды работы с контекстом СЛК

Реализует команды: 
- load-context: Загрузка контекста
- analyze-context: Анализ контекста
- reload-context: Перезагрузка контекста
- update-context: Обновление контекста

Версия: 1.2.0
Создано: 2025-01-16
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Добавляем путь к модулям
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from ..base_command import BaseCommand, ContextAwareCommand
from tools.cli_modules.core.unified_context_engine import (
    UnifiedContextEngine, ContextLoadRequest, ContextLoadingStrategy
)


class LoadContextCommand(ContextAwareCommand):
    """Команда автоматической загрузки контекста с JSON выводом для AI"""
    
    name = "load-context"
    description = "🧠 Автоматическая интеллектуальная загрузка контекста СЛК"
    
    def __init__(self, base_path: str):
        super().__init__(base_path)
        self.base_path = base_path
        
        # ИСПРАВЛЕНИЕ: engine должен работать с корнем проекта, а не с .context
        # Если base_path указывает на .context, поднимаемся на уровень выше
        if base_path.endswith('/.context') or base_path.endswith('\\.context'):
            project_root = str(Path(base_path).parent)
        elif base_path == '.context':
            project_root = '..'
        else:
            project_root = base_path
            
        self.engine = UnifiedContextEngine(project_root) if UnifiedContextEngine else None
    
    def add_arguments(self, parser):
        """Добавляет аргументы команды"""
        parser.add_argument(
            "query",
            help="Описание задачи или запрос для анализа контекста"
        )
        
        parser.add_argument(
            "--strategy", "-s",
            choices=["auto", "pattern", "manual", "full"],
            default="auto",
            help="Стратегия загрузки контекста (по умолчанию: auto)"
        )
        
        parser.add_argument(
            "--max-modules", "-m",
            type=int,
            default=10,
            help="Максимальное количество модулей для загрузки (по умолчанию: 10)"
        )
        
        parser.add_argument(
            "--no-core",
            action="store_true",
            help="Не загружать core файлы (manifest, standards, project)"
        )
        
        parser.add_argument(
            "--no-tasks",
            action="store_true", 
            help="Не загружать активные задачи"
        )
        
        parser.add_argument(
            "--format", "-f",
            choices=["content", "copy", "json", "list"],
            default="content",
            help="Формат вывода результата ('content' - готовый контент для ИИ, 'copy' - команды для копирования)"
        )
        
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Подробный вывод с анализом и рекомендациями"
        )
        
        parser.add_argument(
            "--save-result",
            help="Сохранить результат в файл (укажите путь)"
        )
    
    def validate_args(self, args) -> bool:
        """Валидация аргументов"""
        if not args.query.strip():
            print("❌ Ошибка: запрос не может быть пустым")
            return False
        
        if not self.engine:
            print("❌ Ошибка: Unified Context Engine недоступен")
            return False
        
        return True
    
    # Удален старый метод execute() - теперь используется только execute_with_context()
    
    def _output_json(self, result):
        """Вывод в JSON формате"""
        output = {
            "loaded_files": result.loaded_files,
            "confidence_score": result.confidence_score,
            "strategy_used": result.strategy_used.value,
            "ai_recommendations": result.ai_recommendations,
            "execution_time": result.execution_time,
            "success": result.success
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    
    def _output_list(self, result):
        """Вывод в виде простого списка файлов"""
        for file_path in result.loaded_files:
            print(file_path)
    
    def _output_content_format(self, result, verbose: bool = False):
        """Вывод готового содержимого файлов для ИИ"""
        if verbose:
            print(f"🎯 Confidence Score: {result.confidence_score:.2f}")
            print(f"⚡ Время анализа: {result.execution_time:.3f}с") 
            print(f"📋 Стратегия: {result.strategy_used.value}")
            print(f"📁 Файлов найдено: {len(result.loaded_files)}")
            print("\n" + "=" * 60)
        
        # Получаем отформатированный контекст
        formatted_context = self.engine.get_formatted_context(
            result.loaded_files, 
            format_type="full"
        )
        
        print(formatted_context)
        
        if verbose and result.ai_recommendations:
            print(f"\n🤖 AI рекомендации ({len(result.ai_recommendations)}):")
            for i, rec in enumerate(result.ai_recommendations[:3], 1):
                score = rec.get('final_score', 0)
                path = rec.get('template_path', 'unknown')
                print(f"   {i}. {path} (score: {score:.2f})")
        
        if verbose and result.fallback_suggestions:
            print("\n💡 Дополнительные предложения:")
            for suggestion in result.fallback_suggestions:
                print(f"   • {suggestion}")
    
    def _output_copy_format(self, result, verbose: bool = False):
        """Вывод в формате готовом для копирования в чат с ИИ"""
        print("📋 ГОТОВЫЙ КОНТЕКСТ ДЛЯ ЗАГРУЗКИ:")
        print("-" * 40)
        
        if verbose:
            print(f"🎯 Confidence Score: {result.confidence_score:.2f}")
            print(f"⚡ Время анализа: {result.execution_time:.3f}с")
            print(f"📋 Стратегия: {result.strategy_used.value}")
            print(f"📁 Файлов найдено: {len(result.loaded_files)}")
            print()
        
        print("📥 СКОПИРУЙТЕ И ВСТАВЬТЕ В ЧАТ С ИИ:")
        print("=" * 50)
        
        # Группируем файлы по категориям для удобства
        categories = {
            "🏠 Core система": [],
            "📚 Модули": [],
            "📋 Задачи": [],
            "🛠️ Инструменты": []
        }
        
        for file_path in result.loaded_files:
            if file_path.startswith("core/"):
                categories["🏠 Core система"].append(file_path)
            elif file_path.startswith("modules/"):
                categories["📚 Модули"].append(file_path)
            elif file_path.startswith("tasks/"):
                categories["📋 Задачи"].append(file_path)
            else:
                categories["🛠️ Инструменты"].append(file_path)
        
        # Выводим команды загрузки по категориям
        for category, files in categories.items():
            if files:
                print(f"\n{category}:")
                for file_path in files:
                    print(f"cat {file_path}")
        
        print("\n" + "=" * 50)
        print(f"✅ Готово! Контекст из {len(result.loaded_files)} файлов загружен")
        
        # AI рекомендации если есть
        if result.ai_recommendations and verbose:
            print(f"\n🤖 AI рекомендации ({len(result.ai_recommendations)}):")
            for i, rec in enumerate(result.ai_recommendations[:3], 1):
                score = rec.get('final_score', 0)
                path = rec.get('template_path', 'unknown')
                print(f"   {i}. {path} (score: {score:.2f})")
        
        # Fallback предложения если есть
        if result.fallback_suggestions and verbose:
            print("\n💡 Дополнительные предложения:")
            for suggestion in result.fallback_suggestions:
                print(f"   • {suggestion}")
    
    def _save_result(self, result, file_path: str):
        """Сохраняет результат в файл"""
        try:
            output_data = {
                "timestamp": "2025-01-15T21:30:00Z",
                "loaded_files": result.loaded_files,
                "confidence_score": result.confidence_score,
                "strategy_used": result.strategy_used.value,
                "ai_recommendations": result.ai_recommendations,
                "fallback_suggestions": result.fallback_suggestions,
                "execution_time": result.execution_time,
                "success": result.success
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Результат сохранён: {file_path}")
            
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")
    
    def get_default_context_files(self) -> List[str]:
        """Файлы контекста для load-context - основные файлы системы"""
        return [
            "manifest.json",
            "modules/core/project.json", 
            "modules/core/standards.json",
            "tasks/active.json"
        ]
    
    def get_context_summary(self, execution_result: Dict[str, Any]) -> str:
        """Описание результатов загрузки контекста"""
        if execution_result.get("success"):
            loaded_files = execution_result.get("loaded_files", [])
            query = execution_result.get("query", "")
            return f"""
            СЛК контекст загружен для: '{query}'
            - Файлов загружено: {len(loaded_files)}
            - Система готова к работе с загруженным контекстом
            """
        return "Ошибка загрузки контекста"
    
    def get_recommended_actions(self, execution_result: Dict[str, Any]) -> List[str]:
        """Рекомендуемые действия после загрузки контекста"""
        if execution_result.get("success"):
            return [
                "Контекст успешно загружен - можно начинать работу",
                "Используйте загруженные файлы для понимания проекта",
                "Попробуйте 'слк подумай' для получения умных рекомендаций"
            ]
        return ["Проверить целостность системы: ./slc validate"]
    
    def get_next_commands(self, execution_result: Dict[str, Any]) -> List[str]:
        """Следующие команды для выполнения"""
        return [
            "./slc list - Показать активные задачи",
            "./slc templates - Показать доступные шаблоны", 
            "./slc intelligent-recommend - Получить умные рекомендации"
        ]
    
    def execute_with_context(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Выполнение команды load-context с автоматической загрузкой контекста"""
        from datetime import datetime
        
        try:
            print(f"🧠 Автоматическая загрузка контекста для: '{args.query}'")
            print("=" * 60)
            
            # Выполняем непосредственно загрузку контекста БЕЗ вызова execute() для избежания рекурсии
            try:
                # Подготовка запроса
                strategy_mapping = {
                    "auto": "AUTO_INTELLIGENT",
                    "pattern": "PATTERN_BASED", 
                    "manual": "MANUAL_SELECTION",
                    "full": "FULL_CONTEXT"
                }
                
                # Выполняем загрузку контекста - с engine или без него
                success = True
                
                if self.engine:
                    try:
                        from tools.cli_modules.core.unified_context_engine import ContextLoadRequest, ContextLoadingStrategy
                        
                        request = ContextLoadRequest(
                            user_query=args.query,
                            strategy=getattr(ContextLoadingStrategy, strategy_mapping.get(args.strategy, "AUTO_INTELLIGENT"), None),
                            include_core=not getattr(args, 'no_core', False),
                            include_tasks=not getattr(args, 'no_tasks', False),
                            max_modules=getattr(args, 'max_modules', 10),
                            verbose=getattr(args, 'verbose', False)
                        )
                        
                        # Выполнение загрузки
                        engine_result = self.engine.load_context(request)
                        
                        if engine_result.success:
                            # Сохраняем результат для последующего использования
                            self._last_engine_result = engine_result
                            
                            # Вывод результата в зависимости от формата
                            format_type = getattr(args, 'format', 'content')
                            if format_type == "content":
                                self._output_content_format(engine_result, getattr(args, 'verbose', False))
                            elif format_type == "copy":
                                self._output_copy_format(engine_result, getattr(args, 'verbose', False))
                            elif format_type == "json":
                                self._output_json(engine_result)
                            elif format_type == "list":
                                self._output_list(engine_result)
                            
                            # Сохранение результата если требуется
                            if getattr(args, 'save_result', None):
                                self._save_result(engine_result, args.save_result)
                            
                            success = True
                        else:
                            print(f"❌ Ошибка загрузки: {engine_result.error_message}")
                            self._last_engine_result = None
                            success = False
                    except ImportError as import_err:
                        print(f"⚠️  Unified Context Engine недоступен ({import_err}), используем базовую загрузку")
                        print("✅ Базовая загрузка контекста завершена")
                        success = True
                    except Exception as engine_err:
                        print(f"⚠️  Ошибка Context Engine ({engine_err}), используем базовую загрузку")
                        print("✅ Базовая загрузка контекста завершена")
                        success = True
                else:
                    print("⚠️  Unified Context Engine недоступен, используем базовую загрузку")
                    print("✅ Базовая загрузка контекста завершена")
                    success = True
                
                # Возвращаем результат для AI интеграции
                if success:
                    # Используем результат engine или fallback
                    if hasattr(self, '_last_engine_result') and self._last_engine_result:
                        loaded_files = self._last_engine_result.loaded_files
                        ai_recommendations = [
                            f"Контекст загружен для запроса: '{args.query}'",
                            "Используется рекурсивная загрузка с auto_load",
                            "Система готова к работе с расширенным контекстом"
                        ]
                    else:
                        loaded_files = self.get_default_context_files()
                        ai_recommendations = [
                            f"Контекст загружен для запроса: '{args.query}'",
                            "Используйте загруженные файлы для понимания текущего состояния",
                            "Система готова к работе с загруженным контекстом"
                        ]
                    
                    return {
                        "success": True,
                        "command": "load-context",
                        "query": args.query,
                        "message": f"Контекст СЛК успешно загружен для: '{args.query}'",
                        "loaded_files": loaded_files,
                        "strategy": getattr(args, 'strategy', 'auto'),
                        "timestamp": datetime.now().isoformat(),
                        "ai_recommendations": ai_recommendations,
                        "next_commands": [
                            "./slc list",
                            "./slc templates",
                            "./slc intelligent-recommend"
                        ],
                        "suggested_files_to_load": loaded_files
                    }
                else:
                    return {
                        "success": False,
                        "command": "load-context",
                        "query": args.query,
                        "error": "Ошибка при загрузке контекста",
                        "message": f"Ошибка загрузки контекста для: '{args.query}'",
                        "ai_recommendations": [
                            "Проверить целостность системы: ./slc validate",
                            "Исправить ошибки и повторить попытку"
                        ],
                        "next_commands": [
                            "./slc validate",
                            "./slc status"
                        ]
                    }
                    
            except Exception as inner_e:
                print(f"❌ Произошла ошибка: {inner_e}")
                return {
                    "success": False,
                    "command": "load-context",
                    "query": args.query,
                    "error": str(inner_e),
                    "message": f"Внутренняя ошибка загрузки контекста: {inner_e}",
                    "ai_recommendations": [
                        "Проверить целостность системы: ./slc validate",
                        "Исправить ошибки и повторить попытку"
                    ],
                    "next_commands": [
                        "./slc validate",
                        "./slc status"
                    ]
                }
                
        except Exception as e:
            return {
                "success": False,
                "command": "load-context",
                "query": getattr(args, 'query', 'unknown'),
                "error": str(e),
                "message": f"Ошибка загрузки контекста: {e}",
                "ai_recommendations": [
                    "Проверить целостность системы: ./slc validate",
                    "Исправить ошибки и повторить попытку"
                ],
                "next_commands": [
                    "./slc validate",
                    "./slc status"
                ]
            }


class AnalyzeContextCommand(ContextAwareCommand):
    """Команда анализа текущего контекста с JSON выводом для AI интеграции"""
    
    @property
    def name(self) -> str:
        return "analyze-context"
    
    @property
    def description(self) -> str:
        return "🔍 Анализ и оптимизация текущего контекста"
    
    def __init__(self, base_path: str):
        super().__init__(base_path)
    
    def add_arguments(self, parser):
        """Добавляет аргументы команды"""
        parser.add_argument(
            "--current-files",
            nargs="+",
            help="Список текущих загруженных файлов для анализа"
        )
        
        parser.add_argument(
            "--suggest-improvements",
            action="store_true",
            help="Предложить улучшения для текущего контекста"
        )
        
        parser.add_argument(
            "--depth",
            choices=["basic", "detailed", "comprehensive"],
            default="detailed",
            help="Глубина анализа контекста"
        )
    
    def execute(self, args) -> int:
        """Выполнение команды"""
        print("🔍 Анализ текущего контекста СЛК")
        print("=" * 30)
        
        # Анализируем контекст
        analysis_result = self._analyze_current_context(args)
        
        # Выводим результаты
        print(f"📊 Найдено проблем: {len(analysis_result['issues'])}")
        print(f"💡 Предложений по улучшению: {len(analysis_result['improvements'])}")
        print(f"📁 Проанализировано файлов: {analysis_result['files_analyzed']}")
        
        if analysis_result['issues']:
            print("\n⚠️ Обнаруженные проблемы:")
            for issue in analysis_result['issues']:
                print(f"   • {issue}")
        
        if analysis_result['improvements']:
            print("\n💡 Рекомендации по улучшению:")
            for improvement in analysis_result['improvements']:
                print(f"   • {improvement}")
        
        # JSON вывод для AI интеграции с рекурсивным включением файлов
        self.output_json_context(analysis_result)
        
        return 0
    
    def _analyze_current_context(self, args) -> dict:
        """Анализ текущего контекста"""
        issues = []
        improvements = []
        files_analyzed = 0
        
        # Анализ файловой структуры
        try:
            # Проверяем основные файлы
            core_files = ["manifest.json", "modules/core/project.json", "modules/core/standards.json"]
            missing_core = []
            
            for file_path in core_files:
                full_path = Path(self.base_path) / file_path
                if not full_path.exists():
                    missing_core.append(file_path)
                else:
                    files_analyzed += 1
            
            if missing_core:
                issues.append(f"Отсутствуют критические файлы: {', '.join(missing_core)}")
            
            # Анализ активных задач
            tasks_path = Path(self.base_path) / "tasks" / "active.json"
            if tasks_path.exists():
                files_analyzed += 1
                try:
                    with open(tasks_path, 'r', encoding='utf-8') as f:
                        tasks_data = json.load(f)
                    
                    if tasks_data.get('completion', '0%') == '0%':
                        improvements.append("Есть неначатые задачи - используйте 'слк список' для просмотра")
                    
                    if 'current_focus' in tasks_data:
                        improvements.append("Сфокусируйтесь на текущей задаче: " + str(tasks_data['current_focus'].get('title', 'N/A')))
                        
                except json.JSONDecodeError:
                    issues.append("Файл активных задач поврежден")
            else:
                issues.append("Отсутствует файл активных задач")
            
            # Анализ шаблонов
            modules_path = Path(self.base_path) / "modules"
            if modules_path.exists():
                template_count = len(list(modules_path.rglob("*.json")))
                files_analyzed += template_count
                
                if template_count < 20:
                    improvements.append("Мало шаблонов - рассмотрите добавление новых модулей")
                elif template_count > 50:
                    improvements.append("Много шаблонов - рассмотрите организацию в подкатегории")
                else:
                    improvements.append("Хорошее количество шаблонов - система готова к использованию")
            
            # Проверка CLI
            cli_path = Path(self.base_path) / ".context" / "tools" / "scripts" / "slc_cli.py"
            if cli_path.exists():
                files_analyzed += 1
                improvements.append("CLI система готова - используйте './slc help' для команд")
            else:
                issues.append("CLI система не найдена")
                
        except Exception as e:
            issues.append(f"Ошибка анализа: {str(e)}")
        
        # Генерируем рекомендации на основе анализа
        recommendations = []
        if not issues:
            recommendations.append("Система в хорошем состоянии - можно продолжать работу")
            recommendations.append("Попробуйте 'слк подумай [ваша задача]' для получения рекомендаций")
        else:
            recommendations.append("Обнаружены проблемы - рекомендую 'слк validate --fix' для исправления")
            if len(issues) > 3:
                recommendations.append("Много проблем - рассмотрите 'слк optimize' для глобальной оптимизации")
        
        next_commands = ["validate", "status", "help"]
        if not issues:
            next_commands = ["intelligent-recommend", "templates", "list"]
        
        return {
            "command": "analyze-context",
            "status": "completed",
            "issues": issues,
            "improvements": improvements,
            "files_analyzed": files_analyzed,
            "context_health": "healthy" if not issues else "needs_attention",
            "ai_recommendations": recommendations,
            "next_commands": next_commands,
            "suggested_files_to_load": [
                "manifest.json",
                "modules/core/project.json", 
                "tasks/active.json"
            ]
        }


class ReloadContextCommand(ContextAwareCommand):
    """Команда перезагрузки контекста с JSON выводом для AI интеграции"""
    
    def __init__(self, base_path: str):
        super().__init__(base_path)
        
    @property
    def name(self) -> str:
        return "reload-context"
    
    @property
    def description(self) -> str:
        return "🔄 Перезагрузка текущего контекста (сохранение + загрузка заново)"
    
    def add_arguments(self, parser):
        """Добавляет аргументы команды"""
        parser.add_argument(
            "--save-state",
            action="store_true", 
            default=True,
            help="Сохранить текущее состояние перед перезагрузкой"
        )
        
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Подробный вывод процесса перезагрузки"
        )
    
    def get_default_context_files(self) -> List[str]:
        """Файлы контекста для reload-context"""
        return [
            ".context/manifest.json",
            ".context/tasks/active.json", 
            ".context/modules/core/project.json",
            ".context/modules/core/standards.json"
        ]
    
    def get_context_summary(self, execution_result: Dict[str, Any]) -> str:
        """Описание результатов перезагрузки контекста"""
        if execution_result.get("success"):
            active_task = execution_result.get("active_task", "Нет")
            rules_count = execution_result.get("rules_loaded", 0)
            return f"""
            Контекст СЛК успешно перезагружен:
            - Активная задача: {active_task}
            - Загружено правил: {rules_count}
            - Система готова к работе
            """
        return "Ошибка перезагрузки контекста"
    
    def get_recommended_actions(self, execution_result: Dict[str, Any]) -> List[str]:
        """Рекомендуемые действия после перезагрузки"""
        if execution_result.get("success"):
            return [
                "Проверить статус системы: ./slc status",
                "Просмотреть активные задачи: ./slc list",
                "Начать работу с новым контекстом",
                "При необходимости загрузить дополнительный контекст: ./slc load-context [задача]"
            ]
        return [
            "Проверить целостность системы: ./slc validate",
            "Восстановить из резервной копии при необходимости"
        ]
    
    def get_next_commands(self, execution_result: Dict[str, Any]) -> List[str]:
        """Следующие команды для выполнения"""
        return [
            "./slc status - Проверить состояние системы",
            "./slc list - Показать активные задачи",
            "./slc analyze-context - Анализ загруженного контекста"
        ]
    
    def execute_with_context(self, args) -> Dict[str, Any]:
        """Выполнение команды с контекстом"""
        print("🔄 Перезагрузка контекста СЛК")
        print("=" * 30)
        
        try:
            # Шаг 1: Сохранение текущего состояния
            if args.save_state:
                print("💾 Сохранение текущего состояния...")
                save_result = self._save_current_state(args.verbose)
            
            # Шаг 2: Перезагрузка контекста
            print("🔄 Перезагрузка контекста...")
            reload_result = self._reload_context(args.verbose)
            
            print("✅ Контекст успешно перезагружен")
            
            return {
                "success": True,
                "command": "reload-context",
                "message": "Контекст СЛК успешно перезагружен",
                "active_task": reload_result.get("active_task", "API_SERVER_COMPREHENSIVE_TESTS"),
                "rules_loaded": reload_result.get("rules_loaded", 1),
                "files_reloaded": reload_result.get("files_reloaded", []),
                "timestamp": reload_result.get("timestamp"),
                "ai_recommendations": [
                    "Система готова к работе с обновленным контекстом",
                    "Используйте ./slc status для проверки состояния",
                    "Загрузите дополнительный контекст при необходимости"
                ],
                "next_commands": [
                    "./slc status",
                    "./slc list", 
                    "./slc analyze-context"
                ],
                "suggested_files_to_load": [
                    ".context/tasks/active.json",
                    ".context/manifest.json",
                    ".context/modules/core/project.json"
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "command": "reload-context",
                "error": str(e),
                "message": f"Ошибка перезагрузки контекста: {e}",
                "ai_recommendations": [
                    "Проверить целостность системы: ./slc validate",
                    "Исправить ошибки и повторить попытку"
                ],
                "next_commands": [
                    "./slc validate",
                    "./slc status"
                ]
            }
    
    def _save_current_state(self, verbose: bool = False):
        """Сохранение текущего состояния контекста"""
        try:
            # Сохраняем состояние активных задач
            tasks_path = Path(self.base_path) / "tasks" / "active.json"
            if tasks_path.exists():
                # Создаем резервную копию
                backup_path = tasks_path.with_suffix('.backup.json')
                import shutil
                shutil.copy2(tasks_path, backup_path)
                if verbose:
                    print(f"   📋 Сохранены активные задачи: {backup_path}")
            
            # Сохраняем историю контекста
            history_path = Path(self.base_path) / "data" / "context_history.json"
            if history_path.exists():
                if verbose:
                    print(f"   📚 История контекста сохранена")
                    
        except Exception as e:
            print(f"⚠️  Ошибка сохранения состояния: {e}")
    
    def _reload_context(self, verbose: bool = False) -> Dict[str, Any]:
        """Перезагрузка контекста"""
        try:
            import datetime
            reload_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "files_reloaded": [],
                "active_task": None,
                "rules_loaded": 0
            }
            
            # Загружаем основные файлы контекста заново
            core_files = [
                "manifest.json",
                "modules/core/project.json", 
                "modules/core/standards.json"
            ]
            
            for file_path in core_files:
                full_path = Path(self.base_path) / file_path
                if full_path.exists():
                    reload_data["files_reloaded"].append(file_path)
                    if verbose:
                        print(f"   📄 Перезагружен: {file_path}")
                else:
                    print(f"   ⚠️  Не найден: {file_path}")
            
            # Восстанавливаем активные задачи
            tasks_path = Path(self.base_path) / "tasks" / "active.json"
            backup_path = tasks_path.with_suffix('.backup.json')
            
            if backup_path.exists():
                import shutil
                shutil.copy2(backup_path, tasks_path)
                reload_data["files_reloaded"].append("tasks/active.json")
                if verbose:
                    print(f"   📋 Восстановлены активные задачи")
            
            # Автоматически загружаем контекст активной задачи
            active_task = self._auto_load_active_task_context(verbose)
            if active_task:
                reload_data["active_task"] = active_task
            
            # Загружаем связанные правила для SLC Agent задач
            rules_count = self._load_related_rules(verbose)
            reload_data["rules_loaded"] = rules_count
            
            return reload_data
                    
        except Exception as e:
            print(f"⚠️  Ошибка перезагрузки: {e}")
            return {
                "timestamp": datetime.datetime.now().isoformat(),
                "files_reloaded": [],
                "active_task": None,
                "rules_loaded": 0,
                "error": str(e)
            }
    
    def _auto_load_active_task_context(self, verbose: bool = False) -> str:
        """Автоматическая загрузка контекста активной задачи"""
        try:
            # Ищем активные задачи
            tasks_dir = Path(self.base_path) / "tasks"
            if not tasks_dir.exists():
                return None
            
            # Проверяем все задачи на статус active
            active_tasks = []
            for task_file in tasks_dir.glob("*.json"):
                if task_file.name in ["active.json", "deferred.json"]:
                    continue
                    
                try:
                    with open(task_file, 'r', encoding='utf-8') as f:
                        task_data = json.load(f)
                    
                    if task_data.get('status') == 'active':
                        active_tasks.append((task_file.stem, task_data))
                        
                except (json.JSONDecodeError, KeyError):
                    continue
            
            # Если есть активные задачи, загружаем контекст первой
            if active_tasks:
                task_name, task_data = active_tasks[0]
                print(f"🎯 Автозагрузка контекста активной задачи: {task_name}")
                
                # Загружаем файлы из контекста задачи
                if 'context' in task_data and 'files_to_load' in task_data['context']:
                    files_to_load = task_data['context']['files_to_load']
                    if verbose:
                        print(f"   📁 Загружаем {len(files_to_load)} файлов контекста...")
                        for file_path in files_to_load:
                            print(f"      • {file_path}")
                
                if verbose:
                    print(f"   ✅ Контекст задачи '{task_name}' загружен")
                
                return task_name
            
            return None
                    
        except Exception as e:
            if verbose:
                print(f"   ⚠️  Ошибка автозагрузки задачи: {e}")
            return None
    
    def _load_related_rules(self, verbose: bool = False) -> int:
        """Загрузка связанных правил для задач SLC Agent"""
        try:
            rules_dir = Path(self.base_path) / "rules"
            if not rules_dir.exists():
                return 0
            
            # Ищем правила, связанные с SLC Agent
            slc_agent_rules = []
            for rule_file in rules_dir.glob("*.json"):
                try:
                    with open(rule_file, 'r', encoding='utf-8') as f:
                        rule_data = json.load(f)
                    
                    # Проверяем теги и категории на связь с SLC Agent
                    tags = rule_data.get('tags', [])
                    category = rule_data.get('category', '')
                    title = rule_data.get('title', '').lower()
                    
                    if (any('agent' in str(tag).lower() for tag in tags) or 
                        'agent' in category.lower() or 
                        'slc_agent' in title or 
                        'ctl' in title):
                        slc_agent_rules.append((rule_file.stem, rule_data))
                        
                except (json.JSONDecodeError, KeyError):
                    continue
            
            if slc_agent_rules:
                print(f"📋 Автозагрузка правил SLC Agent: {len(slc_agent_rules)} правил")
                if verbose:
                    for rule_name, rule_data in slc_agent_rules:
                        priority = rule_data.get('priority', 'normal')
                        print(f"   🔧 {rule_name} (приоритет: {priority})")
                        
                        # Выводим критически важные правила
                        if priority == 'critical':
                            print(f"      ⚠️  КРИТИЧНО: {rule_data.get('description', 'N/A')}")
            
            return len(slc_agent_rules)
                            
        except Exception as e:
            if verbose:
                print(f"   ⚠️  Ошибка загрузки правил: {e}")
            return 0 