#!/usr/bin/env python3
"""
Cellframe API Extractor
Автоматическое извлечение API функций из исходного кода Cellframe для документации
"""

import os
import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import argparse

@dataclass
class APIFunction:
    """Структура для хранения информации об API функции"""
    name: str
    signature: str
    return_type: str
    parameters: List[Dict[str, str]]
    file_path: str
    line_number: int
    comments: List[str]
    is_public: bool
    module: str

@dataclass
class APIModule:
    """Структура для хранения информации о модуле API"""
    name: str
    path: str
    functions: List[APIFunction]
    headers: List[str]
    description: str

class CellframeAPIExtractor:
    """Экстрактор API функций из исходного кода Cellframe"""
    
    def __init__(self, cellframe_root: str):
        self.cellframe_root = Path(cellframe_root)
        self.api_functions = []
        self.modules = {}
        
        # Паттерны для поиска функций
        self.function_patterns = [
            # C функции с префиксом dap_
            r'^\s*([a-zA-Z_][a-zA-Z0-9_*\s]*)\s+(dap_[a-zA-Z0-9_]+)\s*\(',
            # Публичные функции
            r'^\s*([a-zA-Z_][a-zA-Z0-9_*\s]*)\s+([a-zA-Z0-9_]+)\s*\(',
        ]
        
        # Директории для поиска
        self.search_dirs = [
            'cellframe-sdk/modules',
            'cellframe-sdk/dap-sdk/core/include',
            'cellframe-sdk/dap-sdk/crypto/include',
            'cellframe-sdk/dap-sdk/io/include',
            'python-cellframe/modules',
            'python-cellframe/include'
        ]
        
        # Расширения файлов для анализа
        self.file_extensions = ['.h', '.c', '.py']
        
    def extract_apis(self) -> Dict[str, APIModule]:
        """Извлекает все API функции из исходного кода"""
        print("🔍 Сканирование исходного кода Cellframe...")
        
        for search_dir in self.search_dirs:
            dir_path = self.cellframe_root / search_dir
            if dir_path.exists():
                print(f"📁 Анализ директории: {search_dir}")
                self._scan_directory(dir_path, search_dir)
            else:
                print(f"⚠️ Директория не найдена: {search_dir}")
        
        print(f"✅ Найдено {len(self.api_functions)} API функций в {len(self.modules)} модулях")
        return self.modules
    
    def _scan_directory(self, directory: Path, module_name: str):
        """Сканирует директорию на наличие API функций"""
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix in self.file_extensions:
                self._analyze_file(file_path, module_name)
    
    def _analyze_file(self, file_path: Path, module_name: str):
        """Анализирует файл на наличие API функций"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
            functions = self._extract_functions_from_content(content, lines, file_path, module_name)
            
            if functions:
                if module_name not in self.modules:
                    self.modules[module_name] = APIModule(
                        name=module_name,
                        path=str(file_path.parent),
                        functions=[],
                        headers=[],
                        description=f"API модуль {module_name}"
                    )
                
                self.modules[module_name].functions.extend(functions)
                self.api_functions.extend(functions)
                
                if file_path.suffix == '.h':
                    self.modules[module_name].headers.append(str(file_path))
                    
        except Exception as e:
            print(f"⚠️ Ошибка при анализе файла {file_path}: {e}")
    
    def _extract_functions_from_content(self, content: str, lines: List[str], 
                                      file_path: Path, module_name: str) -> List[APIFunction]:
        """Извлекает функции из содержимого файла"""
        functions = []
        
        for i, line in enumerate(lines):
            for pattern in self.function_patterns:
                match = re.match(pattern, line)
                if match:
                    func_info = self._parse_function(lines, i, file_path, module_name)
                    if func_info and self._is_public_api(func_info):
                        functions.append(func_info)
                        
        return functions
    
    def _parse_function(self, lines: List[str], line_num: int, 
                       file_path: Path, module_name: str) -> Optional[APIFunction]:
        """Парсит информацию о функции"""
        try:
            # Получаем полную сигнатуру функции
            signature_lines = []
            current_line = line_num
            
            # Ищем начало функции
            while current_line < len(lines):
                line = lines[current_line].strip()
                signature_lines.append(line)
                if '{' in line or ';' in line:
                    break
                current_line += 1
            
            full_signature = ' '.join(signature_lines)
            
            # Извлекаем имя функции
            func_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', full_signature)
            if not func_match:
                return None
                
            func_name = func_match.group(1)
            
            # Извлекаем тип возвращаемого значения
            return_type = self._extract_return_type(full_signature, func_name)
            
            # Извлекаем параметры
            parameters = self._extract_parameters(full_signature)
            
            # Извлекаем комментарии
            comments = self._extract_comments(lines, line_num)
            
            return APIFunction(
                name=func_name,
                signature=full_signature.replace('\n', ' ').strip(),
                return_type=return_type,
                parameters=parameters,
                file_path=str(file_path),
                line_number=line_num + 1,
                comments=comments,
                is_public=True,
                module=module_name
            )
            
        except Exception as e:
            print(f"⚠️ Ошибка при парсинге функции в строке {line_num}: {e}")
            return None
    
    def _extract_return_type(self, signature: str, func_name: str) -> str:
        """Извлекает тип возвращаемого значения"""
        # Убираем имя функции и параметры
        before_func = signature.split(func_name)[0].strip()
        return_type = before_func.split()[-1] if before_func.split() else 'void'
        return return_type
    
    def _extract_parameters(self, signature: str) -> List[Dict[str, str]]:
        """Извлекает параметры функции"""
        parameters = []
        
        # Находим содержимое скобок
        paren_match = re.search(r'\((.*?)\)', signature)
        if not paren_match:
            return parameters
            
        params_str = paren_match.group(1).strip()
        if not params_str or params_str == 'void':
            return parameters
        
        # Разбиваем параметры
        param_parts = params_str.split(',')
        
        for param in param_parts:
            param = param.strip()
            if param:
                # Простой парсинг: последнее слово - имя, остальное - тип
                parts = param.split()
                if len(parts) >= 2:
                    param_name = parts[-1].replace('*', '').replace('&', '')
                    param_type = ' '.join(parts[:-1])
                else:
                    param_name = param
                    param_type = 'unknown'
                
                parameters.append({
                    'name': param_name,
                    'type': param_type,
                    'description': ''
                })
        
        return parameters
    
    def _extract_comments(self, lines: List[str], line_num: int) -> List[str]:
        """Извлекает комментарии перед функцией"""
        comments = []
        
        # Ищем комментарии выше функции
        i = line_num - 1
        while i >= 0 and i >= line_num - 10:  # Максимум 10 строк выше
            line = lines[i].strip()
            if line.startswith('//') or line.startswith('/*') or line.startswith('*'):
                comments.insert(0, line)
            elif line and not line.startswith('#'):
                break
            i -= 1
        
        return comments
    
    def _is_public_api(self, func_info: APIFunction) -> bool:
        """Определяет, является ли функция публичным API"""
        # Критерии для публичного API
        public_criteria = [
            func_info.name.startswith('dap_'),
            func_info.name.startswith('cellframe_'),
            func_info.file_path.endswith('.h'),  # Заголовочные файлы
            'include' in func_info.file_path,
            not func_info.name.startswith('_'),  # Не приватные функции
        ]
        
        return any(public_criteria)
    
    def generate_documentation_json(self, output_file: str):
        """Генерирует JSON файл с документацией API"""
        doc_data = {
            'metadata': {
                'generator': 'Cellframe API Extractor',
                'version': '1.0.0',
                'timestamp': '2025-01-16T18:30:00Z',
                'total_functions': len(self.api_functions),
                'total_modules': len(self.modules)
            },
            'modules': {}
        }
        
        for module_name, module in self.modules.items():
            doc_data['modules'][module_name] = {
                'name': module.name,
                'path': module.path,
                'description': module.description,
                'headers': module.headers,
                'functions': [asdict(func) for func in module.functions]
            }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(doc_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Документация сохранена в {output_file}")
    
    def generate_markdown_summary(self, output_file: str):
        """Генерирует краткий отчет в формате Markdown"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Cellframe API Analysis Report\n\n")
            f.write(f"**Дата анализа:** 2025-01-16\n")
            f.write(f"**Всего функций:** {len(self.api_functions)}\n")
            f.write(f"**Всего модулей:** {len(self.modules)}\n\n")
            
            f.write("## Модули\n\n")
            for module_name, module in self.modules.items():
                f.write(f"### {module_name}\n")
                f.write(f"- **Путь:** `{module.path}`\n")
                f.write(f"- **Функций:** {len(module.functions)}\n")
                f.write(f"- **Заголовки:** {len(module.headers)}\n\n")
                
                if module.functions:
                    f.write("#### Функции:\n")
                    for func in module.functions[:5]:  # Показываем первые 5
                        f.write(f"- `{func.name}()` - {func.return_type}\n")
                    if len(module.functions) > 5:
                        f.write(f"- ... и еще {len(module.functions) - 5} функций\n")
                    f.write("\n")
        
        print(f"📄 Отчет сохранен в {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Cellframe API Extractor')
    parser.add_argument('--cellframe-root', default='.', 
                       help='Корневая директория Cellframe проекта')
    parser.add_argument('--output-json', default='cellframe_api_analysis.json',
                       help='Выходной JSON файл')
    parser.add_argument('--output-md', default='cellframe_api_report.md',
                       help='Выходной Markdown файл')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.cellframe_root):
        print(f"❌ Директория не найдена: {args.cellframe_root}")
        sys.exit(1)
    
    print("🚀 Запуск Cellframe API Extractor...")
    
    extractor = CellframeAPIExtractor(args.cellframe_root)
    modules = extractor.extract_apis()
    
    # Генерируем документацию
    extractor.generate_documentation_json(args.output_json)
    extractor.generate_markdown_summary(args.output_md)
    
    print("✅ Анализ завершен!")
    print(f"📊 Результаты: {len(extractor.api_functions)} функций в {len(modules)} модулях")

if __name__ == '__main__':
    main() 