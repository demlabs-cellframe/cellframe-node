#!/usr/bin/env python3
"""
Команды развертывания

Реализует команды:
- create-archive: Создание архива для развертывания
- export-readme: Экспорт README для Redmine

Версия: 1.0.0
Создано: 2025-01-16
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Добавляем путь к модулям
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..base_command import ContextAwareCommand


class CreateArchiveCommand(ContextAwareCommand):
    """Команда создания архива для развертывания"""
    
    def __init__(self, base_path: str):
        super().__init__(base_path)
        self.context_dir = Path(base_path) / ".context"
    
    @property
    def name(self):
        return "create-archive"
    
    @property
    def description(self):
        return "Создать архив для развертывания"
    
    def execute_with_context(self, args):
        """Выполнить создание архива"""
        try:
            script_path = Path(self.context_dir) / "tools" / "deployment" / "create_deployment_archive.sh"
            
            if not script_path.exists():
                return {
                    "success": False,
                    "error": f"Скрипт не найден: {script_path}"
                }
                
            # Выполнить скрипт
            result = subprocess.run([str(script_path)], 
                                  capture_output=True, 
                                  text=True, 
                                  cwd=self.context_dir.parent)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "status": "АРХИВ СОЗДАН",
                    "message": "Архив успешно создан",
                    "output": result.stdout,
                    "ai_recommendations": [
                        "Архивы созданы в папке ../releases/",
                        "Готовы к распространению",
                        "Содержат чистую структуру без локальных данных"
                    ],
                    "next_commands": [
                        "./slc status - Проверить состояние системы",
                        "./slc validate - Валидировать перед релизом"
                    ]
                }
            else:
                return {
                    "success": False,
                    "error": f"Ошибка создания архива: {result.stderr}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка выполнения команды: {e}"
            }


class ExportReadmeCommand(ContextAwareCommand):
    """Команда экспорта README для Redmine"""
    
    def __init__(self, base_path: str):
        super().__init__(base_path)
        self.context_dir = Path(base_path) / ".context"
    
    @property
    def name(self):
        return "export-readme"
    
    @property
    def description(self):
        return "Экспорт README для Redmine (Textile/Markdown)"
    
    def add_arguments(self, parser):
        # Добавляем аргументы родительского класса (JSON контекст)
        super().add_arguments(parser)
        
        parser.add_argument(
            "--format", 
            choices=["textile", "markdown"], 
            default="textile",
            help="Формат экспорта (textile/markdown)"
        )
        parser.add_argument(
            "--output", 
            type=str,
            help="Выходной файл (по умолчанию README_redmine.{format})"
        )
        parser.add_argument(
            "--include-toc", 
            action="store_true",
            help="Включить автоматическое оглавление"
        )
        parser.add_argument(
            "--project-info", 
            action="store_true",
            help="Включить информацию о проекте из manifest.json"
        )
    
    def get_default_context_files(self):
        return [
            ".context/manifest.json",
            "README.md",
            ".context/modules/core/project.json"
        ]
    
    def get_context_summary(self, execution_result):
        """Получить краткое описание результата экспорта"""
        if execution_result.get("success"):
            format_type = execution_result.get("format", "unknown")
            return f"README экспортирован в формате {format_type} для Redmine"
        return "Ошибка экспорта README"
    
    def get_recommended_actions(self, execution_result):
        """Получить рекомендуемые действия после экспорта"""
        if execution_result.get("success"):
            return [
                "Скопировать содержимое файла в Redmine Wiki",
                "Проверить корректность отображения разметки",
                "При необходимости настроить ссылки на внешние ресурсы",
                "Обновить оглавление если используется TOC"
            ]
        return [
            "Проверить существование README.md",
            "Убедиться в корректности manifest.json",
            "Проверить права доступа к выходной директории"
        ]
    
    def get_next_commands(self, execution_result):
        """Получить следующие команды для выполнения"""
        if execution_result.get("success"):
            return [
                "./slc validate - Проверить целостность системы",
                "./slc status - Показать статус проекта"
            ]
        return [
            "./slc status - Проверить состояние системы",
            "./slc help export-readme - Показать справку по команде"
        ]
    
    def execute_with_context(self, args):
        """Выполнить экспорт README с контекстом"""
        try:
            # Определить входной файл README
            readme_path = self._find_readme_file()
            if not readme_path:
                return {
                    "success": False,
                    "error": "README.md не найден в проекте",
                    "format": args.format
                }
            
            # Прочитать содержимое README
            content = self._read_readme(readme_path)
            
            # Получить информацию о проекте если запрошено
            project_info = None
            if args.project_info:
                project_info = self._get_project_info()
            
            # Конвертировать в нужный формат
            if args.format == "textile":
                converted_content = self._convert_to_textile(content, project_info, args.include_toc)
                file_extension = "textile"
            else:  # markdown
                converted_content = self._enhance_markdown(content, project_info, args.include_toc)
                file_extension = "md"
            
            # Определить выходной файл
            output_file = args.output or f"README_redmine.{file_extension}"
            output_path = Path(output_file)
            
            # Записать результат
            output_path.write_text(converted_content, encoding='utf-8')
            
            return {
                "success": True,
                "message": f"README экспортирован в формате {args.format}",
                "format": args.format,
                "input_file": str(readme_path),
                "output_file": str(output_path),
                "size": len(converted_content),
                "lines": len(converted_content.splitlines()),
                "includes_toc": args.include_toc,
                "includes_project_info": args.project_info
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка экспорта README: {e}",
                "format": args.format
            }
    
    def _find_readme_file(self):
        """Найти файл README в проекте"""
        # Поиск в корне проекта
        project_root = self.context_dir.parent
        
        for readme_name in ["README.md", "readme.md", "Readme.md", "README.rst", "readme.rst"]:
            readme_path = project_root / readme_name
            if readme_path.exists():
                return readme_path
        
        # Поиск в .context/docs
        docs_path = self.context_dir / "docs"
        if docs_path.exists():
            for readme_name in ["README.md", "readme.md", "project_overview.md"]:
                readme_path = docs_path / readme_name
                if readme_path.exists():
                    return readme_path
        
        return None
    
    def _read_readme(self, readme_path):
        """Прочитать и обработать README файл"""
        content = readme_path.read_text(encoding='utf-8')
        
        # Удалить служебные комментарии если есть
        content = re.sub(r'<!-- .* -->', '', content, flags=re.DOTALL)
        
        return content.strip()
    
    def _get_project_info(self):
        """Получить информацию о проекте из manifest.json"""
        try:
            manifest_path = self.context_dir / "manifest.json"
            if manifest_path.exists():
                manifest_data = json.loads(manifest_path.read_text(encoding='utf-8'))
                
                project_info = {
                    "name": manifest_data.get("name", "Unknown Project"),
                    "version": manifest_data.get("version", "Unknown"),
                    "description": manifest_data.get("description", ""),
                    "author": manifest_data.get("system_info", {}).get("author", ""),
                    "created": manifest_data.get("created", ""),
                    "type": manifest_data.get("type", "")
                }
                
                return project_info
        except Exception:
            pass
        
        return None
    
    def _convert_to_textile(self, content, project_info=None, include_toc=False):
        """Конвертировать Markdown в Textile для Redmine"""
        
        # Добавить информацию о проекте если есть
        textile_content = ""
        
        if project_info:
            textile_content += f"h1. {project_info['name']}\n\n"
            if project_info.get('description'):
                textile_content += f"_{project_info['description']}_\n\n"
            
            textile_content += "*Информация о проекте:*\n"
            if project_info.get('version'):
                textile_content += f"* Версия: *{project_info['version']}*\n"
            if project_info.get('author'):
                textile_content += f"* Автор: {project_info['author']}\n"
            if project_info.get('type'):
                textile_content += f"* Тип: {project_info['type']}\n"
            
            textile_content += f"* Экспортировано: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            textile_content += "---\n\n"
        
        # Конвертировать Markdown в Textile
        
        # Заголовки
        content = re.sub(r'^# (.*)', r'h1. \1', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.*)', r'h2. \1', content, flags=re.MULTILINE)
        content = re.sub(r'^### (.*)', r'h3. \1', content, flags=re.MULTILINE)
        content = re.sub(r'^#### (.*)', r'h4. \1', content, flags=re.MULTILINE)
        content = re.sub(r'^##### (.*)', r'h5. \1', content, flags=re.MULTILINE)
        content = re.sub(r'^###### (.*)', r'h6. \1', content, flags=re.MULTILINE)
        
        # Жирный текст
        content = re.sub(r'\*\*(.*?)\*\*', r'*\1*', content)
        content = re.sub(r'__(.*?)__', r'*\1*', content)
        
        # Курсив  
        content = re.sub(r'\*(.*?)\*', r'_\1_', content)
        content = re.sub(r'_(.*?)_', r'_\1_', content)
        
        # Код (inline)
        content = re.sub(r'`(.*?)`', r'@\1@', content)
        
        # Блоки кода
        content = re.sub(r'^```(\w+)?\n(.*?)^```', r'<pre><code class="\1">\n\2</code></pre>', content, flags=re.MULTILINE | re.DOTALL)
        
        # Списки (маркированные)
        content = re.sub(r'^- (.*)', r'* \1', content, flags=re.MULTILINE)
        content = re.sub(r'^\* (.*)', r'* \1', content, flags=re.MULTILINE)
        
        # Списки (нумерованные)
        content = re.sub(r'^(\d+)\. (.*)', r'# \2', content, flags=re.MULTILINE)
        
        # Ссылки
        content = re.sub(r'\[(.*?)\]\((.*?)\)', r'"\1":\2', content)
        
        # Изображения
        content = re.sub(r'!\[(.*?)\]\((.*?)\)', r'!\2(\1)!', content)
        
        # Горизонтальная линия
        content = re.sub(r'^---+', r'---', content, flags=re.MULTILINE)
        
        # Цитаты
        content = re.sub(r'^> (.*)', r'bq. \1', content, flags=re.MULTILINE)
        
        # Таблицы (базовая поддержка)
        content = re.sub(r'\|(.*?)\|', lambda m: '|' + m.group(1).replace('|', '|') + '|', content)
        
        # Добавить оглавление если нужно
        if include_toc:
            toc = self._generate_textile_toc(content)
            textile_content += toc + "\n\n"
        
        textile_content += content
        return textile_content
    
    def _enhance_markdown(self, content, project_info=None, include_toc=False):
        """Улучшить Markdown для Redmine"""
        
        enhanced_content = ""
        
        # Добавить информацию о проекте если есть
        if project_info:
            enhanced_content += f"# {project_info['name']}\n\n"
            if project_info.get('description'):
                enhanced_content += f"_{project_info['description']}_\n\n"
            
            enhanced_content += "**Информация о проекте:**\n\n"
            if project_info.get('version'):
                enhanced_content += f"- **Версия:** {project_info['version']}\n"
            if project_info.get('author'):
                enhanced_content += f"- **Автор:** {project_info['author']}\n"
            if project_info.get('type'):
                enhanced_content += f"- **Тип:** {project_info['type']}\n"
            
            enhanced_content += f"- **Экспортировано:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            enhanced_content += "---\n\n"
        
        # Добавить оглавление если нужно
        if include_toc:
            toc = self._generate_markdown_toc(content)
            enhanced_content += toc + "\n\n"
        
        # Улучшить существующий контент
        # Добавить якоря для заголовков
        content = re.sub(r'^(#{1,6}) (.*)$', lambda m: f"{m.group(1)} {m.group(2)} {{#{''.join(m.group(2).lower().split())}}}", content, flags=re.MULTILINE)
        
        enhanced_content += content
        return enhanced_content
    
    def _generate_textile_toc(self, content):
        """Генерировать оглавление для Textile"""
        headers = re.findall(r'^h([1-6])\. (.*)$', content, flags=re.MULTILINE)
        
        if not headers:
            return ""
        
        toc = "h2. Оглавление\n\n"
        for level, title in headers:
            indent = "  " * (int(level) - 1)
            anchor = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '-').lower()
            toc += f"{indent}* \"#{title}\":{anchor}\n"
        
        return toc
    
    def _generate_markdown_toc(self, content):
        """Генерировать оглавление для Markdown"""
        headers = re.findall(r'^(#{1,6}) (.*)$', content, flags=re.MULTILINE)
        
        if not headers:
            return ""
        
        toc = "## Оглавление\n\n"
        for level_hash, title in headers:
            level = len(level_hash)
            indent = "  " * (level - 1)
            anchor = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '-').lower()
            toc += f"{indent}- [#{title}](#{anchor})\n"
        
        return toc


# Экспорт команды
def get_commands():
    """Возвращает список доступных команд"""
    return [CreateArchiveCommand, ExportReadmeCommand] 