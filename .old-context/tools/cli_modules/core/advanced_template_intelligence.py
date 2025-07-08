#!/usr/bin/env python3
"""
Advanced Template Intelligence - Продвинутая интеллектуальная система работы с шаблонами СЛК

Расширяет IntelligentRecommendationEngine следующими возможностями:
- Adaptive Template Generation - создание шаблонов на основе паттернов
- Dynamic Template Customization - адаптация существующих шаблонов
- Template Evolution Tracking - отслеживание эволюции шаблонов
- Intelligent Template Composition - композиция шаблонов
- Context-Aware Template Selection - выбор на основе полного контекста проекта

Версия: 1.0.0
Создано: 2025-01-15
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import hashlib
from collections import defaultdict, Counter
import math

try:
    from tools.cli_modules.core.template_manager import TemplateManager
    from tools.cli_modules.commands.ai_commands import IntelligentRecommendationEngine
    from tools.cli_modules.core.unified_context_engine import UnifiedContextEngine
except ImportError:
    # Fallback для случаев когда модули не найдены
    TemplateManager = None
    IntelligentRecommendationEngine = None
    UnifiedContextEngine = None


@dataclass
class TemplateUsagePattern:
    """Паттерн использования шаблона"""
    template_path: str
    usage_count: int
    success_rate: float
    avg_project_size: int
    common_modifications: List[str]
    typical_extensions: List[str]
    user_feedback_score: float
    last_used: datetime
    contexts_used_in: List[str]


@dataclass
class ProjectContext:
    """Контекст проекта для intelligent selection"""
    domain: str
    technologies: List[str]
    project_size: str  # small, medium, large
    complexity: str    # simple, moderate, complex
    team_size: int
    existing_files: List[str]
    git_history: Optional[Dict[str, Any]]
    dependencies: List[str]


@dataclass
class GeneratedTemplate:
    """Сгенерированный шаблон"""
    name: str
    description: str
    content: Dict[str, Any]
    source_templates: List[str]
    generation_method: str
    confidence_score: float
    created_at: datetime
    usage_prediction: float


class TemplateComposer:
    """Композитор шаблонов - объединение и адаптация"""
    
    def __init__(self, template_manager: TemplateManager):
        self.template_manager = template_manager
    
    def compose_templates(self, template_paths: List[str], composition_strategy: str = "merge") -> Dict[str, Any]:
        """
        Композиция нескольких шаблонов в один
        
        Args:
            template_paths: Список путей к шаблонам
            composition_strategy: Стратегия композиции (merge, overlay, pick_best)
        """
        if composition_strategy == "merge":
            return self._merge_templates(template_paths)
        elif composition_strategy == "overlay":
            return self._overlay_templates(template_paths)
        elif composition_strategy == "pick_best":
            return self._pick_best_from_templates(template_paths)
        else:
            raise ValueError(f"Unknown composition strategy: {composition_strategy}")
    
    def _merge_templates(self, template_paths: List[str]) -> Dict[str, Any]:
        """Мерж шаблонов с intelligent conflict resolution"""
        merged = {
            "type": "composed_template",
            "source_templates": template_paths,
            "composition_method": "merge",
            "created_at": datetime.now().isoformat(),
            "template_info": {},
            "project_structure": {},
            "dependencies": {},
            "scripts": {},
            "configuration": {}
        }
        
        for template_path in template_paths:
            template_data = self.template_manager.get_template_info(template_path)
            if not template_data or template_data.get("error"):
                continue
                
            # Загружаем полные данные шаблона
            full_template = self._load_full_template(template_path)
            if not full_template:
                continue
            
            # Интеллектуальное слияние секций
            self._merge_section(merged["template_info"], full_template.get("template_info", {}))
            self._merge_section(merged["project_structure"], full_template.get("project_structure", {}))
            self._merge_section(merged["dependencies"], full_template.get("dependencies", {}))
            self._merge_section(merged["scripts"], full_template.get("scripts", {}))
            self._merge_section(merged["configuration"], full_template.get("configuration", {}))
        
        return merged
    
    def _merge_section(self, target: Dict, source: Dict):
        """Интеллектуальное слияние секций с приоритетами"""
        for key, value in source.items():
            if key not in target:
                target[key] = value
            elif isinstance(value, dict) and isinstance(target[key], dict):
                self._merge_section(target[key], value)
            elif isinstance(value, list) and isinstance(target[key], list):
                # Объединяем списки без дубликатов
                target[key] = list(set(target[key] + value))
            else:
                # Для конфликтов используем приоритет по качеству/актуальности
                if self._is_better_value(value, target[key]):
                    target[key] = value
    
    def _is_better_value(self, new_value: Any, existing_value: Any) -> bool:
        """Определяет какое значение лучше в случае конфликта"""
        # Простая эвристика - больше информации = лучше
        if isinstance(new_value, str) and isinstance(existing_value, str):
            return len(new_value) > len(existing_value)
        return False
    
    def _load_full_template(self, template_path: str) -> Optional[Dict[str, Any]]:
        """Загружает полные данные шаблона"""
        try:
            full_path = self.template_manager.modules_path / template_path
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return None


class PatternAnalyzer:
    """Анализатор паттернов использования шаблонов"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.patterns_db_path = self.base_path / ".slc" / "template_patterns.json"
        self.patterns_db_path.parent.mkdir(exist_ok=True)
        
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict[str, TemplateUsagePattern]:
        """Загружает сохранённые паттерны"""
        if not self.patterns_db_path.exists():
            return {}
        
        try:
            with open(self.patterns_db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                patterns = {}
                for template_path, pattern_data in data.items():
                    # Восстанавливаем datetime объекты
                    pattern_data["last_used"] = datetime.fromisoformat(pattern_data["last_used"])
                    patterns[template_path] = TemplateUsagePattern(**pattern_data)
                return patterns
        except Exception:
            return {}
    
    def _save_patterns(self):
        """Сохраняет паттерны"""
        try:
            data = {}
            for template_path, pattern in self.patterns.items():
                pattern_dict = asdict(pattern)
                pattern_dict["last_used"] = pattern.last_used.isoformat()
                data[template_path] = pattern_dict
            
            with open(self.patterns_db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Ошибка сохранения паттернов: {e}")
    
    def record_template_usage(self, template_path: str, context: ProjectContext, 
                            success: bool = True, modifications: List[str] = None):
        """Записывает использование шаблона"""
        if template_path not in self.patterns:
            self.patterns[template_path] = TemplateUsagePattern(
                template_path=template_path,
                usage_count=0,
                success_rate=1.0,
                avg_project_size=0,
                common_modifications=[],
                typical_extensions=[],
                user_feedback_score=5.0,
                last_used=datetime.now(),
                contexts_used_in=[]
            )
        
        pattern = self.patterns[template_path]
        pattern.usage_count += 1
        pattern.last_used = datetime.now()
        
        # Обновляем success rate
        total_attempts = pattern.usage_count
        current_successes = pattern.success_rate * (total_attempts - 1)
        if success:
            current_successes += 1
        pattern.success_rate = current_successes / total_attempts
        
        # Добавляем контекст
        if context.domain not in pattern.contexts_used_in:
            pattern.contexts_used_in.append(context.domain)
        
        # Записываем модификации
        if modifications:
            for mod in modifications:
                if mod not in pattern.common_modifications:
                    pattern.common_modifications.append(mod)
        
        self._save_patterns()
    
    def get_usage_patterns(self, min_usage: int = 2) -> List[TemplateUsagePattern]:
        """Возвращает паттерны с минимальным использованием"""
        return [p for p in self.patterns.values() if p.usage_count >= min_usage]
    
    def predict_template_success(self, template_path: str, context: ProjectContext) -> float:
        """Предсказывает успешность использования шаблона в данном контексте"""
        if template_path not in self.patterns:
            return 0.5  # Нейтральная оценка для новых шаблонов
        
        pattern = self.patterns[template_path]
        
        # Базовая оценка на основе исторических данных
        base_score = pattern.success_rate * 0.6
        
        # Бонус за опыт использования
        experience_bonus = min(pattern.usage_count / 10, 0.2)
        
        # Контекстуальное соответствие
        context_match = 0.0
        if context.domain in pattern.contexts_used_in:
            context_match = 0.15
        
        # Актуальность использования
        days_since_use = (datetime.now() - pattern.last_used).days
        recency_factor = max(0, (30 - days_since_use) / 30) * 0.05
        
        return base_score + experience_bonus + context_match + recency_factor


class AdvancedTemplateIntelligence:
    """Основной класс Advanced Template Intelligence"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.slc_dir = self.base_path / ".slc"
        self.slc_dir.mkdir(exist_ok=True)
        
        # Инициализация компонентов
        self.template_manager = TemplateManager(base_path) if TemplateManager else None
        self.recommendation_engine = IntelligentRecommendationEngine(base_path) if IntelligentRecommendationEngine else None
        self.template_composer = TemplateComposer(self.template_manager) if self.template_manager else None
        self.pattern_analyzer = PatternAnalyzer(base_path)
        
        # Кэш для производительности
        self.template_cache = {}
        self.context_cache = {}
        
        # Система логирования
        self.intelligence_log = self.slc_dir / "template_intelligence.json"
        self._init_logging()
    
    def _init_logging(self):
        """Инициализация системы логирования"""
        if not self.intelligence_log.exists():
            initial_log = {
                "system": "Advanced Template Intelligence",
                "version": "1.0.0",
                "created": datetime.now().isoformat(),
                "sessions": [],
                "statistics": {
                    "templates_generated": 0,
                    "successful_recommendations": 0,
                    "user_satisfaction": 0.0
                }
            }
            with open(self.intelligence_log, 'w', encoding='utf-8') as f:
                json.dump(initial_log, f, indent=2, ensure_ascii=False)
    
    def get_intelligent_recommendations(self, query: str, project_context: ProjectContext = None,
                                     max_results: int = 5) -> List[Dict[str, Any]]:
        """Получает интеллектуальные рекомендации с учётом контекста и паттернов"""
        # Базовые рекомендации от существующего движка
        base_recommendations = []
        if self.recommendation_engine:
            base_recommendations = self.recommendation_engine.get_recommendations(
                query, max_results * 2  # Берём больше для фильтрации
            )
        
        # Применяем advanced intelligence
        enhanced_recommendations = []
        
        for rec in base_recommendations:
            template_path = rec["template"]
            base_score = rec["score"]
            
            # Прогнозируем успешность на основе паттернов
            success_prediction = 0.5
            if project_context:
                success_prediction = self.pattern_analyzer.predict_template_success(
                    template_path, project_context
                )
            
            # Комбинированная оценка
            combined_score = (base_score * 0.7) + (success_prediction * 0.3)
            
            enhanced_recommendations.append({
                "template": template_path,
                "score": combined_score,
                "base_score": base_score,
                "success_prediction": success_prediction,
                "intelligence_features": {
                    "pattern_based_scoring": True,
                    "context_aware": project_context is not None,
                    "usage_history": template_path in self.pattern_analyzer.patterns
                }
            })
        
        # Сортируем по комбинированной оценке
        enhanced_recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        return enhanced_recommendations[:max_results]
    
    def generate_adaptive_template(self, query: str, project_context: ProjectContext,
                                 base_templates: List[str] = None) -> GeneratedTemplate:
        """Генерирует адаптивный шаблон на основе контекста и паттернов"""
        if not base_templates:
            # Автоматически находим подходящие базовые шаблоны
            recommendations = self.get_intelligent_recommendations(query, project_context, 3)
            base_templates = [r["template"] for r in recommendations]
        
        if not base_templates:
            raise ValueError("Не найдено подходящих базовых шаблонов")
        
        # Композиция базовых шаблонов
        if self.template_composer:
            composed_template = self.template_composer.compose_templates(
                base_templates, "merge"
            )
        else:
            composed_template = {"error": "Template composer not available"}
        
        # Адаптация под контекст проекта
        adapted_template = self._adapt_template_to_context(composed_template, project_context)
        
        # Создаём GeneratedTemplate
        generated = GeneratedTemplate(
            name=f"Adaptive_{project_context.domain}_{datetime.now().strftime('%Y%m%d_%H%M')}",
            description=f"Адаптивный шаблон для {project_context.domain} проекта",
            content=adapted_template,
            source_templates=base_templates,
            generation_method="adaptive_composition",
            confidence_score=self._calculate_generation_confidence(base_templates, project_context),
            created_at=datetime.now(),
            usage_prediction=0.8  # Оптимистичная оценка для адаптивных шаблонов
        )
        
        # Логируем генерацию
        self._log_template_generation(generated)
        
        return generated
    
    def _adapt_template_to_context(self, template: Dict[str, Any], context: ProjectContext) -> Dict[str, Any]:
        """Адаптирует шаблон под конкретный контекст проекта"""
        adapted = template.copy()
        
        # Адаптация на основе размера проекта
        if context.project_size == "small":
            adapted = self._simplify_template(adapted)
        elif context.project_size == "large":
            adapted = self._enhance_template_for_scale(adapted)
        
        # Адаптация на основе технологий
        if context.technologies:
            adapted = self._customize_for_technologies(adapted, context.technologies)
        
        # Адаптация на основе команды
        if context.team_size > 5:
            adapted = self._add_collaboration_features(adapted)
        
        return adapted
    
    def _simplify_template(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """Упрощает шаблон для небольших проектов"""
        # Убираем сложные конфигурации
        simplified = template.copy()
        
        # Упрощаем структуру проекта
        if "project_structure" in simplified:
            structure = simplified["project_structure"]
            # Оставляем только основные директории
            essential_dirs = ["src", "docs", "tests"]
            if isinstance(structure, dict):
                for key in list(structure.keys()):
                    if key not in essential_dirs and not key.startswith("essential"):
                        structure.pop(key, None)
        
        return simplified
    
    def _enhance_template_for_scale(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """Расширяет шаблон для больших проектов"""
        enhanced = template.copy()
        
        # Добавляем дополнительные директории для масштабирования
        if "project_structure" not in enhanced:
            enhanced["project_structure"] = {}
        
        scale_additions = {
            "infrastructure": "Infrastructure и deployment конфигурации",
            "monitoring": "Система мониторинга и логирования", 
            "ci_cd": "Continuous Integration и Deployment",
            "documentation": {
                "architecture": "Архитектурная документация",
                "deployment": "Инструкции по развёртыванию",
                "scaling": "Руководство по масштабированию"
            }
        }
        
        enhanced["project_structure"].update(scale_additions)
        
        return enhanced
    
    def _customize_for_technologies(self, template: Dict[str, Any], technologies: List[str]) -> Dict[str, Any]:
        """Кастомизирует шаблон под выбранные технологии"""
        customized = template.copy()
        
        # Добавляем конфигурации под конкретные технологии
        if "dependencies" not in customized:
            customized["dependencies"] = {}
        
        for tech in technologies:
            if tech.lower() == "docker":
                customized["project_structure"]["Dockerfile"] = "Docker containerization"
                customized["project_structure"]["docker-compose.yml"] = "Docker Compose configuration"
            
            elif tech.lower() == "kubernetes":
                customized["project_structure"]["k8s"] = "Kubernetes deployment manifests"
            
            elif tech.lower() in ["react", "vue", "angular"]:
                customized["project_structure"]["public"] = "Static assets"
                customized["project_structure"]["src/components"] = "UI components"
        
        return customized
    
    def _add_collaboration_features(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """Добавляет возможности для командной работы"""
        collaborative = template.copy()
        
        if "project_structure" not in collaborative:
            collaborative["project_structure"] = {}
        
        collaboration_additions = {
            ".github": {
                "workflows": "GitHub Actions workflows",
                "ISSUE_TEMPLATE": "Issue templates",
                "PULL_REQUEST_TEMPLATE.md": "PR template"
            },
            "docs/team": {
                "CONTRIBUTING.md": "Contribution guidelines",
                "CODE_OF_CONDUCT.md": "Code of conduct", 
                "DEVELOPMENT.md": "Development setup guide"
            }
        }
        
        collaborative["project_structure"].update(collaboration_additions)
        
        return collaborative
    
    def _calculate_generation_confidence(self, base_templates: List[str], context: ProjectContext) -> float:
        """Рассчитывает уверенность в сгенерированном шаблоне"""
        # Базовая уверенность на основе количества базовых шаблонов
        base_confidence = min(len(base_templates) / 3, 0.8)
        
        # Бонус за известные паттерны
        pattern_bonus = 0.0
        for template_path in base_templates:
            if template_path in self.pattern_analyzer.patterns:
                pattern = self.pattern_analyzer.patterns[template_path]
                pattern_bonus += pattern.success_rate * 0.1
        
        # Контекстная уверенность
        context_confidence = 0.1 if context.domain else 0.0
        
        return min(base_confidence + pattern_bonus + context_confidence, 1.0)
    
    def _log_template_generation(self, generated: GeneratedTemplate):
        """Логирует генерацию шаблона"""
        try:
            with open(self.intelligence_log, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            session_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": "template_generation",
                "template_name": generated.name,
                "generation_method": generated.generation_method,
                "confidence_score": generated.confidence_score,
                "source_templates": generated.source_templates
            }
            
            log_data["sessions"].append(session_entry)
            log_data["statistics"]["templates_generated"] += 1
            
            with open(self.intelligence_log, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"⚠️ Ошибка логирования: {e}")
    
    def analyze_template_evolution(self, template_path: str) -> Dict[str, Any]:
        """Анализирует эволюцию использования шаблона"""
        if template_path not in self.pattern_analyzer.patterns:
            return {"error": "Недостаточно данных для анализа"}
        
        pattern = self.pattern_analyzer.patterns[template_path]
        
        return {
            "template": template_path,
            "usage_trend": "increasing" if pattern.usage_count > 5 else "stable",
            "success_rate": pattern.success_rate,
            "adaptability_score": len(pattern.common_modifications) / max(pattern.usage_count, 1),
            "context_diversity": len(pattern.contexts_used_in),
            "recommendations": self._generate_evolution_recommendations(pattern)
        }
    
    def _generate_evolution_recommendations(self, pattern: TemplateUsagePattern) -> List[str]:
        """Генерирует рекомендации по улучшению шаблона"""
        recommendations = []
        
        if pattern.success_rate < 0.7:
            recommendations.append("Рассмотрите упрощение шаблона для повышения успешности")
        
        if len(pattern.common_modifications) > 3:
            recommendations.append("Рассмотрите создание вариантов шаблона с часто используемыми модификациями")
        
        if len(pattern.contexts_used_in) < 2:
            recommendations.append("Попробуйте адаптировать шаблон для других доменов")
        
        days_since_use = (datetime.now() - pattern.last_used).days
        if days_since_use > 30:
            recommendations.append("Шаблон давно не использовался - возможно нужно обновление")
        
        return recommendations
    
    def get_system_intelligence_stats(self) -> Dict[str, Any]:
        """Возвращает статистику работы системы интеллекта"""
        try:
            with open(self.intelligence_log, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            patterns_stats = {
                "total_patterns": len(self.pattern_analyzer.patterns),
                "active_patterns": len([p for p in self.pattern_analyzer.patterns.values() 
                                     if (datetime.now() - p.last_used).days < 30]),
                "avg_success_rate": sum(p.success_rate for p in self.pattern_analyzer.patterns.values()) / 
                                  max(len(self.pattern_analyzer.patterns), 1)
            }
            
            return {
                "system_stats": log_data["statistics"],
                "patterns_stats": patterns_stats,
                "recent_activity": log_data["sessions"][-10:] if log_data["sessions"] else []
            }
            
        except Exception as e:
            return {"error": f"Ошибка получения статистики: {e}"}


# Утилиты для тестирования и демонстрации
def demo_advanced_intelligence():
    """Демонстрационная функция возможностей"""
    print("🧠 Демонстрация Advanced Template Intelligence")
    
    # Создаём пример контекста проекта
    demo_context = ProjectContext(
        domain="ai_ml",
        technologies=["python", "tensorflow", "docker"],
        project_size="medium",
        complexity="moderate",
        team_size=3,
        existing_files=[],
        git_history=None,
        dependencies=["tensorflow", "pandas", "numpy"]
    )
    
    # Инициализируем систему
    ati = AdvancedTemplateIntelligence()
    
    # Получаем рекомендации
    print("\n📋 Intelligent Recommendations:")
    recommendations = ati.get_intelligent_recommendations(
        "создать ML проект для обработки данных", 
        demo_context
    )
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['template']} (score: {rec['score']:.3f})")
    
    print(f"\n📊 System Statistics:")
    stats = ati.get_system_intelligence_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    demo_advanced_intelligence()