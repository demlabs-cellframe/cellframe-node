"""
System Validator - Валидация системы СЛК

Компонент для проверки целостности и корректности системы Smart Layered Context.
Извлечен из SLCManager в рамках рефакторинга.

Версия: 1.0.0
Создано: 2025-01-25
"""

from pathlib import Path
from typing import Dict


class SystemValidator:
    """Валидатор системы СЛК - проверка целостности и корректности"""
    
    def __init__(self, base_path: str = "."):
        """
        Инициализация валидатора системы
        
        Args:
            base_path: Базовый путь к проекту СЛК
        """
        self.base_path = Path(base_path)
    
    def validate_system(self) -> Dict:
        """
        Комплексная валидация системы СЛК
        
        Returns:
            Словарь с результатами валидации
        """
        issues = []
        components_checked = 0
        files_checked = 0
        
        # Проверка основных директорий
        required_dirs = ["modules", "tools"]
        for dir_name in required_dirs:
            components_checked += 1
            if not (self.base_path / dir_name).exists():
                issues.append({
                    "type": "missing_directory",
                    "severity": "high",
                    "description": f"Отсутствует директория: {dir_name}",
                    "fix_suggestion": f"Создать директорию {dir_name}"
                })
        
        # Проверка основных файлов
        required_files = [
            ("manifest.json", "high", "Основной манифест системы"),
            ("VERSION", "medium", "Файл версии"),
            ("README.md", "low", "Документация проекта")
        ]
        
        for file_path, severity, description in required_files:
            files_checked += 1
            if not (self.base_path / file_path).exists():
                issues.append({
                    "type": "missing_file",
                    "severity": severity,
                    "description": f"Отсутствует файл: {file_path}",
                    "details": description,
                    "fix_suggestion": f"Создать файл {file_path}"
                })
        
        # Проверка CLI
        cli_files = [
            "tools/scripts/slc_cli.py"
        ]
        
        for cli_file in cli_files:
            files_checked += 1
            if not (self.base_path / cli_file).exists():
                issues.append({
                    "type": "missing_cli",
                    "severity": "medium",
                    "description": f"Отсутствует CLI файл: {cli_file}",
                    "fix_suggestion": "Восстановить CLI файлы"
                })
        
        # Проверка модульной структуры CLI
        cli_modules_path = self.base_path / "tools" / "cli_modules"
        cli_dirs = ["core", "commands", "common"]
        
        for cli_dir in cli_dirs:
            components_checked += 1
            if not (cli_modules_path / cli_dir).exists():
                issues.append({
                    "type": "missing_cli_module",
                    "severity": "medium",
                    "description": f"Отсутствует модуль CLI: {cli_dir}",
                    "fix_suggestion": f"Создать директорию tools/cli_modules/{cli_dir}"
                })
        
        # Проверка шаблонов
        components_checked += 1
        if not self._check_templates_available():
            issues.append({
                "type": "missing_templates",
                "severity": "high",
                "description": "Нет доступных шаблонов в системе",
                "fix_suggestion": "Добавить шаблоны в директорию modules/"
            })
        
        return {
            "is_valid": len(issues) == 0,
            "components_checked": components_checked,
            "files_checked": files_checked,
            "issues": issues
        }
    
    def _check_templates_available(self) -> bool:
        """Проверка наличия шаблонов в системе"""
        modules_path = self.base_path / "modules"
        if not modules_path.exists():
            return False
        
        # Ищем JSON файлы в modules
        json_files = list(modules_path.rglob("*.json"))
        return len(json_files) > 0
    
    def fix_issues(self, issues: list) -> Dict:
        """
        Попытка автоматического исправления проблем
        
        Args:
            issues: Список проблем для исправления
            
        Returns:
            Результат исправления
        """
        fixed_count = 0
        remaining_issues = []
        
        for issue in issues:
            if self._try_fix_issue(issue):
                fixed_count += 1
            else:
                remaining_issues.append(issue)
        
        return {
            "success": fixed_count == len(issues),
            "fixed_count": fixed_count,
            "total_count": len(issues),
            "remaining_issues": remaining_issues
        }
    
    def _try_fix_issue(self, issue: Dict) -> bool:
        """Попытка исправить конкретную проблему"""
        issue_type = issue.get("type")
        
        try:
            if issue_type == "missing_directory":
                # Создаем отсутствующую директорию
                dir_name = issue["description"].split(": ")[1]
                (self.base_path / dir_name).mkdir(parents=True, exist_ok=True)
                return True
                
            elif issue_type == "missing_file":
                # Создаем базовые файлы
                file_path = issue["description"].split(": ")[1]
                full_path = self.base_path / file_path
                
                if file_path == "VERSION":
                    full_path.write_text("3.0.0\n")
                    return True
                elif file_path == "README.md":
                    full_path.write_text("# Smart Layered Context\n\nСистема управления контекстом разработки.\n")
                    return True
                elif file_path == "manifest.json":
                    import json
                    manifest = {
                        "name": "Smart Layered Context",
                        "version": "4.1.0",
                        "type": "context_system",
                        "description": "Система управления контекстом разработки",
                        "created": "2025-06-09"
                    }
                    full_path.write_text(json.dumps(manifest, indent=2))
                    return True
                    
        except Exception:
            pass
        
        return False
    
    def validate_cli_structure(self) -> Dict[str, bool]:
        """
        Валидация модульной структуры CLI
        
        Returns:
            Результаты проверки модульной структуры
        """
        results = {}
        cli_modules_path = self.base_path / "tools" / "cli_modules"
        
        # Основные директории
        results["cli_modules_root"] = cli_modules_path.exists()
        results["core_dir"] = (cli_modules_path / "core").exists()
        results["commands_dir"] = (cli_modules_path / "commands").exists()
        results["common_dir"] = (cli_modules_path / "common").exists()
        
        # Основные файлы
        results["template_manager"] = (cli_modules_path / "core" / "template_manager.py").exists()
        results["base_command"] = (cli_modules_path / "common" / "base_command.py").exists()
        results["template_commands"] = (cli_modules_path / "commands" / "template_commands.py").exists()
        
        # Инициализационные файлы
        results["root_init"] = (cli_modules_path / "__init__.py").exists()
        results["core_init"] = (cli_modules_path / "core" / "__init__.py").exists()
        results["commands_init"] = (cli_modules_path / "commands" / "__init__.py").exists()
        results["common_init"] = (cli_modules_path / "common" / "__init__.py").exists()
        
        return results
    
    def get_system_health_score(self) -> float:
        """
        Получить общую оценку здоровья системы
        
        Returns:
            Оценка от 0.0 до 1.0 (1.0 = отличное состояние)
        """
        validation_results = self.validate_system()
        cli_results = self.validate_cli_structure()
        
        # Объединяем все результаты
        all_results = {**validation_results, **cli_results}
        
        # Подсчитываем процент успешных проверок
        total_checks = len(all_results)
        passed_checks = sum(1 for result in all_results.values() if result)
        
        return passed_checks / total_checks if total_checks > 0 else 0.0
    
    def get_critical_issues(self) -> list:
        """
        Получить список критических проблем системы
        
        Returns:
            Список критических проблем, требующих немедленного внимания
        """
        issues = []
        validation_results = self.validate_system()
        
        # Критические файлы и директории
        critical_checks = {
            "manifest_exist": "Отсутствует .context/manifest.json",
            "modules_exist": "Отсутствует директория .context/modules/", 
            "tools_exist": "Отсутствует директория .context/tools/",
            "templates_available": "Нет доступных шаблонов в .context/modules/"
        }
        
        for check, description in critical_checks.items():
            if not validation_results.get(check, False):
                issues.append(description)
        
        return issues
    
    def get_recommendations(self) -> list:
        """
        Получить рекомендации по улучшению системы
        
        Returns:
            Список рекомендаций для улучшения системы
        """
        recommendations = []
        validation_results = self.validate_system()
        cli_results = self.validate_cli_structure()
        
        # Рекомендации по основной структуре
        if not validation_results.get("standards_exist", False):
            recommendations.append("Создать файл modules/core/standards.json с стандартами разработки")
        
        if not validation_results.get("project_exist", False):
            recommendations.append("Создать файл modules/core/project.json с информацией о проекте")
        
        # Рекомендации по CLI
        if not validation_results.get("cli_new_exist", False):
            recommendations.append("Завершить рефакторинг CLI - создать модульную версию")
        
        if not cli_results.get("template_manager", False):
            recommendations.append("Создать модуль template_manager.py для управления шаблонами")
        
        # Рекомендации по шаблонам
        if not validation_results.get("templates_available", False):
            recommendations.append("Добавить шаблоны в директорию modules/")
        
        return recommendations
    
    def generate_health_report(self) -> Dict:
        """
        Сгенерировать полный отчет о состоянии системы
        
        Returns:
            Подробный отчет о состоянии системы
        """
        validation_results = self.validate_system()
        cli_results = self.validate_cli_structure()
        health_score = self.get_system_health_score()
        critical_issues = self.get_critical_issues()
        recommendations = self.get_recommendations()
        
        return {
            "health_score": health_score,
            "health_grade": self._get_health_grade(health_score),
            "validation_results": validation_results,
            "cli_structure_results": cli_results,
            "critical_issues": critical_issues,
            "recommendations": recommendations,
            "summary": {
                "total_checks": len(validation_results) + len(cli_results),
                "passed_checks": sum(1 for v in validation_results.values() if v) + 
                               sum(1 for v in cli_results.values() if v),
                "critical_issues_count": len(critical_issues),
                "recommendations_count": len(recommendations)
            }
        }
    
    def _get_health_grade(self, score: float) -> str:
        """
        Получить текстовую оценку здоровья системы
        
        Args:
            score: Численная оценка (0.0 - 1.0)
            
        Returns:
            Текстовая оценка
        """
        if score >= 0.9:
            return "Отлично"
        elif score >= 0.7:
            return "Хорошо"
        elif score >= 0.5:
            return "Удовлетворительно"
        elif score >= 0.3:
            return "Плохо"
        else:
            return "Критично" 