"""
Базовые классы для команд CLI
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Union


class BaseCommand:
    """Базовый класс для команд"""
    
    name = ""
    description = ""
    
    def add_arguments(self, parser):
        """Добавляет аргументы команды"""
        pass
    
    def execute(self, args) -> int:
        """Выполняет команду"""
        raise NotImplementedError
    
    def validate_args(self, args) -> bool:
        """Валидация аргументов команды"""
        return True
    
    def print_error(self, message: str):
        """Выводит сообщение об ошибке"""
        print(f"❌ {message}")
    
    def print_success(self, message: str):
        """Выводит сообщение об успехе"""
        print(f"✅ {message}")
    
    def print_warning(self, message: str):
        """Выводит предупреждение"""
        print(f"⚠️ {message}")


class ContextAwareCommand(BaseCommand):
    """Базовый класс для команд с контекстом"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
    
    def validate_args(self, args) -> bool:
        """Валидация аргументов команды с контекстом"""
        return True
    
    def execute(self, args) -> int:
        """
        Базовая реализация execute с поддержкой execute_with_context
        """
        try:
            # Если команда имеет execute_with_context, используем его
            if hasattr(self, 'execute_with_context') and callable(getattr(self, 'execute_with_context')):
                execution_result = self.execute_with_context(args)
                
                # Если команда возвращает словарь, выводим JSON контекст
                if isinstance(execution_result, dict):
                    self.output_json_context(execution_result)
                
                # Возвращаем код на основе успеха выполнения
                if isinstance(execution_result, dict):
                    return 0 if execution_result.get("success", True) else 1
                else:
                    return 0
            else:
                # Fallback на стандартное поведение
                raise NotImplementedError(f"Команда {self.__class__.__name__} должна реализовать execute или execute_with_context")
                
        except Exception as e:
            self.print_error(f"Ошибка выполнения команды: {e}")
            return 1
    
    def output_json_context(self, data: Dict[str, Any], expand_files: bool = True):
        """
        Выводит JSON контекст для AI интеграции с рекурсивным включением файлов
        
        Args:
            data: Словарь с данными для вывода
            expand_files: Если True, заменяет ссылки на файлы их содержимым
        """
        print("\n" + "=" * 60)
        print("🤖 JSON КОНТЕКСТ ДЛЯ AI:")
        print("=" * 60)
        
        if expand_files:
            # Инициализируем индексацию файлов для избежания дублирования
            self._file_index = {}  # normalized_path -> file_id
            self._loaded_files = {}  # file_id -> content
            self._file_counter = 0
            data = self._expand_file_references(data)
            
            # Пост-обработка: применяем рекурсивную обработку к содержимому загруженных файлов
            # self._post_process_loaded_files()  # Отключаем пост-обработку
            
            # Добавляем индекс загруженных файлов в итоговый JSON
            if self._loaded_files:
                data["loaded_files"] = self._loaded_files
                data["file_index_info"] = {
                    "total_files": len(self._loaded_files),
                    "description": "Индекс загруженных файлов для избежания дублирования",
                    "ref_format": "Ссылки имеют формат {'$ref': '#/loaded_files/file_XXX'}"
                }
            
            # Очищаем индексы после обработки
            loaded_files_backup = self._loaded_files.copy()
            self._file_index = {}
            self._loaded_files = {}
            self._file_counter = 0
        
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("=" * 60)
    
    def _post_process_loaded_files(self):
        """
        Пост-обработка загруженных файлов - применяет рекурсивную обработку к их содержимому
        """
        if not hasattr(self, '_loaded_files'):
            return
        
        # Создаем копию ключей чтобы избежать изменения размера словаря во время итерации
        file_ids = list(self._loaded_files.keys())
        
        for file_id in file_ids:
            file_info = self._loaded_files[file_id]
            if file_info.get('_needs_recursive_processing', False):
                # Применяем рекурсивную обработку к содержимому
                processed_content = self._expand_file_references(file_info['content'], max_depth=10, current_depth=1)
                file_info['content'] = processed_content
                # Убираем флаг обработки
                file_info.pop('_needs_recursive_processing', None)
    
    def _expand_file_references(self, data: Union[Dict, List, str], max_depth: int = 10, current_depth: int = 0, context_file_path: str = None, only_from_file_blocks: bool = True) -> Union[Dict, List, str]:
        """
        Рекурсивно заменяет ссылки на файлы их содержимым
        
        Args:
            data: Данные для обработки
            max_depth: Максимальная глубина рекурсии
            current_depth: Текущая глубина рекурсии
            
        Returns:
            Обработанные данные с включенным содержимым файлов
        """
        if current_depth >= max_depth:
            return data
        
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if key in ["suggested_files_to_load", "files_to_load", "related_files"] and isinstance(value, list):
                    # СОЗДАЕМ АЛИАСЫ вместо дублирования содержимого файлов
                    result[key] = self._create_file_aliases(value, current_depth + 1, context_file_path)
                else:
                    # Рекурсивно обрабатываем все остальные значения
                    if only_from_file_blocks:
                        # В режиме only_from_file_blocks НЕ ищем файлы в обычных значениях
                        result[key] = self._expand_file_references(value, max_depth, current_depth + 1, context_file_path, only_from_file_blocks)
                    else:
                        # В обычном режиме ищем файлы везде
                        result[key] = self._expand_file_references(value, max_depth, current_depth + 1, context_file_path, only_from_file_blocks)
            return result
        
        elif isinstance(data, list):
            # Обрабатываем каждый элемент списка
            result = []
            for item in data:
                if not only_from_file_blocks and isinstance(item, str) and self._looks_like_file_path(item):
                    # Заменяем путь к файлу на его содержимое только если режим отключен
                    resolved_path = self._resolve_relative_path(item, context_file_path)
                    file_content = self._load_file_content(resolved_path)
                    result.append(file_content)
                else:
                    result.append(self._expand_file_references(item, max_depth, current_depth + 1, context_file_path, only_from_file_blocks))
            return result
        
        elif isinstance(data, str):
            # Проверяем, является ли строка путем к файлу только если режим отключен
            if not only_from_file_blocks and self._looks_like_file_path(data):
                resolved_path = self._resolve_relative_path(data, context_file_path)
                return self._load_file_content(resolved_path)
            return data
        
        return data
    
    def _create_file_aliases(self, file_paths: List[str], current_depth: int, context_file_path: str = None) -> Dict[str, Any]:
        """
        Создает алиасы для файлов вместо дублирования содержимого
        
        Args:
            file_paths: Список путей к файлам
            current_depth: Текущая глубина рекурсии
            context_file_path: Путь к контекстному файлу
            
        Returns:
            Словарь где ключ = путь к файлу, значение = алиас на загруженный файл
        """
        file_aliases = {}
        
        for file_path in file_paths:
            if isinstance(file_path, str):
                # Разрешаем относительные пути относительно контекстного файла
                resolved_path = self._resolve_relative_path(file_path, context_file_path)
                
                # Нормализуем путь для поиска в индексе
                normalized_path = self._normalize_path(resolved_path)
                
                # Проверяем есть ли файл уже в индексе
                if hasattr(self, '_file_index') and normalized_path in self._file_index:
                    file_id = self._file_index[normalized_path]
                    file_aliases[file_path] = {
                        "$ref": f"#/loaded_files/{file_id}",
                        "$file_path": file_path,
                        "$normalized_path": normalized_path,
                        "$note": "Алиас на уже загруженный файл"
                    }
                else:
                    # Если файла нет в индексе, загружаем его
                    content = self._load_file_content(resolved_path)
                    
                    # Если загрузка успешна и файл теперь в индексе, создаем алиас
                    if hasattr(self, '_file_index') and normalized_path in self._file_index:
                        file_id = self._file_index[normalized_path]
                        file_aliases[file_path] = {
                            "$ref": f"#/loaded_files/{file_id}",
                            "$file_path": file_path,
                            "$normalized_path": normalized_path,
                            "$note": "Алиас на загруженный файл"
                        }
                    else:
                        # Если загрузка не удалась, возвращаем ошибку
                        file_aliases[file_path] = content  # это будет строка с ошибкой
        
        return file_aliases

    def _load_files_as_dict(self, file_paths: List[str], current_depth: int, context_file_path: str = None) -> Dict[str, Any]:
        """
        DEPRECATED: Используйте _create_file_aliases для избежания дублирования
        
        Загружает содержимое списка файлов в словарь
        
        Args:
            file_paths: Список путей к файлам
            current_depth: Текущая глубина рекурсии
            
        Returns:
            Словарь где ключ = путь к файлу, значение = содержимое файла
        """
        # Переадресуем на новый метод
        return self._create_file_aliases(file_paths, current_depth, context_file_path)
    
    def _load_file_content(self, file_path: str) -> Union[Dict, List, str]:
        """
        Загружает содержимое файла с индексацией для избежания дублирования
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Содержимое файла или ссылка на уже загруженный файл
        """
        # Нормализуем путь
        normalized_path = self._normalize_path(file_path)
        
        # Проверяем индекс - если файл уже загружен, возвращаем ссылку
        if hasattr(self, '_file_index') and normalized_path in self._file_index:
            file_id = self._file_index[normalized_path]
            return {
                "$ref": f"#/loaded_files/{file_id}",
                "$file_path": file_path,
                "$normalized_path": normalized_path,
                "$note": "Ссылка на уже загруженный файл"
            }
        
        try:
            # DEBUG: Добавляем отладочные принты
            # print(f"DEBUG: Loading file: {file_path}")
            # print(f"DEBUG: base_path type: {type(self.base_path)}, value: {self.base_path}")
            
            # Определяем полный путь с учетом разных форматов путей
            if file_path.startswith('/'):
                # Абсолютный путь
                full_path = Path(file_path)
            elif file_path.startswith('./'):
                # Путь начинается с ./ - убираем ./ и обрабатываем как обычный
                clean_path = file_path[2:]  # Убираем './'
                if clean_path.startswith('.context/') and Path(self.base_path).name == '.context':
                    # Убираем .context/ из начала пути если base_path уже .context
                    relative_path = clean_path[9:]  # Убираем '.context/'
                    full_path = Path(self.base_path) / relative_path
                else:
                    full_path = Path(self.base_path) / clean_path
            elif file_path.startswith('.context/'):
                # Путь начинается с .context/ - убираем этот префикс если base_path уже .context
                if Path(self.base_path).name == '.context':
                    # Убираем .context/ из начала пути
                    relative_path = file_path[9:]  # Убираем '.context/'
                    full_path = Path(self.base_path) / relative_path
                else:
                    # base_path не .context - используем как есть
                    full_path = Path(self.base_path) / file_path
            else:
                # Обычный относительный путь
                # print(f"DEBUG: Creating path from base_path={self.base_path} (type: {type(self.base_path)}) + file_path={file_path}")
                if isinstance(self.base_path, str):
                    # Если base_path строка, конвертируем в Path
                    full_path = Path(self.base_path) / file_path
                else:
                    full_path = self.base_path / file_path
            
            if not full_path.exists():
                return f"[FILE_NOT_FOUND: {file_path} -> {full_path}]"
            
            # Проверяем размер файла (ограничиваем большие файлы)
            if full_path.stat().st_size > 100 * 1024:  # 100KB
                return f"[FILE_TOO_LARGE: {file_path} ({full_path.stat().st_size} bytes)]"
            
            # Читаем содержимое
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Пытаемся парсить как JSON
            result = None
            if file_path.endswith('.json'):
                try:
                    result = json.loads(content)
                except json.JSONDecodeError:
                    result = f"[INVALID_JSON: {file_path}]"
            else:
                # Для текстовых файлов возвращаем содержимое (ограничиваем длину)
                if len(content) > 5000:  # 5000 символов
                    result = content[:5000] + f"\n[TRUNCATED: {len(content) - 5000} more characters]"
                else:
                    result = content
            
            # Создаем уникальный ID для файла и сохраняем в индекс
            if hasattr(self, '_file_index') and hasattr(self, '_loaded_files'):
                self._file_counter += 1
                file_id = f"file_{self._file_counter:03d}"
                self._file_index[normalized_path] = file_id
                
                # Если содержимое JSON, применяем рекурсивную обработку сразу
                processed_result = result
                if isinstance(result, dict):
                    processed_result = self._expand_file_references(result, max_depth=10, current_depth=1, context_file_path=file_path, only_from_file_blocks=True)
                
                self._loaded_files[file_id] = {
                    "file_path": file_path,
                    "normalized_path": normalized_path,
                    "content": processed_result
                }
            
            return result
            
        except Exception as e:
            result = f"[ERROR_LOADING: {file_path} - {str(e)}]"
            
            # Сохраняем ошибку в индекс тоже
            if hasattr(self, '_file_index') and hasattr(self, '_loaded_files'):
                self._file_counter += 1
                file_id = f"file_{self._file_counter:03d}"
                self._file_index[normalized_path] = file_id
                self._loaded_files[file_id] = {
                    "file_path": file_path,
                    "normalized_path": normalized_path,
                    "content": result,
                    "error": True
                }
            
            return result
    
    def _resolve_relative_path(self, file_path: str, context_file_path: str = None) -> str:
        """
        Разрешает относительные пути относительно контекстного файла
        
        Args:
            file_path: Путь к файлу (может быть относительным)
            context_file_path: Путь к файлу из которого идет ссылка
            
        Returns:
            Разрешенный путь к файлу
        """
        if not file_path:
            return file_path
        
        # Если путь абсолютный или начинается с .context/ - используем как есть
        if (file_path.startswith('/') or 
            file_path.startswith('.context/') or 
            file_path.startswith('./')):
            return file_path
        
        # Если нет контекстного файла - используем путь как есть
        if not context_file_path:
            return file_path
        
        # Если это простое имя файла без слешей - пытаемся найти в папке контекстного файла
        if '/' not in file_path:
            try:
                context_dir = Path(context_file_path).parent
                # Проверяем есть ли файл в той же папке что и контекстный файл
                potential_path = context_dir / file_path
                if (self.base_path / potential_path).exists():
                    return str(potential_path)
            except Exception:
                pass
        
        # Если ничего не помогло - возвращаем исходный путь
        return file_path
    
    def _normalize_path(self, file_path: str) -> str:
        """
        Нормализует путь к файлу для избежания циклических ссылок
        
        Args:
            file_path: Путь к файлу
            
        Returns:
            Нормализованный абсолютный путь
        """
        try:
            # Определяем полный путь (та же логика что в _load_file_content)
            if file_path.startswith('/'):
                full_path = Path(file_path)
            elif file_path.startswith('./'):
                clean_path = file_path[2:]  # Убираем './'
                if clean_path.startswith('.context/') and self.base_path.name == '.context':
                    relative_path = clean_path[9:]  # Убираем '.context/'
                    full_path = self.base_path / relative_path
                else:
                    full_path = self.base_path / clean_path
            elif file_path.startswith('.context/'):
                if self.base_path.name == '.context':
                    relative_path = file_path[9:]  # Убираем '.context/'
                    full_path = self.base_path / relative_path
                else:
                    full_path = self.base_path / file_path
            else:
                full_path = self.base_path / file_path
            
            # Возвращаем нормализованный абсолютный путь
            return str(full_path.resolve())
        except Exception:
            # Если не удается нормализовать, возвращаем исходный путь
            return file_path
    
    def _looks_like_file_path(self, text: str) -> bool:
        """
        Проверяет, похожа ли строка на путь к файлу
        
        Args:
            text: Строка для проверки
            
        Returns:
            True если строка похожа на путь к файлу
        """
        if not isinstance(text, str) or len(text) < 3:
            return False
        
        # Исключаем команды CLI и скрипты Python
        if (text.startswith('./slc ') or text.startswith('slc ') or text.startswith('слк ') or
            text.startswith('python3 ') or text.startswith('python ') or 
            ' load-context ' in text or ' -c ' in text):
            return False
        
        # Исключаем описания и строки с пробелами (кроме путей с пробелами в именах)
        if (' - ' in text or 
            text.startswith('Загрузить ') or text.startswith('Файл ') or
            text.startswith('Критический ') or text.startswith('AI/ML ') or
            text.startswith('Современная ') or text.startswith('Базовые ') or
            text.startswith('Python ') or text.startswith('Async/') or
            'шаблоны и инструменты' in text or 'для понимания' in text or
            'рефакторинг' in text or 'архитектуры' in text or
            'альтернатива' in text or 'зависимости' in text or
            'support' in text):
            return False
        
        # Исключаем маски файлов, шаблоны, npm пакеты и статусы
        if (text.startswith('*') or text.endswith('*') or 
            'test_*.py' in text or '*_test.py' in text or
            'async/await' in text or text.startswith('@') or
            '/' in text and ('Draft/' in text or 'Review/' in text or 'Published' in text) or
            text in ['requirements.txt', 'dev-requirements.txt', 'environment.yml', 'conda-lock.yml']):
            return False
        
        # Исключаем URL
        if text.startswith('http') or '://' in text:
            return False
        
        # Проверяем расширения файлов - должны быть в конце строки
        file_extensions = ['.json', '.py', '.md', '.txt', '.yaml', '.yml', '.js', '.ts', '.sh']
        has_extension = any(text.endswith(ext) for ext in file_extensions)
        
        # Если есть расширение - проверяем что это простой путь
        if has_extension:
            # Исключаем строки с описаниями даже если есть расширение
            if (len(text.split()) > 3 or 
                any(word in text.lower() for word in ['для', 'система', 'файл', 'модуль', 'шаблон'])):
                return False
            return True
        
        # Проверяем структуру пути без расширения (папки)
        if '/' in text and not ' ' in text:
            # Простой путь без пробелов
            parts = text.split('/')
            if (len(parts) > 1 and 
                all(part.strip() and not ' ' in part for part in parts) and
                not any(part.startswith('.') and len(part) > 4 for part in parts)):
                return True
        
        return False


class CommandRegistry:
    """Реестр команд CLI"""
    
    def __init__(self):
        self._commands: Dict[str, BaseCommand] = {}
    
    def register(self, command: BaseCommand):
        """
        Регистрация команды
        
        Args:
            command: Экземпляр команды для регистрации
        """
        self._commands[command.name] = command
    
    def get_command(self, name: str) -> BaseCommand:
        """
        Получение команды по имени
        
        Args:
            name: Имя команды
            
        Returns:
            Экземпляр команды или None если не найдена
        """
        return self._commands.get(name)
    
    def get_all_commands(self) -> Dict[str, BaseCommand]:
        """Получение всех зарегистрированных команд"""
        return self._commands.copy()
    
    def list_commands(self) -> list:
        """Получение списка имен команд"""
        return list(self._commands.keys()) 