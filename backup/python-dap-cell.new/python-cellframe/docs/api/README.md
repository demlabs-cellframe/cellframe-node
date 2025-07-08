# Python Cellframe SDK API Documentation

Полная документация Python Cellframe SDK с примерами использования и типизацией.

## 🏗️ Архитектура

### Режимы работы

#### Plugin Mode
```python
import cellframe

# Автоматическое обнаружение plugin mode
node = cellframe.auto_create_node()

# Или явное создание plugin node
node = cellframe.create_plugin_node("my-plugin")
```

#### Library Mode
```python
import cellframe

# Автоматическое обнаружение library mode
node = cellframe.auto_create_node()

# Или явное создание library node
node = cellframe.create_library_node("my-app")
```

### Универсальный контекст
```python
from cellframe.core.context import get_context

context = get_context()
if context.is_plugin_mode:
    # Доступ к node API
    manifest = context.get_manifest()
    node_config = context.get_node_config()
elif context.is_library_mode:
    # Локальная конфигурация
    app_config = context.get_config()
    data_dir = context.get_data_dir()
```

## 📚 Модули

### [Core](./core.md)
- `CellframeNode` - основной координатор
- `CellframeComponent` - базовый компонент
- `AppContext` - система контекстов
- `ExecutionMode` - режимы работы

### [DAP Integration](./dap.md)
- Интеграция с DAP SDK
- Криптографические операции через DAP
- Низкоуровневые DAP функции

### [Network](./network.md)
- Сетевые операции
- Подключение к блокчейн сетям
- Синхронизация

### [Wallet](./wallet.md)
- Операции с кошельками
- Управление адресами
- Транзакции

### [Services](./services.md)
- Высокоуровневые сервисы
- Staking, DEX, другие протоколы

### [Legacy](./legacy.md)
- Обратная совместимость
- Миграция с старого API
- Предупреждения о deprecation

### [Migration](./migration.md)
- Инструменты автоматической миграции
- Анализ кода
- Трансформация паттернов

## 🔧 Быстрый старт

### Установка
```bash
pip install cellframe
```

### Минимальный пример
```python
import cellframe

# Создание узла (автоматическое определение режима)
node = cellframe.auto_create_node()

# Получение статуса
status = node.get_status()
print(f"Node status: {status}")

# Работа с блокчейном
chain = node.chain.get_by_id("mainnet")
print(f"Chain info: {chain.get_info()}")
```

## 🛠️ Расширенное использование

### Context Manager
```python
import cellframe

with cellframe.create_library_node("my-app") as node:
    # Автоматическое управление ресурсами
    chain = node.chain.get_by_id("mainnet")
    balance = node.wallet.get_balance("address")
    
    # Ресурсы автоматически освобождаются
```

### Async Operations
```python
import cellframe
import asyncio

async def example():
    node = cellframe.auto_create_node()
    
    # Асинхронные операции
    balance = await node.wallet.get_balance_async("address")
    tx_hash = await node.wallet.transfer_async(
        to="target_address",
        amount=1000
    )
```

## 📖 Дополнительные ресурсы

- [Tutorials](../tutorials/) - пошаговые руководства
- [Migration Guide](../guides/migration.md) - переход с старого API
- [Performance Benchmarks](../benchmarks/) - тесты производительности
- [Examples](../examples/) - примеры кода

## 🐛 Поддержка

- GitHub Issues: [cellframe-node/issues](https://github.com/demlabs-cellframe/cellframe-node/issues)
- Documentation: [cellframe.net/docs](https://cellframe.net/docs)
- Community: [t.me/cellframe_dev](https://t.me/cellframe_dev) 