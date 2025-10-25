#!/usr/bin/env python3
"""
🧠 Unified Context Engine - Единая система автоматической загрузки контекста
Заменяет разрозненные системы загрузки контекста единым интеллектуальным движком

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
from datetime import datetime
import time

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
    
    def __init__(self, root_path: str = "."):
        """
        Инициализация движка
        
        Args:
            root_path: Путь к корню проекта СЛК
        """
        self.root_path = Path(root_path).resolve()
        self.context_path = self.root_path / ".context"
        self.modules_path = self.context_path / "modules"
        self.tasks_path = self.context_path / "tasks"
        
        # Кэш для ускорения работы
        self.cache = {
            "modules": {},
            "tasks": {},
            "patterns": {},
            "last_update": None
        }
        
        # Паттерны для автоматического определения контекста
        self.context_patterns = {
            "ai_ml": {
                "keywords": ["ai", "ml", "llm", "prompt", "fine-tuning", "agent", "chatbot", "gpt", "claude", "neural", "model", "машинное обучение"],
                "modules": ["ai_ml/prompt_engineering.json", "ai_ml/ai_agent_development.json"],
                "confidence_boost": 0.3
            },
            "python": {
                "keywords": ["python", "django", "fastapi", "pytorch", "tensorflow", "pandas", "pytest", "тестирование"],
                "modules": ["languages/python/python_development.json", "core/standards.json"],
                "confidence_boost": 0.2
            },
            "python_dap": {
                "keywords": ["dap", "биндинг", "биндинги", "binding", "bindings", "python-dap", "питон-дап", "dap-sdk", "cellframe", "события", "events", "криптография", "crypto"],
                "modules": [
                    "projects/dap_sdk_project.json",
                    "languages/python/python_development.json", 
                    "languages/python/knowledge_base/dap_sdk_binding_standards.json",
                    "core/development_standards.json",
                    "core/standards.json"
                ],
                "confidence_boost": 0.4
            },
            "javascript": {
                "keywords": ["javascript", "react", "vue", "node", "web3", "ethereum", "frontend"],
                "modules": ["languages/javascript/javascript_development.json"],
                "confidence_boost": 0.2
            },
            "crypto": {
                "keywords": ["crypto", "blockchain", "defi", "smart-contract", "post-quantum", "security", "audit"],
                "modules": ["projects/cryptography_project.json", "projects/dap_sdk_project.json"],
                "confidence_boost": 0.3
            },
            "documentation": {
                "keywords": ["documentation", "docs", "markdown", "wiki", "obsidian", "knowledge", "документация"],
                "modules": ["methodologies/documentation_systems.json", "methodologies/obsidian_workflow.json"],
                "confidence_boost": 0.2
            },
            "architecture": {
                "keywords": ["architecture", "refactoring", "structure", "design", "архитектура", "рефакторинг"],
                "modules": ["core/standards.json", "core/project.json"],
                "confidence_boost": 0.2
            }
        }
        
        # Всегда загружаемые базовые модули
        self.core_modules = [
            "core/manifest.json",
            "core/standards.json", 
            "core/project.json"
        ]
        
        self.load_cache()
        
    def load_cache(self):
        """Загружает кэш модулей и задач"""
        try:
            # Загружаем информацию о модулях
            if self.modules_path.exists():
                for category_dir in self.modules_path.iterdir():
                    if category_dir.is_dir():
                        category = category_dir.name
                        self.cache["modules"][category] = []
                        
                        for module_file in category_dir.rglob("*.json"):
                            rel_path = module_file.relative_to(self.modules_path)
                            self.cache["modules"][category].append(str(rel_path))
                            
            # Загружаем информацию о задачах
            if self.tasks_path.exists():
                for task_file in self.tasks_path.glob("*.json"):
                    if not task_file.name.startswith("completed"):
                        self.cache["tasks"][task_file.stem] = str(task_file.relative_to(self.context_path))
                        
            self.cache["last_update"] = datetime.now().isoformat()
            
        except Exception as e:
            print(f"Warning: Не удалось загрузить кэш: {e}")
            
    def analyze_user_intent(self, query: str) -> Dict[str, Any]:
        """Анализирует запрос пользователя и определяет намерения"""
        query_lower = query.lower()
        
        # Результаты анализа
        analysis = {
            "query": query,
            "detected_domains": [],
            "confidence_scores": {},
            "suggested_modules": [],
            "suggested_tasks": [],
            "total_confidence": 0.0
        }
        
        # Проверяем паттерны доменов
        for domain, config in self.context_patterns.items():
            score = 0.0
            matched_keywords = []
            
            for keyword in config["keywords"]:
                if keyword in query_lower:
                    score += config["confidence_boost"]
                    matched_keywords.append(keyword)
                    
            if score > 0:
                analysis["detected_domains"].append({
                    "domain": domain,
                    "score": score,
                    "matched_keywords": matched_keywords,
                    "suggested_modules": config["modules"]
                })
                analysis["confidence_scores"][domain] = score
                analysis["suggested_modules"].extend(config["modules"])
                
        # Сортируем по уверенности
        analysis["detected_domains"].sort(key=lambda x: x["score"], reverse=True)
        analysis["total_confidence"] = sum(analysis["confidence_scores"].values())
        
        # Убираем дубликаты из модулей
        analysis["suggested_modules"] = list(set(analysis["suggested_modules"]))
        
        return analysis
        
    def find_relevant_tasks(self, query: str) -> List[Dict[str, Any]]:
        """Находит релевантные задачи по запросу"""
        relevant_tasks = []
        query_lower = query.lower()
        
        for task_name, task_path in self.cache["tasks"].items():
            full_path = self.context_path / task_path
            
            try:
                if full_path.exists():
                    with open(full_path, 'r', encoding='utf-8') as f:
                        task_data = json.load(f)
                        
                    # Проверяем совпадения в названии и описании
                    score = 0.0
                    
                    # Название задачи
                    if any(word in task_name.lower() for word in query_lower.split()):
                        score += 0.5
                        
                    # Описание проекта
                    if "project" in task_data:
                        project_text = task_data["project"].lower()
                        if any(word in project_text for word in query_lower.split()):
                            score += 0.3
                            
                    # Статус и фаза
                    if "status" in task_data:
                        status_text = task_data["status"].lower()
                        if any(word in status_text for word in query_lower.split()):
                            score += 0.2
                            
                    if score > 0:
                        relevant_tasks.append({
                            "name": task_name,
                            "path": task_path,
                            "score": score,
                            "completion": task_data.get("completion", "0%"),
                            "status": task_data.get("status", "unknown")
                        })
                        
            except Exception as e:
                continue
                
        # Сортируем по релевантности
        relevant_tasks.sort(key=lambda x: x["score"], reverse=True)
        return relevant_tasks[:5]  # Топ 5 задач
        
    def build_context_package(self, analysis: Dict[str, Any], max_modules: int = 6) -> Dict[str, Any]:
        """Собирает пакет контекста на основе анализа"""
        start_time = time.time()
        
        package = {
            "timestamp": datetime.now().isoformat(),
            "query_analysis": analysis,
            "files_to_load": [],
            "loading_strategy": "automatic",
            "confidence": analysis["total_confidence"],
            "performance": {},
            "processed_files": set()  # Для предотвращения циклических ссылок
        }
        
        # Всегда добавляем базовые модули
        for core_module in self.core_modules:
            module_path = self.modules_path / core_module
            if module_path.exists():
                package["files_to_load"].append({
                    "path": str(module_path.relative_to(self.root_path)),
                    "type": "core_module",
                    "priority": "high",
                    "reason": "Базовый модуль системы"
                })
                
        # Добавляем модули на основе анализа
        added_modules = 0
        for domain_info in analysis["detected_domains"]:
            if added_modules >= max_modules - len(self.core_modules):
                break
                
            for module_rel_path in domain_info["suggested_modules"]:
                if added_modules >= max_modules - len(self.core_modules):
                    break
                    
                module_path = self.modules_path / module_rel_path
                if module_path.exists():
                    package["files_to_load"].append({
                        "path": str(module_path.relative_to(self.root_path)),
                        "type": "domain_module",
                        "priority": "medium",
                        "reason": f"Обнаружен домен: {domain_info['domain']} (score: {domain_info['score']:.2f})",
                        "matched_keywords": domain_info["matched_keywords"]
                    })
                    added_modules += 1
                    
        # Добавляем релевантные задачи
        relevant_tasks = self.find_relevant_tasks(analysis["query"])
        for task in relevant_tasks[:2]:  # Максимум 2 задачи
            task_path = self.context_path / task["path"]
            if task_path.exists():
                package["files_to_load"].append({
                    "path": str(task_path.relative_to(self.root_path)),
                    "type": "task",
                    "priority": "low",
                    "reason": f"Релевантная задача (score: {task['score']:.2f})",
                    "task_status": task["status"],
                    "completion": task["completion"]
                })
                
        # ДОБАВЛЕНО: Рекурсивная обработка auto_load файлов
        self._process_recursive_loading(package)
                
        # Метрики производительности
        end_time = time.time()
        package["performance"] = {
            "analysis_time_ms": round((end_time - start_time) * 1000, 2),
            "total_files": len(package["files_to_load"]),
            "core_modules": len(self.core_modules),
            "domain_modules": added_modules,
            "tasks": len([f for f in package["files_to_load"] if f["type"] == "task"]),
            "recursive_files": len(package.get("processed_files", set()))
        }
        
        return package
        
    def load_context(self, request: 'ContextLoadRequest') -> 'ContextLoadResult':
        """Основная функция загрузки контекста"""
        import time
        start_time = time.time()
        
        try:
            query = request.user_query
            
            if request.verbose:
                print(f"🧠 Анализ запроса: '{query}'")
                
            # Анализируем намерения пользователя
            analysis = self.analyze_user_intent(query)
        
            if request.verbose:
                print(f"🎯 Обнаружено доменов: {len(analysis['detected_domains'])}")
                for domain_info in analysis["detected_domains"]:
                    print(f"   {domain_info['domain']}: {domain_info['score']:.2f} ({', '.join(domain_info['matched_keywords'])})")
                    
            # Собираем пакет контекста
            package = self.build_context_package(analysis, request.max_modules)
            
            if request.verbose:
                print(f"📦 Пакет контекста собран:")
                print(f"   Файлов к загрузке: {package['performance']['total_files']}")
                print(f"   Время анализа: {package['performance']['analysis_time_ms']}ms")
                print(f"   Уверенность: {package['confidence']:.2f}")
                
            # Формируем список загруженных файлов
            loaded_files = [f["path"] for f in package["files_to_load"]]
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            return ContextLoadResult(
                loaded_files=loaded_files,
                confidence_score=package.get('confidence', 0.0),
                strategy_used=request.strategy,
                ai_recommendations=analysis.get('detected_domains', []),
                fallback_suggestions=[],
                execution_time=execution_time,
                success=True
            )
            
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            
            return ContextLoadResult(
                loaded_files=[],
                confidence_score=0.0,
                strategy_used=request.strategy,
                ai_recommendations=[],
                fallback_suggestions=[],
                execution_time=execution_time,
                success=False,
                error_message=str(e)
            )
        
    def generate_loading_commands(self, package: Dict[str, Any]) -> List[str]:
        """Генерирует команды для загрузки файлов"""
        commands = []
        
        # Группируем файлы по приоритету
        high_priority = [f for f in package["files_to_load"] if f["priority"] == "high"]
        medium_priority = [f for f in package["files_to_load"] if f["priority"] == "medium"]
        low_priority = [f for f in package["files_to_load"] if f["priority"] == "low"]
        
        # Команды загрузки
        for file_info in high_priority + medium_priority + low_priority:
            commands.append(f"# {file_info['reason']}")
            commands.append(f"load_file('{file_info['path']}')")
            
        return commands
        
    def get_fallback_context(self) -> Dict[str, Any]:
        """Возвращает базовый контекст если автоматический анализ не сработал"""
        return {
            "timestamp": datetime.now().isoformat(),
            "loading_strategy": "fallback",
            "files_to_load": [
                {
                    "path": str((self.modules_path / module).relative_to(self.root_path)),
                    "type": "core_module",
                    "priority": "high",
                    "reason": "Базовый контекст системы"
                }
                for module in self.core_modules
                if (self.modules_path / module).exists()
            ],
            "confidence": 0.0,
            "performance": {
                "analysis_time_ms": 0,
                "total_files": len(self.core_modules)
            }
        }
    
    def get_formatted_context(self, file_paths: List[str], format_type: str = "full") -> str:
        """Получает отформатированный контекст из файлов"""
        try:
            formatted_context = []
            
            for file_path in file_paths:
                full_path = self.root_path / file_path
                
                if full_path.exists():
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        if format_type == "full":
                            formatted_context.append(f"=== {file_path} ===")
                            formatted_context.append(content)
                            formatted_context.append("")
                        elif format_type == "summary":
                            # Краткое содержимое
                            lines = content.split('\n')
                            summary = '\n'.join(lines[:10])  # Первые 10 строк
                            formatted_context.append(f"--- {file_path} (краткое содержание) ---")
                            formatted_context.append(summary)
                            if len(lines) > 10:
                                formatted_context.append(f"... и еще {len(lines) - 10} строк")
                            formatted_context.append("")
                            
                    except Exception as e:
                        formatted_context.append(f"❌ Ошибка чтения {file_path}: {e}")
                        
                else:
                    formatted_context.append(f"❌ Файл не найден: {file_path}")
                    
            return '\n'.join(formatted_context)
            
        except Exception as e:
            return f"❌ Ошибка форматирования контекста: {e}"
            
    def _process_recursive_loading(self, package: Dict[str, Any]) -> None:
        """Рекурсивно обрабатывает auto_load файлы в JSON"""
        
        max_depth = 5  # Максимальная глубина рекурсии
        current_depth = 0
        files_to_process = list(package["files_to_load"])
        
        while files_to_process and current_depth < max_depth:
            current_depth += 1
            new_files = []
            
            for file_info in files_to_process:
                file_path = self.root_path / file_info["path"]
                file_key = str(file_path)
                
                # Пропускаем уже обработанные файлы
                if file_key in package["processed_files"]:
                    continue
                    
                package["processed_files"].add(file_key)
                
                try:
                    if file_path.exists() and file_path.suffix == '.json':
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                        # Обрабатываем context_loading_policy.auto_load
                        context = data.get("context", {})
                        loading_policy = context.get("context_loading_policy", {})
                        auto_load_files = loading_policy.get("auto_load", [])
                        
                        # Добавляем файлы из auto_load
                        for auto_file in auto_load_files:
                            if isinstance(auto_file, str):
                                auto_file_path = self.modules_path / auto_file
                                if auto_file_path.exists():
                                    new_file_info = {
                                        "path": str(auto_file_path.relative_to(self.root_path)),
                                        "type": "auto_loaded",
                                        "priority": "high",
                                        "reason": f"Автозагрузка из {file_info['path']}",
                                        "source_file": file_info["path"]
                                    }
                                    
                                    # Проверяем не добавлен ли уже
                                    if not any(f["path"] == new_file_info["path"] for f in package["files_to_load"]):
                                        package["files_to_load"].append(new_file_info)
                                        new_files.append(new_file_info)
                                        
                        # Обрабатываем $ref ссылки (JSON Schema style)
                        self._process_json_refs(data, file_path, package, new_files)
                        
                except Exception as e:
                    # Игнорируем ошибки чтения файлов (могут быть не JSON)
                    continue
                    
            files_to_process = new_files
            
    def _process_json_refs(self, data: Any, source_file: Path, package: Dict[str, Any], new_files: List[Dict]) -> None:
        """Рекурсивно обрабатывает $ref ссылки в JSON"""
        
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "$ref" and isinstance(value, str):
                    # Обрабатываем локальные ссылки (не URLs)
                    if not value.startswith(('http://', 'https://', '#/')):
                        ref_path = source_file.parent / value
                        if ref_path.exists():
                            new_file_info = {
                                "path": str(ref_path.relative_to(self.root_path)),
                                "type": "referenced",
                                "priority": "medium",
                                "reason": f"$ref ссылка из {source_file.name}",
                                "source_file": str(source_file.relative_to(self.root_path))
                            }
                            
                            if not any(f["path"] == new_file_info["path"] for f in package["files_to_load"]):
                                package["files_to_load"].append(new_file_info)
                                new_files.append(new_file_info)
                                
                elif isinstance(value, (dict, list)):
                    self._process_json_refs(value, source_file, package, new_files)
                    
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self._process_json_refs(item, source_file, package, new_files)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified Context Engine - автоматическая загрузка контекста")
    parser.add_argument("query", help="Запрос пользователя для анализа контекста")
    parser.add_argument("--max-modules", type=int, default=6, help="Максимальное количество модулей")
    parser.add_argument("--verbose", "-v", action="store_true", help="Подробный вывод")
    parser.add_argument("--json", action="store_true", help="JSON вывод")
    parser.add_argument("--commands", action="store_true", help="Генерировать команды загрузки")
    
    args = parser.parse_args()
    
    engine = UnifiedContextEngine()
    
    # Создаем запрос
    request = ContextLoadRequest(
        user_query=args.query,
        max_modules=args.max_modules,
        verbose=args.verbose
    )
    
    result = engine.load_context(request)
    
    if not result.success:
        print(f"❌ Ошибка: {result.error_message}")
        return 1
    
    if args.json:
        output = {
            "loaded_files": result.loaded_files,
            "confidence_score": result.confidence_score,
            "strategy_used": result.strategy_used.value,
            "ai_recommendations": result.ai_recommendations,
            "execution_time": result.execution_time,
            "success": result.success
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(f"✅ Контекст для '{args.query}' готов к загрузке")
        print(f"📊 Файлов: {len(result.loaded_files)}, Уверенность: {result.confidence_score:.2f}")
        
        if args.verbose:
            print("\n📋 Загруженные файлы:")
            for file_path in result.loaded_files:
                print(f"   • {file_path}")
                
    return 0

if __name__ == "__main__":
    main() 