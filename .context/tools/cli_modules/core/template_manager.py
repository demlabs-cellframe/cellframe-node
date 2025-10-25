"""
Template Manager - Управление шаблонами системы СЛК

Специализированный компонент для работы с шаблонами: поиск, получение информации, валидация.
Извлечен из SLCManager в рамках рефакторинга.

Версия: 1.0.0
Создано: 2025-01-25
"""

import json
from pathlib import Path
from typing import Dict, List, Optional


class TemplateManager:
    """Менеджер шаблонов - управление и поиск шаблонов СЛК"""
    
    def __init__(self, base_path: str = "."):
        """
        Инициализация менеджера шаблонов
        
        Args:
            base_path: Базовый путь к проекту СЛК
        """
        self.base_path = Path(base_path)
        self.modules_path = self.base_path / "modules"
    
    def list_templates(self, category: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Получить список доступных шаблонов
        
        Args:
            category: Фильтр по категории (опционально)
            
        Returns:
            Словарь с категориями и списком шаблонов
        """
        templates = {
            "languages": [],
            "methodologies": [], 
            "tools": [],
            "projects": []
        }
        
        if not self.modules_path.exists():
            return templates
            
        for category_path in self.modules_path.iterdir():
            if category_path.is_dir():
                category_name = category_path.name
                if category_name not in templates:
                    templates[category_name] = []
                    
                for template_file in category_path.glob("**/*.json"):
                    relative_path = template_file.relative_to(category_path)
                    templates[category_name].append(str(relative_path))
        
        if category:
            return {category: templates.get(category, [])}
        return templates
    
    def get_template_info(self, template_path: str) -> Optional[Dict]:
        """
        Получить подробную информацию о шаблоне
        
        Args:
            template_path: Путь к шаблону относительно modules/
            
        Returns:
            Словарь с информацией о шаблоне или None если не найден
        """
        full_path = self.modules_path / template_path
        if not full_path.exists():
            return None
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
                return {
                    "name": template_data.get("template_info", {}).get("name", "Unknown"),
                    "description": template_data.get("template_info", {}).get("description", "No description"),
                    "version": template_data.get("version", "1.0.0"),
                    "domain": template_data.get("domain", "unknown"),
                    "applicability": template_data.get("template_info", {}).get("applicability", "Unknown"),
                    "target_projects": template_data.get("template_info", {}).get("target_projects", []),
                    "file_path": str(full_path),
                    "relative_path": template_path
                }
        except Exception as e:
            return {"error": f"Failed to read template: {e}"}
    
    def search_templates(self, query: str) -> Dict[str, List[str]]:
        """
        Поиск шаблонов по ключевым словам
        
        Args:
            query: Поисковый запрос
            
        Returns:
            Словарь с найденными шаблонами по категориям
        """
        results = {}
        templates = self.list_templates()
        query_lower = query.lower()
        
        for category, template_list in templates.items():
            matching_templates = []
            for template_path in template_list:
                template_info = self.get_template_info(f"{category}/{template_path}")
                if template_info and not template_info.get("error"):
                    # Поиск в названии, описании и target_projects
                    search_text = (
                        template_info.get("name", "") + " " +
                        template_info.get("description", "") + " " +
                        " ".join(template_info.get("target_projects", []))
                    ).lower()
                    
                    if query_lower in search_text:
                        matching_templates.append(template_path)
            
            if matching_templates:
                results[category] = matching_templates
        
        return results
    
    def validate_template(self, template_path: str) -> Dict[str, bool]:
        """
        Валидация шаблона
        
        Args:
            template_path: Путь к шаблону
            
        Returns:
            Результаты валидации
        """
        results = {
            "exists": False,
            "readable": False,
            "valid_json": False,
            "has_template_info": False,
            "has_required_fields": False
        }
        
        full_path = self.modules_path / template_path
        results["exists"] = full_path.exists()
        
        if not results["exists"]:
            return results
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                results["readable"] = True
                template_data = json.load(f)
                results["valid_json"] = True
                
                # Проверяем наличие обязательных полей
                template_info = template_data.get("template_info", {})
                results["has_template_info"] = bool(template_info)
                
                required_fields = ["name", "description"]
                results["has_required_fields"] = all(
                    field in template_info for field in required_fields
                )
                
        except json.JSONDecodeError:
            results["readable"] = True
            results["valid_json"] = False
        except Exception:
            results["readable"] = False
        
        return results
    
    def get_template_stats(self) -> Dict:
        """
        Получить статистику по шаблонам
        
        Returns:
            Статистика по количеству шаблонов, категориям и доменам
        """
        templates = self.list_templates()
        total_templates = sum(len(v) for v in templates.values())
        
        domains = {}
        for category, template_list in templates.items():
            for template_path in template_list:
                template_info = self.get_template_info(f"{category}/{template_path}")
                if template_info and not template_info.get("error"):
                    domain = template_info.get("domain", "unknown")
                    domains[domain] = domains.get(domain, 0) + 1
        
        return {
            "total_templates": total_templates,
            "categories": {cat: len(templates) for cat, templates in templates.items()},
            "domains": domains,
            "modules_path_exists": self.modules_path.exists()
        }
    
    def find_templates_by_domain(self, domain: str) -> List[Dict]:
        """
        Найти все шаблоны для определенного домена
        
        Args:
            domain: Домен для поиска (например, "python", "ai_ml")
            
        Returns:
            Список шаблонов с информацией
        """
        results = []
        templates = self.list_templates()
        
        for category, template_list in templates.items():
            for template_path in template_list:
                template_info = self.get_template_info(f"{category}/{template_path}")
                if template_info and not template_info.get("error"):
                    if domain.lower() in template_info.get("domain", "").lower():
                        results.append({
                            "category": category,
                            "path": template_path,
                            "info": template_info
                        })
        
        return results 