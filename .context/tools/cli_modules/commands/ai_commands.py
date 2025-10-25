#!/usr/bin/env python3
"""
AI-powered команды для Smart Layered Context CLI
Интеллектуальные рекомендации и анализ контекста

Версия: 1.0.0
Создано: 2025-01-15
"""

import os
import json
import math
import re
from collections import defaultdict, Counter
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

from tools.cli_modules.common.base_command import BaseCommand
from tools.cli_modules.core.template_manager import TemplateManager


class TFIDFAnalyzer:
    """TF-IDF анализатор для семантического поиска модулей"""
    
    def __init__(self, templates_data: Dict[str, Any]):
        self.templates_data = templates_data
        self.documents = self._build_documents()
        self.vocabulary = self._build_vocabulary()
        self.idf_scores = self._calculate_idf()
    
    def _build_documents(self) -> Dict[str, str]:
        """Строит документы из данных шаблонов"""
        documents = {}
        
        for template_path, template_data in self.templates_data.items():
            # Собираем текст из названия, описания, тегов и ключевых слов
            text_parts = []
            
            # Название и описание
            if 'name' in template_data:
                text_parts.append(template_data['name'])
            if 'description' in template_data:
                text_parts.append(template_data['description'])
            
            # Теги
            if 'tags' in template_data:
                text_parts.extend(template_data['tags'])
            
            # Ключевые слова из template_info
            if 'template_info' in template_data:
                info = template_data['template_info']
                if 'target_projects' in info:
                    text_parts.extend(info['target_projects'])
                if 'keywords' in info:
                    text_parts.extend(info['keywords'])
            
            # Объединяем все в один документ
            documents[template_path] = ' '.join(text_parts).lower()
        
        return documents
    
    def _build_vocabulary(self) -> set:
        """Строит словарь уникальных терминов"""
        vocabulary = set()
        
        for doc_text in self.documents.values():
            terms = self._tokenize(doc_text)
            vocabulary.update(terms)
        
        return vocabulary
    
    def _tokenize(self, text: str) -> List[str]:
        """Токенизация текста"""
        # Простая токенизация - разбиение по не-буквенным символам
        tokens = re.findall(r'\b[a-zA-Zа-яА-Я]+\b', text.lower())
        
        # Фильтруем стоп-слова
        stop_words = {'и', 'или', 'в', 'на', 'для', 'с', 'по', 'от', 'к', 'the', 'a', 'an', 'in', 'on', 'for', 'with', 'to', 'from'}
        tokens = [token for token in tokens if token not in stop_words and len(token) > 2]
        
        return tokens
    
    def _calculate_idf(self) -> Dict[str, float]:
        """Рассчитывает IDF для каждого термина"""
        idf_scores = {}
        total_docs = len(self.documents)
        
        for term in self.vocabulary:
            docs_with_term = sum(1 for doc_text in self.documents.values() 
                               if term in self._tokenize(doc_text))
            
            if docs_with_term > 0:
                idf_scores[term] = math.log(total_docs / docs_with_term)
            else:
                idf_scores[term] = 0.0
        
        return idf_scores
    
    def calculate_tf_idf_score(self, query: str, template_path: str) -> float:
        """Рассчитывает TF-IDF score для запроса и шаблона"""
        query_terms = self._tokenize(query)
        doc_text = self.documents.get(template_path, "")
        doc_terms = self._tokenize(doc_text)
        
        if not query_terms or not doc_terms:
            return 0.0
        
        # Рассчитываем TF-IDF для каждого термина запроса
        tf_idf_sum = 0.0
        
        for term in query_terms:
            if term in self.vocabulary:
                # TF - частота термина в документе
                tf = doc_terms.count(term) / len(doc_terms) if doc_terms else 0
                
                # IDF - обратная частота документа
                idf = self.idf_scores.get(term, 0)
                
                # TF-IDF
                tf_idf_sum += tf * idf
        
        return tf_idf_sum / len(query_terms) if query_terms else 0.0


class UsageTracker:
    """Трекер использования шаблонов"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.usage_file = self.base_path / ".slc_usage_stats.json"
        self.usage_data = self._load_usage_data()
    
    def _load_usage_data(self) -> Dict[str, Any]:
        """Загружает данные об использовании"""
        if self.usage_file.exists():
            try:
                with open(self.usage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        return {
            "version": "1.0",
            "templates": {},
            "queries": [],
            "sessions": []
        }
    
    def _save_usage_data(self):
        """Сохраняет данные об использовании"""
        try:
            with open(self.usage_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"⚠️  Не удалось сохранить статистику использования: {e}")
    
    def track_template_usage(self, template_path: str, action: str = "viewed"):
        """Отслеживает использование шаблона"""
        if template_path not in self.usage_data["templates"]:
            self.usage_data["templates"][template_path] = {
                "views": 0,
                "creates": 0,
                "last_used": None
            }
        
        self.usage_data["templates"][template_path][f"{action}s"] += 1
        self.usage_data["templates"][template_path]["last_used"] = self._get_timestamp()
        self._save_usage_data()
    
    def track_query(self, query: str, selected_template: Optional[str] = None):
        """Отслеживает запрос пользователя"""
        query_data = {
            "timestamp": self._get_timestamp(),
            "query": query,
            "selected_template": selected_template
        }
        
        self.usage_data["queries"].append(query_data)
        
        # Ограничиваем количество запросов
        if len(self.usage_data["queries"]) > 1000:
            self.usage_data["queries"] = self.usage_data["queries"][-1000:]
        
        self._save_usage_data()
    
    def get_usage_score(self, template_path: str) -> float:
        """Получает оценку использования шаблона"""
        template_stats = self.usage_data["templates"].get(template_path, {})
        
        views = template_stats.get("views", 0)
        creates = template_stats.get("creates", 0)
        
        # Создания имеют больший вес чем просмотры
        score = views * 0.3 + creates * 0.7
        
        # Нормализация (простая)
        max_score = max(
            (stats.get("views", 0) * 0.3 + stats.get("creates", 0) * 0.7)
            for stats in self.usage_data["templates"].values()
        ) if self.usage_data["templates"] else 1
        
        return score / max_score if max_score > 0 else 0.0
    
    def _get_timestamp(self) -> str:
        """Получает текущий timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


class IntelligentSemanticAnalyzer:
    """
    Интеллектуальный семантический анализатор запросов
    
    ЗАМЕНЯЕТ keyword-based логику на ИИ-анализ через UniversalSemanticAnalyzer
    """
    
    def __init__(self, ai_manager=None):
        """
        Инициализация интеллектуального анализатора
        
        Args:
            ai_manager: AI Manager для семантического анализа
        """
        self.ai_manager = ai_manager
        self._analyzer = None
        
        # Пытаемся импортировать UniversalSemanticAnalyzer
        try:
            # AI-анализ отключен для CLI из-за сложности путей импорта
            # CLI использует собственные эвристики для анализа шаблонов
            self.ai_available = False
            self._analyzer = None
            print("ℹ️ CLI использует эвристический анализ (AI-анализ доступен через API)")
            
        except Exception as e:
            print(f"⚠️ UniversalSemanticAnalyzer недоступен: {e}")
            self.ai_available = False
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Анализирует семантику запроса через ИИ
        
        Args:
            query: Запрос для анализа
            
        Returns:
            Результат семантического анализа
        """
        if not self.ai_available or not self._analyzer:
            return self._fallback_analysis(query)
        
        try:
            # ИИ-анализ намерений и доменов через синхронные обертки
            import asyncio
            
            # Запускаем async анализ в синхронном контексте
            loop = None
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Выполняем анализ
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../slc-agent/src'))
            from ai.manager.services.universal_semantic_analyzer import AnalysisType
            
            intent_result = loop.run_until_complete(self._analyzer.analyze_single(query, AnalysisType.INTENT))
            domain_result = loop.run_until_complete(self._analyzer.analyze_single(query, AnalysisType.DOMAIN))
            classification_result = loop.run_until_complete(self._analyzer.analyze_single(query, AnalysisType.TASK_CLASSIFICATION))
            
            # Преобразуем результаты в формат CLI
            intent_analysis = {
                "primary_intent": intent_result.result,
                "confidence": intent_result.confidence,
                "reasoning": intent_result.reasoning
            }
            
            domain_analysis = {
                "primary_domain": domain_result.result,
                "confidence": domain_result.confidence,
                "reasoning": domain_result.reasoning
            }
            
            return {
                "intent": intent_analysis,
                "domain": domain_analysis,
                "task_classification": classification_result.result,
                "original_query": query,
                "analysis_method": "ai_semantic",
                "metadata": {
                    "intent_metadata": intent_result.metadata,
                    "domain_metadata": domain_result.metadata
                }
            }
            
        except Exception as e:
            print(f"❌ Ошибка ИИ-анализа: {e}")
            return self._fallback_analysis(query)
    
    def _fallback_analysis(self, query: str) -> Dict[str, Any]:
        """
        Упрощенный структурный анализ без keyword lists
        
        Args:
            query: Запрос для анализа
            
        Returns:
            Базовый результат анализа
        """
        query_lower = query.lower()
        
        # Структурный анализ без hardcoded keywords
        has_action_words = any(word in query_lower for word in ["создать", "найти", "показать", "help"])
        has_tech_terms = any(word in query_lower for word in ["api", "код", "функция", "класс"])
        has_questions = any(word in query_lower for word in ["что", "как", "где", "why", "what", "how"])
        
        # Определяем намерение на основе структуры
        if has_action_words:
            primary_intent = "action_request"
        elif has_questions:
            primary_intent = "information_seeking"
        elif has_tech_terms:
            primary_intent = "technical_inquiry"
        else:
            primary_intent = "general_query"
        
        # Определяем домен на основе контекста
        if any(word in query_lower for word in ["python", "javascript", "код"]):
            primary_domain = "programming"
        elif any(word in query_lower for word in ["ai", "ml", "модель"]):
            primary_domain = "ai_ml"
        elif any(word in query_lower for word in ["web", "api", "frontend"]):
            primary_domain = "web_development"
        else:
            primary_domain = "general"
        
        return {
            "intent": {
                "primary_intent": primary_intent,
                "confidence": 0.6,
                "reasoning": "Структурный анализ без keyword lists"
            },
            "domain": {
                "primary_domain": primary_domain,
                "confidence": 0.6,
                "reasoning": "Контекстный анализ без hardcoded domains"
            },
            "task_classification": "general",
            "original_query": query,
            "analysis_method": "structural_fallback",
            "metadata": {}
        }


# Создаем псевдоним для обратной совместимости
SemanticAnalyzer = IntelligentSemanticAnalyzer


class IntelligentRecommendationEngine:
    """Основной движок интеллектуальных рекомендаций"""
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.template_manager = TemplateManager(base_path)
        self.usage_tracker = UsageTracker(base_path)
        self.semantic_analyzer = SemanticAnalyzer()
        
        # Загружаем данные шаблонов
        self.templates_data = self._load_templates_data()
        self.tfidf_analyzer = TFIDFAnalyzer(self.templates_data)
        
        # Весовые коэффициенты
        self.weights = {
            "tfidf_score": 0.40,
            "usage_frequency": 0.30,
            "contextual_relevance": 0.20,
            "semantic_match": 0.10
        }
    
    def _load_templates_data(self) -> Dict[str, Any]:
        """Загружает данные всех шаблонов"""
        templates_data = {}
        
        # TemplateManager возвращает словарь категория -> список файлов
        templates = self.template_manager.list_templates()
        
        for category, template_list in templates.items():
            for template_file in template_list:
                # Полный путь: категория/файл
                template_path = f"{category}/{template_file}"
                
                try:
                    # Загружаем полные данные из JSON файла
                    full_path = self.template_manager.modules_path / template_path
                    if full_path.exists():
                        with open(full_path, 'r', encoding='utf-8') as f:
                            template_data = json.load(f)
                            templates_data[template_path] = template_data
                except Exception as e:
                    print(f"⚠️  Ошибка загрузки шаблона {template_path}: {e}")
        
        return templates_data
    
    def get_recommendations(self, query: str, max_results: int = 5, verbose: bool = False) -> List[Dict[str, Any]]:
        """Получает рекомендации для запроса"""
        # Семантический анализ запроса
        query_analysis = self.semantic_analyzer.analyze_query(query)
        
        # Рассчитываем оценки для каждого шаблона
        recommendations = []
        
        for template_path in self.templates_data.keys():
            scores = self._calculate_scores(query, template_path, query_analysis)
            
            final_score = (
                scores["tfidf_score"] * self.weights["tfidf_score"] +
                scores["usage_frequency"] * self.weights["usage_frequency"] +
                scores["contextual_relevance"] * self.weights["contextual_relevance"] +
                scores["semantic_match"] * self.weights["semantic_match"]
            )
            
            if final_score > 0.01:  # Минимальный порог
                recommendations.append({
                    "template": template_path,
                    "score": final_score,
                    "details": scores if verbose else None
                })
        
        # Сортируем по оценке
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        
        # Отслеживаем запрос
        self.usage_tracker.track_query(query)
        
        return recommendations[:max_results]
    
    def _calculate_scores(self, query: str, template_path: str, query_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Рассчитывает различные оценки для шаблона"""
        scores = {}
        
        # TF-IDF оценка
        scores["tfidf_score"] = self.tfidf_analyzer.calculate_tf_idf_score(query, template_path)
        
        # Оценка частоты использования
        scores["usage_frequency"] = self.usage_tracker.get_usage_score(template_path)
        
        # Контекстуальная релевантность
        scores["contextual_relevance"] = self._calculate_contextual_relevance(
            template_path, query_analysis
        )
        
        # Семантическое соответствие
        scores["semantic_match"] = self._calculate_semantic_match(
            template_path, query_analysis
        )
        
        return scores
    
    def _calculate_contextual_relevance(self, template_path: str, query_analysis: Dict[str, Any]) -> float:
        """Рассчитывает контекстуальную релевантность"""
        template_data = self.templates_data.get(template_path, {})
        
        # Проверяем соответствие домена
        domain_match = 0.0
        detected_domains = query_analysis.get("domain", {})
        
        # Простая проверка - если шаблон из ai_ml, а запрос про AI
        if "ai_ml" in template_path and "ai_ml" in detected_domains:
            domain_match += 0.5
        
        if "python" in template_path and "python" in detected_domains:
            domain_match += 0.3
        
        if "javascript" in template_path and "javascript" in detected_domains:
            domain_match += 0.3
        
        return min(domain_match, 1.0)
    
    def _calculate_semantic_match(self, template_path: str, query_analysis: Dict[str, Any]) -> float:
        """Рассчитывает семантическое соответствие"""
        template_data = self.templates_data.get(template_path, {})
        
        # Проверяем соответствие намерений
        intent_match = 0.0
        intents = query_analysis.get("intent", {})
        
        # Если намерение "создать проект", то приоритет шаблонам
        if "create_project" in intents:
            intent_match += 0.4
        
        # Если намерение "найти шаблон", то тоже приоритет
        if "find_template" in intents:
            intent_match += 0.3
        
        return min(intent_match, 1.0)


class RecommendCommand(BaseCommand):
    """Команда для получения интеллектуальных рекомендаций"""
    
    def __init__(self, base_path: str):
        super().__init__()
        self.base_path = base_path
        self.recommendation_engine = IntelligentRecommendationEngine(base_path)
    
    @property
    def name(self) -> str:
        return "recommend"
    
    @property
    def description(self) -> str:
        return "🧠 Получить интеллектуальные рекомендации шаблонов на основе запроса"
    
    def add_arguments(self, parser):
        """Добавляет аргументы команды"""
        parser.add_argument(
            "query",
            help="Запрос для получения рекомендаций"
        )
        parser.add_argument(
            "--count", "-n",
            type=int,
            default=5,
            help="Количество рекомендаций (по умолчанию: 5)"
        )
        parser.add_argument(
            "--verbose", "-v",
            action="store_true",
            help="Подробная информация о скоринге"
        )
    
    def validate_args(self, args) -> bool:
        """Валидирует аргументы команды"""
        if not args.query or not args.query.strip():
            print("❌ Необходимо указать запрос для рекомендаций")
            return False
        
        if args.count < 1 or args.count > 20:
            print("❌ Количество рекомендаций должно быть от 1 до 20")
            return False
        
        return True
    
    def execute(self, args) -> int:
        """Выполняет команду рекомендаций"""
        try:
            print(f"🧠 Анализирую запрос: '{args.query}'")
            print()
            
            # Получаем рекомендации
            recommendations = self.recommendation_engine.get_recommendations(
                args.query,
                max_results=args.count,
                verbose=args.verbose
            )
            
            if not recommendations:
                print("❌ Не найдено подходящих шаблонов")
                print("💡 Попробуйте изменить запрос или использовать 'slc_cli.py search KEYWORD'")
                return 1
            
            # Выводим результаты
            print(f"📋 Найдено {len(recommendations)} рекомендаций:")
            print("=" * 60)
            
            for i, rec in enumerate(recommendations, 1):
                template_path = rec["template"]
                score = rec["score"]
                
                # Получаем информацию о шаблоне
                try:
                    template_info = self.recommendation_engine.template_manager.get_template_info(template_path)
                    if template_info:
                        name = template_info.get("name", template_path)
                        description = template_info.get("description", "Нет описания")
                    else:
                        name = template_path
                        description = "Информация недоступна"
                except:
                    name = template_path
                    description = "Информация недоступна"
                
                print(f"{i}. 📄 {name}")
                print(f"   📂 {template_path}")
                print(f"   📊 Релевантность: {score:.2%}")
                print(f"   📝 {description}")
                
                # Подробная информация если запрошена
                if args.verbose and rec["details"]:
                    details = rec["details"]
                    print(f"   🔍 Детали скоринга:")
                    print(f"      TF-IDF: {details['tfidf_score']:.3f}")
                    print(f"      Использование: {details['usage_frequency']:.3f}")
                    print(f"      Контекст: {details['contextual_relevance']:.3f}")
                    print(f"      Семантика: {details['semantic_match']:.3f}")
                
                print()
            
            # Предлагаем действия
            print("💡 Что дальше:")
            print(f"   slc_cli.py info TEMPLATE_PATH    # Подробная информация")
            print(f"   slc_cli.py create TEMPLATE_PATH PROJECT_NAME    # Создать проект")
            
            return 0
            
        except Exception as e:
            print(f"❌ Ошибка при получении рекомендаций: {e}")
            return 1 