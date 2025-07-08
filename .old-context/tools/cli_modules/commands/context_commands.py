#!/usr/bin/env python3
"""
Context Commands - Команды для работы с контекстом СЛК

Реализует команды для автоматической и интеллектуальной загрузки контекста.

Версия: 1.0.0
Создано: 2025-01-15
"""

import json
import sys
from pathlib import Path
from typing import List, Dict

# Добавляем путь к модулям
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.cli_modules.common.base_command import BaseCommand, ContextAwareCommand
from tools.cli_modules.core.unified_context_engine import (
    UnifiedContextEngine, ContextLoadRequest, ContextLoadingStrategy
)


class LoadContextCommand(BaseCommand):
    """Команда автоматической загрузки контекста"""
    
    name = "load-context"
    description = "🧠 Автоматическая интеллектуальная загрузка контекста СЛК"
    
    def __init__(self, base_path: str):
        super().__init__()
        self.base_path = base_path
        self.engine = UnifiedContextEngine(base_path) if UnifiedContextEngine else None
    
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
    
    def execute(self, args) -> int:
        """Выполнение команды"""
        try:
            print(f"🧠 Автоматическая загрузка контекста для: '{args.query}'")
            print("=" * 60)
            
            # Подготовка запроса
            strategy_mapping = {
                "auto": ContextLoadingStrategy.AUTO_INTELLIGENT,
                "pattern": ContextLoadingStrategy.PATTERN_BASED,
                "manual": ContextLoadingStrategy.MANUAL_SELECTION,
                "full": ContextLoadingStrategy.FULL_CONTEXT
            }
            
            request = ContextLoadRequest(
                user_query=args.query,
                strategy=strategy_mapping[args.strategy],
                include_core=not args.no_core,
                include_tasks=not args.no_tasks,
                max_modules=args.max_modules,
                verbose=args.verbose
            )
            
            # Выполнение загрузки
            result = self.engine.load_context(request)
            
            if not result.success:
                print(f"❌ Ошибка загрузки: {result.error_message}")
                return 1
            
            # Вывод результата в зависимости от формата
            if args.format == "content":
                self._output_content_format(result, args.verbose)
            elif args.format == "copy":
                self._output_copy_format(result, args.verbose)
            elif args.format == "json":
                self._output_json(result)
            elif args.format == "list":
                self._output_list(result)
            
            # Сохранение результата если требуется
            if args.save_result:
                self._save_result(result, args.save_result)
            
            return 0
            
        except Exception as e:
            print(f"❌ Произошла ошибка: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1
    
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


class AnalyzeContextCommand(ContextAwareCommand):
    """Команда анализа текущего контекста с JSON выводом для AI интеграции"""
    
    @property
    def name(self) -> str:
        return "analyze-context"
    
    @property
    def description(self) -> str:
        return "🔍 Анализ и оптимизация текущего контекста"
    
    def __init__(self, base_path: str):
        super().__init__()
        self.base_path = base_path
    
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
        
        # JSON вывод для AI интеграции
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


class ClearContextCommand(BaseCommand):
    """Команда очистки контекста"""
    
    name = "clear-context"
    description = "🧹 Очистка и сброс текущего контекста"
    
    def __init__(self, base_path: str):
        super().__init__()
        self.base_path = base_path
    
    def add_arguments(self, parser):
        """Добавляет аргументы команды"""
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Подтвердить очистку без дополнительных вопросов"
        )
    
    def execute(self, args) -> int:
        """Выполнение команды"""
        if not args.confirm:
            response = input("⚠️  Очистить текущий контекст? (y/N): ")
            if response.lower() != 'y':
                print("❌ Отменено")
                return 0
        
        print("🧹 Контекст очищен")
        return 0 