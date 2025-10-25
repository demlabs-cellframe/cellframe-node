"""
ProjectGenerator - модуль для создания проектов из шаблонов СЛК
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
import time
from datetime import datetime


class ProjectGenerator:
    """Генератор проектов из шаблонов СЛК"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path).resolve()
        self.templates_path = self.base_path / "modules"
    
    def create_project(self, template_path: str, project_name: str, 
                      output_dir: str = ".", force: bool = False) -> Dict[str, Any]:
        """
        Создание проекта из шаблона
        
        Args:
            template_path: Путь к шаблону относительно templates/
            project_name: Имя создаваемого проекта
            output_dir: Директория для создания проекта
            force: Перезаписать существующий проект
            
        Returns:
            Dict с результатом операции
        """
        try:
            # Загружаем шаблон
            template_info = self._load_template(template_path)
            if not template_info:
                return {
                    "success": False,
                    "error": f"Шаблон не найден: {template_path}"
                }
            
            # Создаем целевую директорию
            output_path = Path(output_dir) / project_name
            if output_path.exists() and not force:
                return {
                    "success": False,
                    "error": f"Директория уже существует: {output_path}"
                }
            
            if output_path.exists() and force:
                shutil.rmtree(output_path)
            
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Генерируем проект
            result = self._generate_project_structure(template_info, output_path, project_name)
            
            if result["success"]:
                # Создаем метаданные проекта
                self._create_project_metadata(output_path, template_path, project_name, template_info)
                
                return {
                    "success": True,
                    "project_path": str(output_path),
                    "template_name": template_info.get("template_info", {}).get("name", "Unknown"),
                    "files_created": result.get("files_created", 0)
                }
            else:
                return result
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка создания проекта: {str(e)}"
            }
    
    def _load_template(self, template_path: str) -> Optional[Dict[str, Any]]:
        """Загрузка шаблона из файла"""
        full_path = self.templates_path / template_path
        
        if not full_path.exists():
            return None
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    def _generate_project_structure(self, template_info: Dict[str, Any], 
                                  output_path: Path, project_name: str) -> Dict[str, Any]:
        """Генерация структуры проекта из шаблона"""
        files_created = 0
        
        try:
            # Получаем структуру файлов из шаблона
            structure = template_info.get("structure", {})
            
            # Создаем файлы и директории
            for item_path, item_config in structure.items():
                if isinstance(item_config, dict):
                    # Это директория
                    dir_path = output_path / item_path
                    dir_path.mkdir(parents=True, exist_ok=True)
                    
                    # Обрабатываем содержимое директории
                    for sub_item, sub_config in item_config.items():
                        self._create_file_from_template(
                            dir_path / sub_item, 
                            sub_config, 
                            project_name, 
                            template_info
                        )
                        files_created += 1
                else:
                    # Это файл
                    self._create_file_from_template(
                        output_path / item_path, 
                        item_config, 
                        project_name, 
                        template_info
                    )
                    files_created += 1
            
            # Создаем основные файлы проекта если их нет
            self._ensure_basic_files(output_path, project_name, template_info)
            
            return {
                "success": True,
                "files_created": files_created
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка генерации структуры: {str(e)}"
            }
    
    def _create_file_from_template(self, file_path: Path, content: Any, 
                                 project_name: str, template_info: Dict[str, Any]):
        """Создание файла из шаблонного содержимого"""
        # Создаем директорию для файла если нужно
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if isinstance(content, str):
            # Простой текстовый контент с подстановкой переменных
            processed_content = self._process_template_variables(
                content, project_name, template_info
            )
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)
        
        elif isinstance(content, dict) and content.get("type") == "template":
            # Шаблонный файл с метаданными
            template_content = content.get("content", "")
            processed_content = self._process_template_variables(
                template_content, project_name, template_info
            )
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)
        
        else:
            # Базовый файл
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {project_name}\n\nСоздано из шаблона: {template_info.get('name', 'Unknown')}\n")
    
    def _process_template_variables(self, content: str, project_name: str, 
                                  template_info: Dict[str, Any]) -> str:
        """Обработка переменных в шаблонном контенте"""
        variables = {
            "PROJECT_NAME": project_name,
            "PROJECT_NAME_LOWER": project_name.lower(),
            "PROJECT_NAME_UPPER": project_name.upper(),
            "TEMPLATE_NAME": template_info.get("template_info", {}).get("name", "Unknown"),
            "TEMPLATE_VERSION": template_info.get("version", "1.0.0"),
            "CREATION_DATE": datetime.now().strftime("%Y-%m-%d"),
            "CREATION_DATETIME": datetime.now().isoformat()
        }
        
        processed = content
        for var, value in variables.items():
            processed = processed.replace(f"{{{var}}}", str(value))
            processed = processed.replace(f"${var}", str(value))
        
        return processed
    
    def _ensure_basic_files(self, output_path: Path, project_name: str, 
                          template_info: Dict[str, Any]):
        """Создание базовых файлов проекта если они отсутствуют"""
        
        # README.md
        readme_path = output_path / "README.md"
        if not readme_path.exists():
            template_name = template_info.get("template_info", {}).get("name", "Unknown")
            template_description = template_info.get("template_info", {}).get("description", "Описание проекта")
            
            readme_content = f"""# {project_name}

Проект создан из шаблона СЛК: **{template_name}**

## Описание

{template_description}

## Структура проекта

Этот проект создан с использованием системы Smart Layered Context (СЛК).

## Использование

[Инструкции по использованию проекта]

---

*Создано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Шаблон: {template_name} v{template_info.get('version', '1.0.0')}*
"""
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
    
    def _create_project_metadata(self, output_path: Path, template_path: str, 
                               project_name: str, template_info: Dict[str, Any]):
        """Создание метаданных проекта"""
        metadata = {
            "project_name": project_name,
            "template_path": template_path,
            "template_name": template_info.get("template_info", {}).get("name", "Unknown"),
            "template_version": template_info.get("version", "1.0.0"),
            "created_at": datetime.now().isoformat(),
            "slc_version": "3.0.0",
            "generator_version": "1.0.0"
        }
        
        metadata_path = output_path / ".slc_project.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def list_available_templates(self) -> Dict[str, List[str]]:
        """Получение списка доступных шаблонов"""
        templates = {}
        
        if not self.templates_path.exists():
            return templates
        
        for root, dirs, files in os.walk(self.templates_path):
            for file in files:
                if file.endswith('.json'):
                    rel_path = Path(root).relative_to(self.templates_path)
                    category = str(rel_path) if str(rel_path) != '.' else 'root'
                    
                    if category not in templates:
                        templates[category] = []
                    
                    templates[category].append(str(rel_path / file))
        
        return templates 