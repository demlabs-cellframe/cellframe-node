# 🐍 Python Cellframe - Проблемы сборки и решения

## 🚨 Критические проблемы

### Проблема с Python 3.13
**Симптом**: `ModuleNotFoundError: No module named 'distutils'`
**Причина**: distutils удален из Python 3.13
**Решение**:
```bash
pip3 install setuptools
# или
python3 -m pip install setuptools wheel
```

### Отсутствие собранного SDK
**Симптом**: `ImportError: No module named 'libCellFrame'`
**Причина**: Cellframe SDK не собран
**Решение**:
1. Собрать cellframe-sdk первым
2. Инициализировать submodules
3. Собрать python-cellframe

## 🔧 Правильная последовательность сборки

### 1. Инициализация submodules
```bash
git submodule update --init --recursive
```

### 2. Сборка Cellframe SDK
```bash
cd cellframe-sdk
./prod_build/build.sh --target osx release
# или для Linux:
# ./prod_build/build.sh --target linux release
```

### 3. Сборка Python модуля
```bash
cd ../python-cellframe
python3 setup.py build_ext --inplace
```

## 🧪 Проблемы с unit тестами

### Все тесты пропускаются
**Симптом**: `4210 skipped, 0 passed`
**Причина**: `@pytest.mark.skipif(not cellframe_available)`
**Решение**: Убедиться что CellFrame модуль доступен

### Проверка доступности модуля
```bash
cd python-cellframe
PYTHONPATH=. python3 -c "import CellFrame; print('OK')"
```

### Исправление синтаксических ошибок
**Проблема**: Дефисы в именах классов
```python
# Неправильно:
class TestLibdap-Chain-Python:

# Правильно:
class TestLibdapChainPython:
```

## 📁 Структура файлов

### Ожидаемая структура после сборки
```
python-cellframe/
├── CellFrame/
│   ├── __init__.py
│   └── libCellFrame.so      # Собранная библиотека
├── cellframe-sdk/           # Submodule
│   └── build_osx_release/   # Собранный SDK
├── tests/                   # Unit тесты
└── setup.py                # Скрипт сборки
```

## 🔍 Диагностика проблем

### Проверка зависимостей
```bash
# Проверить Python версию
python3 --version

# Проверить наличие setuptools
python3 -c "import setuptools; print(setuptools.__version__)"

# Проверить CMake
cmake --version

# Проверить компилятор
gcc --version  # Linux
clang --version  # macOS
```

### Проверка путей
```bash
# Проверить PYTHONPATH
echo $PYTHONPATH

# Найти собранные библиотеки
find . -name "*.so" -o -name "*.dylib"

# Проверить символы в библиотеке
nm -D libCellFrame.so | grep PyInit  # Linux
nm -D libCellFrame.dylib | grep PyInit  # macOS
```

## 🛠️ Решение типичных проблем

### Setup.py синтаксические ошибки
**Проблема**: Отсутствующие запятые в setup.py
```python
# Исправить:
ext_package='CellFrame',  # Добавить запятую
ext_modules=[CMakeExtension('CellFrame/libCellFrame')],
```

### Проблемы с CMake
**Проблема**: CMake не находит зависимости
**Решение**:
```bash
# Установить недостающие зависимости
brew install cmake sqlite3 zlib  # macOS
sudo apt-get install cmake libsqlite3-dev  # Linux

# Очистить кэш CMake
rm -rf build/
mkdir build && cd build
cmake ../
```

### Проблемы с линковкой
**Проблема**: Undefined symbols при импорте
**Решение**:
1. Проверить что все библиотеки собраны
2. Проверить пути к библиотекам
3. Пересобрать с правильными флагами

## 📋 Чеклист для успешной сборки

### Перед началом
- [ ] Python 3.7+ установлен
- [ ] setuptools установлен
- [ ] CMake установлен
- [ ] Компилятор C/C++ доступен
- [ ] Git submodules инициализированы

### Процесс сборки
- [ ] Cellframe SDK собран успешно
- [ ] Python модуль собран без ошибок
- [ ] libCellFrame.so создан
- [ ] CellFrame модуль импортируется
- [ ] Unit тесты запускаются

### После сборки
- [ ] Все тесты проходят
- [ ] Нет ошибок импорта
- [ ] API функции доступны
- [ ] Производительность приемлема

## 🔄 Автоматизация сборки

### Скрипт автоматической сборки
```bash
#!/bin/bash
set -e

echo "🔄 Инициализация submodules..."
git submodule update --init --recursive

echo "🏗️ Сборка Cellframe SDK..."
cd cellframe-sdk
./prod_build/build.sh --target $(uname -s | tr '[:upper:]' '[:lower:]') release
cd ..

echo "🐍 Сборка Python модуля..."
cd python-cellframe
python3 setup.py build_ext --inplace

echo "🧪 Запуск тестов..."
PYTHONPATH=. python3 -m pytest tests/ -v

echo "✅ Сборка завершена успешно!"
```

## 📞 Получение помощи

### Логи для диагностики
```bash
# Подробные логи сборки
python3 setup.py build_ext --inplace --verbose

# Логи CMake
cmake .. -DCMAKE_VERBOSE_MAKEFILE=ON

# Логи тестов
pytest tests/ -v --tb=long
```

### Контакты
- **Telegram**: @cellframe_dev_en
- **GitHub Issues**: https://github.com/demlabs-cellframe/python-cellframe/issues
- **Документация**: https://wiki.cellframe.net 