#!/usr/bin/env python3
"""
Notion Exporter
Экспорт документации в формат Notion
"""

class NotionExporter:
    """Экспортер для Notion"""
    
    def export_function(self, function_data: dict) -> dict:
        """Экспортирует функцию в формат Notion blocks"""
        blocks = [
            {
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": function_data['name']}}]
                }
            },
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": f"Категория: {function_data.get('category', 'utilities')}"}}
                    ]
                }
            },
            {
                "type": "code",
                "code": {
                    "language": "c",
                    "rich_text": [{"type": "text", "text": {"content": function_data.get('signature', 'Сигнатура не определена')}}]
                }
            }
        ]
        
        return {"blocks": blocks}
    
    def export_batch(self, functions: list, output_file: str):
        """Экспортирует пакет функций"""
        import json
        
        all_blocks = []
        for func in functions:
            notion_data = self.export_function(func)
            all_blocks.extend(notion_data['blocks'])
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({"blocks": all_blocks}, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Экспорт в Notion: {output_file}")

if __name__ == '__main__':
    exporter = NotionExporter()
    print("📝 Notion Exporter готов к использованию")
