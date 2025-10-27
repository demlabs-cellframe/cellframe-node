# Common Test Templates

Общие элементы и шаблоны для переиспользования в тестовых сценариях Cellframe Node.

## Структура

```
tests/common/
├── README.md                    # Эта документация
├── networks/                    # Общие конфигурации сетей
│   ├── single_node.yml         # Одна нода
│   └── multi_node.yml          # Несколько нод
├── wallets/                     # Шаблоны работы с кошельками
│   ├── create_wallet.yml       # Создание кошелька
│   └── multi_wallet.yml        # Несколько кошельков
└── tokens/                      # Шаблоны работы с токенами
    ├── create_token.yml        # Базовый токен
    └── token_with_flags.yml    # Токен с флагами
```

## Использование

Включайте общие шаблоны в ваши тесты:

```yaml
includes:
  - ../../common/networks/single_node.yml
  - ../../common/wallets/create_wallet.yml
```

## Создание новых шаблонов

При создании общих шаблонов:

1. **Используйте описательные имена**
2. **Документируйте что предоставляет шаблон**
3. **Указывайте предоставляемые переменные**
4. **Делайте шаблоны переиспользуемыми**

### Пример шаблона

```yaml
# Файл: common/tokens/create_token.yml
# Предоставляет: {{token_hash}}, {{token_name}}
# Требует: {{wallet_addr}}

variables:
  token_name: TEST_TOKEN

setup:
  - cli: token_decl -token {{token_name}} -total 1000000
    save: token_hash
    wait: 3s
```

## Категории шаблонов

### Networks
Базовые конфигурации сетей для разных сценариев

### Wallets
Операции с кошельками (создание, экспорт, множественные)

### Tokens
Работа с токенами (создание, эмиссия, различные флаги)

## См. также

- [E2E Tests](../e2e/) - End-to-end тесты
- [Functional Tests](../functional/) - Функциональные тесты
- [Stage-env Scenarios](../stage-env/scenarios/) - Документация системы сценариев

