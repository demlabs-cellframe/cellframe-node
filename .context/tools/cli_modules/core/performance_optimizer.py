#!/usr/bin/env python3
"""
Performance Optimizer для SLC CLI System
Оптимизирует время запуска, кэширование и общую производительность
"""

import os
import json
import time
import pickle
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from functools import wraps

class PerformanceOptimizer:
    """Система оптимизации производительности SLC"""
    
    def __init__(self, cache_dir: str = ".slc/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.command_cache_file = self.cache_dir / "commands.cache"
        self.context_cache_dir = self.cache_dir / "context"
        self.context_cache_dir.mkdir(exist_ok=True)
        
    def get_cache_key(self, data: Any) -> str:
        """Генерирует ключ кэша для данных"""
        if isinstance(data, str):
            return hashlib.md5(data.encode()).hexdigest()
        elif isinstance(data, dict):
            return hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()
        else:
            return hashlib.md5(str(data).encode()).hexdigest()
    
    def cache_commands(self, commands: Dict[str, Any]) -> None:
        """Кэширует зарегистрированные команды"""
        try:
            cache_data = {
                'commands': commands,
                'timestamp': time.time(),
                'version': '1.0'
            }
            with open(self.command_cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
        except Exception as e:
            print(f"Warning: Failed to cache commands: {e}")
    
    def load_cached_commands(self, max_age: int = 3600) -> Optional[Dict[str, Any]]:
        """Загружает кэшированные команды если они свежие"""
        try:
            if not self.command_cache_file.exists():
                return None
                
            with open(self.command_cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # Проверяем возраст кэша
            if time.time() - cache_data['timestamp'] > max_age:
                return None
                
            return cache_data['commands']
        except Exception as e:
            print(f"Warning: Failed to load cached commands: {e}")
            return None
    
    def cache_context(self, context_key: str, context_data: Any) -> None:
        """Кэширует данные контекста"""
        try:
            cache_file = self.context_cache_dir / f"{self.get_cache_key(context_key)}.cache"
            cache_data = {
                'data': context_data,
                'timestamp': time.time(),
                'key': context_key
            }
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
        except Exception as e:
            print(f"Warning: Failed to cache context: {e}")
    
    def load_cached_context(self, context_key: str, max_age: int = 1800) -> Optional[Any]:
        """Загружает кэшированный контекст"""
        try:
            cache_file = self.context_cache_dir / f"{self.get_cache_key(context_key)}.cache"
            if not cache_file.exists():
                return None
                
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # Проверяем возраст кэша
            if time.time() - cache_data['timestamp'] > max_age:
                return None
                
            return cache_data['data']
        except Exception as e:
            print(f"Warning: Failed to load cached context: {e}")
            return None
    
    def clear_cache(self) -> None:
        """Очищает весь кэш"""
        try:
            if self.command_cache_file.exists():
                self.command_cache_file.unlink()
            
            for cache_file in self.context_cache_dir.glob("*.cache"):
                cache_file.unlink()
                
            print("✅ Кэш очищен")
        except Exception as e:
            print(f"❌ Ошибка очистки кэша: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Возвращает статистику кэша"""
        stats = {
            'command_cache_exists': self.command_cache_file.exists(),
            'context_cache_files': len(list(self.context_cache_dir.glob("*.cache"))),
            'cache_size_mb': 0
        }
        
        try:
            # Подсчитываем размер кэша
            total_size = 0
            if self.command_cache_file.exists():
                total_size += self.command_cache_file.stat().st_size
            
            for cache_file in self.context_cache_dir.glob("*.cache"):
                total_size += cache_file.stat().st_size
            
            stats['cache_size_mb'] = round(total_size / 1024 / 1024, 2)
        except Exception:
            pass
            
        return stats

def performance_monitor(func):
    """Декоратор для мониторинга производительности функций"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        # Логируем только медленные операции (>0.1 сек)
        if end_time - start_time > 0.1:
            print(f"⏱️ {func.__name__}: {end_time - start_time:.3f}s")
        
        return result
    return wrapper

class LazyLoader:
    """Система ленивой загрузки для модулей"""
    
    def __init__(self):
        self._loaded_modules = {}
    
    def load_module(self, module_path: str, module_name: str):
        """Ленивая загрузка модуля"""
        if module_name not in self._loaded_modules:
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self._loaded_modules[module_name] = module
            except Exception as e:
                print(f"Warning: Failed to load module {module_name}: {e}")
                return None
        
        return self._loaded_modules[module_name]

# Глобальные экземпляры
optimizer = PerformanceOptimizer()
lazy_loader = LazyLoader()

def benchmark_operation(operation_name: str, operation_func, *args, **kwargs):
    """Бенчмаркинг операции"""
    start_time = time.time()
    result = operation_func(*args, **kwargs)
    end_time = time.time()
    
    print(f"📊 {operation_name}: {end_time - start_time:.3f}s")
    return result

def optimize_json_loading(file_path: str) -> Optional[Dict]:
    """Оптимизированная загрузка JSON с кэшированием"""
    cache_key = f"json:{file_path}:{os.path.getmtime(file_path)}"
    
    # Пытаемся загрузить из кэша
    cached_data = optimizer.load_cached_context(cache_key)
    if cached_data is not None:
        return cached_data
    
    # Загружаем и кэшируем
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        optimizer.cache_context(cache_key, data)
        return data
    except Exception as e:
        print(f"Error loading JSON {file_path}: {e}")
        return None

if __name__ == "__main__":
    # Тестирование системы оптимизации
    print("🚀 Performance Optimizer Test")
    print("=" * 40)
    
    # Тест кэширования команд
    test_commands = {"test": "command"}
    optimizer.cache_commands(test_commands)
    loaded = optimizer.load_cached_commands()
    print(f"✅ Command cache test: {loaded == test_commands}")
    
    # Статистика кэша
    stats = optimizer.get_cache_stats()
    print(f"📊 Cache stats: {stats}")
    
    print("✅ Performance Optimizer готов к использованию!") 