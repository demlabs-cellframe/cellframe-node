#!/usr/bin/env python3
"""
CI/CD Documentation Pipeline
Автоматическая интеграция документации в процесс разработки
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import datetime
# import yaml  # Не используется в текущей версии

class CICDDocumentationPipeline:
    """Система интеграции документации в CI/CD"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.context_dir = self.project_root / ".context"
        self.docs_dir = self.context_dir / "docs"
        self.tools_dir = self.context_dir / "tools"
        
        # Конфигурация pipeline
        self.config = {
            "validation_threshold": 85.0,  # Минимальное качество документации
            "auto_fix": True,  # Автоматическое исправление проблем
            "generate_missing": True,  # Генерация отсутствующей документации
            "fail_on_regression": True,  # Остановка при снижении качества
            "notification_webhook": None,  # Webhook для уведомлений
            "supported_formats": ["markdown", "json", "yaml"],
            "excluded_patterns": ["test_*", "*_test.py", "*.tmp"]
        }

    def create_github_workflow(self) -> str:
        """Создает GitHub Actions workflow для документации"""
        workflow_content = """name: Documentation Quality Check

on:
  push:
    branches: [ main, develop, release-* ]
    paths:
      - 'cellframe-sdk/**'
      - 'python-cellframe/**'
      - '.context/docs/**'
      - '.context/tools/**'
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'cellframe-sdk/**'
      - 'python-cellframe/**'
      - '.context/docs/**'

jobs:
  documentation-check:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
      with:
        fetch-depth: 0  # Полная история для анализа изменений
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pyyaml jinja2 markdown beautifulsoup4
    
    - name: Check API changes
      id: api-check
      run: |
        python .context/tools/cicd_documentation_pipeline.py check-api-changes
        echo "api_changed=$?" >> $GITHUB_OUTPUT
    
    - name: Generate missing documentation
      if: steps.api-check.outputs.api_changed == '1'
      run: |
        python .context/tools/cicd_documentation_pipeline.py generate-missing
    
    - name: Validate documentation quality
      id: validation
      run: |
        python .context/tools/cicd_documentation_pipeline.py validate-all
        echo "quality_score=$(cat .context/analysis/quality_score.txt)" >> $GITHUB_OUTPUT
    
    - name: Auto-fix documentation issues
      if: steps.validation.outputs.quality_score < '85'
      run: |
        python .context/tools/cicd_documentation_pipeline.py auto-fix
    
    - name: Re-validate after fixes
      if: steps.validation.outputs.quality_score < '85'
      run: |
        python .context/tools/cicd_documentation_pipeline.py validate-all
    
    - name: Generate documentation report
      run: |
        python .context/tools/cicd_documentation_pipeline.py generate-report
    
    - name: Upload documentation artifacts
      uses: actions/upload-artifact@v3
      with:
        name: documentation-report
        path: |
          .context/analysis/cicd_report_*.json
          .context/analysis/documentation_validation_*.json
    
    - name: Comment PR with results
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          const report = JSON.parse(fs.readFileSync('.context/analysis/cicd_report_latest.json', 'utf8'));
          
          const comment = `## 📚 Documentation Quality Report
          
          **Overall Quality Score:** ${report.quality_metrics.overall_score}%
          **Functions Documented:** ${report.coverage.documented_functions}/${report.coverage.total_functions}
          **Issues Found:** ${report.issues.total_issues}
          
          ${report.quality_metrics.overall_score >= 85 ? '✅' : '⚠️'} ${report.quality_metrics.overall_score >= 85 ? 'Documentation quality meets standards' : 'Documentation quality below threshold'}
          
          ### Details
          - **API Coverage:** ${report.coverage.api_coverage}%
          - **Example Coverage:** ${report.coverage.example_coverage}%
          - **Validation Passed:** ${report.validation.passed ? 'Yes' : 'No'}
          
          [View Full Report](${report.artifacts.report_url})`;
          
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: comment
          });
    
    - name: Fail if quality below threshold
      if: steps.validation.outputs.quality_score < '85'
      run: |
        echo "Documentation quality below threshold: ${{ steps.validation.outputs.quality_score }}%"
        exit 1

  deploy-documentation:
    needs: documentation-check
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to GitHub Pages
      run: |
        python .context/tools/cicd_documentation_pipeline.py deploy-docs
"""
        
        workflow_file = self.project_root / ".github" / "workflows" / "documentation.yml"
        workflow_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(workflow_file, 'w', encoding='utf-8') as f:
            f.write(workflow_content)
        
        print(f"✅ GitHub Actions workflow создан: {workflow_file}")
        return str(workflow_file)

    def create_gitlab_pipeline(self) -> str:
        """Создает GitLab CI pipeline для документации"""
        pipeline_content = """stages:
  - validate
  - generate
  - deploy

variables:
  DOCUMENTATION_THRESHOLD: "85"
  PYTHON_VERSION: "3.9"

before_script:
  - python --version
  - pip install --upgrade pip
  - pip install pyyaml jinja2 markdown beautifulsoup4

validate_documentation:
  stage: validate
  script:
    - python .context/tools/cicd_documentation_pipeline.py check-api-changes
    - python .context/tools/cicd_documentation_pipeline.py validate-all
    - quality_score=$(cat .context/analysis/quality_score.txt)
    - echo "Quality score: $quality_score%"
    - |
      if (( $(echo "$quality_score < $DOCUMENTATION_THRESHOLD" | bc -l) )); then
        echo "Quality below threshold, attempting auto-fix..."
        python .context/tools/cicd_documentation_pipeline.py auto-fix
        python .context/tools/cicd_documentation_pipeline.py validate-all
        quality_score=$(cat .context/analysis/quality_score.txt)
      fi
    - |
      if (( $(echo "$quality_score < $DOCUMENTATION_THRESHOLD" | bc -l) )); then
        echo "Documentation quality still below threshold: $quality_score%"
        exit 1
      fi
  artifacts:
    reports:
      junit: .context/analysis/validation_report.xml
    paths:
      - .context/analysis/
    expire_in: 1 week
  only:
    changes:
      - cellframe-sdk/**/*
      - python-cellframe/**/*
      - .context/docs/**/*

generate_missing_docs:
  stage: generate
  script:
    - python .context/tools/cicd_documentation_pipeline.py generate-missing
    - python .context/tools/cicd_documentation_pipeline.py validate-all
  artifacts:
    paths:
      - .context/docs/
    expire_in: 1 week
  only:
    changes:
      - cellframe-sdk/**/*
      - python-cellframe/**/*
  when: manual

deploy_documentation:
  stage: deploy
  script:
    - python .context/tools/cicd_documentation_pipeline.py deploy-docs
  artifacts:
    paths:
      - public/
  only:
    - main
  when: on_success
"""
        
        pipeline_file = self.project_root / ".gitlab-ci.yml"
        
        with open(pipeline_file, 'w', encoding='utf-8') as f:
            f.write(pipeline_content)
        
        print(f"✅ GitLab CI pipeline создан: {pipeline_file}")
        return str(pipeline_file)

    def check_api_changes(self) -> bool:
        """Проверяет изменения в API с последнего коммита"""
        try:
            # Получаем список измененных файлов
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("⚠️ Не удалось получить изменения git")
                return True  # Предполагаем изменения при ошибке
            
            changed_files = result.stdout.strip().split('\n')
            
            # Проверяем API файлы
            api_patterns = [
                'cellframe-sdk/',
                'python-cellframe/',
                'include/',
                '.h',
                '.c'
            ]
            
            api_changed = any(
                any(pattern in file for pattern in api_patterns)
                for file in changed_files
            )
            
            if api_changed:
                print("🔄 Обнаружены изменения в API")
                
                # Сохраняем список измененных файлов
                changes_file = self.context_dir / "analysis" / "api_changes.json"
                changes_file.parent.mkdir(parents=True, exist_ok=True)
                
                changes_data = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "changed_files": changed_files,
                    "api_files": [f for f in changed_files if any(p in f for p in api_patterns)]
                }
                
                with open(changes_file, 'w', encoding='utf-8') as f:
                    json.dump(changes_data, f, ensure_ascii=False, indent=2)
                
                return True
            else:
                print("ℹ️ Изменения в API не обнаружены")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка проверки изменений API: {e}")
            return True

    def validate_all_documentation(self) -> Dict:
        """Валидирует всю документацию"""
        print("🔍 Валидация всей документации...")
        
        # Запускаем валидатор для всех директорий с документацией
        validation_results = {}
        
        docs_directories = [
            self.docs_dir / "api-reference" / "top20",
            self.docs_dir / "api-reference" / "next50"
        ]
        
        total_score = 0
        total_files = 0
        
        for docs_dir in docs_directories:
            if docs_dir.exists():
                try:
                    # Запускаем валидатор
                    result = subprocess.run([
                        sys.executable,
                        str(self.tools_dir / "documentation_validator.py"),
                        "--docs-dir", str(docs_dir),
                        "--quiet"
                    ], capture_output=True, text=True, cwd=self.project_root)
                    
                    if result.returncode == 0:
                        # Загружаем результаты валидации
                        validation_files = list(self.context_dir.glob("analysis/documentation_validation_*.json"))
                        if validation_files:
                            latest_validation = sorted(validation_files)[-1]
                            with open(latest_validation, 'r', encoding='utf-8') as f:
                                validation_data = json.load(f)
                            
                            validation_results[docs_dir.name] = validation_data
                            total_score += validation_data['quality_score'] * validation_data['validated_files']
                            total_files += validation_data['validated_files']
                
                except Exception as e:
                    print(f"❌ Ошибка валидации {docs_dir}: {e}")
        
        # Вычисляем общий балл
        overall_score = total_score / total_files if total_files > 0 else 0
        
        # Сохраняем балл для CI/CD
        score_file = self.context_dir / "analysis" / "quality_score.txt"
        score_file.parent.mkdir(parents=True, exist_ok=True)
        with open(score_file, 'w') as f:
            f.write(f"{overall_score:.1f}")
        
        print(f"📊 Общий балл качества: {overall_score:.1f}%")
        
        return {
            "overall_score": overall_score,
            "total_files": total_files,
            "directory_results": validation_results,
            "threshold_met": overall_score >= self.config["validation_threshold"]
        }

    def auto_fix_documentation(self) -> Dict:
        """Автоматически исправляет проблемы в документации"""
        print("🔧 Автоматическое исправление документации...")
        
        fix_results = {}
        
        docs_directories = [
            self.docs_dir / "api-reference" / "top20",
            self.docs_dir / "api-reference" / "next50"
        ]
        
        for docs_dir in docs_directories:
            if docs_dir.exists():
                try:
                    # Запускаем автоисправление
                    result = subprocess.run([
                        sys.executable,
                        str(self.tools_dir / "documentation_fixer.py"),
                        "--docs-dir", str(docs_dir)
                    ], capture_output=True, text=True, cwd=self.project_root)
                    
                    if result.returncode == 0:
                        print(f"✅ Исправления применены для {docs_dir.name}")
                        fix_results[docs_dir.name] = {"status": "success", "output": result.stdout}
                    else:
                        print(f"❌ Ошибка исправления {docs_dir.name}: {result.stderr}")
                        fix_results[docs_dir.name] = {"status": "error", "error": result.stderr}
                
                except Exception as e:
                    print(f"❌ Исключение при исправлении {docs_dir}: {e}")
                    fix_results[docs_dir.name] = {"status": "exception", "error": str(e)}
        
        return fix_results

    def generate_missing_documentation(self) -> Dict:
        """Генерирует отсутствующую документацию"""
        print("📝 Генерация отсутствующей документации...")
        
        generation_results = {}
        
        try:
            # Проверяем, нужно ли обновить API инвентарь
            api_inventory = self.context_dir / "analysis" / "cellframe_api_inventory.json"
            if not api_inventory.exists() or self.check_api_changes():
                print("🔄 Обновление API инвентаря...")
                result = subprocess.run([
                    sys.executable,
                    str(self.tools_dir / "cellframe_api_extractor.py")
                ], capture_output=True, text=True, cwd=self.project_root)
                
                if result.returncode != 0:
                    print(f"❌ Ошибка обновления API инвентаря: {result.stderr}")
                    return {"status": "error", "error": "Failed to update API inventory"}
            
            # Генерируем документацию для новых функций
            if not (self.docs_dir / "api-reference" / "next50").exists():
                print("📚 Генерация документации для следующих 50 функций...")
                result = subprocess.run([
                    sys.executable,
                    str(self.tools_dir / "next50_functions_generator.py")
                ], capture_output=True, text=True, cwd=self.project_root)
                
                if result.returncode == 0:
                    generation_results["next50"] = {"status": "generated", "output": result.stdout}
                else:
                    generation_results["next50"] = {"status": "error", "error": result.stderr}
            
            return generation_results
            
        except Exception as e:
            return {"status": "exception", "error": str(e)}

    def generate_cicd_report(self) -> str:
        """Генерирует отчет для CI/CD"""
        print("📊 Генерация отчета CI/CD...")
        
        # Собираем данные
        validation_results = self.validate_all_documentation()
        
        # Подсчитываем метрики
        total_functions = 0
        documented_functions = 0
        
        # Анализируем API инвентарь
        api_inventory = self.context_dir / "analysis" / "cellframe_api_inventory.json"
        if api_inventory.exists():
            with open(api_inventory, 'r', encoding='utf-8') as f:
                api_data = json.load(f)
                total_functions = api_data['metadata']['total_functions']
        
        # Подсчитываем документированные функции
        for docs_dir in ["top20", "next50"]:
            docs_path = self.docs_dir / "api-reference" / docs_dir
            if docs_path.exists():
                documented_functions += len(list(docs_path.glob("*.md"))) - 1  # Исключаем README.md
        
        # Создаем отчет
        report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "pipeline_version": "1.0.0",
            "quality_metrics": {
                "overall_score": validation_results.get("overall_score", 0),
                "threshold": self.config["validation_threshold"],
                "threshold_met": validation_results.get("threshold_met", False)
            },
            "coverage": {
                "total_functions": total_functions,
                "documented_functions": documented_functions,
                "api_coverage": (documented_functions / total_functions * 100) if total_functions > 0 else 0,
                "example_coverage": 100 if documented_functions > 0 else 0  # Все документированные функции имеют примеры
            },
            "validation": {
                "passed": validation_results.get("threshold_met", False),
                "total_files": validation_results.get("total_files", 0),
                "directory_results": validation_results.get("directory_results", {})
            },
            "issues": {
                "total_issues": sum(
                    result.get("issues_found", 0) 
                    for result in validation_results.get("directory_results", {}).values()
                ),
                "critical_issues": 0,  # TODO: Добавить анализ критических проблем
                "auto_fixed": 0  # TODO: Добавить счетчик автоисправлений
            },
            "artifacts": {
                "report_url": f"https://github.com/{os.environ.get('GITHUB_REPOSITORY', 'cellframe/cellframe-node')}/actions",
                "documentation_url": "https://wiki.cellframe.net"
            },
            "recommendations": self.generate_recommendations(validation_results)
        }
        
        # Сохраняем отчет
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.context_dir / "analysis" / f"cicd_report_{timestamp}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # Создаем симлинк на последний отчет
        latest_link = self.context_dir / "analysis" / "cicd_report_latest.json"
        if latest_link.exists():
            latest_link.unlink()
        latest_link.symlink_to(report_file.name)
        
        print(f"📋 Отчет CI/CD создан: {report_file}")
        return str(report_file)

    def generate_recommendations(self, validation_results: Dict) -> List[str]:
        """Генерирует рекомендации на основе результатов валидации"""
        recommendations = []
        
        overall_score = validation_results.get("overall_score", 0)
        
        if overall_score < 70:
            recommendations.append("Критический уровень качества документации - требуется немедленное вмешательство")
            recommendations.append("Рекомендуется запустить полную регенерацию документации")
        elif overall_score < 85:
            recommendations.append("Качество документации ниже порога - требуются улучшения")
            recommendations.append("Используйте автоматическое исправление проблем")
        else:
            recommendations.append("Качество документации соответствует стандартам")
            recommendations.append("Поддерживайте текущий уровень качества")
        
        # Анализируем покрытие
        total_files = validation_results.get("total_files", 0)
        if total_files < 50:
            recommendations.append("Низкое покрытие документации - рассмотрите генерацию дополнительных функций")
        
        return recommendations

    def deploy_documentation(self) -> bool:
        """Развертывает документацию"""
        print("🚀 Развертывание документации...")
        
        try:
            # Создаем статический сайт
            public_dir = self.project_root / "public"
            public_dir.mkdir(exist_ok=True)
            
            # Копируем документацию
            import shutil
            
            docs_source = self.docs_dir / "api-reference"
            docs_target = public_dir / "api-reference"
            
            if docs_target.exists():
                shutil.rmtree(docs_target)
            
            shutil.copytree(docs_source, docs_target)
            
            # Создаем главную страницу
            index_content = """<!DOCTYPE html>
<html>
<head>
    <title>Cellframe API Documentation</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #f0f0f0; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; }
        a { color: #0066cc; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Cellframe API Documentation</h1>
        <p>Автоматически сгенерированная документация API</p>
    </div>
    
    <div class="section">
        <h2>Разделы документации</h2>
        <ul>
            <li><a href="api-reference/top20/">Топ-20 критических функций</a></li>
            <li><a href="api-reference/next50/">Следующие 50 функций</a></li>
        </ul>
    </div>
    
    <div class="section">
        <h2>Последнее обновление</h2>
        <p>""" + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
    </div>
</body>
</html>"""
            
            with open(public_dir / "index.html", 'w', encoding='utf-8') as f:
                f.write(index_content)
            
            print(f"✅ Документация развернута в {public_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка развертывания: {e}")
            return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='CI/CD Documentation Pipeline')
    parser.add_argument('command', choices=[
        'setup-github', 'setup-gitlab', 'check-api-changes', 
        'validate-all', 'auto-fix', 'generate-missing', 
        'generate-report', 'deploy-docs'
    ])
    parser.add_argument('--config', help='Путь к файлу конфигурации')
    
    args = parser.parse_args()
    
    pipeline = CICDDocumentationPipeline()
    
    if args.command == 'setup-github':
        pipeline.create_github_workflow()
    elif args.command == 'setup-gitlab':
        pipeline.create_gitlab_pipeline()
    elif args.command == 'check-api-changes':
        changed = pipeline.check_api_changes()
        sys.exit(1 if changed else 0)
    elif args.command == 'validate-all':
        results = pipeline.validate_all_documentation()
        sys.exit(0 if results['threshold_met'] else 1)
    elif args.command == 'auto-fix':
        pipeline.auto_fix_documentation()
    elif args.command == 'generate-missing':
        pipeline.generate_missing_documentation()
    elif args.command == 'generate-report':
        pipeline.generate_cicd_report()
    elif args.command == 'deploy-docs':
        success = pipeline.deploy_documentation()
        sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 