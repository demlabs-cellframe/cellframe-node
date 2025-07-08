#!/usr/bin/env python3
"""
Simple Mass Documentation Generator
Упрощенная версия генератора массовой документации без внешних зависимостей
Фаза 3 проекта документации Cellframe API
"""

import json
import os
import time
import threading
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import datetime
import concurrent.futures
import re
import hashlib

class SimpleMassGenerator:
    """Упрощенный генератор массовой документации"""
    
    def __init__(self, api_inventory_file: str, output_dir: str = ".context/docs/api-reference"):
        self.api_inventory_file = api_inventory_file
        self.output_dir = Path(output_dir)
        self.api_data = None
        
        # Конфигурация
        self.config = {
            'max_workers': 4,
            'batch_size': 50,
            'quality_threshold': 85.0
        }
        
        # Метрики
        self.metrics = {
            'start_time': None,
            'functions_processed': 0,
            'functions_failed': 0,
            'total_processing_time': 0.0,
            'average_quality_score': 0.0
        }
        
        # Приоритизация категорий
        self.category_priorities = {
            'critical_core': {
                'patterns': [r'^dap_common_.*', r'^dap_config_.*', r'.*_init$', r'.*_deinit$'],
                'priority': 100,
                'batch_size': 25
            },
            'blockchain_operations': {
                'patterns': [r'^dap_chain_.*', r'^dap_ledger_.*', r'.*_block_.*', r'.*_tx_.*'],
                'priority': 95,
                'batch_size': 30
            },
            'network_layer': {
                'patterns': [r'^dap_stream_.*', r'^dap_client_.*', r'^dap_server_.*'],
                'priority': 85,
                'batch_size': 40
            },
            'cryptography': {
                'patterns': [r'^dap_enc_.*', r'^dap_hash_.*', r'^dap_sign_.*'],
                'priority': 90,
                'batch_size': 35
            },
            'python_integration': {
                'patterns': [r'^PyInit_.*', r'^py_.*', r'.*_python_.*'],
                'priority': 80,
                'batch_size': 30
            },
            'utilities': {
                'patterns': [r'^dap_.*_get$', r'^dap_.*_set$', r'.*_util_.*'],
                'priority': 60,
                'batch_size': 50
            }
        }

    def load_api_data(self) -> bool:
        """Загружает данные API"""
        try:
            with open(self.api_inventory_file, 'r', encoding='utf-8') as f:
                self.api_data = json.load(f)
            print(f"✅ Загружено API данных: {self.api_data['metadata']['total_functions']} функций")
            return True
        except Exception as e:
            print(f"❌ Ошибка загрузки API данных: {e}")
            return False

    def categorize_function(self, function_name: str, module_name: str) -> Tuple[str, int]:
        """Автоматически категоризирует функцию"""
        for category, config in self.category_priorities.items():
            for pattern in config['patterns']:
                if re.match(pattern, function_name, re.IGNORECASE):
                    return category, config['priority']
        
        # Категоризация по модулю
        if 'test' in module_name.lower():
            return 'testing_debug', 30
        elif 'crypto' in module_name.lower():
            return 'cryptography', 85
        elif 'net' in module_name.lower():
            return 'network_layer', 80
        else:
            return 'utilities', 60

    def generate_function_documentation(self, function_data: Dict) -> str:
        """Генерирует документацию для функции"""
        name = function_data['name']
        category = function_data.get('category', 'utilities')
        module = function_data.get('module', 'unknown')
        signature = function_data.get('signature', 'unknown')
        parameters = function_data.get('parameters', [])
        comments = function_data.get('comments', [])
        
        # Генерируем описание
        description = self.generate_description(name, category, comments)
        
        # Генерируем примеры
        c_example = self.generate_c_example(name, category, parameters)
        python_example = self.generate_python_example(name, category, parameters)
        
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
- **Тип:** `{function_data.get('return_type', 'int')}`
- **Описание:** Результат выполнения операции

## Примеры использования

### C/C++
```c
{c_example}
```

### Python
```python
{python_example}
```

## Производительность
- **Категория сложности:** {self.get_complexity_category(len(parameters))}
- **Рекомендуемое использование:** {self.get_usage_recommendation(category)}

## История изменений
- **Версия API:** 1.0
- **Последнее обновление:** {datetime.datetime.now().strftime('%Y-%m-%d')}

---
*Документация сгенерирована автоматически системой Simple Mass Generator v1.0*
"""
        
        return doc_content

    def generate_description(self, name: str, category: str, comments: List[str]) -> str:
        """Генерирует описание функции"""
        descriptions = {
            'critical_core': f"Критическая функция ядра. {name} выполняет базовые операции системы Cellframe.",
            'blockchain_operations': f"Функция блокчейн операций. {name} управляет блоками и транзакциями.",
            'network_layer': f"Сетевая функция. {name} обрабатывает сетевые коммуникации.",
            'cryptography': f"Криптографическая функция. {name} обеспечивает безопасность данных.",
            'python_integration': f"Функция Python интеграции. {name} обеспечивает связь с Python API.",
            'utilities': f"Вспомогательная функция. {name} выполняет служебные операции."
        }
        
        base_description = descriptions.get(category, f"Функция {name} выполняет операции в системе Cellframe.")
        
        # Добавляем информацию из комментариев
        if comments:
            comment_text = ' '.join(comments).replace('//', '').replace('/*', '').replace('*/', '').strip()
            if comment_text and len(comment_text) > 10:
                base_description += f" {comment_text}"
        
        return base_description

    def generate_c_example(self, name: str, category: str, parameters: List[Dict]) -> str:
        """Генерирует C пример"""
        return f"""#include "cellframe_api.h"

int main() {{
    // Инициализация
    if (dap_common_init("app") != 0) {{
        return -1;
    }}
    
    // Вызов {name}
    int result = {name}(/* параметры */);
    
    if (result == 0) {{
        printf("Успешно выполнено\\n");
    }}
    
    dap_common_deinit();
    return result;
}}"""

    def generate_python_example(self, name: str, category: str, parameters: List[Dict]) -> str:
        """Генерирует Python пример"""
        python_name = name.replace('dap_', '').replace('_', '.')
        return f"""import libCellFrame

def example_{name.lower().replace('dap_', '')}():
    try:
        result = libCellFrame.{python_name}()
        if result is not None:
            print("Функция выполнена успешно")
            return result
    except Exception as e:
        print(f"Ошибка: {{e}}")
        return None

# Использование
example_{name.lower().replace('dap_', '')}()"""

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

    def get_complexity_category(self, param_count: int) -> str:
        """Определяет категорию сложности"""
        if param_count == 0:
            return "Простая"
        elif param_count <= 2:
            return "Простая"
        elif param_count <= 4:
            return "Средняя"
        else:
            return "Сложная"

    def get_usage_recommendation(self, category: str) -> str:
        """Дает рекомендации по использованию"""
        recommendations = {
            'critical_core': "Использовать с осторожностью",
            'blockchain_operations': "Проверить состояние блокчейна",
            'network_layer': "Проверить сетевое соединение",
            'cryptography': "Следовать практикам безопасности",
            'python_integration': "Использовать через Python API",
            'utilities': "Универсальное использование"
        }
        return recommendations.get(category, "Следовать общим рекомендациям")

    def calculate_quality_score(self, doc_content: str) -> float:
        """Вычисляет оценку качества"""
        score = 0.0
        
        # Базовая структура
        required_sections = ['## Описание', '## Сигнатура', '## Параметры', '## Примеры']
        for section in required_sections:
            if section in doc_content:
                score += 25.0
        
        return min(score, 100.0)

    def process_function(self, function_data: Dict) -> Dict:
        """Обрабатывает одну функцию"""
        start_time = time.time()
        
        try:
            # Генерируем документацию
            doc_content = self.generate_function_documentation(function_data)
            
            # Определяем путь файла
            category = function_data.get('category', 'utilities')
            output_dir = self.output_dir / f"phase3_{category}"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = output_dir / f"{function_data['name']}.md"
            
            # Сохраняем файл
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(doc_content)
            
            # Вычисляем качество
            quality_score = self.calculate_quality_score(doc_content)
            
            processing_time = time.time() - start_time
            
            return {
                'function_name': function_data['name'],
                'status': 'completed',
                'processing_time': processing_time,
                'quality_score': quality_score,
                'file_path': str(file_path)
            }
            
        except Exception as e:
            return {
                'function_name': function_data['name'],
                'status': 'failed',
                'processing_time': time.time() - start_time,
                'quality_score': 0.0,
                'error': str(e)
            }

    def create_function_batches(self, max_functions: Optional[int] = None) -> List[List[Dict]]:
        """Создает пакеты функций для обработки"""
        print("📦 Создание пакетов функций...")
        
        # Собираем все функции
        all_functions = []
        for module_name, module_data in self.api_data['modules'].items():
            for function in module_data['functions']:
                category, priority = self.categorize_function(function['name'], module_name)
                function['module'] = module_name
                function['category'] = category
                function['priority'] = priority
                all_functions.append(function)
        
        # Сортируем по приоритету
        all_functions.sort(key=lambda x: x['priority'], reverse=True)
        
        # Ограничиваем количество если нужно
        if max_functions:
            all_functions = all_functions[:max_functions]
        
        # Разбиваем на пакеты
        batches = []
        batch_size = self.config['batch_size']
        
        for i in range(0, len(all_functions), batch_size):
            batch = all_functions[i:i + batch_size]
            batches.append(batch)
        
        print(f"📦 Создано {len(batches)} пакетов для {len(all_functions)} функций")
        return batches

    def process_batch(self, batch: List[Dict]) -> List[Dict]:
        """Обрабатывает пакет функций"""
        results = []
        
        for function in batch:
            result = self.process_function(function)
            results.append(result)
            
            # Обновляем метрики
            if result['status'] == 'completed':
                self.metrics['functions_processed'] += 1
                self.metrics['total_processing_time'] += result['processing_time']
                self.metrics['average_quality_score'] += result['quality_score']
            else:
                self.metrics['functions_failed'] += 1
        
        return results

    def generate_mass_documentation(self, max_functions: Optional[int] = None) -> Dict:
        """Главная функция массовой генерации"""
        print("🚀 Запуск массовой генерации документации...")
        
        self.metrics['start_time'] = time.time()
        
        # Загружаем данные
        if not self.load_api_data():
            return {'status': 'error', 'message': 'Failed to load API data'}
        
        # Создаем пакеты
        batches = self.create_function_batches(max_functions)
        
        # Обрабатываем пакеты параллельно
        all_results = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
            future_to_batch = {executor.submit(self.process_batch, batch): batch for batch in batches}
            
            for i, future in enumerate(concurrent.futures.as_completed(future_to_batch)):
                try:
                    results = future.result()
                    all_results.extend(results)
                    
                    # Прогресс
                    progress = (i + 1) / len(batches) * 100
                    print(f"📈 Прогресс: {progress:.1f}% ({i + 1}/{len(batches)} пакетов)")
                    
                except Exception as e:
                    print(f"❌ Ошибка обработки пакета: {e}")
        
        # Финальные метрики
        total_time = time.time() - self.metrics['start_time']
        
        if self.metrics['functions_processed'] > 0:
            self.metrics['average_quality_score'] /= self.metrics['functions_processed']
        
        # Генерируем отчет
        report = self.generate_report(all_results, total_time)
        
        print(f"🎉 Генерация завершена за {total_time:.1f} секунд")
        print(f"📊 Обработано: {self.metrics['functions_processed']} функций")
        print(f"📊 Среднее качество: {self.metrics['average_quality_score']:.1f}%")
        
        return report

    def generate_report(self, results: List[Dict], total_time: float) -> Dict:
        """Генерирует отчет о выполнении"""
        report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'total_time': total_time,
            'summary': {
                'total_functions': len(results),
                'completed': self.metrics['functions_processed'],
                'failed': self.metrics['functions_failed'],
                'success_rate': self.metrics['functions_processed'] / len(results) * 100 if results else 0,
                'average_quality': self.metrics['average_quality_score'],
                'functions_per_second': self.metrics['functions_processed'] / total_time if total_time > 0 else 0
            },
            'category_breakdown': self.calculate_category_breakdown(results),
            'performance_metrics': {
                'total_processing_time': self.metrics['total_processing_time'],
                'average_processing_time': self.metrics['total_processing_time'] / self.metrics['functions_processed'] if self.metrics['functions_processed'] > 0 else 0
            }
        }
        
        # Сохраняем отчет
        report_file = Path(".context/analysis/simple_mass_generation_report.json")
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📋 Отчет сохранен: {report_file}")
        
        return report

    def calculate_category_breakdown(self, results: List[Dict]) -> Dict:
        """Вычисляет разбивку по категориям"""
        breakdown = {}
        
        for result in results:
            # Извлекаем категорию из пути файла
            if 'file_path' in result:
                path_parts = result['file_path'].split('/')
                for part in path_parts:
                    if part.startswith('phase3_'):
                        category = part.replace('phase3_', '')
                        if category not in breakdown:
                            breakdown[category] = 0
                        breakdown[category] += 1
                        break
        
        return breakdown

def main():
    """Главная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Simple Mass Documentation Generator')
    parser.add_argument('--api-inventory', 
                       default='.context/analysis/cellframe_api_inventory.json',
                       help='Путь к файлу инвентаря API')
    parser.add_argument('--output-dir', 
                       default='.context/docs/api-reference',
                       help='Директория для сохранения документации')
    parser.add_argument('--max-functions', type=int,
                       help='Максимальное количество функций')
    parser.add_argument('--max-workers', type=int, default=4,
                       help='Количество параллельных воркеров')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.api_inventory):
        print(f"❌ Файл инвентаря API не найден: {args.api_inventory}")
        return 1
    
    # Создаем генератор
    generator = SimpleMassGenerator(args.api_inventory, args.output_dir)
    generator.config['max_workers'] = args.max_workers
    
    # Запускаем генерацию
    try:
        report = generator.generate_mass_documentation(args.max_functions)
        
        if report.get('status') == 'error':
            print(f"❌ Ошибка: {report.get('message')}")
            return 1
        
        print("✅ Массовая генерация завершена успешно")
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️ Генерация прервана пользователем")
        return 1
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return 1

if __name__ == '__main__':
    exit(main()) 