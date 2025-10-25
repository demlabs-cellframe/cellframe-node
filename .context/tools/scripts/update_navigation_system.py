#!/usr/bin/env python3
"""
Автоматическое обновление navigation_system во всех файлах СЛК
Приводит к единому стандарту согласно navigation_system_standard.json
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

class NavigationSystemUpdater:
    """Обновляет navigation_system во всех JSON файлах СЛК"""
    
    def __init__(self, root_path: str = ".context"):
        self.root = Path(root_path).resolve()
        self.dry_run = False
        self.updated_files = []
        self.errors = []
        
        # Единый стандарт navigation_system
        self.standard_template = {
            "purpose": "",
            "recovery_path": ".context/manifest.json",
            "current_file": "",
            "file_role": "",
            "related_files": [],
            "quick_navigation": {
                "🏠 Главная": ".context/manifest.json - главный навигатор системы",
                "📋 Задачи": ".context/tasks/ - управление задачами",
                "🛠️ CLI": ".context/tools/scripts/slc_cli.py - автоматизация"
            },
            "usage_hint": "",
            "ai_context": ""
        }
        
        # Роли файлов
        self.file_roles = {
            "manifest.json": "MASTER_MANIFEST",
            "core/manifest.json": "CORE_MANIFEST", 
            "core/standards.json": "CORE_STANDARDS",
            "core/project.json": "CORE_PROJECT",
            "ai_ml/": "AI_ML_TEMPLATE",
            "languages/": "LANGUAGE_TEMPLATE",
            "methodologies/": "METHODOLOGY_TEMPLATE",
            "tools/": "TOOLS_TEMPLATE",
            "projects/": "PROJECT_TEMPLATE",
            "tasks/": "TASK_DEFINITION"
        }
    
    def determine_file_role(self, file_path: Path) -> str:
        """Определить роль файла на основе пути"""
        relative_path = file_path.relative_to(self.root)
        path_str = str(relative_path)
        
        # Точные совпадения
        for pattern, role in self.file_roles.items():
            if pattern in path_str:
                return role
                
        return "UNKNOWN"
    
    def generate_purpose(self, file_path: Path) -> str:
        """Генерировать описание назначения файла"""
        relative_path = file_path.relative_to(self.root)
        path_str = str(relative_path)
        
        if "manifest.json" in path_str and "core" not in path_str:
            return "Главный манифест Smart Layered Context системы"
        elif "core/manifest.json" in path_str:
            return "Манифест core модулей СЛК системы"
        elif "core/standards.json" in path_str:
            return "Стандарты разработки и coding guidelines"
        elif "core/project.json" in path_str:
            return "Информация о проекте СЛК"
        elif "ai_ml/" in path_str:
            return "Шаблон для AI/ML разработки"
        elif "languages/" in path_str:
            return "Шаблон языка программирования"
        elif "methodologies/" in path_str:
            return "Методология разработки"
        elif "tools/" in path_str:
            return "Инструмент разработки"
        elif "projects/" in path_str:
            return "Специализированный проект"
        elif "tasks/" in path_str:
            if "completed/" in path_str:
                return "Завершенная задача"
            else:
                return "Определение задачи"
        else:
            return f"Файл СЛК: {relative_path.name}"
    
    def generate_related_files(self, file_path: Path) -> List[str]:
        """Генерировать список связанных файлов"""
        relative_path = file_path.relative_to(self.root)
        related = []
        
        # Всегда добавляем главный манифест если это не он сам
        if str(relative_path) != "manifest.json":
            related.append(".context/manifest.json")
            
        # Core файлы связаны друг с другом
        if "core/" in str(relative_path):
            core_files = [
                ".context/modules/core/manifest.json",
                ".context/modules/core/standards.json", 
                ".context/modules/core/project.json"
            ]
            for cf in core_files:
                if cf not in str(file_path):
                    related.append(cf)
        
        return related
    
    def generate_quick_navigation(self, file_path: Path) -> Dict[str, str]:
        """Генерировать быструю навигацию"""
        navigation = {
            "🏠 Главная": ".context/manifest.json - главный навигатор системы"
        }
        
        relative_path = file_path.relative_to(self.root)
        
        # Для core файлов
        if "core/" in str(relative_path):
            navigation.update({
                "📋 Core": ".context/modules/core/manifest.json - манифест core модулей",
                "📐 Стандарты": ".context/modules/core/standards.json - стандарты разработки",
                "🏗️ Проект": ".context/modules/core/project.json - информация о проекте"
            })
        
        # Для задач
        if "tasks/" in str(relative_path):
            navigation["📋 Задачи"] = ".context/tasks/ - управление задачами"
            
        # CLI всегда доступен
        navigation["🛠️ CLI"] = ".context/tools/scripts/slc_cli.py - автоматизация"
        
        return navigation
    
    def generate_usage_hint(self, file_path: Path) -> str:
        """Генерировать подсказку по использованию"""
        relative_path = file_path.relative_to(self.root)
        path_str = str(relative_path)
        
        if "manifest.json" in path_str and "core" not in path_str:
            return "./slc load-context 'ваш запрос' для автоматической загрузки контекста"
        elif "core/manifest.json" in path_str:
            return "./slc templates для просмотра всех доступных шаблонов"
        elif "core/standards.json" in path_str:
            return "Этот файл содержит стандарты кодирования и best practices"
        elif "ai_ml/" in path_str:
            return "./slc create ai_ml/[шаблон].json [проект] для создания AI/ML проекта"
        elif "tasks/" in path_str:
            return "./slc list для просмотра всех задач проекта"
        else:
            return f"./slc info {relative_path} для подробной информации"
    
    def create_standard_navigation_system(self, file_path: Path) -> Dict[str, Any]:
        """Создать стандартную navigation_system секцию"""
        relative_path = file_path.relative_to(self.root)
        
        navigation_system = {
            "purpose": self.generate_purpose(file_path),
            "recovery_path": ".context/manifest.json",
            "current_file": f".context/{relative_path}",
            "file_role": self.determine_file_role(file_path),
            "related_files": self.generate_related_files(file_path),
            "quick_navigation": self.generate_quick_navigation(file_path),
            "usage_hint": self.generate_usage_hint(file_path),
            "ai_context": f"Файл СЛК системы: {relative_path.name}"
        }
        
        return navigation_system
    
    def find_json_files(self) -> List[Path]:
        """Найти все JSON файлы в системе СЛК"""
        json_files = []
        
        # Исключаем определенные директории
        exclude_dirs = {'.git', '__pycache__', 'node_modules', '.pytest_cache'}
        
        for file_path in self.root.rglob("*.json"):
            # Проверяем, что файл не в исключенных директориях
            if not any(excluded in file_path.parts for excluded in exclude_dirs):
                json_files.append(file_path)
        
        return sorted(json_files)
    
    def update_file(self, file_path: Path) -> bool:
        """Обновить navigation_system в файле"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Создаем новую navigation_system
            new_navigation = self.create_standard_navigation_system(file_path)
            
            # Сохраняем некоторые существующие данные если они есть
            if "navigation_system" in data:
                old_nav = data["navigation_system"]
                
                # Сохраняем custom purpose если он более информативен
                if "purpose" in old_nav and len(old_nav["purpose"]) > len(new_navigation["purpose"]):
                    new_navigation["purpose"] = old_nav["purpose"]
                
                # Сохраняем дополнительные related_files
                if "related_files" in old_nav:
                    existing_related = set(new_navigation["related_files"])
                    for rf in old_nav["related_files"]:
                        if rf not in existing_related:
                            new_navigation["related_files"].append(rf)
            
            # Обновляем navigation_system
            data["navigation_system"] = new_navigation
            
            if not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.updated_files.append(str(file_path))
            return True
            
        except Exception as e:
            error_msg = f"Ошибка обновления {file_path}: {e}"
            self.errors.append(error_msg)
            return False
    
    def run(self, dry_run: bool = False) -> Dict[str, Any]:
        """Запустить обновление всех файлов"""
        self.dry_run = dry_run
        self.updated_files = []
        self.errors = []
        
        json_files = self.find_json_files()
        
        print(f"🔍 Найдено JSON файлов: {len(json_files)}")
        if dry_run:
            print("🧪 РЕЖИМ ТЕСТИРОВАНИЯ - изменения не будут сохранены")
        
        success_count = 0
        for file_path in json_files:
            if self.update_file(file_path):
                success_count += 1
                print(f"✅ Обновлен: {file_path.relative_to(self.root)}")
            else:
                print(f"❌ Ошибка: {file_path.relative_to(self.root)}")
        
        result = {
            "total_files": len(json_files),
            "updated_files": success_count,
            "errors": len(self.errors),
            "updated_list": self.updated_files,
            "error_list": self.errors,
            "dry_run": dry_run
        }
        
        return result

def main():
    parser = argparse.ArgumentParser(description="Обновление navigation_system во всех файлах СЛК")
    parser.add_argument("--dry-run", action="store_true", help="Режим тестирования без изменений")
    parser.add_argument("--root", default=".context", help="Корневая директория СЛК")
    
    args = parser.parse_args()
    
    updater = NavigationSystemUpdater(args.root)
    result = updater.run(dry_run=args.dry_run)
    
    print(f"\n📊 РЕЗУЛЬТАТЫ:")
    print(f"   Всего файлов: {result['total_files']}")
    print(f"   Обновлено: {result['updated_files']}")
    print(f"   Ошибок: {result['errors']}")
    
    if result['errors'] > 0:
        print(f"\n❌ ОШИБКИ:")
        for error in result['error_list']:
            print(f"   {error}")
    
    if not args.dry_run and result['updated_files'] > 0:
        print(f"\n✅ Navigation system успешно стандартизирован!")
    elif args.dry_run:
        print(f"\n🧪 Тестирование завершено. Используйте без --dry-run для применения изменений.")

if __name__ == "__main__":
    main() 