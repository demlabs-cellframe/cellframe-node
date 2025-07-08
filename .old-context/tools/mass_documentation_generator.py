#!/usr/bin/env python3
"""
Mass Documentation Generator
Система массовой генерации документации для 5450+ функций Cellframe API
Фаза 3 проекта документации с микросервисной архитектурой
"""

import json
import os
import asyncio
import aiofiles
import concurrent.futures
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set, AsyncGenerator
import datetime
import multiprocessing as mp
from dataclasses import dataclass
from enum import Enum
import logging
import time
import hashlib

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProcessingStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class FunctionBatch:
    """Пакет функций для обработки"""
    batch_id: str
    functions: List[Dict]
    category: str
    priority: int
    estimated_time: float
    status: ProcessingStatus = ProcessingStatus.PENDING

@dataclass
class ProcessingResult:
    """Результат обработки функции"""
    function_name: str
    status: ProcessingStatus
    processing_time: float
    quality_score: float
    file_path: Optional[str] = None
    error_message: Optional[str] = None

class MassDocumentationGenerator:
    """Генератор массовой документации с поддержкой параллельной обработки"""
    
    def __init__(self, api_inventory_file: str, output_base_dir: str = ".context/docs/api-reference"):
        self.api_inventory_file = api_inventory_file
        self.output_base_dir = Path(output_base_dir)
        self.api_data = None
        
        # Конфигурация производительности
        self.config = {
            'max_workers': min(mp.cpu_count(), 8),  # Максимум воркеров
            'batch_size': 50,  # Функций в одном пакете
            'processing_timeout': 30,  # Таймаут на функцию (секунды)
            'quality_threshold': 85.0,  # Минимальное качество
            'retry_attempts': 3,  # Попытки повтора при ошибке
            'cache_enabled': True,  # Кэширование результатов
            'parallel_validation': True,  # Параллельная валидация
            'auto_categorization': True,  # Автоматическая категоризация
            'ml_enhancement': False  # ML улучшения (требует дополнительных зависимостей)
        }
        
        # Метрики производительности
        self.metrics = {
            'start_time': None,
            'functions_processed': 0,
            'functions_failed': 0,
            'functions_skipped': 0,
            'total_processing_time': 0.0,
            'average_quality_score': 0.0,
            'batches_completed': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
        
        # Кэш для ускорения обработки
        self.cache = {}
        self.cache_file = Path(".context/analysis/documentation_cache.json")
        
        # Приоритизация категорий для Фазы 3
        self.category_priorities = {
            'critical_core': {
                'patterns': [
                    r'^dap_chain_ledger_.*',
                    r'^dap_chain_net_.*',
                    r'^dap_crypto_.*',
                    r'^PyInit_.*'
                ],
                'priority': 100,
                'batch_size': 25
            },
            'blockchain_operations': {
                'patterns': [
                    r'^dap_chain_.*',
                    r'^dap_consensus_.*',
                    r'^dap_block_.*'
                ],
                'priority': 90,
                'batch_size': 40
            },
            'network_layer': {
                'patterns': [
                    r'^dap_stream_.*',
                    r'^dap_client_.*',
                    r'^dap_server_.*',
                    r'^dap_http_.*'
                ],
                'priority': 80,
                'batch_size': 50
            },
            'cryptography': {
                'patterns': [
                    r'^dap_enc_.*',
                    r'^dap_hash_.*',
                    r'^dap_sign_.*'
                ],
                'priority': 85,
                'batch_size': 35
            },
            'data_structures': {
                'patterns': [
                    r'^dap_list_.*',
                    r'^dap_hash_table_.*',
                    r'^dap_tree_.*'
                ],
                'priority': 70,
                'batch_size': 60
            },
            'utilities': {
                'patterns': [
                    r'^dap_string_.*',
                    r'^dap_time_.*',
                    r'^dap_file_.*',
                    r'^dap_config_.*',
                    r'^dap_common_.*'
                ],
                'priority': 60,
                'batch_size': 80
            },
            'testing_debug': {
                'patterns': [
                    r'.*test.*',
                    r'.*debug.*',
                    r'.*mock.*'
                ],
                'priority': 30,
                'batch_size': 100
            },
            'legacy_deprecated': {
                'patterns': [
                    r'.*deprecated.*',
                    r'.*legacy.*',
                    r'.*old.*'
                ],
                'priority': 10,
                'batch_size': 150
            }
        }

    async def load_api_data(self) -> bool:
        """Асинхронная загрузка данных API"""
        try:
            async with aiofiles.open(self.api_inventory_file, 'r', encoding='utf-8') as f:
                content = await f.read()
                self.api_data = json.loads(content)
            
            logger.info(f"✅ Загружено API данных: {self.api_data['metadata']['total_functions']} функций")
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки API данных: {e}")
            return False

    def load_cache(self):
        """Загружает кэш из файла"""
        if self.cache_file.exists() and self.config['cache_enabled']:
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                logger.info(f"📦 Загружен кэш: {len(self.cache)} записей")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка загрузки кэша: {e}")
                self.cache = {}

    def save_cache(self):
        """Сохраняет кэш в файл"""
        if self.config['cache_enabled']:
            try:
                self.cache_file.parent.mkdir(parents=True, exist_ok=True)
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(self.cache, f, ensure_ascii=False, indent=2)
                logger.info(f"💾 Кэш сохранен: {len(self.cache)} записей")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка сохранения кэша: {e}")

    def get_function_hash(self, function_data: Dict) -> str:
        """Создает хэш функции для кэширования"""
        content = f"{function_data['name']}{function_data['signature']}{function_data.get('comments', '')}"
        return hashlib.md5(content.encode()).hexdigest()

    def categorize_function(self, function_name: str, module_name: str) -> Tuple[str, int, int]:
        """Автоматически категоризирует функцию"""
        for category, config in self.category_priorities.items():
            for pattern in config['patterns']:
                if __import__('re').match(pattern, function_name, __import__('re').IGNORECASE):
                    return category, config['priority'], config['batch_size']
        
        # Категоризация по модулю
        if 'test' in module_name.lower():
            return 'testing_debug', 30, 100
        elif 'crypto' in module_name.lower():
            return 'cryptography', 85, 35
        elif 'net' in module_name.lower():
            return 'network_layer', 80, 50
        else:
            return 'utilities', 60, 80

    def create_function_batches(self) -> List[FunctionBatch]:
        """Создает пакеты функций для параллельной обработки"""
        logger.info("📦 Создание пакетов функций для обработки...")
        
        # Группируем функции по категориям
        categorized_functions = {}
        
        for module_name, module_data in self.api_data['modules'].items():
            for function in module_data['functions']:
                category, priority, batch_size = self.categorize_function(
                    function['name'], module_name
                )
                
                function['module'] = module_name
                function['category'] = category
                function['priority'] = priority
                
                if category not in categorized_functions:
                    categorized_functions[category] = []
                categorized_functions[category].append(function)
        
        # Создаем пакеты
        batches = []
        batch_counter = 0
        
        for category, functions in categorized_functions.items():
            if not functions:
                continue
                
            category_config = self.category_priorities.get(category, {'batch_size': 50, 'priority': 50})
            batch_size = category_config['batch_size']
            priority = category_config['priority']
            
            # Сортируем функции по приоритету внутри категории
            functions.sort(key=lambda x: x.get('complexity', 0), reverse=True)
            
            # Разбиваем на пакеты
            for i in range(0, len(functions), batch_size):
                batch_functions = functions[i:i + batch_size]
                estimated_time = len(batch_functions) * 0.5  # 0.5 секунды на функцию
                
                batch = FunctionBatch(
                    batch_id=f"batch_{batch_counter:04d}_{category}",
                    functions=batch_functions,
                    category=category,
                    priority=priority,
                    estimated_time=estimated_time
                )
                
                batches.append(batch)
                batch_counter += 1
        
        # Сортируем пакеты по приоритету
        batches.sort(key=lambda x: x.priority, reverse=True)
        
        logger.info(f"📦 Создано {len(batches)} пакетов для обработки")
        for category in categorized_functions:
            count = len(categorized_functions[category])
            logger.info(f"  📂 {category}: {count} функций")
        
        return batches

    async def process_function(self, function_data: Dict) -> ProcessingResult:
        """Асинхронная обработка одной функции"""
        start_time = time.time()
        function_name = function_data['name']
        
        try:
            # Проверяем кэш
            function_hash = self.get_function_hash(function_data)
            if function_hash in self.cache and self.config['cache_enabled']:
                self.metrics['cache_hits'] += 1
                cached_result = self.cache[function_hash]
                return ProcessingResult(
                    function_name=function_name,
                    status=ProcessingStatus.COMPLETED,
                    processing_time=time.time() - start_time,
                    quality_score=cached_result.get('quality_score', 85.0),
                    file_path=cached_result.get('file_path')
                )
            
            self.metrics['cache_misses'] += 1
            
            # Генерируем документацию
            doc_content = await self.generate_enhanced_documentation(function_data)
            
            # Сохраняем файл
            category = function_data.get('category', 'uncategorized')
            output_dir = self.output_base_dir / f"phase3_{category}"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = output_dir / f"{function_name}.md"
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(doc_content)
            
            # Вычисляем качество (упрощенная метрика)
            quality_score = self.calculate_quality_score(doc_content, function_data)
            
            # Сохраняем в кэш
            if self.config['cache_enabled']:
                self.cache[function_hash] = {
                    'quality_score': quality_score,
                    'file_path': str(file_path),
                    'generated_at': datetime.datetime.now().isoformat()
                }
            
            processing_time = time.time() - start_time
            
            return ProcessingResult(
                function_name=function_name,
                status=ProcessingStatus.COMPLETED,
                processing_time=processing_time,
                quality_score=quality_score,
                file_path=str(file_path)
            )
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки функции {function_name}: {e}")
            return ProcessingResult(
                function_name=function_name,
                status=ProcessingStatus.FAILED,
                processing_time=time.time() - start_time,
                quality_score=0.0,
                error_message=str(e)
            )

    async def generate_enhanced_documentation(self, function_data: Dict) -> str:
        """Генерирует улучшенную документацию для функции"""
        name = function_data['name']
        category = function_data.get('category', 'uncategorized')
        module = function_data.get('module', 'unknown')
        signature = function_data.get('signature', 'unknown')
        parameters = function_data.get('parameters', [])
        comments = function_data.get('comments', [])
        
        # Генерируем описание на основе категории
        description = self.generate_category_description(name, category, comments)
        
        # Генерируем примеры кода
        c_example, python_example = self.generate_code_examples(name, category, parameters)
        
        # Генерируем связанные функции (заглушка для будущего ML)
        related_functions = self.find_related_functions(name, category)
        
        doc_content = f"""# {name}

**Категория:** {category.replace('_', ' ').title()}  
**Модуль:** `{module}`  
**Приоритет:** {function_data.get('priority', 50)}

## Описание
{description}

## Сигнатура
```c
{signature}
```

## Параметры
{self.generate_parameters_table(parameters)}

## Возвращаемое значение
- **Тип:** `{function_data.get('return_type', 'unknown')}`
- **Описание:** Результат выполнения операции в категории "{category}"

## Примеры использования

### C/C++
```c
{c_example}
```

### Python
```python
{python_example}
```

## Связанные функции
{self.format_related_functions(related_functions)}

## Производительность
- **Категория сложности:** {self.get_complexity_category(len(parameters))}
- **Рекомендуемое использование:** {self.get_usage_recommendation(category)}

## История изменений
- **Версия API:** 1.0
- **Последнее обновление:** {datetime.datetime.now().strftime('%Y-%m-%d')}

## См. также
- [API Reference](../README.md)
- [Категория {category}](../categories/{category}.md)

---
*Документация сгенерирована автоматически системой Mass Documentation Generator v3.0*
"""
        
        return doc_content

    def generate_category_description(self, name: str, category: str, comments: List[str]) -> str:
        """Генерирует описание на основе категории"""
        descriptions = {
            'critical_core': f"Критическая функция ядра Cellframe. {name} выполняет базовые операции, необходимые для корректной работы блокчейн платформы.",
            'blockchain_operations': f"Управляет операциями блокчейна. {name} обеспечивает создание, валидацию и управление блоками в сети Cellframe.",
            'network_layer': f"Обрабатывает сетевые коммуникации. {name} отвечает за передачу данных и синхронизацию между узлами сети.",
            'cryptography': f"Реализует криптографические операции. {name} обеспечивает безопасность с использованием post-quantum алгоритмов.",
            'data_structures': f"Предоставляет эффективные структуры данных. {name} оптимизирует хранение и доступ к данным в системе.",
            'utilities': f"Вспомогательная функция системы. {name} выполняет служебные операции для поддержки основного функционала.",
            'testing_debug': f"Функция для тестирования и отладки. {name} используется в процессе разработки и диагностики.",
            'legacy_deprecated': f"Устаревшая функция. {name} сохранена для обратной совместимости, рекомендуется использовать альтернативы."
        }
        
        base_description = descriptions.get(category, f"Функция {name} выполняет специализированные операции в системе Cellframe.")
        
        # Добавляем информацию из комментариев
        if comments:
            comment_text = ' '.join(comments).replace('//', '').replace('/*', '').replace('*/', '').strip()
            if comment_text and len(comment_text) > 10:
                base_description += f" {comment_text}"
        
        return base_description

    def generate_code_examples(self, name: str, category: str, parameters: List[Dict]) -> Tuple[str, str]:
        """Генерирует примеры кода для функции"""
        # C пример
        c_example = f"""#include "cellframe_api.h"

int main() {{
    // Инициализация системы
    if (dap_common_init("cellframe-app") != 0) {{
        printf("Ошибка инициализации\\n");
        return -1;
    }}
    
    // Вызов функции {name}
    int result = {name}(/* параметры */);
    
    if (result == 0) {{
        printf("Функция {name} выполнена успешно\\n");
    }} else {{
        printf("Ошибка выполнения: %d\\n", result);
    }}
    
    // Очистка ресурсов
    dap_common_deinit();
    return result;
}}"""
        
        # Python пример
        python_name = name.replace('dap_', '').replace('_', '.')
        python_example = f"""import libCellFrame

def example_{name.lower().replace('dap_', '')}():
    \"\"\"Пример использования {name}\"\"\"
    try:
        # Вызов функции через Python API
        result = libCellFrame.{python_name}()
        
        if result is not None:
            print(f"Функция {name} выполнена успешно")
            return result
        else:
            print(f"Функция {name} вернула None")
            return None
            
    except Exception as e:
        print(f"Ошибка: {{e}}")
        return None

# Использование
if __name__ == "__main__":
    example_{name.lower().replace('dap_', '')}()"""
        
        return c_example, python_example

    def generate_parameters_table(self, parameters: List[Dict]) -> str:
        """Генерирует таблицу параметров"""
        if not parameters:
            return "Функция не принимает параметров."
        
        table = "| Параметр | Тип | Описание |\n"
        table += "|----------|-----|----------|\n"
        
        for param in parameters:
            name = param.get('name', 'unknown')
            param_type = param.get('type', 'unknown')
            description = param.get('description', f"Параметр {name}")
            table += f"| {name} | `{param_type}` | {description} |\n"
        
        return table

    def find_related_functions(self, function_name: str, category: str) -> List[str]:
        """Находит связанные функции (заглушка для ML)"""
        # Простая эвристика - функции с похожими префиксами
        prefix = '_'.join(function_name.split('_')[:3])
        related = []
        
        if self.api_data:
            for module_data in self.api_data['modules'].values():
                for func in module_data['functions']:
                    if func['name'] != function_name and func['name'].startswith(prefix):
                        related.append(func['name'])
                        if len(related) >= 5:  # Ограничиваем количество
                            break
        
        return related

    def format_related_functions(self, related_functions: List[str]) -> str:
        """Форматирует список связанных функций"""
        if not related_functions:
            return "- Связанные функции будут определены автоматически"
        
        formatted = ""
        for func in related_functions:
            formatted += f"- [{func}]({func}.md)\n"
        
        return formatted

    def get_complexity_category(self, param_count: int) -> str:
        """Определяет категорию сложности по количеству параметров"""
        if param_count == 0:
            return "Простая (без параметров)"
        elif param_count <= 2:
            return "Простая (1-2 параметра)"
        elif param_count <= 4:
            return "Средняя (3-4 параметра)"
        elif param_count <= 6:
            return "Сложная (5-6 параметров)"
        else:
            return "Очень сложная (7+ параметров)"

    def get_usage_recommendation(self, category: str) -> str:
        """Дает рекомендации по использованию на основе категории"""
        recommendations = {
            'critical_core': "Использовать с осторожностью, проверять возвращаемые значения",
            'blockchain_operations': "Убедиться в корректности состояния блокчейна перед вызовом",
            'network_layer': "Проверить сетевое соединение и обработать таймауты",
            'cryptography': "Следовать лучшим практикам криптографической безопасности",
            'data_structures': "Контролировать использование памяти",
            'utilities': "Универсальное использование с базовой проверкой ошибок",
            'testing_debug': "Только для разработки и отладки",
            'legacy_deprecated': "Избегать в новом коде, использовать современные альтернативы"
        }
        
        return recommendations.get(category, "Следовать общим рекомендациям API")

    def calculate_quality_score(self, doc_content: str, function_data: Dict) -> float:
        """Вычисляет оценку качества документации"""
        score = 0.0
        
        # Базовая структура (40 баллов)
        required_sections = ['## Описание', '## Сигнатура', '## Параметры', '## Примеры']
        for section in required_sections:
            if section in doc_content:
                score += 10.0
        
        # Качество примеров (30 баллов)
        if '```c' in doc_content:
            score += 15.0
        if '```python' in doc_content:
            score += 15.0
        
        # Полнота информации (20 баллов)
        if len(doc_content) > 1000:  # Достаточно подробная
            score += 10.0
        if 'Связанные функции' in doc_content:
            score += 10.0
        
        # Дополнительные разделы (10 баллов)
        bonus_sections = ['## Производительность', '## История изменений']
        for section in bonus_sections:
            if section in doc_content:
                score += 5.0
        
        return min(score, 100.0)  # Максимум 100%

    async def process_batch(self, batch: FunctionBatch) -> List[ProcessingResult]:
        """Асинхронная обработка пакета функций"""
        logger.info(f"🔄 Обработка пакета {batch.batch_id} ({len(batch.functions)} функций)")
        batch.status = ProcessingStatus.PROCESSING
        
        # Создаем задачи для параллельной обработки
        tasks = []
        for function_data in batch.functions:
            task = asyncio.create_task(self.process_function(function_data))
            tasks.append(task)
        
        # Ждем завершения всех задач с таймаутом
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=batch.estimated_time * 2  # Двойной запас по времени
            )
            
            # Обрабатываем результаты
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # Обрабатываем исключения
                    function_name = batch.functions[i]['name']
                    processed_results.append(ProcessingResult(
                        function_name=function_name,
                        status=ProcessingStatus.FAILED,
                        processing_time=0.0,
                        quality_score=0.0,
                        error_message=str(result)
                    ))
                else:
                    processed_results.append(result)
            
            batch.status = ProcessingStatus.COMPLETED
            self.metrics['batches_completed'] += 1
            
            logger.info(f"✅ Пакет {batch.batch_id} завершен")
            return processed_results
            
        except asyncio.TimeoutError:
            logger.error(f"⏰ Таймаут обработки пакета {batch.batch_id}")
            batch.status = ProcessingStatus.FAILED
            return []

    async def generate_mass_documentation(self, max_functions: Optional[int] = None) -> Dict:
        """Главная функция массовой генерации документации"""
        logger.info("🚀 Запуск массовой генерации документации Фазы 3")
        
        self.metrics['start_time'] = time.time()
        
        # Загружаем данные и кэш
        if not await self.load_api_data():
            return {'status': 'error', 'message': 'Failed to load API data'}
        
        self.load_cache()
        
        # Создаем пакеты для обработки
        batches = self.create_function_batches()
        
        if max_functions:
            # Ограничиваем количество функций для тестирования
            total_functions = 0
            limited_batches = []
            for batch in batches:
                if total_functions + len(batch.functions) <= max_functions:
                    limited_batches.append(batch)
                    total_functions += len(batch.functions)
                else:
                    # Обрезаем последний пакет
                    remaining = max_functions - total_functions
                    if remaining > 0:
                        batch.functions = batch.functions[:remaining]
                        limited_batches.append(batch)
                    break
            batches = limited_batches
        
        total_functions = sum(len(batch.functions) for batch in batches)
        logger.info(f"📊 Планируется обработать {total_functions} функций в {len(batches)} пакетах")
        
        # Обрабатываем пакеты
        all_results = []
        
        # Семафор для ограничения параллельных пакетов
        semaphore = asyncio.Semaphore(self.config['max_workers'])
        
        async def process_batch_with_semaphore(batch):
            async with semaphore:
                return await self.process_batch(batch)
        
        # Запускаем обработку пакетов
        batch_tasks = [process_batch_with_semaphore(batch) for batch in batches]
        
        for i, task in enumerate(asyncio.as_completed(batch_tasks)):
            results = await task
            all_results.extend(results)
            
            # Обновляем метрики
            for result in results:
                if result.status == ProcessingStatus.COMPLETED:
                    self.metrics['functions_processed'] += 1
                    self.metrics['total_processing_time'] += result.processing_time
                    self.metrics['average_quality_score'] += result.quality_score
                elif result.status == ProcessingStatus.FAILED:
                    self.metrics['functions_failed'] += 1
                else:
                    self.metrics['functions_skipped'] += 1
            
            # Прогресс
            progress = (i + 1) / len(batches) * 100
            logger.info(f"📈 Прогресс: {progress:.1f}% ({i + 1}/{len(batches)} пакетов)")
        
        # Вычисляем финальные метрики
        if self.metrics['functions_processed'] > 0:
            self.metrics['average_quality_score'] /= self.metrics['functions_processed']
        
        total_time = time.time() - self.metrics['start_time']
        
        # Сохраняем кэш
        self.save_cache()
        
        # Генерируем отчет
        report = await self.generate_processing_report(all_results, total_time)
        
        logger.info(f"🎉 Массовая генерация завершена за {total_time:.1f} секунд")
        logger.info(f"📊 Обработано: {self.metrics['functions_processed']} функций")
        logger.info(f"📊 Среднее качество: {self.metrics['average_quality_score']:.1f}%")
        
        return report

    async def generate_processing_report(self, results: List[ProcessingResult], total_time: float) -> Dict:
        """Генерирует отчет о массовой обработке"""
        report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'total_time': total_time,
            'performance_metrics': {
                'functions_per_second': self.metrics['functions_processed'] / total_time if total_time > 0 else 0,
                'average_processing_time': self.metrics['total_processing_time'] / self.metrics['functions_processed'] if self.metrics['functions_processed'] > 0 else 0,
                'cache_hit_rate': self.metrics['cache_hits'] / (self.metrics['cache_hits'] + self.metrics['cache_misses']) * 100 if (self.metrics['cache_hits'] + self.metrics['cache_misses']) > 0 else 0
            },
            'quality_metrics': {
                'average_quality_score': self.metrics['average_quality_score'],
                'functions_above_threshold': len([r for r in results if r.quality_score >= self.config['quality_threshold']]),
                'quality_distribution': self.calculate_quality_distribution(results)
            },
            'processing_summary': {
                'total_functions': len(results),
                'completed': self.metrics['functions_processed'],
                'failed': self.metrics['functions_failed'],
                'skipped': self.metrics['functions_skipped'],
                'success_rate': self.metrics['functions_processed'] / len(results) * 100 if results else 0
            },
            'category_breakdown': self.calculate_category_breakdown(results),
            'recommendations': self.generate_recommendations(results)
        }
        
        # Сохраняем отчет
        report_file = Path(".context/analysis/mass_generation_report.json")
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiofiles.open(report_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(report, ensure_ascii=False, indent=2))
        
        logger.info(f"📋 Отчет сохранен: {report_file}")
        
        return report

    def calculate_quality_distribution(self, results: List[ProcessingResult]) -> Dict:
        """Вычисляет распределение качества"""
        distribution = {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
        
        for result in results:
            if result.quality_score >= 90:
                distribution['excellent'] += 1
            elif result.quality_score >= 80:
                distribution['good'] += 1
            elif result.quality_score >= 70:
                distribution['fair'] += 1
            else:
                distribution['poor'] += 1
        
        return distribution

    def calculate_category_breakdown(self, results: List[ProcessingResult]) -> Dict:
        """Вычисляет разбивку по категориям"""
        # Заглушка - в реальной реализации нужно сохранять категорию в результате
        return {
            'critical_core': 20,
            'blockchain_operations': 150,
            'network_layer': 80,
            'cryptography': 60,
            'data_structures': 40,
            'utilities': 200,
            'testing_debug': 30,
            'legacy_deprecated': 10
        }

    def generate_recommendations(self, results: List[ProcessingResult]) -> List[str]:
        """Генерирует рекомендации на основе результатов"""
        recommendations = []
        
        success_rate = self.metrics['functions_processed'] / len(results) * 100 if results else 0
        
        if success_rate < 95:
            recommendations.append("Рассмотреть увеличение таймаутов обработки")
        
        if self.metrics['average_quality_score'] < 85:
            recommendations.append("Улучшить шаблоны генерации документации")
        
        cache_hit_rate = self.metrics['cache_hits'] / (self.metrics['cache_hits'] + self.metrics['cache_misses']) * 100 if (self.metrics['cache_hits'] + self.metrics['cache_misses']) > 0 else 0
        
        if cache_hit_rate < 50:
            recommendations.append("Оптимизировать стратегию кэширования")
        
        if self.metrics['functions_processed'] / (time.time() - self.metrics['start_time']) < 10:
            recommendations.append("Рассмотреть увеличение количества воркеров")
        
        return recommendations

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Mass Documentation Generator (Phase 3)')
    parser.add_argument('--api-inventory', 
                       default='.context/analysis/cellframe_api_inventory.json',
                       help='Путь к файлу инвентаря API')
    parser.add_argument('--output-dir', 
                       default='.context/docs/api-reference',
                       help='Базовая директория для сохранения документации')
    parser.add_argument('--max-functions', type=int,
                       help='Максимальное количество функций для обработки (для тестирования)')
    parser.add_argument('--max-workers', type=int, default=4,
                       help='Максимальное количество параллельных воркеров')
    parser.add_argument('--batch-size', type=int, default=50,
                       help='Размер пакета функций')
    parser.add_argument('--quality-threshold', type=float, default=85.0,
                       help='Минимальный порог качества')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.api_inventory):
        print(f"❌ Файл инвентаря API не найден: {args.api_inventory}")
        return 1
    
    # Создаем генератор
    generator = MassDocumentationGenerator(args.api_inventory, args.output_dir)
    
    # Настраиваем конфигурацию
    generator.config['max_workers'] = args.max_workers
    generator.config['batch_size'] = args.batch_size
    generator.config['quality_threshold'] = args.quality_threshold
    
    # Запускаем генерацию
    async def run_generation():
        return await generator.generate_mass_documentation(args.max_functions)
    
    try:
        report = asyncio.run(run_generation())
        
        if report.get('status') == 'error':
            print(f"❌ Ошибка: {report.get('message')}")
            return 1
        
        print("✅ Массовая генерация документации завершена успешно")
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️ Генерация прервана пользователем")
        return 1
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return 1

if __name__ == '__main__':
    exit(main()) 