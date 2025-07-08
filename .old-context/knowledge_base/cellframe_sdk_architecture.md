# 🏗️ Cellframe SDK & DAP SDK - База знаний

## 📋 Обзор архитектуры

**Cellframe SDK** - это комплексная блокчейн-платформа третьего поколения с модульной архитектурой, построенная на базе **DAP SDK**.

### Ключевые особенности
- **Post-quantum криптография** (NIST PQC Round 3)
- **2-уровневый шардинг**
- **P2P cross-chain операции**
- **Модульная архитектура** на языке C
- **Python SDK** для разработки dApps

## 🏛️ Структура проектов

### Cellframe Node
```
cellframe-node/
├── cellframe-sdk/          # Основной SDK (submodule)
├── dap-sdk/               # Базовый SDK (submodule)  
├── python-cellframe/      # Python bindings (submodule)
├── sources/               # Исходники ноды
├── conftool/              # Инструмент конфигурации
└── diagtool/              # Диагностический инструмент
```

### Cellframe SDK
```
cellframe-sdk/
├── dap-sdk/               # Базовый SDK (submodule)
├── modules/               # Модули блокчейна
│   ├── chain/            # Управление цепями
│   ├── consensus/        # Консенсус алгоритмы
│   ├── ledger/           # Книга транзакций
│   ├── mempool/          # Пул транзакций
│   ├── net/              # Сетевой уровень
│   └── wallet/           # Кошельки
└── 3rdparty/             # Внешние зависимости
```

## 🔧 Процесс сборки

### Зависимости (Linux)
```bash
sudo apt-get install build-essential cmake dpkg-dev \
    libz-dev libmagic-dev libsqlite3-dev traceroute \
    debconf-utils xsltproc libpq-dev
```

### Зависимости (macOS)
```bash
brew install cmake sqlite3 zlib
```

### Сборка SDK
```bash
git clone --recursive https://gitlab.demlabs.net/cellframe/cellframe-node.git
cd cellframe-node
mkdir build && cd build
cmake ../
make -j$(nproc)
```

### Сборка Python модуля
```bash
cd python-cellframe
git submodule update --init
cd cellframe-sdk
git submodule update --init
cd ..
python3 setup.py build_ext --inplace
```

## 🐍 Python SDK

### Установка зависимостей
- Python 3.7+
- scikit-build
- Собранный Cellframe SDK

### Структура модуля
- **CellFrame** - основной Python модуль
- **libCellFrame** - нативная библиотека (.so/.dll)
- **Wrappers** для всех основных компонентов

### Типичный плагин
```python
def init():
    """Инициализация плагина"""
    pass

def deinit():
    """Деинициализация плагина"""
    pass
```

## 🌐 Сетевые компоненты

### Поддерживаемые сети
- **Backbone** - Mainnet
- **Mileena** - Testnet
- **Subzero** - Testnet  
- **KelVPN** - VPN сеть

### Консенсус алгоритмы
- **DAG-PoA** (Directed Acyclic Graph Proof of Authority)
- **Block-PoS** (Block Proof of Stake)
- **ESBOCS** (Enhanced Scalable Byzantine Consensus)

## 💎 Криптография

### Post-quantum алгоритмы
- **CRYSTALS-Dilithium** - цифровые подписи
- **CRYSTALS-Kyber** - обмен ключами
- **Falcon** - компактные подписи

### Классические алгоритмы
- **ECDSA** (secp256k1)
- **SHA-3** (Keccak)
- **AES** шифрование

## 🔗 Ключевые компоненты

### Chain (Цепи)
- Управление блокчейн цепями
- Поддержка DAG и Block структур
- Атомарные операции

### Ledger (Книга)
- Учет балансов и транзакций
- Верификация операций
- Кэширование для производительности

### Mempool (Пул транзакций)
- Временное хранение транзакций
- Валидация перед включением в блок
- Приоритизация транзакций

### Global DB
- Распределенная база данных
- Синхронизация между нодами
- Кластерная архитектура

## 🛠️ Инструменты разработки

### CLI команды
```bash
cellframe-node-cli help           # Справка
cellframe-node-cli wallet new     # Создать кошелек
cellframe-node-cli tx_create      # Создать транзакцию
cellframe-node-cli net sync       # Синхронизация
```

### Диагностика
- **diagtool** - диагностический инструмент
- **Логирование** с различными уровнями
- **Мониторинг** состояния сети

## 📚 Документация и ресурсы

### Официальные источники
- **Wiki**: https://wiki.cellframe.net
- **GitHub**: https://github.com/demlabs-cellframe
- **Блог**: https://cellframe.net/blog
- **Telegram**: @cellframe_dev_en

### Примеры и туториалы
- Создание плагинов
- Работа с кошельками
- Настройка VPN сервиса
- Разработка dApps

## 🚨 Известные проблемы

### Python 3.13
- Проблемы с `distutils` (удален в Python 3.13)
- Решение: использовать `setuptools`

### Сборка
- Требуется правильная инициализация submodules
- Зависимости от системных библиотек
- Проблемы совместимости между версиями

### Тестирование
- Unit тесты требуют собранного модуля
- Пропуск тестов при отсутствии CellFrame
- Необходимость валидации API

## 🔄 Версионирование

### Текущие версии
- **Cellframe Node**: 5.3-348
- **Cellframe SDK**: Синхронизируется с Node
- **Python Cellframe**: Синхронизируется с SDK

### Обновления
- Регулярные релизы
- Обратная совместимость
- Миграционные руководства 