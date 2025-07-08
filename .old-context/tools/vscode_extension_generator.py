#!/usr/bin/env python3
"""
VS Code Extension Generator
Генератор расширения VS Code для интеграции с документацией Cellframe API
Фаза 3 проекта документации
"""

import json
import os
from pathlib import Path
from typing import Dict, List

class VSCodeExtensionGenerator:
    """Генератор VS Code расширения для документации API"""
    
    def __init__(self, output_dir: str = ".context/vscode-extension"):
        self.output_dir = Path(output_dir)
        self.extension_name = "cellframe-api-docs"
        self.display_name = "Cellframe API Documentation"
        
    def generate_package_json(self) -> str:
        """Генерирует package.json для расширения"""
        return json.dumps({
            "name": "cellframe-api-docs",
            "displayName": "Cellframe API Documentation",
            "description": "IntelliSense и документация для Cellframe API",
            "version": "1.0.0",
            "publisher": "cellframe",
            "engines": {
                "vscode": "^1.74.0"
            },
            "categories": [
                "Other",
                "Snippets",
                "Programming Languages"
            ],
            "keywords": [
                "cellframe",
                "blockchain",
                "api",
                "documentation",
                "intellisense"
            ],
            "activationEvents": [
                "onLanguage:c",
                "onLanguage:cpp",
                "onLanguage:python",
                "onCommand:cellframe.searchAPI",
                "onCommand:cellframe.openDocs"
            ],
            "main": "./out/extension.js",
            "contributes": {
                "commands": [
                    {
                        "command": "cellframe.searchAPI",
                        "title": "Search Cellframe API",
                        "category": "Cellframe"
                    },
                    {
                        "command": "cellframe.openDocs",
                        "title": "Open API Documentation",
                        "category": "Cellframe"
                    },
                    {
                        "command": "cellframe.insertFunction",
                        "title": "Insert Function Template",
                        "category": "Cellframe"
                    }
                ],
                "keybindings": [
                    {
                        "command": "cellframe.searchAPI",
                        "key": "ctrl+shift+f1",
                        "mac": "cmd+shift+f1",
                        "when": "editorTextFocus"
                    }
                ],
                "menus": {
                    "editor/context": [
                        {
                            "command": "cellframe.searchAPI",
                            "when": "editorTextFocus",
                            "group": "cellframe"
                        }
                    ]
                },
                "configuration": {
                    "title": "Cellframe API",
                    "properties": {
                        "cellframe.enableIntelliSense": {
                            "type": "boolean",
                            "default": True,
                            "description": "Enable IntelliSense for Cellframe API"
                        },
                        "cellframe.autoComplete": {
                            "type": "boolean",
                            "default": True,
                            "description": "Enable auto-completion"
                        },
                        "cellframe.showHover": {
                            "type": "boolean",
                            "default": True,
                            "description": "Show hover information"
                        }
                    }
                }
            },
            "scripts": {
                "vscode:prepublish": "npm run compile",
                "compile": "tsc -p ./",
                "watch": "tsc -watch -p ./"
            },
            "devDependencies": {
                "@types/vscode": "^1.74.0",
                "@types/node": "16.x",
                "typescript": "^4.9.4"
            }
        }, indent=2)

    def generate_extension_ts(self) -> str:
        """Генерирует основной файл расширения"""
        return '''import * as vscode from 'vscode';
import { CellframeAPIProvider } from './providers/apiProvider';
import { CellframeCompletionProvider } from './providers/completionProvider';
import { CellframeHoverProvider } from './providers/hoverProvider';
import { CellframeDocumentationPanel } from './panels/documentationPanel';

export function activate(context: vscode.ExtensionContext) {
    console.log('Cellframe API Documentation extension activated');

    const apiProvider = new CellframeAPIProvider(context);
    
    // Регистрируем провайдеры
    const completionProvider = vscode.languages.registerCompletionItemProvider(
        ['c', 'cpp', 'python'],
        new CellframeCompletionProvider(apiProvider),
        '.'
    );

    const hoverProvider = vscode.languages.registerHoverProvider(
        ['c', 'cpp', 'python'],
        new CellframeHoverProvider(apiProvider)
    );

    // Регистрируем команды
    const searchCommand = vscode.commands.registerCommand('cellframe.searchAPI', async () => {
        const query = await vscode.window.showInputBox({
            prompt: 'Search Cellframe API functions',
            placeHolder: 'Enter function name or keyword'
        });

        if (query) {
            const results = await apiProvider.searchFunctions(query);
            CellframeDocumentationPanel.showSearchResults(context.extensionUri, results);
        }
    });

    const openDocsCommand = vscode.commands.registerCommand('cellframe.openDocs', () => {
        CellframeDocumentationPanel.createOrShow(context.extensionUri);
    });

    const insertFunctionCommand = vscode.commands.registerCommand('cellframe.insertFunction', async () => {
        const functions = await apiProvider.getAllFunctions();
        const quickPick = vscode.window.createQuickPick();
        quickPick.items = functions.map(func => ({
            label: func.name,
            description: func.category,
            detail: func.description
        }));

        quickPick.onDidChangeSelection(selection => {
            if (selection[0]) {
                const selectedFunction = functions.find(f => f.name === selection[0].label);
                if (selectedFunction && vscode.window.activeTextEditor) {
                    const snippet = apiProvider.generateFunctionSnippet(selectedFunction);
                    const snippetString = new vscode.SnippetString(snippet);
                    vscode.window.activeTextEditor.insertSnippet(snippetString);
                }
            }
            quickPick.hide();
        });

        quickPick.show();
    });

    // Добавляем в контекст
    context.subscriptions.push(
        completionProvider,
        hoverProvider,
        searchCommand,
        openDocsCommand,
        insertFunctionCommand
    );
}

export function deactivate() {
    console.log('Cellframe API Documentation extension deactivated');
}'''

    def generate_api_provider(self) -> str:
        """Генерирует провайдер API данных"""
        return '''import * as vscode from 'vscode';
import * as fs from 'fs';
import * as path from 'path';

export interface CellframeFunction {
    name: string;
    signature: string;
    description: string;
    category: string;
    parameters: Parameter[];
    returnType: string;
    examples: {
        c?: string;
        python?: string;
    };
    relatedFunctions?: string[];
}

export interface Parameter {
    name: string;
    type: string;
    description: string;
}

export class CellframeAPIProvider {
    private functions: CellframeFunction[] = [];
    private context: vscode.ExtensionContext;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.loadAPIData();
    }

    private async loadAPIData() {
        try {
            const dataPath = path.join(this.context.extensionPath, 'data', 'api_functions.json');
            const data = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
            this.functions = data.functions || [];
            console.log(`Loaded ${this.functions.length} API functions`);
        } catch (error) {
            console.error('Failed to load API data:', error);
            vscode.window.showErrorMessage('Failed to load Cellframe API data');
        }
    }

    async getAllFunctions(): Promise<CellframeFunction[]> {
        return this.functions;
    }

    async searchFunctions(query: string): Promise<CellframeFunction[]> {
        const lowerQuery = query.toLowerCase();
        return this.functions.filter(func => 
            func.name.toLowerCase().includes(lowerQuery) ||
            func.description.toLowerCase().includes(lowerQuery) ||
            func.category.toLowerCase().includes(lowerQuery)
        );
    }

    async getFunctionByName(name: string): Promise<CellframeFunction | undefined> {
        return this.functions.find(func => func.name === name);
    }

    generateFunctionSnippet(func: CellframeFunction): string {
        const params = func.parameters.map((param, index) => 
            `\${${index + 1}:${param.name}}`
        ).join(', ');
        
        return `${func.name}(${params})`;
    }

    generateHoverContent(func: CellframeFunction): vscode.MarkdownString {
        const markdown = new vscode.MarkdownString();
        markdown.isTrusted = true;
        
        markdown.appendMarkdown(`## ${func.name}\\n\\n`);
        markdown.appendMarkdown(`**Category:** ${func.category}\\n\\n`);
        markdown.appendMarkdown(`${func.description}\\n\\n`);
        
        markdown.appendCodeblock(func.signature, 'c');
        
        if (func.parameters.length > 0) {
            markdown.appendMarkdown(`### Parameters\\n\\n`);
            func.parameters.forEach(param => {
                markdown.appendMarkdown(`- **${param.name}** (\`${param.type}\`): ${param.description}\\n`);
            });
        }
        
        if (func.examples.c) {
            markdown.appendMarkdown(`\\n### Example\\n\\n`);
            markdown.appendCodeblock(func.examples.c, 'c');
        }
        
        return markdown;
    }
}'''

    def generate_completion_provider(self) -> str:
        """Генерирует провайдер автодополнения"""
        return '''import * as vscode from 'vscode';
import { CellframeAPIProvider, CellframeFunction } from './apiProvider';

export class CellframeCompletionProvider implements vscode.CompletionItemProvider {
    private apiProvider: CellframeAPIProvider;

    constructor(apiProvider: CellframeAPIProvider) {
        this.apiProvider = apiProvider;
    }

    async provideCompletionItems(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken,
        context: vscode.CompletionContext
    ): Promise<vscode.CompletionItem[]> {
        
        const config = vscode.workspace.getConfiguration('cellframe');
        if (!config.get('enableIntelliSense') || !config.get('autoComplete')) {
            return [];
        }

        const functions = await this.apiProvider.getAllFunctions();
        const completionItems: vscode.CompletionItem[] = [];

        functions.forEach(func => {
            const item = new vscode.CompletionItem(func.name, vscode.CompletionItemKind.Function);
            item.detail = func.category;
            item.documentation = new vscode.MarkdownString(func.description);
            
            // Создаем snippet для функции
            const params = func.parameters.map((param, index) => 
                `\${${index + 1}:${param.name}}`
            ).join(', ');
            
            item.insertText = new vscode.SnippetString(`${func.name}(${params})`);
            
            // Добавляем информацию о сигнатуре
            item.command = {
                command: 'editor.action.triggerParameterHints',
                title: 'Trigger Parameter Hints'
            };

            completionItems.push(item);
        });

        return completionItems;
    }
}'''

    def generate_hover_provider(self) -> str:
        """Генерирует провайдер hover информации"""
        return '''import * as vscode from 'vscode';
import { CellframeAPIProvider } from './apiProvider';

export class CellframeHoverProvider implements vscode.HoverProvider {
    private apiProvider: CellframeAPIProvider;

    constructor(apiProvider: CellframeAPIProvider) {
        this.apiProvider = apiProvider;
    }

    async provideHover(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken
    ): Promise<vscode.Hover | undefined> {
        
        const config = vscode.workspace.getConfiguration('cellframe');
        if (!config.get('enableIntelliSense') || !config.get('showHover')) {
            return undefined;
        }

        const wordRange = document.getWordRangeAtPosition(position);
        if (!wordRange) {
            return undefined;
        }

        const word = document.getText(wordRange);
        const func = await this.apiProvider.getFunctionByName(word);
        
        if (!func) {
            return undefined;
        }

        const hoverContent = this.apiProvider.generateHoverContent(func);
        return new vscode.Hover(hoverContent, wordRange);
    }
}'''

    def create_extension_files(self) -> bool:
        """Создает файлы расширения VS Code"""
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            # Создаем структуру проекта
            files = {
                'package.json': self.generate_package_json(),
                'src/extension.ts': self.generate_extension_ts(),
                'src/providers/apiProvider.ts': self.generate_api_provider(),
                'src/providers/completionProvider.ts': self.generate_completion_provider(),
                'src/providers/hoverProvider.ts': self.generate_hover_provider(),
                'tsconfig.json': self.generate_tsconfig(),
                'README.md': self.generate_readme(),
                '.vscode/launch.json': self.generate_launch_config(),
                'data/api_functions.json': '{"functions": []}'
            }
            
            for file_path, content in files.items():
                full_path = self.output_dir / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            print(f"✅ VS Code расширение создано в {self.output_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания расширения: {e}")
            return False

    def generate_tsconfig(self) -> str:
        """Генерирует tsconfig.json"""
        return json.dumps({
            "compilerOptions": {
                "module": "commonjs",
                "target": "ES2020",
                "outDir": "out",
                "lib": ["ES2020"],
                "sourceMap": True,
                "rootDir": "src",
                "strict": True
            },
            "exclude": ["node_modules", ".vscode-test"]
        }, indent=2)

    def generate_readme(self) -> str:
        """Генерирует README для расширения"""
        return '''# Cellframe API Documentation Extension

VS Code расширение для работы с документацией Cellframe API.

## Возможности

- 🔍 **Поиск API функций** - быстрый поиск по названию и описанию
- 💡 **IntelliSense** - автодополнение для функций API
- 📖 **Hover документация** - подробная информация при наведении
- 📝 **Сниппеты** - быстрая вставка шаблонов функций
- ⌨️ **Горячие клавиши** - быстрый доступ к функциям

## Использование

### Поиск API функций
- Нажмите `Ctrl+Shift+F1` (или `Cmd+Shift+F1` на Mac)
- Введите название функции или ключевое слово
- Выберите нужную функцию из результатов

### Автодополнение
- Начните вводить название функции Cellframe API
- Выберите функцию из списка автодополнения
- Используйте Tab для перехода между параметрами

### Hover документация
- Наведите курсор на название функции
- Получите подробную информацию о параметрах и использовании

## Настройки

- `cellframe.enableIntelliSense` - включить IntelliSense
- `cellframe.autoComplete` - включить автодополнение  
- `cellframe.showHover` - показывать hover информацию

## Поддерживаемые языки

- C/C++
- Python

## Установка

1. Откройте VS Code
2. Перейдите в Extensions (Ctrl+Shift+X)
3. Найдите "Cellframe API Documentation"
4. Нажмите Install
'''

    def generate_launch_config(self) -> str:
        """Генерирует конфигурацию запуска для отладки"""
        return json.dumps({
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "Extension",
                    "type": "extensionHost",
                    "request": "launch",
                    "args": [
                        "--extensionDevelopmentPath=${workspaceFolder}"
                    ]
                }
            ]
        }, indent=2)

def main():
    """Главная функция для создания VS Code расширения"""
    generator = VSCodeExtensionGenerator()
    
    print("🚀 Создание VS Code расширения для Cellframe API...")
    
    if generator.create_extension_files():
        print("✅ VS Code расширение создано успешно")
        print(f"📁 Расположение: {generator.output_dir}")
        print("📋 Следующие шаги:")
        print("   1. cd .context/vscode-extension")
        print("   2. npm install")
        print("   3. npm run compile")
        print("   4. F5 для запуска в режиме разработки")
        return 0
    else:
        return 1

if __name__ == '__main__':
    exit(main()) 