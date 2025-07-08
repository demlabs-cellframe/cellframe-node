#!/usr/bin/env python3
"""
Documentation Validator & Quality Assurance
Автоматическая валидация и контроль качества документации Cellframe
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import datetime

class DocumentationValidator:
    """Валидатор качества документации"""
    
    def __init__(self, docs_dir: str):
        self.docs_dir = Path(docs_dir)
        self.validation_results = {
            'timestamp': datetime.datetime.now().isoformat(),
            'total_files': 0,
            'validated_files': 0,
            'issues_found': 0,
            'quality_score': 0.0,
            'files': {},
            'summary': {},
            'recommendations': []
        }
        
        # Критерии качества документации
        self.quality_criteria = {
            'structure': {
                'required_sections': [
                    'Описание', 'Сигнатура', 'Параметры', 'Возвращаемое значение',
                    'Пример использования', 'Связанные функции'
                ],
                'weight': 30
            },
            'examples': {
                'required_languages': ['C/C++', 'Python'],
                'min_example_lines': 5,
                'weight': 25
            },
            'parameters': {
                'required_fields': ['Параметр', 'Тип', 'Описание'],
                'min_description_length': 10,
                'weight': 20
            },
            'completeness': {
                'min_description_length': 50,
                'required_error_codes': True,
                'weight': 15
            },
            'formatting': {
                'code_blocks': True,
                'tables': True,
                'links': True,
                'weight': 10
            }
        }

    def validate_file_structure(self, content: str, filename: str) -> Dict:
        """Валидирует структуру файла документации"""
        issues = []
        score = 0
        max_score = self.quality_criteria['structure']['weight']
        
        required_sections = self.quality_criteria['structure']['required_sections']
        found_sections = []
        
        # Проверяем наличие обязательных разделов
        for section in required_sections:
            pattern = rf'^#+\s*{re.escape(section)}'
            if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                found_sections.append(section)
            else:
                issues.append(f"Отсутствует раздел: {section}")
        
        # Вычисляем оценку
        score = (len(found_sections) / len(required_sections)) * max_score
        
        return {
            'score': score,
            'max_score': max_score,
            'issues': issues,
            'found_sections': found_sections,
            'missing_sections': list(set(required_sections) - set(found_sections))
        }

    def validate_examples(self, content: str, filename: str) -> Dict:
        """Валидирует примеры кода"""
        issues = []
        score = 0
        max_score = self.quality_criteria['examples']['weight']
        
        required_languages = self.quality_criteria['examples']['required_languages']
        min_lines = self.quality_criteria['examples']['min_example_lines']
        
        found_examples = {}
        
        # Ищем блоки кода для каждого языка
        for lang in required_languages:
            lang_pattern = rf'###\s*{re.escape(lang)}.*?```\w*\n(.*?)```'
            matches = re.findall(lang_pattern, content, re.DOTALL | re.IGNORECASE)
            
            if matches:
                example_code = matches[0].strip()
                lines_count = len([line for line in example_code.split('\n') if line.strip()])
                
                found_examples[lang] = {
                    'present': True,
                    'lines_count': lines_count,
                    'adequate_length': lines_count >= min_lines
                }
                
                if lines_count < min_lines:
                    issues.append(f"Пример {lang} слишком короткий ({lines_count} строк, минимум {min_lines})")
            else:
                found_examples[lang] = {'present': False, 'lines_count': 0, 'adequate_length': False}
                issues.append(f"Отсутствует пример для {lang}")
        
        # Вычисляем оценку
        present_count = sum(1 for ex in found_examples.values() if ex['present'])
        adequate_count = sum(1 for ex in found_examples.values() if ex['adequate_length'])
        
        score = ((present_count * 0.5 + adequate_count * 0.5) / len(required_languages)) * max_score
        
        return {
            'score': score,
            'max_score': max_score,
            'issues': issues,
            'found_examples': found_examples
        }

    def validate_parameters_table(self, content: str, filename: str) -> Dict:
        """Валидирует таблицу параметров"""
        issues = []
        score = 0
        max_score = self.quality_criteria['parameters']['weight']
        
        # Ищем таблицу параметров
        table_pattern = r'\|.*Параметр.*\|.*Тип.*\|.*Описание.*\|(.*?)(?=\n\n|\n#|$)'
        table_match = re.search(table_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if not table_match:
            issues.append("Отсутствует таблица параметров")
            return {
                'score': 0,
                'max_score': max_score,
                'issues': issues,
                'parameters_count': 0,
                'adequate_descriptions': 0
            }
        
        table_content = table_match.group(1)
        parameter_rows = [row for row in table_content.split('\n') if '|' in row and not row.strip().startswith('|---')]
        
        parameters_count = len(parameter_rows)
        adequate_descriptions = 0
        min_desc_length = self.quality_criteria['parameters']['min_description_length']
        
        for row in parameter_rows:
            cells = [cell.strip() for cell in row.split('|') if cell.strip()]
            if len(cells) >= 3:  # Параметр, Тип, Описание
                description = cells[2] if len(cells) > 2 else ""
                if len(description) >= min_desc_length:
                    adequate_descriptions += 1
                else:
                    issues.append(f"Слишком короткое описание параметра: {description[:20]}...")
        
        # Вычисляем оценку
        if parameters_count > 0:
            score = (adequate_descriptions / parameters_count) * max_score
        else:
            score = max_score  # Если параметров нет, это нормально для некоторых функций
        
        return {
            'score': score,
            'max_score': max_score,
            'issues': issues,
            'parameters_count': parameters_count,
            'adequate_descriptions': adequate_descriptions
        }

    def validate_completeness(self, content: str, filename: str) -> Dict:
        """Валидирует полноту документации"""
        issues = []
        score = 0
        max_score = self.quality_criteria['completeness']['weight']
        
        # Проверяем длину описания
        description_pattern = r'##\s*Описание\s*\n(.*?)(?=\n##|\n#|$)'
        desc_match = re.search(description_pattern, content, re.DOTALL)
        
        description_length = 0
        if desc_match:
            description_text = desc_match.group(1).strip()
            description_length = len(description_text)
        
        min_desc_length = self.quality_criteria['completeness']['min_description_length']
        if description_length < min_desc_length:
            issues.append(f"Описание слишком короткое ({description_length} символов, минимум {min_desc_length})")
        
        # Проверяем наличие кодов ошибок
        error_codes_present = bool(re.search(r'##\s*Коды?\s*ошибок?', content, re.IGNORECASE))
        if not error_codes_present:
            issues.append("Отсутствует раздел с кодами ошибок")
        
        # Вычисляем оценку
        desc_score = min(description_length / min_desc_length, 1.0) * 0.7
        error_score = 0.3 if error_codes_present else 0
        score = (desc_score + error_score) * max_score
        
        return {
            'score': score,
            'max_score': max_score,
            'issues': issues,
            'description_length': description_length,
            'error_codes_present': error_codes_present
        }

    def validate_formatting(self, content: str, filename: str) -> Dict:
        """Валидирует форматирование документации"""
        issues = []
        score = 0
        max_score = self.quality_criteria['formatting']['weight']
        
        # Проверяем блоки кода
        code_blocks = len(re.findall(r'```\w*\n.*?```', content, re.DOTALL))
        if code_blocks < 2:
            issues.append("Недостаточно блоков кода (минимум 2)")
        
        # Проверяем таблицы
        tables = len(re.findall(r'\|.*\|.*\|', content))
        if tables < 1:
            issues.append("Отсутствуют таблицы")
        
        # Проверяем ссылки
        links = len(re.findall(r'\[.*?\]\(.*?\)', content))
        if links < 1:
            issues.append("Отсутствуют ссылки")
        
        # Проверяем inline код
        inline_code = len(re.findall(r'`[^`]+`', content))
        
        # Вычисляем оценку
        formatting_score = 0
        formatting_score += 0.4 if code_blocks >= 2 else (code_blocks * 0.2)
        formatting_score += 0.3 if tables >= 1 else 0
        formatting_score += 0.2 if links >= 1 else 0
        formatting_score += 0.1 if inline_code >= 5 else (inline_code * 0.02)
        
        score = min(formatting_score, 1.0) * max_score
        
        return {
            'score': score,
            'max_score': max_score,
            'issues': issues,
            'code_blocks': code_blocks,
            'tables': tables,
            'links': links,
            'inline_code': inline_code
        }

    def validate_file(self, file_path: Path) -> Dict:
        """Валидирует один файл документации"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {
                'filename': file_path.name,
                'error': f"Ошибка чтения файла: {e}",
                'total_score': 0,
                'max_total_score': 100
            }
        
        filename = file_path.name
        
        # Выполняем все проверки
        structure_result = self.validate_file_structure(content, filename)
        examples_result = self.validate_examples(content, filename)
        parameters_result = self.validate_parameters_table(content, filename)
        completeness_result = self.validate_completeness(content, filename)
        formatting_result = self.validate_formatting(content, filename)
        
        # Собираем все проблемы
        all_issues = []
        all_issues.extend(structure_result['issues'])
        all_issues.extend(examples_result['issues'])
        all_issues.extend(parameters_result['issues'])
        all_issues.extend(completeness_result['issues'])
        all_issues.extend(formatting_result['issues'])
        
        # Вычисляем общую оценку
        total_score = (
            structure_result['score'] +
            examples_result['score'] +
            parameters_result['score'] +
            completeness_result['score'] +
            formatting_result['score']
        )
        
        max_total_score = 100  # Сумма всех весов
        
        return {
            'filename': filename,
            'total_score': total_score,
            'max_total_score': max_total_score,
            'percentage': (total_score / max_total_score) * 100,
            'issues_count': len(all_issues),
            'issues': all_issues,
            'details': {
                'structure': structure_result,
                'examples': examples_result,
                'parameters': parameters_result,
                'completeness': completeness_result,
                'formatting': formatting_result
            }
        }

    def generate_improvement_suggestions(self, file_result: Dict) -> List[str]:
        """Генерирует предложения по улучшению"""
        suggestions = []
        details = file_result['details']
        
        # Предложения по структуре
        if details['structure']['score'] < details['structure']['max_score']:
            missing = details['structure']['missing_sections']
            if missing:
                suggestions.append(f"Добавить отсутствующие разделы: {', '.join(missing)}")
        
        # Предложения по примерам
        if details['examples']['score'] < details['examples']['max_score']:
            for lang, info in details['examples']['found_examples'].items():
                if not info['present']:
                    suggestions.append(f"Добавить пример кода для {lang}")
                elif not info['adequate_length']:
                    suggestions.append(f"Расширить пример для {lang} (минимум 5 строк кода)")
        
        # Предложения по параметрам
        if details['parameters']['score'] < details['parameters']['max_score']:
            if details['parameters']['parameters_count'] > 0:
                suggestions.append("Улучшить описания параметров (минимум 10 символов каждое)")
        
        # Предложения по полноте
        if details['completeness']['score'] < details['completeness']['max_score']:
            if details['completeness']['description_length'] < 50:
                suggestions.append("Расширить описание функции (минимум 50 символов)")
            if not details['completeness']['error_codes_present']:
                suggestions.append("Добавить раздел с кодами ошибок")
        
        # Предложения по форматированию
        if details['formatting']['score'] < details['formatting']['max_score']:
            if details['formatting']['code_blocks'] < 2:
                suggestions.append("Добавить больше примеров кода")
            if details['formatting']['tables'] < 1:
                suggestions.append("Добавить таблицы для структурирования информации")
            if details['formatting']['links'] < 1:
                suggestions.append("Добавить ссылки на связанную документацию")
        
        return suggestions

    def validate_all_files(self) -> Dict:
        """Валидирует все файлы в директории"""
        print(f"🔍 Валидация документации в {self.docs_dir}")
        
        # Находим все .md файлы
        md_files = list(self.docs_dir.glob('**/*.md'))
        self.validation_results['total_files'] = len(md_files)
        
        if not md_files:
            print("❌ Файлы документации не найдены")
            return self.validation_results
        
        total_score = 0
        total_issues = 0
        
        # Валидируем каждый файл
        for file_path in md_files:
            print(f"📄 Проверка: {file_path.name}")
            result = self.validate_file(file_path)
            
            self.validation_results['files'][result['filename']] = result
            total_score += result['total_score']
            total_issues += result['issues_count']
            
            # Генерируем предложения по улучшению
            suggestions = self.generate_improvement_suggestions(result)
            if suggestions:
                self.validation_results['files'][result['filename']]['suggestions'] = suggestions
        
        self.validation_results['validated_files'] = len(md_files)
        self.validation_results['issues_found'] = total_issues
        self.validation_results['quality_score'] = (total_score / (len(md_files) * 100)) * 100
        
        # Генерируем общие рекомендации
        self.generate_global_recommendations()
        
        return self.validation_results

    def generate_global_recommendations(self):
        """Генерирует глобальные рекомендации по улучшению"""
        files_data = self.validation_results['files']
        
        # Анализируем общие проблемы
        common_issues = {}
        for file_data in files_data.values():
            for issue in file_data.get('issues', []):
                common_issues[issue] = common_issues.get(issue, 0) + 1
        
        # Топ-5 самых частых проблем
        top_issues = sorted(common_issues.items(), key=lambda x: x[1], reverse=True)[:5]
        
        recommendations = []
        
        if top_issues:
            recommendations.append("🎯 Приоритетные улучшения:")
            for issue, count in top_issues:
                percentage = (count / self.validation_results['validated_files']) * 100
                recommendations.append(f"- {issue} (в {count} файлах, {percentage:.1f}%)")
        
        # Рекомендации по качеству
        avg_score = self.validation_results['quality_score']
        if avg_score < 70:
            recommendations.append("⚠️ Критический уровень качества - требуется комплексная доработка")
        elif avg_score < 85:
            recommendations.append("📈 Хороший уровень качества - требуются точечные улучшения")
        else:
            recommendations.append("✅ Отличный уровень качества - поддерживайте стандарт")
        
        # Автоматизация
        if self.validation_results['issues_found'] > 10:
            recommendations.append("🤖 Рекомендуется настроить автоматическую проверку качества в CI/CD")
        
        self.validation_results['recommendations'] = recommendations

    def save_report(self, output_file: str = None):
        """Сохраняет отчет о валидации"""
        if not output_file:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f".context/analysis/documentation_validation_{timestamp}.json"
        
        # Создаем директорию если не существует
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, ensure_ascii=False, indent=2)
        
        print(f"📊 Отчет сохранен: {output_file}")
        return output_file

    def print_summary(self):
        """Выводит краткий отчет"""
        results = self.validation_results
        
        print("\n" + "="*60)
        print("📋 ОТЧЕТ О ВАЛИДАЦИИ ДОКУМЕНТАЦИИ")
        print("="*60)
        
        print(f"📁 Проверено файлов: {results['validated_files']}")
        print(f"🎯 Общий балл качества: {results['quality_score']:.1f}/100")
        print(f"⚠️ Найдено проблем: {results['issues_found']}")
        
        # Топ проблемных файлов
        files_by_score = sorted(
            results['files'].items(),
            key=lambda x: x[1]['percentage']
        )
        
        print("\n🔴 Файлы требующие внимания:")
        for filename, data in files_by_score[:5]:
            print(f"  {filename}: {data['percentage']:.1f}% ({data['issues_count']} проблем)")
        
        # Лучшие файлы
        print("\n🟢 Лучшие файлы:")
        for filename, data in files_by_score[-3:]:
            print(f"  {filename}: {data['percentage']:.1f}%")
        
        # Рекомендации
        if results['recommendations']:
            print("\n💡 Рекомендации:")
            for rec in results['recommendations']:
                print(f"  {rec}")
        
        print("\n" + "="*60)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Documentation Validator & Quality Assurance')
    parser.add_argument('--docs-dir', 
                       default='.context/docs/api-reference/top20',
                       help='Директория с документацией для проверки')
    parser.add_argument('--output', 
                       help='Файл для сохранения отчета')
    parser.add_argument('--quiet', action='store_true',
                       help='Тихий режим (только JSON отчет)')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.docs_dir):
        print(f"❌ Директория не найдена: {args.docs_dir}")
        return 1
    
    validator = DocumentationValidator(args.docs_dir)
    results = validator.validate_all_files()
    
    # Сохраняем отчет
    report_file = validator.save_report(args.output)
    
    if not args.quiet:
        validator.print_summary()
    
    # Возвращаем соответствующий код выхода
    if results['quality_score'] < 70:
        return 2  # Критические проблемы
    elif results['quality_score'] < 85:
        return 1  # Есть проблемы
    else:
        return 0  # Все хорошо

if __name__ == '__main__':
    exit(main()) 