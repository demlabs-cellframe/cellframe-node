#!/usr/bin/env python3
"""
Команды Template Intelligence

Реализует команды:
- intelligent-recommend: Умные рекомендации шаблонов
- generate-adaptive: Генерация адаптивного шаблона
- record-usage: Запись использования шаблона
- intelligence-stats: Статистика работы системы
- template-evolution: Анализ эволюции шаблона

Версия: 1.1.0
Создано: 2025-01-15
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..base_command import BaseCommand, ContextAwareCommand

try:
    from tools.cli_modules.core.advanced_template_intelligence import (
        AdvancedTemplateIntelligence, ProjectContext, TemplateUsagePattern
    )
except ImportError:
    AdvancedTemplateIntelligence = None
    ProjectContext = None


class IntelligentRecommendCommand(BaseCommand):
    """Команда получения интеллектуальных рекомендаций"""
    
    @property
    def name(self) -> str:
        return "intelligent-recommend"
    
    @property
    def description(self) -> str:
        return "🧠 Получить умные рекомендации шаблонов на основе контекста и паттернов"
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("query", help="Запрос для поиска шаблонов")
        parser.add_argument("--domain", help="Домен проекта (ai_ml, python, web)")
        parser.add_argument("--technologies", nargs="+", help="Список технологий")
        parser.add_argument("--project-size", choices=["small", "medium", "large"], 
                           default="medium", help="Размер проекта")
        parser.add_argument("--complexity", choices=["simple", "moderate", "complex"],
                           default="moderate", help="Сложность проекта")
        parser.add_argument("--team-size", type=int, default=1, help="Размер команды")
        parser.add_argument("--max-results", type=int, default=5, help="Максимум результатов")
        parser.add_argument("--verbose", action="store_true", help="Подробный вывод")
    
    def execute(self, args) -> int:
        if not AdvancedTemplateIntelligence:
            print("❌ Advanced Template Intelligence не доступна")
            return 1
        
        try:
            # Создаём контекст проекта
            project_context = None
            if args.domain:
                project_context = ProjectContext(
                    domain=args.domain,
                    technologies=args.technologies or [],
                    project_size=args.project_size,
                    complexity=args.complexity,
                    team_size=args.team_size,
                    existing_files=[],
                    git_history=None,
                    dependencies=[]
                )
            
            # Инициализируем систему
            ati = AdvancedTemplateIntelligence()
            
            print(f"🧠 Интеллектуальные рекомендации для: '{args.query}'")
            if project_context:
                print(f"📊 Контекст: {project_context.domain}, {project_context.project_size}, команда {project_context.team_size}")
            print()
            
            # Получаем рекомендации  
            recommendations = ati.get_intelligent_recommendations(
                args.query, project_context, args.max_results
            )
            
            if not recommendations:
                print("❌ Рекомендации не найдены")
                return 0
            
            for i, rec in enumerate(recommendations, 1):
                template_path = rec["template"]
                score = rec["score"]
                base_score = rec.get("base_score", 0)
                success_prediction = rec.get("success_prediction", 0)
                features = rec.get("intelligence_features", {})
                
                print(f"{i}. 🎯 {template_path}")
                print(f"   📊 Общая оценка: {score:.3f}")
                
                if args.verbose:
                    print(f"   📈 Базовая оценка: {base_score:.3f}")
                    print(f"   🔮 Прогноз успеха: {success_prediction:.3f}")
                    print(f"   🧠 Интеллектуальные фичи:")
                    for feature, enabled in features.items():
                        status = "✅" if enabled else "❌"
                        print(f"      {status} {feature}")
                
                print()
            
            print("💡 Следующие шаги:")
            print(f"   slc_cli.py generate-adaptive '{args.query}' --domain {args.domain or 'auto'}")
            print(f"   slc_cli.py create TEMPLATE_PATH PROJECT_NAME")
            
            return 0
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return 1


class GenerateAdaptiveCommand(BaseCommand):
    """Команда генерации адаптивного шаблона"""
    
    @property
    def name(self) -> str:
        return "generate-adaptive"
    
    @property
    def description(self) -> str:
        return "🔧 Генерация адаптивного шаблона на основе контекста и паттернов"
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("query", help="Описание желаемого шаблона")
        parser.add_argument("--domain", required=True, help="Домен проекта")
        parser.add_argument("--technologies", nargs="+", help="Список технологий")
        parser.add_argument("--project-size", choices=["small", "medium", "large"],
                           default="medium", help="Размер проекта")
        parser.add_argument("--complexity", choices=["simple", "moderate", "complex"],
                           default="moderate", help="Сложность проекта")
        parser.add_argument("--team-size", type=int, default=1, help="Размер команды")
        parser.add_argument("--base-templates", nargs="+", help="Базовые шаблоны для композиции")
        parser.add_argument("--save-to", help="Сохранить сгенерированный шаблон в файл")
        parser.add_argument("--dry-run", action="store_true", help="Только показать результат")
    
    def execute(self, args) -> int:
        if not AdvancedTemplateIntelligence:
            print("❌ Advanced Template Intelligence не доступна")
            return 1
        
        try:
            # Создаём контекст проекта
            project_context = ProjectContext(
                domain=args.domain,
                technologies=args.technologies or [],
                project_size=args.project_size,
                complexity=args.complexity,
                team_size=args.team_size,
                existing_files=[],
                git_history=None,
                dependencies=[]
            )
            
            # Инициализируем систему
            ati = AdvancedTemplateIntelligence()
            
            print(f"🔧 Генерация адаптивного шаблона")
            print(f"   Запрос: {args.query}")
            print(f"   Домен: {args.domain}")
            print(f"   Технологии: {args.technologies}")
            print(f"   Размер: {args.project_size}")
            print(f"   Сложность: {args.complexity}")
            print(f"   Команда: {args.team_size}")
            print()
            
            # Генерируем адаптивный шаблон
            generated_template = ati.generate_adaptive_template(
                args.query, project_context, args.base_templates
            )
            
            print(f"✅ Шаблон сгенерирован: {generated_template.name}")
            print(f"📊 Уверенность: {generated_template.confidence_score:.3f}")
            print(f"🔮 Прогноз использования: {generated_template.usage_prediction:.3f}")
            print(f"📝 Описание: {generated_template.description}")
            print(f"🧩 Источники: {', '.join(generated_template.source_templates)}")
            print()
            
            if args.dry_run:
                print("🔍 Сгенерированный контент (dry-run):")
                print(json.dumps(generated_template.content, indent=2, ensure_ascii=False))
                return 0
            
            # Сохраняем шаблон
            if args.save_to:
                save_path = Path(args.save_to)
                save_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(generated_template.content, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Шаблон сохранён: {save_path}")
            
            return 0
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return 1


class TemplateEvolutionCommand(BaseCommand):
    """Команда анализа эволюции шаблона"""
    
    @property
    def name(self) -> str:
        return "template-evolution"
    
    @property
    def description(self) -> str:
        return "📈 Анализ эволюции и использования шаблона"
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("template_path", help="Путь к шаблону для анализа")
        parser.add_argument("--detailed", action="store_true", help="Подробный анализ")
    
    def execute(self, args) -> int:
        if not AdvancedTemplateIntelligence:
            print("❌ Advanced Template Intelligence не доступна")
            return 1
        
        try:
            ati = AdvancedTemplateIntelligence()
            
            print(f"📈 Анализ эволюции шаблона: {args.template_path}")
            print()
            
            # Анализируем эволюцию
            evolution = ati.analyze_template_evolution(args.template_path)
            
            if "error" in evolution:
                print(f"❌ {evolution['error']}")
                return 1
            
            print(f"📊 Статистика использования:")
            print(f"   Тренд: {evolution['usage_trend']}")
            print(f"   Успешность: {evolution['success_rate']:.2%}")
            print(f"   Адаптивность: {evolution['adaptability_score']:.3f}")
            print(f"   Разнообразие контекстов: {evolution['context_diversity']}")
            print()
            
            if evolution['recommendations']:
                print(f"💡 Рекомендации по улучшению:")
                for i, rec in enumerate(evolution['recommendations'], 1):
                    print(f"   {i}. {rec}")
                print()
            
            if args.detailed:
                # Получаем подробную информацию о паттернах
                pattern = ati.pattern_analyzer.patterns.get(args.template_path)
                if pattern:
                    print(f"🔍 Детальная информация:")
                    print(f"   Использований: {pattern.usage_count}")  
                    print(f"   Последнее использование: {pattern.last_used.strftime('%Y-%m-%d %H:%M')}")
                    print(f"   Рейтинг пользователей: {pattern.user_feedback_score:.1f}/5.0")
                    print(f"   Контексты: {', '.join(pattern.contexts_used_in)}")
                    
                    if pattern.common_modifications:
                        print(f"   Частые модификации:")
                        for mod in pattern.common_modifications:
                            print(f"      • {mod}")
            
            return 0
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return 1


class IntelligenceStatsCommand(ContextAwareCommand):
    """Команда статистики работы Template Intelligence"""
    
    def __init__(self, base_path: str):
        super().__init__(base_path)
        
    @property
    def name(self) -> str:
        return "intelligence-stats"
    
    @property
    def description(self) -> str:
        return "📊 Статистика работы системы Template Intelligence"
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        super().add_arguments(parser)  # Добавляет JSON контекст
        parser.add_argument("--detailed", action="store_true", help="Подробная статистика")
        parser.add_argument("--recent", type=int, default=10, help="Количество последних активностей")
    
    def get_default_context_files(self) -> List[str]:
        """Файлы контекста для intelligence-stats"""
        return [
            ".slc_usage_stats.json",
            "modules/ai_ml/machine_learning.json",
            "tools/template_intelligence/"
        ]
    
    def get_context_summary(self, execution_result: Dict[str, Any]) -> str:
        """Описание результатов статистики"""
        system_stats = execution_result.get("system_stats", {})
        patterns_stats = execution_result.get("patterns_stats", {})
        
        return f"""
        Статистика Template Intelligence системы:
        - Шаблонов сгенерировано: {system_stats.get('templates_generated', 0)}
        - Успешных рекомендаций: {system_stats.get('successful_recommendations', 0)}
        - Активных паттернов: {patterns_stats.get('active_patterns', 0)}
        - Средняя успешность: {patterns_stats.get('avg_success_rate', 0):.1%}
        """
    
    def get_recommended_actions(self, execution_result: Dict[str, Any]) -> List[str]:
        """Рекомендуемые действия на основе статистики"""
        actions = []
        
        system_stats = execution_result.get("system_stats", {})
        patterns_stats = execution_result.get("patterns_stats", {})
        
        if system_stats.get('successful_recommendations', 0) == 0:
            actions.append("Записать использование шаблонов для обучения системы")
        
        if patterns_stats.get('active_patterns', 0) < 5:
            actions.append("Использовать больше различных шаблонов для расширения базы знаний")
        
        success_rate = patterns_stats.get('avg_success_rate', 0)
        if success_rate < 0.8:
            actions.append("Проанализировать неуспешные использования и улучшить рекомендации")
        
        actions.extend([
            "Проанализировать наиболее успешные паттерны",
            "Оптимизировать слабые места в рекомендациях",
            "Создать адаптивные шаблоны на основе данных"
        ])
        
        return actions
    
    def get_next_commands(self, execution_result: Dict[str, Any]) -> List[str]:
        """Предлагаемые следующие команды"""
        return [
            "слк record-usage [шаблон] --domain [домен]",
            "слк generate-adaptive [описание] --domain [домен]",
            "слк template-evolution [шаблон]",
            "слк рефлексия"
        ]
    
    def execute_with_context(self, args: argparse.Namespace) -> Dict[str, Any]:
        """Выполнить команду и вернуть результат для контекста"""
        if not AdvancedTemplateIntelligence:
            print("❌ Advanced Template Intelligence не доступна")
            return {"error": "AdvancedTemplateIntelligence не доступна"}
        
        try:
            ati = AdvancedTemplateIntelligence()
            
            print("📊 Статистика Template Intelligence System")
            print()
            
            # Получаем статистику
            stats = ati.get_system_intelligence_stats()
            
            if "error" in stats:
                print(f"❌ {stats['error']}")
                return stats
            
            # Общая статистика
            system_stats = stats.get("system_stats", {})
            print(f"🏗️ Системная статистика:")
            print(f"   Шаблонов сгенерировано: {system_stats.get('templates_generated', 0)}")
            print(f"   Успешных рекомендаций: {system_stats.get('successful_recommendations', 0)}")
            print(f"   Удовлетворённость пользователей: {system_stats.get('user_satisfaction', 0):.1%}")
            print()
            
            # Статистика паттернов
            patterns_stats = stats.get("patterns_stats", {})
            print(f"🔍 Статистика паттернов:")
            print(f"   Всего паттернов: {patterns_stats.get('total_patterns', 0)}")
            print(f"   Активных паттернов: {patterns_stats.get('active_patterns', 0)}")
            print(f"   Средняя успешность: {patterns_stats.get('avg_success_rate', 0):.2%}")
            print()
            
            # Последняя активность
            recent_activity = stats.get("recent_activity", [])
            if recent_activity:
                print(f"📈 Последняя активность (последние {min(args.recent, len(recent_activity))}):")
                for activity in recent_activity[-args.recent:]:
                    timestamp = activity.get("timestamp", "")[:19].replace("T", " ")
                    action = activity.get("action", "unknown")
                    print(f"   {timestamp} - {action}")
                    
                    if args.detailed:
                        for key, value in activity.items():
                            if key not in ["timestamp", "action"]:
                                print(f"      {key}: {value}")
                print()
            
            # Топ шаблоны по использованию
            if args.detailed:
                patterns = ati.pattern_analyzer.get_usage_patterns(min_usage=1)
                if patterns:
                    print(f"🏆 Топ шаблоны по использованию:")
                    sorted_patterns = sorted(patterns, key=lambda p: p.usage_count, reverse=True)
                    for i, pattern in enumerate(sorted_patterns[:5], 1):
                        print(f"   {i}. {pattern.template_path}")
                        print(f"      Использований: {pattern.usage_count}, Успешность: {pattern.success_rate:.2%}")
                    
                    # Добавляем топ шаблоны в результат
                    stats["top_templates"] = [
                        {
                            "template_path": p.template_path,
                            "usage_count": p.usage_count,
                            "success_rate": p.success_rate
                        }
                        for p in sorted_patterns[:5]
                    ]
            
            return stats
            
        except Exception as e:
            error_message = f"Ошибка: {e}"
            print(f"❌ {error_message}")
            return {"error": error_message}


class RecordUsageCommand(BaseCommand):
    """Команда записи использования шаблона"""
    
    @property
    def name(self) -> str:
        return "record-usage"
    
    @property
    def description(self) -> str:
        return "📝 Записать использование шаблона для обучения системы"
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("template_path", help="Путь к использованному шаблону")
        parser.add_argument("--domain", required=True, help="Домен проекта")
        parser.add_argument("--success", type=bool, default=True, help="Успешное ли использование")
        parser.add_argument("--modifications", nargs="+", help="Внесённые модификации")
        parser.add_argument("--feedback-score", type=float, default=5.0, 
                           help="Оценка пользователя (1-5)")
        parser.add_argument("--technologies", nargs="+", help="Использованные технологии")
        parser.add_argument("--project-size", choices=["small", "medium", "large"],
                           default="medium", help="Размер проекта")
    
    def execute(self, args) -> int:
        if not AdvancedTemplateIntelligence:
            print("❌ Advanced Template Intelligence не доступна")
            return 1
        
        try:
            # Создаём контекст проекта
            project_context = ProjectContext(
                domain=args.domain,
                technologies=args.technologies or [],
                project_size=args.project_size,
                complexity="moderate",  # default
                team_size=1,  # default
                existing_files=[],
                git_history=None,
                dependencies=[]
            )
            
            ati = AdvancedTemplateIntelligence()
            
            print(f"📝 Запись использования шаблона: {args.template_path}")
            print(f"   Домен: {args.domain}")
            print(f"   Успех: {'✅' if args.success else '❌'}")
            print(f"   Оценка: {args.feedback_score}/5.0")
            
            # Записываем использование
            ati.pattern_analyzer.record_template_usage(
                args.template_path,
                project_context,
                args.success,
                args.modifications
            )
            
            print("✅ Использование записано успешно")
            print("🧠 Система обучается на основе вашего опыта")
            
            return 0
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return 1


# Функция для создания команд с base_path
def get_template_intelligence_commands(base_path: str = "."):
    """Создает список команд Template Intelligence с base_path"""
    return [
        IntelligentRecommendCommand(),
        GenerateAdaptiveCommand(),
        TemplateEvolutionCommand(),
        IntelligenceStatsCommand(base_path),  # Создаем с base_path
        RecordUsageCommand()
    ]

# Список всех команд для регистрации (для обратной совместимости)
TEMPLATE_INTELLIGENCE_COMMANDS = get_template_intelligence_commands() 