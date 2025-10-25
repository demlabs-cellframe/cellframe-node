#!/usr/bin/env python3
"""
Автоматический скрипт очистки и организации файловой структуры проекта
Поддерживает правильную архитектуру согласно СЛК стандартам
"""

import os
import shutil
from pathlib import Path
import re
from typing import List, Dict
import json
from datetime import datetime

class FileOrganizer:
    """Автоматический организатор файлов проекта"""
    
    def __init__(self, root_path: str = "."):
        self.root = Path(root_path).resolve()
        self.dry_run = False
        
        # Разрешенные файлы и папки в корне
        self.allowed_in_root = {
            '.git', '.context', 'slc-agent', '.cursorrules', 
            'README.md', 'slc', '.cursor', '.pytest_cache', 
            '.benchmarks', '.slc', '.gitignore'
        }
        
        # Правила перемещения
        self.move_rules = {
            'reports': {
                'patterns': [r'.*_REPORT\.md$', r'.*_ANALYSIS\.md$', r'.*_COMPLETION\.md$'],
                'destination': '.context/docs/reports/'
            },
            'plans': {
                'patterns': [r'.*_PLAN\.md$', r'.*_STRATEGY\.md$'],
                'destination': '.context/docs/plans/'
            },
            'archives': {
                'patterns': [r'.*\.slc-update$', r'backup_.*\.tar\.gz$'],
                'destination': '.context/archives/'
            },
            'temp': {
                'patterns': [r'test_.*\.py$', r'fix_.*\.py$', r'.*_temp\..*$', r'\..*_stats\.json$'],
                'destination': '.context/temp/'
            },
            'tasks': {
                'patterns': [r'ЗАДАЧА_.*\.md$', r'TASK_.*\.md$'],
                'destination': '.context/docs/reports/'
            }
        }
    
    def analyze_root_directory(self) -> Dict:
        """Анализ корневой директории"""
        analysis = {
            'total_items': 0,
            'allowed_items': [],
            'violations': [],
            'recommendations': []
        }
        
        for item in self.root.iterdir():
            analysis['total_items'] += 1
            
            if item.name in self.allowed_in_root:
                analysis['allowed_items'].append(item.name)
            else:
                analysis['violations'].append({
                    'name': item.name,
                    'type': 'directory' if item.is_dir() else 'file',
                    'size': item.stat().st_size if item.is_file() else None,
                    'recommended_action': self._get_recommended_action(item)
                })
        
        return analysis
    
    def _get_recommended_action(self, item: Path) -> Dict:
        """Получить рекомендуемое действие для элемента"""
        for rule_name, rule in self.move_rules.items():
            for pattern in rule['patterns']:
                if re.match(pattern, item.name, re.IGNORECASE):
                    return {
                        'action': 'move',
                        'destination': rule['destination'],
                        'rule': rule_name
                    }
        
        if item.is_dir():
            return {
                'action': 'move',
                'destination': '.context/',
                'rule': 'project_directories'
            }
        else:
            return {
                'action': 'review',
                'destination': '.context/temp/',
                'rule': 'manual_review'
            }
    
    def create_required_directories(self):
        """Создание необходимых директорий"""
        required_dirs = [
            '.context/docs/reports',
            '.context/docs/plans', 
            '.context/archives',
            '.context/temp'
        ]
        
        for dir_path in required_dirs:
            full_path = self.root / dir_path
            if not full_path.exists():
                if not self.dry_run:
                    full_path.mkdir(parents=True, exist_ok=True)
                    print(f"✅ Создана директория: {dir_path}")
                else:
                    print(f"🔍 [DRY RUN] Будет создана: {dir_path}")
    
    def organize_files(self, auto_approve: bool = False) -> Dict:
        """Основная функция организации файлов"""
        print("🗂️ Анализ файловой структуры...")
        
        analysis = self.analyze_root_directory()
        
        print(f"\n📊 АНАЛИЗ КОРНЕВОЙ ДИРЕКТОРИИ:")
        print(f"Всего элементов: {analysis['total_items']}")
        print(f"Разрешенных: {len(analysis['allowed_items'])}")
        print(f"Нарушений: {len(analysis['violations'])}")
        
        if not analysis['violations']:
            print("✅ Файловая структура соответствует стандартам!")
            return analysis
        
        print(f"\n🚨 НАЙДЕНЫ НАРУШЕНИЯ:")
        for violation in analysis['violations']:
            action = violation['recommended_action']
            print(f"  📁 {violation['name']} → {action['destination']} ({action['rule']})")
        
        if not auto_approve and not self.dry_run:
            response = input(f"\n❓ Применить изменения? (y/N): ")
            if response.lower() != 'y':
                print("❌ Операция отменена")
                return analysis
        
        # Создаем необходимые директории
        self.create_required_directories()
        
        # Применяем изменения
        moved_count = 0
        for violation in analysis['violations']:
            item_path = self.root / violation['name']
            action = violation['recommended_action']
            dest_path = self.root / action['destination'] / violation['name']
            
            try:
                if not self.dry_run:
                    if dest_path.exists():
                        print(f"⚠️ Файл уже существует: {dest_path}")
                        continue
                    
                    shutil.move(str(item_path), str(dest_path))
                    print(f"✅ Перемещен: {violation['name']} → {action['destination']}")
                else:
                    print(f"🔍 [DRY RUN] {violation['name']} → {action['destination']}")
                
                moved_count += 1
                
            except Exception as e:
                print(f"❌ Ошибка перемещения {violation['name']}: {e}")
        
        print(f"\n🎉 Обработано файлов: {moved_count}")
        
        # Повторный анализ
        final_analysis = self.analyze_root_directory()
        print(f"📊 ИТОГ: {final_analysis['total_items']} элементов в корне")
        
        return final_analysis
    
    def generate_report(self) -> str:
        """Генерация отчета об организации"""
        analysis = self.analyze_root_directory()
        
        report = f"""
# 📊 Отчет об организации файловой структуры
**Дата**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Статистика
- **Всего элементов в корне**: {analysis['total_items']}
- **Соответствуют стандартам**: {len(analysis['allowed_items'])}
- **Нарушения стандартов**: {len(analysis['violations'])}

## Разрешенные элементы
{chr(10).join(f'- {item}' for item in analysis['allowed_items'])}

## Нарушения
{chr(10).join(f'- **{v["name"]}** → {v["recommended_action"]["destination"]}' for v in analysis['violations'])}

## Рекомендации
{'✅ Структура соответствует стандартам!' if not analysis['violations'] else '🔧 Запустите организацию файлов: python .context/tools/scripts/cleanup_file_organization.py'}
"""
        return report

def main():
    """Основная функция"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Автоматическая организация файлов проекта')
    parser.add_argument('--dry-run', action='store_true', help='Показать изменения без применения')
    parser.add_argument('--auto', action='store_true', help='Автоматическое применение без подтверждения')
    parser.add_argument('--report', action='store_true', help='Только сгенерировать отчет')
    
    args = parser.parse_args()
    
    organizer = FileOrganizer()
    organizer.dry_run = args.dry_run
    
    if args.report:
        print(organizer.generate_report())
    else:
        organizer.organize_files(auto_approve=args.auto)

if __name__ == "__main__":
    main() 