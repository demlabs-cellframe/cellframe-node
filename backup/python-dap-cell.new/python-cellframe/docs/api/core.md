# Core Module Documentation

Core модуль содержит базовую архитектуру Python Cellframe SDK.

## Классы

### CellframeNode

Основной координатор для всех операций Cellframe SDK.

#### Создание

```python
import cellframe

# Автоматическое определение режима
node = cellframe.auto_create_node()

# Явное создание plugin node
node = cellframe.create_plugin_node("my-plugin")

# Явное создание library node  
node = cellframe.create_library_node("my-app", config_dir="/path/to/config")
```

#### Методы

##### `get_status() -> Dict[str, Any]`
Получает текущий статус узла.

```python
status = node.get_status()
print(f"Mode: {status['mode']}")
print(f"Context: {status['context_type']}")
print(f"App: {status['app_name']}")
```

##### `get_chains() -> List[CellframeChain]`
Получает список доступных блокчейнов.

```python
chains = node.get_chains()
for chain in chains:
    print(f"Chain: {chain.name}, ID: {chain.id}")
```

##### `get_chain_by_id(chain_id: str) -> CellframeChain`
Получает конкретный блокчейн по ID.

```python
mainnet = node.get_chain_by_id("mainnet")
testnet = node.get_chain_by_id("testnet")
```

##### Context Manager Support

```python
with cellframe.create_library_node("my-app") as node:
    # Автоматическое управление ресурсами
    status = node.get_status()
    # Все ресурсы автоматически освобождаются
```

### CellframeComponent

Базовый класс для всех компонентов SDK.

```python
from cellframe.core import CellframeComponent

class MyComponent(CellframeComponent):
    def __init__(self, node: CellframeNode):
        super().__init__(node)
        
    def my_method(self):
        # Доступ к контексту
        context = self.context
        if context.is_plugin_mode:
            # Plugin-специфичная логика
            pass
        else:
            # Library-специфичная логика
            pass
```

### CellframeChain

Представляет отдельный блокчейн в сети Cellframe.

#### Свойства

- `name: str` - имя блокчейна
- `id: str` - уникальный идентификатор
- `node: CellframeNode` - родительский узел

#### Методы

##### `get_info() -> Dict[str, Any]`
Получает информацию о блокчейне.

```python
chain = node.get_chain_by_id("mainnet")
info = chain.get_info()
print(f"Name: {info['name']}")
print(f"Height: {info['height']}")
```

##### `get_status() -> str`
Получает текущий статус блокчейна.

```python
status = chain.get_status()
print(f"Chain status: {status}")
```

## Система контекстов

### AppContext (abstract)

Базовый класс для всех контекстов приложения.

```python
from cellframe.core.context import get_context

context = get_context()
print(f"Mode: {context.mode}")
print(f"App name: {context.app_name}")
```

#### Свойства

- `mode: ExecutionMode` - режим выполнения
- `app_name: str` - имя приложения
- `is_plugin_mode: bool` - проверка plugin режима
- `is_library_mode: bool` - проверка library режима

### PluginContext

Контекст для plugin режима.

```python
from cellframe.core.context import get_context

context = get_context()
if context.is_plugin_mode:
    # Доступ к манифесту плагина
    manifest = context.get_manifest()
    
    # Доступ к конфигурации ноды
    node_config = context.get_node_config()
    
    # Доступ к DAP integration
    dap_instance = context.get_dap_instance()
```

#### Методы

##### `get_manifest() -> Dict[str, Any]`
Получает манифест плагина.

##### `get_node_config() -> Dict[str, Any]`
Получает конфигурацию ноды.

##### `get_dap_instance() -> Any`
Получает DAP instance для интеграции.

### LibContext

Контекст для library режима.

```python
from cellframe.core.context import get_context

context = get_context()
if context.is_library_mode:
    # Локальная конфигурация
    config = context.get_config()
    
    # Директория данных
    data_dir = context.get_data_dir()
    
    # Локальный DAP instance
    dap_instance = context.get_dap_instance()
```

#### Методы

##### `get_config() -> Dict[str, Any]`
Получает локальную конфигурацию приложения.

##### `get_data_dir() -> str`
Получает путь к директории данных.

##### `get_dap_instance() -> Any`
Получает локальный DAP instance.

### ContextFactory

Фабрика для создания контекстов.

```python
from cellframe.core.context import ContextFactory, ExecutionMode

# Автоматическое определение режима
context = ContextFactory.auto_create("my-app")

# Явное создание plugin контекста
context = ContextFactory.create(
    mode=ExecutionMode.PLUGIN,
    app_name="my-plugin"
)

# Явное создание library контекста
context = ContextFactory.create(
    mode=ExecutionMode.LIBRARY,
    app_name="my-app",
    config_dir="/path/to/config"
)
```

#### Методы

##### `auto_create(app_name: str) -> AppContext`
Автоматически определяет режим и создает контекст.

##### `create(mode: ExecutionMode, app_name: str, **kwargs) -> AppContext`
Явно создает контекст для указанного режима.

##### `detect_mode() -> ExecutionMode`
Определяет режим выполнения на основе окружения.

## Режимы выполнения

### ExecutionMode

Enum для определения режима выполнения.

```python
from cellframe.core.context import ExecutionMode

# Доступные режимы
ExecutionMode.PLUGIN   # Работа как плагин внутри cellframe-node
ExecutionMode.LIBRARY  # Работа как обычная Python библиотека
```

## Глобальные функции

### `get_context() -> AppContext`
Получает текущий глобальный контекст.

```python
from cellframe.core.context import get_context

context = get_context()
print(f"Current mode: {context.mode}")
```

### `set_context(context: AppContext) -> None`
Устанавливает глобальный контекст.

```python
from cellframe.core.context import set_context, ContextFactory

context = ContextFactory.auto_create("my-app")
set_context(context)
```

### `get_mode() -> ExecutionMode`
Получает текущий режим выполнения.

```python
from cellframe.core.context import get_mode, ExecutionMode

mode = get_mode()
if mode == ExecutionMode.PLUGIN:
    print("Running as plugin")
elif mode == ExecutionMode.LIBRARY:
    print("Running as library")
```

## Примеры использования

### Универсальный компонент

```python
from cellframe.core import CellframeComponent

class UniversalWallet(CellframeComponent):
    def get_balance(self, address: str) -> float:
        if self.context.is_plugin_mode:
            # Используем node API
            return self._get_balance_from_node(address)
        else:
            # Используем локальный DAP
            return self._get_balance_from_dap(address)
    
    def _get_balance_from_node(self, address: str) -> float:
        # Plugin-специфичная реализация
        pass
    
    def _get_balance_from_dap(self, address: str) -> float:
        # Library-специфичная реализация
        pass
```

### Инициализация в разных режимах

```python
import cellframe

# Автоматическое определение режима
node = cellframe.auto_create_node()

# Проверка режима
if cellframe.is_plugin_mode():
    print("Working as plugin inside cellframe-node")
    # Доступ к node-специфичным возможностям
elif cellframe.is_library_mode():
    print("Working as standalone library")
    # Локальная конфигурация и управление
```

### Thread-safe операции

```python
import cellframe
import threading

def worker():
    # Каждый поток может безопасно работать с контекстом
    context = cellframe.get_context()
    node = cellframe.auto_create_node()
    
    # Операции с блокчейном
    chain = node.get_chain_by_id("mainnet")
    info = chain.get_info()

# Создание нескольких потоков
threads = []
for i in range(5):
    t = threading.Thread(target=worker)
    threads.append(t)
    t.start()

# Ожидание завершения
for t in threads:
    t.join()
``` 