# Migration Guide: Переход на новый Cellframe Python SDK

Это руководство поможет вам перейти со старого API на новый Python Cellframe SDK.

## 🔄 Обзор изменений

### Старый API (Legacy)
```python
# Старый стиль
from CellFrame import CellFrame
from DAP import DAP

# Инициализация
CellFrame.init(args)
DAP.init(args)

# Использование
wallet = CellFrame.Wallet()
chain = CellFrame.Chain("mainnet")
```

### Новый API (Modern)
```python
# Новый стиль
import cellframe

# Инициализация (автоматическая)
node = cellframe.auto_create_node()

# Использование
wallet = node.wallet
chain = node.chain.get_by_id("mainnet")
```

## 📋 Таблица соответствий

| Старый API | Новый API | Статус |
|------------|-----------|--------|
| `CellFrame.init()` | `cellframe.auto_create_node()` | ✅ Migrated |
| `CellFrame.Wallet()` | `node.wallet` | ✅ Migrated |
| `CellFrame.Chain()` | `node.chain.get_by_id()` | ✅ Migrated |
| `DAP.init()` | `import dap` | ✅ Migrated |
| `DAP.Crypto()` | `dap.crypto` | ✅ Migrated |
| `DAP.Network()` | `dap.network` | ✅ Migrated |

## 🛠️ Автоматическая миграция

### Инструменты миграции

```bash
# Анализ вашего кода
python -m cellframe.migration analyze my_project/

# Автоматическая миграция
python -m cellframe.migration migrate my_project/

# Миграция конфигурации
python -m cellframe.migration config old_config.json new_config.py
```

### CLI инструменты

```bash
# Полный анализ проекта
python -m cellframe.migration analyze \
  --path my_project/ \
  --report migration_report.json \
  --verbose

# Миграция с бэкапом
python -m cellframe.migration migrate \
  --path my_project/ \
  --backup \
  --fix-imports \
  --update-patterns
```

## 🔧 Пошаговая миграция

### Шаг 1: Обновление импортов

**Было:**
```python
from CellFrame import CellFrame, Chain, Wallet
from DAP import DAP, Crypto, Network
```

**Стало:**
```python
import cellframe
import dap
```

### Шаг 2: Инициализация

**Было:**
```python
# Сложная инициализация
args = {
    "debug": True,
    "config_dir": "/path/to/config",
    "log_level": "DEBUG"
}
CellFrame.init(args)
DAP.init(args)
```

**Стало:**
```python
# Простая инициализация
node = cellframe.auto_create_node()
# or
node = cellframe.create_library_node("my-app")
```

### Шаг 3: Работа с кошельком

**Было:**
```python
wallet = CellFrame.Wallet()
wallet.init("mainnet")
balance = wallet.get_balance("address")
```

**Стало:**
```python
node = cellframe.auto_create_node()
balance = node.wallet.get_balance("address")
```

### Шаг 4: Работа с блокчейном

**Было:**
```python
chain = CellFrame.Chain("mainnet")
chain.init()
info = chain.get_info()
```

**Стало:**
```python
node = cellframe.auto_create_node()
chain = node.chain.get_by_id("mainnet")
info = chain.get_info()
```

### Шаг 5: Криптографические операции

**Было:**
```python
crypto = DAP.Crypto()
crypto.init()
key = crypto.generate_key()
```

**Стало:**
```python
with dap.Dap() as dap_instance:
    key = dap_instance.crypto.generate_key()
```

## 📖 Примеры миграции

### Пример 1: Простое приложение

**Старый код:**
```python
from CellFrame import CellFrame
from DAP import DAP

# Инициализация
CellFrame.init({"debug": True})
DAP.init({"debug": True})

# Создание кошелька
wallet = CellFrame.Wallet()
wallet.init("mainnet")

# Получение баланса
balance = wallet.get_balance("Mf8rCqhzWKNZZmkMNmQtMpBGjY8aZzqhv5J8nwBtgQ")
print(f"Balance: {balance}")

# Очистка
wallet.deinit()
CellFrame.deinit()
DAP.deinit()
```

**Новый код:**
```python
import cellframe

# Автоматическая инициализация
node = cellframe.auto_create_node()

# Получение баланса
balance = node.wallet.get_balance("Mf8rCqhzWKNZZmkMNmQtMpBGjY8aZzqhv5J8nwBtgQ")
print(f"Balance: {balance}")

# Автоматическая очистка ресурсов
```

### Пример 2: Работа с транзакциями

**Старый код:**
```python
from CellFrame import CellFrame

CellFrame.init({"network": "mainnet"})

wallet = CellFrame.Wallet()
wallet.init("mainnet")

# Создание транзакции
tx = wallet.create_transaction(
    to="target_address",
    amount=1000,
    token="CELL"
)

# Подписание
signed_tx = wallet.sign_transaction(tx)

# Отправка
tx_hash = wallet.send_transaction(signed_tx)
print(f"Transaction hash: {tx_hash}")

wallet.deinit()
CellFrame.deinit()
```

**Новый код:**
```python
import cellframe

with cellframe.create_library_node("my-app") as node:
    # Создание и отправка транзакции
    tx_hash = node.wallet.transfer(
        to="target_address",
        amount=1000,
        token="CELL"
    )
    print(f"Transaction hash: {tx_hash}")
    
    # Автоматическая очистка ресурсов
```

### Пример 3: Криптографические операции

**Старый код:**
```python
from DAP import DAP

DAP.init({"debug": True})

crypto = DAP.Crypto()
crypto.init()

# Генерация ключа
key = crypto.generate_key("secp256k1")

# Подпись
data = b"Hello, World!"
signature = crypto.sign(key, data)

# Верификация
is_valid = crypto.verify(key, data, signature)
print(f"Signature valid: {is_valid}")

crypto.deinit()
DAP.deinit()
```

**Новый код:**
```python
import dap

with dap.Dap() as dap_instance:
    # Генерация ключа
    key = dap_instance.crypto.generate_key("secp256k1")
    
    # Подпись
    data = b"Hello, World!"
    signature = dap_instance.crypto.sign(key, data)
    
    # Верификация
    is_valid = dap_instance.crypto.verify(key, data, signature)
    print(f"Signature valid: {is_valid}")
    
    # Автоматическая очистка ресурсов
```

## 💡 Полезные советы

### Context Managers

Используйте context managers для автоматического управления ресурсами:

```python
# Хорошо
with cellframe.create_library_node("my-app") as node:
    balance = node.wallet.get_balance("address")

# Альтернативно
node = cellframe.auto_create_node()
try:
    balance = node.wallet.get_balance("address")
finally:
    node.cleanup()  # Если нужно
```

### Обработка ошибок

```python
import cellframe
from cellframe.core.exceptions import CellframeError

try:
    node = cellframe.auto_create_node()
    balance = node.wallet.get_balance("invalid_address")
except CellframeError as e:
    print(f"Cellframe error: {e}")
except Exception as e:
    print(f"General error: {e}")
```

### Асинхронные операции

```python
import cellframe
import asyncio

async def async_example():
    node = cellframe.auto_create_node()
    
    # Асинхронные операции
    balance = await node.wallet.get_balance_async("address")
    tx_hash = await node.wallet.transfer_async(
        to="target_address",
        amount=1000
    )
    
    return balance, tx_hash

# Запуск
balance, tx_hash = asyncio.run(async_example())
```

## 🚨 Типичные проблемы и решения

### Проблема 1: Импорты не найдены

**Ошибка:**
```python
ImportError: No module named 'CellFrame'
```

**Решение:**
```python
# Обновите импорты
import cellframe  # вместо from CellFrame import CellFrame
import dap       # вместо from DAP import DAP
```

### Проблема 2: Неправильная инициализация

**Ошибка:**
```python
AttributeError: 'CellframeNode' object has no attribute 'init'
```

**Решение:**
```python
# Не нужно вызывать init()
node = cellframe.auto_create_node()  # Автоматическая инициализация
```

### Проблема 3: Управление ресурсами

**Ошибка:**
```python
# Забыли вызвать deinit()
wallet.deinit()  # Старый API
```

**Решение:**
```python
# Используйте context managers
with cellframe.create_library_node("my-app") as node:
    # Автоматическая очистка
    pass
```

## 🔍 Проверка совместимости

### Скрипт проверки

```python
import cellframe
from cellframe.migration import check_compatibility

# Проверка совместимости кода
result = check_compatibility("my_project/")
print(f"Compatibility: {result.score}%")

for issue in result.issues:
    print(f"Issue: {issue.description}")
    print(f"Fix: {issue.suggested_fix}")
```

### Автоматическое исправление

```python
from cellframe.migration import auto_fix

# Автоматическое исправление простых проблем
fixes = auto_fix("my_project/")
print(f"Applied {len(fixes)} fixes")
```

## 📚 Дополнительные ресурсы

- [API Documentation](../api/) - полная документация нового API
- [Examples](../examples/) - примеры использования
- [Legacy API Reference](../legacy/) - справочник по старому API
- [Migration Tools](../tools/) - инструменты для миграции

## 🆘 Поддержка

Если у вас возникли проблемы с миграцией:

1. Проверьте [FAQ](../faq.md)
2. Используйте автоматические инструменты миграции
3. Обратитесь в [GitHub Issues](https://github.com/demlabs-cellframe/cellframe-node/issues)
4. Присоединитесь к [Telegram сообществу](https://t.me/cellframe_dev)

## 🎯 Backward Compatibility

Новый SDK включает полную поддержку старого API через compatibility layer:

```python
# Старый код продолжает работать
from CellFrame import CellFrame

CellFrame.init({"debug": True})  # Показывает deprecation warning
wallet = CellFrame.Wallet()     # Использует новый API внутри
```

Это позволяет постепенно мигрировать код без полной переписки. 