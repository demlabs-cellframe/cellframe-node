#!/usr/bin/env node

/**
 * DAP SDK Documentation MCP Server
 * Предоставляет доступ к документации DAP SDK через Model Context Protocol
 */

const fs = require('fs');
const path = require('path');
const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} = require('@modelcontextprotocol/sdk/types.js');

class DapSdkDocsServer {
  constructor() {
    this.server = new Server(
      {
        name: 'dap-sdk-docs-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.docsPath = process.env.PROJECT_ROOT || path.join(__dirname, '../../../');
    this.setupToolHandlers();
  }

  setupToolHandlers() {
    // Обработчик для получения списка доступных инструментов
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'search_docs',
            description: 'Поиск по документации DAP SDK',
            inputSchema: {
              type: 'object',
              properties: {
                query: {
                  type: 'string',
                  description: 'Поисковый запрос'
                },
                category: {
                  type: 'string',
                  enum: ['core', 'crypto', 'net', 'cellframe', 'all'],
                  description: 'Категория поиска'
                }
              },
              required: ['query']
            }
          },
          {
            name: 'get_module_docs',
            description: 'Получение документации конкретного модуля',
            inputSchema: {
              type: 'object',
              properties: {
                module: {
                  type: 'string',
                  description: 'Имя модуля (например: dap_cbuf, dap_math_ops)'
                },
                category: {
                  type: 'string',
                  enum: ['core', 'crypto', 'net'],
                  default: 'core',
                  description: 'Категория модуля'
                }
              },
              required: ['module']
            }
          },
          {
            name: 'list_modules',
            description: 'Получение списка всех доступных модулей',
            inputSchema: {
              type: 'object',
              properties: {
                category: {
                  type: 'string',
                  enum: ['core', 'crypto', 'net', 'cellframe', 'all'],
                  description: 'Категория модулей'
                }
              }
            }
          },
          {
            name: 'get_architecture_info',
            description: 'Получение информации об архитектуре DAP SDK',
            inputSchema: {
              type: 'object',
              properties: {
                component: {
                  type: 'string',
                  enum: ['dap-sdk', 'cellframe-sdk', 'overview'],
                  description: 'Компонент архитектуры'
                }
              }
            }
          }
        ]
      };
    });

    // Обработчик для выполнения инструментов
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'search_docs':
            return await this.searchDocs(args);
          case 'get_module_docs':
            return await this.getModuleDocs(args);
          case 'list_modules':
            return await this.listModules(args);
          case 'get_architecture_info':
            return await this.getArchitectureInfo(args);
          default:
            throw new McpError(
              ErrorCode.MethodNotFound,
              `Unknown tool: ${name}`
            );
        }
      } catch (error) {
        console.error(`Error in tool ${name}:`, error);
        throw new McpError(
          ErrorCode.InternalError,
          `Internal error: ${error.message}`
        );
      }
    });
  }

  async searchDocs(args) {
    const { query, category = 'all' } = args;

    if (!query || query.trim().length === 0) {
      throw new McpError(
        ErrorCode.InvalidParams,
        'Query parameter is required and cannot be empty'
      );
    }

    const results = [];
    const searchPaths = this.getSearchPaths(category);

    for (const searchPath of searchPaths) {
      if (fs.existsSync(searchPath)) {
        const files = this.findMarkdownFiles(searchPath);

        for (const file of files) {
          const content = fs.readFileSync(file, 'utf8');
          const matches = this.searchInContent(content, query);

          if (matches.length > 0) {
            results.push({
              file: path.relative(this.docsPath, file),
              matches: matches.slice(0, 5), // Ограничить до 5 совпадений
              module: this.extractModuleName(file)
            });
          }
        }
      }
    }

    return {
      content: [
        {
          type: 'text',
          text: `Найдено ${results.length} файлов с совпадениями для запроса "${query}":\n\n` +
                results.map(r =>
                  `📄 ${r.file}\n` +
                  `📦 Модуль: ${r.module}\n` +
                  `🔍 Совпадения:\n${r.matches.map(m => `  • ${m}`).join('\n')}\n`
                ).join('\n')
        }
      ]
    };
  }

  async getModuleDocs(args) {
    const { module, category = 'core' } = args;

    if (!module) {
      throw new McpError(
        ErrorCode.InvalidParams,
        'Module parameter is required'
      );
    }

    const docsPath = this.getModuleDocsPath(module, category);

    if (!fs.existsSync(docsPath)) {
      return {
        content: [
          {
            type: 'text',
            text: `Документация для модуля '${module}' не найдена в категории '${category}'`
          }
        ]
      };
    }

    const content = fs.readFileSync(docsPath, 'utf8');

    return {
      content: [
        {
          type: 'text',
          text: `# Документация модуля: ${module}\n\n${content}`
        }
      ]
    };
  }

  async listModules(args) {
    const { category = 'all' } = args;
    const modules = [];

    const searchPaths = this.getSearchPaths(category);

    for (const searchPath of searchPaths) {
      if (fs.existsSync(searchPath)) {
        const files = this.findMarkdownFiles(searchPath);

        for (const file of files) {
          const moduleName = this.extractModuleName(file);
          if (moduleName && !modules.includes(moduleName)) {
            modules.push(moduleName);
          }
        }
      }
    }

    return {
      content: [
        {
          type: 'text',
          text: `Доступные модули в категории '${category}':\n\n` +
                modules.map(m => `• ${m}`).join('\n')
        }
      ]
    };
  }

  async getArchitectureInfo(args) {
    const { component = 'overview' } = args;

    let archPath;
    switch (component) {
      case 'dap-sdk':
        archPath = path.join(this.docsPath, 'dap-sdk/docs/architecture.md');
        break;
      case 'cellframe-sdk':
        archPath = path.join(this.docsPath, 'cellframe-sdk/docs/architecture.md');
        break;
      default:
        // Overview - можно создать комбинированную информацию
        return {
          content: [
            {
              type: 'text',
              text: `# Архитектура DAP SDK\n\n` +
                    `## Компоненты системы:\n\n` +
                    `### DAP SDK Core\n` +
                    `- **Crypto модуль**: Шифрование, подписи, хэширование\n` +
                    `- **Net модуль**: Сетевая коммуникация, HTTP/JSON-RPC\n` +
                    `- **Core модуль**: Базовые утилиты, математика, строки\n\n` +
                    `### CellFrame SDK\n` +
                    `- **Chain модуль**: Блокчейн логика\n` +
                    `- **Wallet модуль**: Управление кошельками\n` +
                    `- **Consensus модуль**: Алгоритмы консенсуса\n` +
                    `- **Mining модуль**: Добыча и валидация\n\n` +
                    `### Модули DAP SDK Core:\n` +
                    `- dap_cbuf: Кольцевые буферы\n` +
                    `- dap_math_ops: Математические операции\n` +
                    `- dap_math_convert: Конвертация чисел\n` +
                    `- portable_endian: Кроссплатформенные функции\n` +
                    `- dap_strfuncs: Работа со строками\n` +
                    `- dap_tsd: Типизированная сериализация\n` +
                    `- dap_json_rpc_errors: Обработка ошибок JSON-RPC\n` +
                    `- dap_fnmatch: Сопоставление шаблонов\n`
            }
          ]
        };
    }

    if (!fs.existsSync(archPath)) {
      throw new McpError(
        ErrorCode.InternalError,
        `Architecture file not found: ${archPath}`
      );
    }

    const content = fs.readFileSync(archPath, 'utf8');

    return {
      content: [
        {
          type: 'text',
          text: `# Архитектура ${component}\n\n${content}`
        }
      ]
    };
  }

  getSearchPaths(category) {
    const basePaths = {
      core: ['dap-sdk/docs/modules/core'],
      crypto: ['dap-sdk/docs/modules/crypto'],
      net: ['dap-sdk/docs/modules/net'],
      cellframe: ['cellframe-sdk/docs/modules'],
      all: [
        'dap-sdk/docs/modules/core',
        'dap-sdk/docs/modules/crypto',
        'dap-sdk/docs/modules/net',
        'cellframe-sdk/docs/modules'
      ]
    };

    return (basePaths[category] || basePaths.all).map(p =>
      path.join(this.docsPath, p)
    );
  }

  findMarkdownFiles(dirPath) {
    const files = [];

    function scanDir(currentPath) {
      if (!fs.existsSync(currentPath)) return;

      const items = fs.readdirSync(currentPath);

      for (const item of items) {
        const itemPath = path.join(currentPath, item);
        const stat = fs.statSync(itemPath);

        if (stat.isDirectory()) {
          scanDir(itemPath);
        } else if (item.endsWith('.md')) {
          files.push(itemPath);
        }
      }
    }

    scanDir(dirPath);
    return files;
  }

  searchInContent(content, query) {
    const lines = content.split('\n');
    const matches = [];
    const queryLower = query.toLowerCase();

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (line.toLowerCase().includes(queryLower)) {
        // Добавить контекст вокруг найденной строки
        const start = Math.max(0, i - 1);
        const end = Math.min(lines.length, i + 2);
        const context = lines.slice(start, end).join('\n');
        matches.push(context);
      }
    }

    return matches;
  }

  extractModuleName(filePath) {
    const filename = path.basename(filePath, '.md');

    // Специальные случаи
    if (filename.startsWith('dap_')) {
      return filename;
    }

    // Попытка извлечь имя модуля из пути
    const relativePath = path.relative(this.docsPath, filePath);
    const parts = relativePath.split(path.sep);

    if (parts.includes('modules') && parts.includes('core')) {
      return filename;
    }

    return filename;
  }

  getModuleDocsPath(module, category) {
    const categoryPaths = {
      core: 'dap-sdk/docs/modules/core',
      crypto: 'dap-sdk/docs/modules/crypto',
      net: 'dap-sdk/docs/modules/net'
    };

    const basePath = categoryPaths[category] || categoryPaths.core;
    return path.join(this.docsPath, basePath, `${module}.md`);
  }

  async run() {
    console.error('Starting DAP SDK Documentation MCP Server...');

    const transport = new StdioServerTransport();
    await this.server.connect(transport);

    console.error('DAP SDK Documentation MCP Server started successfully');
  }
}

// Импорт транспорта (предполагается наличие MCP SDK)
const { StdioServerTransport } = require('@modelcontextprotocol/sdk/server/stdio.js');

// Запуск сервера
const server = new DapSdkDocsServer();
server.run().catch(error => {
  console.error('Server error:', error);
  process.exit(1);
});

