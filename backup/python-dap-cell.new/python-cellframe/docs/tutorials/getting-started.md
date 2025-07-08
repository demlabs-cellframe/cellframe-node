# Getting Started with Cellframe Python SDK

Добро пожаловать в Python Cellframe SDK! Это руководство поможет вам начать работу с новым SDK.

## 📦 Установка

### Требования

- Python 3.8 или выше
- cellframe-node (для plugin режима)

### Установка из PyPI

```bash
pip install cellframe
```

### Установка из исходников

```bash
git clone https://github.com/demlabs-cellframe/cellframe-node.git
cd cellframe-node/python-cellframe-new
pip install -e .
```

## 🚀 Быстрый старт

### Простейший пример

```python
import cellframe

# Создание узла (автоматическое определение режима)
node = cellframe.auto_create_node()

# Проверка статуса
status = node.get_status()
print(f"Node mode: {status['mode']}")
print(f"App name: {status['app_name']}")
```

### Проверка режима работы

```python
import cellframe

# Проверка режима
if cellframe.is_plugin_mode():
    print("🔌 Running as plugin inside cellframe-node")
    node = cellframe.create_plugin_node("my-plugin")
elif cellframe.is_library_mode():
    print("📚 Running as standalone library")
    node = cellframe.create_library_node("my-app")
else:
    print("🔍 Auto-detecting mode...")
    node = cellframe.auto_create_node()
```

## 🏗️ Основные концепции

### Узел (Node)

Узел - это основная точка входа в SDK:

```python
import cellframe

# Создание узла
node = cellframe.auto_create_node()

# Получение информации
print(f"Node status: {node.get_status()}")
print(f"Available chains: {[chain.name for chain in node.get_chains()]}")
```

### Блокчейны (Chains)

Работа с различными блокчейнами в сети Cellframe:

```python
# Получение конкретного блокчейна
mainnet = node.get_chain_by_id("mainnet")
testnet = node.get_chain_by_id("testnet")

# Информация о блокчейне
info = mainnet.get_info()
print(f"Chain: {info['name']}")
print(f"Height: {info['height']}")
```

### Кошельки (Wallets)

Управление кошельками и балансами:

```python
# Доступ к кошельку
wallet = node.wallet

# Получение баланса
balance = wallet.get_balance("address")
print(f"Balance: {balance}")

# Список адресов
addresses = wallet.get_addresses()
print(f"Addresses: {addresses}")
```

## 🔧 Практические примеры

### Пример 1: Проверка баланса

```python
import cellframe

def check_balance(address):
    """Проверяет баланс указанного адреса"""
    
    # Создание узла
    node = cellframe.auto_create_node()
    
    # Получение баланса
    try:
        balance = node.wallet.get_balance(address)
        print(f"Balance for {address}: {balance}")
        return balance
    except Exception as e:
        print(f"Error getting balance: {e}")
        return None

# Использование
balance = check_balance("Mf8rCqhzWKNZZmkMNmQtMpBGjY8aZzqhv5J8nwBtgQ")
```

### Пример 2: Информация о блокчейне

```python
import cellframe

def get_chain_info(chain_id):
    """Получает информацию о блокчейне"""
    
    with cellframe.create_library_node("chain-explorer") as node:
        chain = node.get_chain_by_id(chain_id)
        
        info = chain.get_info()
        status = chain.get_status()
        
        print(f"Chain: {info['name']}")
        print(f"ID: {chain_id}")
        print(f"Height: {info['height']}")
        print(f"Status: {status}")
        
        return info

# Использование
mainnet_info = get_chain_info("mainnet")
testnet_info = get_chain_info("testnet")
```

### Пример 3: Работа с транзакциями

```python
import cellframe

def transfer_tokens(from_address, to_address, amount, token="CELL"):
    """Отправляет токены с одного адреса на другой"""
    
    node = cellframe.auto_create_node()
    
    try:
        # Создание и отправка транзакции
        tx_hash = node.wallet.transfer(
            from_addr=from_address,
            to_addr=to_address,
            amount=amount,
            token=token
        )
        
        print(f"Transaction sent: {tx_hash}")
        return tx_hash
        
    except Exception as e:
        print(f"Transfer failed: {e}")
        return None

# Использование
tx_hash = transfer_tokens(
    from_address="source_address",
    to_address="target_address",
    amount=1000
)
```

## 🛠️ Расширенные возможности

### Context Managers

Используйте context managers для автоматического управления ресурсами:

```python
import cellframe

# Автоматическая очистка ресурсов
with cellframe.create_library_node("my-app") as node:
    # Все операции внутри блока
    chains = node.get_chains()
    for chain in chains:
        info = chain.get_info()
        print(f"Chain {chain.name}: {info['height']} blocks")
    
    # Ресурсы автоматически освобождаются
```

### Асинхронные операции

Для высокопроизводительных приложений:

```python
import cellframe
import asyncio

async def async_operations():
    """Асинхронные операции с блокчейном"""
    
    node = cellframe.auto_create_node()
    
    # Параллельные запросы
    tasks = [
        node.wallet.get_balance_async("address1"),
        node.wallet.get_balance_async("address2"),
        node.wallet.get_balance_async("address3")
    ]
    
    balances = await asyncio.gather(*tasks)
    
    for i, balance in enumerate(balances):
        print(f"Address {i+1} balance: {balance}")
    
    return balances

# Запуск
balances = asyncio.run(async_operations())
```

### Обработка ошибок

```python
import cellframe
from cellframe.core.exceptions import CellframeError

def safe_operation():
    """Безопасная операция с обработкой ошибок"""
    
    try:
        node = cellframe.auto_create_node()
        balance = node.wallet.get_balance("invalid_address")
        
    except CellframeError as e:
        print(f"Cellframe error: {e}")
        print(f"Error code: {e.code}")
        print(f"Error details: {e.details}")
        
    except Exception as e:
        print(f"General error: {e}")
        
    finally:
        print("Operation completed")

safe_operation()
```

## 📊 Мониторинг и отладка

### Логирование

```python
import cellframe
import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_example():
    """Пример с отладочной информацией"""
    
    logger.info("Starting node...")
    node = cellframe.auto_create_node()
    
    logger.info("Getting node status...")
    status = node.get_status()
    logger.debug(f"Node status: {status}")
    
    logger.info("Getting chains...")
    chains = node.get_chains()
    logger.debug(f"Available chains: {[c.name for c in chains]}")
    
    logger.info("Operation completed")

debug_example()
```

### Производительность

```python
import cellframe
import time

def performance_test():
    """Тест производительности операций"""
    
    node = cellframe.auto_create_node()
    
    # Тест времени создания узла
    start = time.time()
    node = cellframe.auto_create_node()
    node_time = time.time() - start
    
    # Тест времени получения статуса
    start = time.time()
    status = node.get_status()
    status_time = time.time() - start
    
    # Тест времени получения цепей
    start = time.time()
    chains = node.get_chains()
    chains_time = time.time() - start
    
    print(f"Node creation: {node_time:.4f}s")
    print(f"Status query: {status_time:.4f}s")
    print(f"Chains query: {chains_time:.4f}s")

performance_test()
```

## 🔍 Отладка и тестирование

### Режим отладки

```python
import cellframe

# Включение отладки
node = cellframe.create_library_node("debug-app", debug=True)

# Детальная информация
status = node.get_status()
print(f"Debug info: {status}")
```

### Тестирование

```python
import cellframe
import unittest

class TestCellframeSDK(unittest.TestCase):
    def setUp(self):
        self.node = cellframe.auto_create_node()
    
    def test_node_creation(self):
        """Тест создания узла"""
        self.assertIsNotNone(self.node)
        status = self.node.get_status()
        self.assertIn('mode', status)
    
    def test_chains_access(self):
        """Тест доступа к блокчейнам"""
        chains = self.node.get_chains()
        self.assertIsInstance(chains, list)
    
    def test_wallet_access(self):
        """Тест доступа к кошельку"""
        wallet = self.node.wallet
        self.assertIsNotNone(wallet)

if __name__ == '__main__':
    unittest.main()
```

## 🎯 Следующие шаги

1. **Изучите [API Documentation](../api/)** - полная документация всех модулей
2. **Посмотрите [Examples](../examples/)** - готовые примеры для различных задач
3. **Прочитайте [Migration Guide](../guides/migration.md)** - если переходите со старого API
4. **Присоединитесь к сообществу** - [Telegram](https://t.me/cellframe_dev) для вопросов и обсуждений

## 📝 Шпаргалка

### Основные команды

```python
import cellframe

# Создание узла
node = cellframe.auto_create_node()

# Статус
status = node.get_status()

# Блокчейны
chains = node.get_chains()
mainnet = node.get_chain_by_id("mainnet")

# Кошелек
wallet = node.wallet
balance = wallet.get_balance("address")

# Транзакции
tx_hash = wallet.transfer(to="address", amount=1000)
```

### Полезные функции

```python
# Проверка режима
cellframe.is_plugin_mode()
cellframe.is_library_mode()

# Получение контекста
context = cellframe.get_context()

# Создание конкретного типа узла
plugin_node = cellframe.create_plugin_node("my-plugin")
library_node = cellframe.create_library_node("my-app")
```

Теперь вы готовы начать работу с Cellframe Python SDK! 🚀 