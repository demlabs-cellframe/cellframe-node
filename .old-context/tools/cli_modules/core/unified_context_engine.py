#!/usr/bin/env python3
"""
Unified Context Engine - Единая система автоматической загрузки контекста СЛК

Объединяет все системы загрузки в один мощный движок:
- AI-powered анализ user intent
- Intelligent preloading на основе patterns
- Integration с recommend engine
- Fallback на manual selection

Версия: 1.0.0
Создано: 2025-01-15
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

# Импортируем существующие компоненты
try:
    from tools.cli_modules.core.template_manager import TemplateManager
    from tools.cli_modules.commands.ai_commands import IntelligentRecommendationEngine
except ImportError:
    # Fallback для случаев когда модули не найдены
    TemplateManager = None
    IntelligentRecommendationEngine = None


class ContextLoadingStrategy(Enum):
    """Стратегии загрузки контекста"""
    AUTO_INTELLIGENT = "auto_intelligent"  # AI-powered автоматическая
    PATTERN_BASED = "pattern_based"        # На основе паттернов
    MANUAL_SELECTION = "manual_selection"  # Ручной выбор
    FULL_CONTEXT = "full_context"          # Загрузить всё


@dataclass
class ContextLoadRequest:
    """Запрос на загрузку контекста"""
    user_query: str
    strategy: ContextLoadingStrategy = ContextLoadingStrategy.AUTO_INTELLIGENT
    include_core: bool = True
    include_tasks: bool = True
    max_modules: int = 10
    verbose: bool = False


@dataclass 
class ContextLoadResult:
    """Результат загрузки контекста"""
    loaded_files: List[str]
    confidence_score: float
    strategy_used: ContextLoadingStrategy
    ai_recommendations: List[Dict]
    fallback_suggestions: List[str]
    execution_time: float
    success: bool
    error_message: Optional[str] = None


class UnifiedContextEngine:
    """Единый движок автоматической загрузки контекста"""
    
    def __init__(self, base_path: str = "."):
        """
        Инициализация движка
        
        Args:
            base_path: Путь к корню проекта СЛК
        """
        self.base_path = Path(base_path)
        self.template_manager = TemplateManager(base_path) if TemplateManager else None
        self.ai_engine = IntelligentRecommendationEngine(base_path) if IntelligentRecommendationEngine else None
        
        # Загружаем конфигурацию системы
        self.core_files = self._load_core_files_config()
        self.intent_patterns = self._load_intent_patterns()
        self.domain_keywords = self._load_domain_keywords()
        
        # Статистика использования
        self.usage_stats = self._load_usage_stats()
        
    def load_context(self, request: ContextLoadRequest) -> ContextLoadResult:
        """
        Основной метод загрузки контекста
        
        Args:
            request: Запрос на загрузку контекста
            
        Returns:
            Результат загрузки с файлами и метаданными
        """
        import time
        start_time = time.time()
        
        try:
            if request.verbose:
                print(f"🧠 Анализирую запрос: '{request.user_query}'")
                print(f"📋 Стратегия: {request.strategy.value}")
            
            # Анализ пользовательского намерения
            intent_analysis = self._analyze_user_intent(request.user_query)
            
            # Выбор стратегии загрузки
            strategy = self._select_loading_strategy(request, intent_analysis)
            
            # Загрузка контекста согласно стратегии
            loaded_files = self._execute_loading_strategy(strategy, request, intent_analysis)
            
            # AI рекомендации (если доступны)
            ai_recommendations = self._get_ai_recommendations(request.user_query) if self.ai_engine else []
            
            # Расчёт confidence score
            confidence = self._calculate_confidence_score(intent_analysis, loaded_files, ai_recommendations)
            
            # Fallback предложения
            fallback_suggestions = self._generate_fallback_suggestions(intent_analysis, loaded_files)
            
            execution_time = time.time() - start_time
            
            # Обновляем статистику
            self._update_usage_stats(request, loaded_files, confidence)
            
            result = ContextLoadResult(
                loaded_files=loaded_files,
                confidence_score=confidence,
                strategy_used=strategy,
                ai_recommendations=ai_recommendations,
                fallback_suggestions=fallback_suggestions,
                execution_time=execution_time,
                success=True
            )
            
            if request.verbose:
                self._print_verbose_result(result)
                
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            return ContextLoadResult(
                loaded_files=[],
                confidence_score=0.0,
                strategy_used=strategy if 'strategy' in locals() else request.strategy,
                ai_recommendations=[],
                fallback_suggestions=[],
                execution_time=execution_time,
                success=False,
                error_message=str(e)
            )
    
    def _analyze_user_intent(self, query: str) -> Dict[str, Any]:
        """Анализ намерения пользователя"""
        query_lower = query.lower()
        
        # Определение типа намерения
        intent_type = "unknown"
        for pattern_name, patterns in self.intent_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                intent_type = pattern_name
                break
        
        # Определение доменов
        detected_domains = []
        for domain, keywords in self.domain_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_domains.append(domain)
        
        # Извлечение ключевых слов
        keywords = self._extract_keywords(query)
        
        # Определение сложности задачи
        complexity = self._assess_complexity(query, keywords)
        
        return {
            "intent_type": intent_type,
            "detected_domains": detected_domains,
            "keywords": keywords,
            "complexity": complexity,
            "query_length": len(query),
            "has_technical_terms": self._has_technical_terms(query)
        }
    
    def _select_loading_strategy(self, request: ContextLoadRequest, intent_analysis: Dict) -> ContextLoadingStrategy:
        """Выбор оптимальной стратегии загрузки"""
        
        # Если пользователь явно указал стратегию
        if request.strategy != ContextLoadingStrategy.AUTO_INTELLIGENT:
            return request.strategy
        
        # Автоматический выбор на основе анализа
        confidence_threshold = 0.7
        
        # Если намерение понятно и есть чёткие домены
        if (intent_analysis["intent_type"] != "unknown" and 
            len(intent_analysis["detected_domains"]) > 0 and
            intent_analysis["complexity"] != "high"):
            return ContextLoadingStrategy.AUTO_INTELLIGENT
        
        # Если есть технические термины но домен неясен
        if intent_analysis["has_technical_terms"]:
            return ContextLoadingStrategy.PATTERN_BASED
        
        # Если запрос очень простой или очень сложный
        if intent_analysis["query_length"] < 10 or intent_analysis["complexity"] == "high":
            return ContextLoadingStrategy.MANUAL_SELECTION
        
        # По умолчанию - intelligent
        return ContextLoadingStrategy.AUTO_INTELLIGENT
    
    def _execute_loading_strategy(self, strategy: ContextLoadingStrategy, 
                                request: ContextLoadRequest, 
                                intent_analysis: Dict) -> List[str]:
        """Выполнение выбранной стратегии загрузки"""
        
        loaded_files = []
        
        # Всегда загружаем core файлы если требуется
        if request.include_core:
            loaded_files.extend(self._load_core_files())
        
        if strategy == ContextLoadingStrategy.AUTO_INTELLIGENT:
            loaded_files.extend(self._load_intelligent_context(request, intent_analysis))
            
        elif strategy == ContextLoadingStrategy.PATTERN_BASED:
            loaded_files.extend(self._load_pattern_based_context(intent_analysis))
            
        elif strategy == ContextLoadingStrategy.MANUAL_SELECTION:
            loaded_files.extend(self._load_manual_selection_context(request, intent_analysis))
            
        elif strategy == ContextLoadingStrategy.FULL_CONTEXT:
            loaded_files.extend(self._load_full_context())
        
        # Загружаем активные задачи если требуется
        if request.include_tasks:
            loaded_files.extend(self._load_active_tasks())
        
        # Убираем дубликаты и сортируем по приоритету
        loaded_files = self._deduplicate_and_prioritize(loaded_files)
        
        # Ограничиваем количество модулей
        if len(loaded_files) > request.max_modules:
            loaded_files = loaded_files[:request.max_modules]
        
        return loaded_files
    
    def _load_intelligent_context(self, request: ContextLoadRequest, intent_analysis: Dict) -> List[str]:
        """Интеллектуальная загрузка на основе AI анализа"""
        files = []
        
        # Используем AI engine если доступен
        if self.ai_engine:
            try:
                # Проверяем сигнатуру метода
                import inspect
                sig = inspect.signature(self.ai_engine.get_recommendations)
                if 'limit' in sig.parameters:
                    ai_recommendations = self.ai_engine.get_recommendations(request.user_query, limit=5)
                else:
                    ai_recommendations = self.ai_engine.get_recommendations(request.user_query, verbose=False)[:5]
                
                for rec in ai_recommendations:
                    if "template_path" in rec:
                        file_path = f"modules/{rec['template_path']}"
                        if self._file_exists(file_path):
                            files.append(file_path)
            except Exception as e:
                print(f"⚠️  AI engine error: {e}")
        
        # Дополняем на основе доменов
        for domain in intent_analysis["detected_domains"]:
            domain_files = self._get_domain_files(domain)
            files.extend(domain_files[:2])  # Максимум 2 файла на домен
        
        # Добавляем файлы на основе намерения
        intent_files = self._get_intent_files(intent_analysis["intent_type"])
        files.extend(intent_files)
        
        return files
    
    def _load_pattern_based_context(self, intent_analysis: Dict) -> List[str]:
        """Загрузка на основе паттернов и правил"""
        files = []
        
        # Файлы на основе ключевых слов
        for keyword in intent_analysis["keywords"][:5]:  # Топ 5 ключевых слов
            keyword_files = self._find_files_by_keyword(keyword)
            files.extend(keyword_files[:2])
        
        # Файлы на основе доменов
        for domain in intent_analysis["detected_domains"]:
            domain_files = self._get_domain_files(domain)
            files.extend(domain_files)
        
        return files
    
    def _load_manual_selection_context(self, request: ContextLoadRequest, intent_analysis: Dict) -> List[str]:
        """Загрузка с предложением ручного выбора"""
        files = []
        
        # Загружаем базовый набор
        if intent_analysis["detected_domains"]:
            # Один файл из каждого домена
            for domain in intent_analysis["detected_domains"][:3]:
                domain_files = self._get_domain_files(domain)
                if domain_files:
                    files.append(domain_files[0])
        else:
            # Загружаем самые популярные модули
            popular_files = self._get_popular_modules(3)
            files.extend(popular_files)
        
        return files
    
    def _load_full_context(self) -> List[str]:
        """Загрузка полного контекста (все модули)"""
        files = []
        
        # Все модули из директории modules/
        modules_path = self.base_path / "modules"
        if modules_path.exists():
            for category_dir in modules_path.iterdir():
                if category_dir.is_dir():
                    for json_file in category_dir.glob("**/*.json"):
                        relative_path = json_file.relative_to(self.base_path)
                        files.append(str(relative_path))
        
        return files
    
    def _load_core_files_config(self) -> List[str]:
        """Загружает конфигурацию core файлов"""
        return [
            "manifest.json",
            "modules/core/standards.json", 
            "modules/core/project.json"
        ]
    
    def _load_core_files(self) -> List[str]:
        """Загружает core файлы системы"""
        files = []
        for file_path in self.core_files:
            if self._file_exists(file_path):
                files.append(file_path)
        return files
    
    def _load_active_tasks(self) -> List[str]:
        """Загружает активные задачи"""
        task_files = [
            "tasks/active.json",
            "tasks/analysis/slc_v4_comprehensive_analysis.json"
        ]
        
        return [f for f in task_files if self._file_exists(f)]
    
    def _get_ai_recommendations(self, query: str) -> List[Dict]:
        """Получает рекомендации от AI engine"""
        if not self.ai_engine:
            return []
        
        try:
            # Проверяем сигнатуру метода get_recommendations
            import inspect
            sig = inspect.signature(self.ai_engine.get_recommendations)
            if 'limit' in sig.parameters:
                return self.ai_engine.get_recommendations(query, limit=3, verbose=False)
            else:
                # Fallback для старой версии
                recommendations = self.ai_engine.get_recommendations(query, verbose=False)
                return recommendations[:3] if recommendations else []
        except Exception as e:
            print(f"⚠️  AI recommendations error: {e}")
            return []
    
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Загружает паттерны намерений"""
        return {
            "create_project": ["создать", "новый проект", "template", "generate", "start"],
            "find_information": ["что такое", "как", "документация", "info", "explain"],
            "solve_problem": ["ошибка", "проблема", "fix", "debug", "помощь", "issue"],
            "analyze_technology": ["анализ", "audit", "review", "оценка", "research"],
            "learn_domain": ["изучить", "learn", "tutorial", "guide", "начало"],
            "optimize_performance": ["оптимизация", "performance", "speed", "optimize", "improve"]
        }
    
    def _load_domain_keywords(self) -> Dict[str, List[str]]:
        """Загружает ключевые слова доменов"""
        return {
            "ai_ml": ["ai", "ml", "машинное обучение", "нейронные сети", "llm", "gpt", "prompt"],
            "python": ["python", "django", "fastapi", "flask", "pandas", "numpy"],
            "javascript": ["javascript", "js", "react", "vue", "node", "npm", "web"],
            "crypto": ["криптография", "blockchain", "defi", "smart contracts", "security"],
            "methodologies": ["методология", "процесс", "workflow", "стандарты", "best practices"],
            "tools": ["инструменты", "автоматизация", "ci/cd", "deployment", "monitoring"],
            "documentation": ["документация", "markdown", "wiki", "guide", "readme"]
        }
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Извлекает ключевые слова из запроса"""
        # Простое извлечение ключевых слов
        words = re.findall(r'\w+', query.lower())
        
        # Фильтруем стоп-слова
        stop_words = {'и', 'в', 'на', 'с', 'по', 'для', 'как', 'что', 'the', 'a', 'an', 'and', 'or', 'but'}
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        return keywords[:10]  # Максимум 10 ключевых слов
    
    def _assess_complexity(self, query: str, keywords: List[str]) -> str:
        """Оценивает сложность запроса"""
        # Простая эвристика
        if len(query) > 100 or len(keywords) > 8:
            return "high"
        elif len(query) < 20 or len(keywords) < 3:
            return "low"
        else:
            return "medium"
    
    def _has_technical_terms(self, query: str) -> bool:
        """Проверяет наличие технических терминов"""
        technical_terms = [
            'api', 'json', 'database', 'algorithm', 'framework', 'library',
            'api', 'json', 'база данных', 'алгоритм', 'фреймворк', 'библиотека'
        ]
        query_lower = query.lower()
        return any(term in query_lower for term in technical_terms)
    
    def _get_domain_files(self, domain: str) -> List[str]:
        """Получает файлы для конкретного домена"""
        domain_mapping = {
            "ai_ml": ["modules/ai_ml/prompt_engineering.json", "modules/ai_ml/fine_tuning_workflow.json"],
            "python": ["modules/languages/python/python_development.json"],
            "javascript": ["modules/languages/javascript/javascript_development.json"],
            "crypto": ["modules/projects/cryptography_project.json", "modules/methodologies/defi_security_audit.json"],
            "methodologies": ["modules/methodologies/obsidian_workflow.json", "modules/methodologies/documentation_systems.json"],
            "tools": ["modules/tools/slc_analytics.json", "modules/tools/slc_evolution_export.json"]
        }
        
        domain_files = domain_mapping.get(domain, [])
        return [f for f in domain_files if self._file_exists(f)]
    
    def _get_intent_files(self, intent_type: str) -> List[str]:
        """Получает файлы для конкретного типа намерения"""
        intent_mapping = {
            "create_project": ["tasks/templates/"],
            "solve_problem": ["modules/tools/", "docs/"],
            "analyze_technology": ["modules/methodologies/"],
            "optimize_performance": ["modules/tools/slc_analytics.json"]
        }
        
        return intent_mapping.get(intent_type, [])
    
    def _find_files_by_keyword(self, keyword: str) -> List[str]:
        """Находит файлы по ключевому слову"""
        files = []
        
        # Поиск в template manager если доступен
        if self.template_manager:
            try:
                search_results = self.template_manager.search_templates(keyword)
                for category, template_list in search_results.items():
                    for template in template_list:
                        files.append(f"modules/{category}/{template}")
            except Exception:
                pass
        
        return files
    
    def _get_popular_modules(self, limit: int = 5) -> List[str]:
        """Получает самые популярные модули"""
        # Возвращаем базовый набор популярных модулей
        popular = [
            "modules/ai_ml/prompt_engineering.json",
            "modules/languages/python/python_development.json",
            "modules/methodologies/obsidian_workflow.json"
        ]
        
        return [f for f in popular[:limit] if self._file_exists(f)]
    
    def _file_exists(self, file_path: str) -> bool:
        """Проверяет существование файла"""
        return (self.base_path / file_path).exists()
    
    def _deduplicate_and_prioritize(self, files: List[str]) -> List[str]:
        """Убирает дубликаты и сортирует по приоритету"""
        # Убираем дубликаты
        unique_files = list(dict.fromkeys(files))
        
        # Сортируем по приоритету (core > modules > tasks > tools)
        def priority_key(file_path: str) -> int:
            if file_path.startswith("modules/core/"):
                return 0
            elif file_path.startswith("modules/"):
                return 1
            elif file_path.startswith("tasks/"):
                return 2
            else:
                return 3
        
        return sorted(unique_files, key=priority_key)
    
    def _calculate_confidence_score(self, intent_analysis: Dict, loaded_files: List[str], ai_recommendations: List[Dict]) -> float:
        """Рассчитывает confidence score для загруженного контекста"""
        score = 0.0
        
        # Базовая оценка на основе анализа намерения
        if intent_analysis["intent_type"] != "unknown":
            score += 0.3
        
        # Оценка на основе найденных доменов
        if intent_analysis["detected_domains"]:
            score += 0.2 * min(len(intent_analysis["detected_domains"]), 3)
        
        # Оценка на основе AI рекомендаций
        if ai_recommendations:
            score += 0.3
        
        # Оценка на основе количества загруженных файлов
        if loaded_files:
            score += min(0.2, len(loaded_files) * 0.02)
        
        return min(score, 1.0)
    
    def _generate_fallback_suggestions(self, intent_analysis: Dict, loaded_files: List[str]) -> List[str]:
        """Генерирует предложения fallback'а"""
        suggestions = []
        
        if not loaded_files:
            suggestions.append("Попробуйте запрос 'загрузить весь контекст'")
            suggestions.append("Используйте более конкретные ключевые слова")
        
        if not intent_analysis["detected_domains"]:
            suggestions.append("Укажите область работы (AI, Python, crypto, etc.)")
        
        return suggestions
    
    def _load_usage_stats(self) -> Dict:
        """Загружает статистику использования"""
        stats_file = self.base_path / ".slc" / ".slc_usage_stats.json"
        if stats_file.exists():
            try:
                with open(stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}
    
    def _update_usage_stats(self, request: ContextLoadRequest, loaded_files: List[str], confidence: float):
        """Обновляет статистику использования"""
        # Пока простая реализация - можно расширить
        pass
    
    def load_files_content(self, file_paths: List[str]) -> Dict[str, str]:
        """
        Загружает содержимое файлов
        
        Args:
            file_paths: Список путей к файлам
            
        Returns:
            Словарь {путь_к_файлу: содержимое}
        """
        content = {}
        
        for file_path in file_paths:
            try:
                full_path = self.base_path / file_path
                if full_path.exists():
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content[file_path] = f.read()
                else:
                    content[file_path] = f"# Файл не найден: {file_path}"
            except Exception as e:
                content[file_path] = f"# Ошибка чтения файла {file_path}: {e}"
        
        return content
    
    def get_formatted_context(self, file_paths: List[str], format_type: str = "full") -> str:
        """
        Возвращает отформатированный контекст готовый для вставки в ИИ
        
        Args:
            file_paths: Список файлов для загрузки
            format_type: Тип форматирования (full, compact, structured)
            
        Returns:
            Отформатированный контекст
        """
        content = self.load_files_content(file_paths)
        
        if format_type == "compact":
            return self._format_compact_context(content)
        elif format_type == "structured":
            return self._format_structured_context(content)
        else:
            return self._format_full_context(content)
    
    def _format_full_context(self, content: Dict[str, str]) -> str:
        """Форматирует полный контекст с разделителями"""
        output = []
        output.append("=" * 80)
        output.append("SMART LAYERED CONTEXT - ПОЛНЫЙ КОНТЕКСТ ДЛЯ ИИ")
        output.append("=" * 80)
        output.append("")
        
        # Группируем по категориям
        categories = {
            "📋 CORE СИСТЕМА": [],
            "🧠 МОДУЛИ": [],
            "📝 ЗАДАЧИ": [],
            "🛠️ ИНСТРУМЕНТЫ": []
        }
        
        for file_path, file_content in content.items():
            if file_path.startswith("modules/core/"):
                categories["📋 CORE СИСТЕМА"].append((file_path, file_content))
            elif file_path.startswith("modules/"):
                categories["🧠 МОДУЛИ"].append((file_path, file_content))
            elif file_path.startswith("tasks/"):
                categories["📝 ЗАДАЧИ"].append((file_path, file_content))
            else:
                categories["🛠️ ИНСТРУМЕНТЫ"].append((file_path, file_content))
        
        # Выводим по категориям
        for category_name, files in categories.items():
            if files:
                output.append(f"\n{category_name}")
                output.append("-" * 60)
                
                for file_path, file_content in files:
                    output.append(f"\n📄 ФАЙЛ: {file_path}")
                    output.append("```")
                    output.append(file_content)
                    output.append("```")
                    output.append("")
        
        output.append("=" * 80)
        output.append(f"✅ КОНТЕКСТ ЗАГРУЖЕН: {len(content)} файлов")
        output.append("=" * 80)
        
        return "\n".join(output)
    
    def _format_compact_context(self, content: Dict[str, str]) -> str:
        """Компактный формат без разделителей"""
        output = []
        
        for file_path, file_content in content.items():
            output.append(f"# {file_path}")
            output.append(file_content)
            output.append("")
        
        return "\n".join(output)
    
    def _format_structured_context(self, content: Dict[str, str]) -> str:
        """Структурированный формат с JSON"""
        structured = {
            "context_metadata": {
                "loaded_files": list(content.keys()),
                "total_files": len(content),
                "timestamp": "2025-01-15T23:45:00Z"
            },
            "file_contents": content
        }
        
        return json.dumps(structured, indent=2, ensure_ascii=False)
    
    def _print_verbose_result(self, result: ContextLoadResult):
        """Выводит подробную информацию о результате"""
        print(f"\n🎯 Результаты загрузки контекста:")
        print(f"   📊 Confidence Score: {result.confidence_score:.2f}")
        print(f"   ⚡ Время выполнения: {result.execution_time:.3f}с")
        print(f"   📋 Стратегия: {result.strategy_used.value}")
        print(f"   📁 Загружено файлов: {len(result.loaded_files)}")
        
        if result.loaded_files:
            print("   📄 Файлы:")
            for file_path in result.loaded_files:
                print(f"      • {file_path}")
        
        if result.ai_recommendations:
            print(f"   🤖 AI рекомендации: {len(result.ai_recommendations)}")
        
        if result.fallback_suggestions:
            print("   💡 Дополнительные предложения:")
            for suggestion in result.fallback_suggestions:
                print(f"      • {suggestion}")


# Удобные функции для быстрого использования
def quick_load_context(query: str, verbose: bool = False) -> ContextLoadResult:
    """Быстрая загрузка контекста по запросу"""
    engine = UnifiedContextEngine()
    request = ContextLoadRequest(user_query=query, verbose=verbose)
    return engine.load_context(request)


def load_full_context(verbose: bool = False) -> ContextLoadResult:
    """Загрузка полного контекста"""
    engine = UnifiedContextEngine()
    request = ContextLoadRequest(
        user_query="load everything",
        strategy=ContextLoadingStrategy.FULL_CONTEXT,
        verbose=verbose
    )
    return engine.load_context(request)


if __name__ == "__main__":
    # Простой CLI для тестирования
    import sys
    
    if len(sys.argv) < 2:
        print("Использование: python unified_context_engine.py 'ваш запрос'")
        sys.exit(1)
    
    query = " ".join(sys.argv[1:])
    result = quick_load_context(query, verbose=True)
    
    if result.success:
        print(f"\n✅ Успешно загружено {len(result.loaded_files)} файлов")
    else:
        print(f"\n❌ Ошибка: {result.error_message}") 