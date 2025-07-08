#!/usr/bin/env python3
"""
Confluence Exporter
Экспорт документации в формат Confluence
"""

import json
from pathlib import Path

class ConfluenceExporter:
    """Экспортер для Confluence"""
    
    def export_function(self, function_data: dict) -> str:
        """Экспортирует функцию в формат Confluence"""
        name = function_data['name']
        category = function_data.get('category', 'utilities')
        
        confluence_content = f"""h1. {name}

*Категория:* {category}
*Модуль:* {function_data.get('module', 'unknown')}

h2. Описание
{function_data.get('description', 'Описание будет добавлено')}

h2. Сигнатура
{{code:language=c}}
{function_data.get('signature', 'Сигнатура не определена')}
{{code}}

h2. Примеры использования

h3. C/C++
{{code:language=c}}
// Пример использования {name}
int result = {name}(/* параметры */);
{{code}}

h3. Python
{{code:language=python}}
# Пример использования {name}
result = libCellFrame.{name.replace('dap_', '').replace('_', '.')}()
{{code}}

----
_Документация сгенерирована автоматически_
"""
        return confluence_content
    
    def export_batch(self, functions: list, output_file: str):
        """Экспортирует пакет функций"""
        content = []
        for func in functions:
            content.append(self.export_function(func))
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n\n'.join(content))
        
        print(f"✅ Экспорт в Confluence: {output_file}")

if __name__ == '__main__':
    exporter = ConfluenceExporter()
    print("📝 Confluence Exporter готов к использованию")
