# 🎯 PHASE 1: ПЛАН ИСПРАВЛЕНИЯ SKIPPED ТЕСТОВ
## Переход от 89 SKIPPED к PASSED тестам

**Дата создания:** 18 июня 2025  
**Приоритет:** CRITICAL  
**Статус:** TODO  

---

## 📊 АНАЛИЗ ТЕКУЩЕГО СОСТОЯНИЯ

### Найденные факты:
- **151 тестовый файл** в директории `tests/`
- **Все тесты используют паттерн:** `@pytest.mark.skipif(not cellframe_available, reason="CellFrame module not available")`
- **Проверка доступности:**
  ```python
  try:
      import CellFrame
      cellframe_available = True
  except ImportError:
      cellframe_available = False
      CellFrame = None
  ```
- **Корневая проблема:** `import CellFrame` не работает → `cellframe_available = False` → все тесты SKIPPED

---

## 🎯 СТРАТЕГИЯ РЕШЕНИЯ

### Вариант 1: Standalone Python Extension (РЕКОМЕНДУЕМЫЙ)
**Цель:** Создать `CellFrame.so` extension модуль для прямого Python импорта

#### Шаги реализации:

1. **Модификация CMakeLists.txt**
   ```cmake
   # В python-cellframe/CMakeLists.txt
   # Заменить:
   add_library(CellFrame MODULE ${PYTHON_CELLFRAME_SRCS} ${PYTHON_CELLFRAME_HEADERS})
   # На:
   add_library(CellFrame SHARED ${PYTHON_CELLFRAME_SRCS} ${PYTHON_CELLFRAME_HEADERS})
   set_target_properties(CellFrame PROPERTIES SUFFIX ".so")
   ```

2. **Исправление циклических зависимостей**
   - Убрать зависимости python модулей от CellFrame target
   - Создать отдельный build target для unit testing

3. **Создание test runner скрипта**
   ```bash
   #!/bin/bash
   export PYTHONPATH="./build_with_python/python-cellframe:$PYTHONPATH"
   export LD_LIBRARY_PATH="./build_with_python/python-cellframe:$LD_LIBRARY_PATH"
   python3 -m pytest tests/ -v
   ```

### Вариант 2: Mock-Based Testing (АЛЬТЕРНАТИВНЫЙ)
**Цель:** Создать mock CellFrame модуль для unit тестирования

#### Преимущества:
- Быстрая реализация
- Независимость от сборки
- Изолированное тестирование

#### Недостатки:
- Не тестирует реальную интеграцию
- Требует поддержки mock API

---

## 🛠️ ДЕТАЛЬНЫЙ ПЛАН РЕАЛИЗАЦИИ

### Этап 1: Подготовка (2-3 часа)

1. **Создание backup текущей сборки**
   ```bash
   cp -r build_with_python build_with_python_backup
   cp python-cellframe/CMakeLists.txt python-cellframe/CMakeLists.txt.backup
   ```

2. **Анализ зависимостей**
   ```bash
   cd python-cellframe
   grep -r "CellFrame" modules/*/CMakeLists.txt > dependencies_analysis.txt
   ```

3. **Создание test environment**
   ```bash
   python3 -m venv test_env
   source test_env/bin/activate
   pip install pytest
   ```

### Этап 2: Модификация Build System (4-6 часов)

1. **Исправление python-cellframe/CMakeLists.txt**
   - Изменить тип библиотеки CellFrame на SHARED
   - Убрать циклические зависимости
   - Добавить proper Python extension настройки

2. **Создание отдельного build target**
   ```cmake
   # Добавить в CMakeLists.txt
   add_custom_target(cellframe_unittest
       DEPENDS CellFrame
       COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:CellFrame> ${CMAKE_SOURCE_DIR}/CellFrame.so
   )
   ```

3. **Тестирование сборки**
   ```bash
   cd build_with_python
   make cellframe_unittest
   ls -la python-cellframe/CellFrame.so
   ```

### Этап 3: Test Enablement (3-4 часа)

1. **Проверка доступности CellFrame**
   ```python
   # Создать test_cellframe_import.py
   import sys
   sys.path.insert(0, './build_with_python/python-cellframe')
   
   try:
       import CellFrame
       print("✅ CellFrame imported successfully!")
       print(f"Available functions: {[f for f in dir(CellFrame) if not f.startswith('_')][:10]}")
   except Exception as e:
       print(f"❌ Import failed: {e}")
   ```

2. **Запуск одного теста для проверки**
   ```bash
   cd python-cellframe
   PYTHONPATH="./build_with_python/python-cellframe" python3 -m pytest tests/core/test_wrapping_dap_chain_tx_out_cond_subtype_srv_stake.py::TestWrappingDapChainTxOutCondSubtypeSrvStake::test_wrapping_dap_chain_tx_out_cond_subtype_srv_stake_get_uid_exists -v
   ```

3. **Массовый запуск тестов**
   ```bash
   PYTHONPATH="./build_with_python/python-cellframe" python3 -m pytest tests/core/ -v --tb=short
   ```

### Этап 4: Debugging & Fixing (4-8 часов)

1. **Анализ failing тестов**
   - Логирование ошибок
   - Исправление API несовместимостей
   - Обновление тестовых данных

2. **Оптимизация производительности**
   - Кэширование импортов
   - Параллельный запуск тестов
   - Уменьшение времени выполнения

---

## 📋 КРИТЕРИИ УСПЕХА

### Минимальные требования:
- [ ] `import CellFrame` работает без ошибок
- [ ] Минимум 80% тестов переходят из SKIPPED в PASSED/FAILED
- [ ] Время выполнения всех тестов < 5 минут
- [ ] 0 тестов в статусе ERROR

### Желаемые результаты:
- [ ] 90%+ тестов в статусе PASSED
- [ ] < 5% тестов в статусе FAILED (с планом исправления)
- [ ] Автоматический test runner готов
- [ ] CI/CD интеграция возможна

### Валидационные команды:
```bash
# Проверка доступности модуля
python3 -c "import CellFrame; print('Success!')"

# Подсчет результатов тестирования
python3 -m pytest tests/ --tb=no -q | grep -E "(passed|failed|skipped|error)"

# Полный отчет
python3 -m pytest tests/ --tb=short -v > test_results.txt
```

---

## ⚠️ РИСКИ И МИТИГАЦИЯ

### Риск 1: Сборка не работает
**Митигация:** Backup текущей рабочей сборки, пошаговое тестирование

### Риск 2: API несовместимости
**Митигация:** Анализ Python C API, постепенное исправление функций

### Риск 3: Производительность
**Митигация:** Профилирование, оптимизация критических путей

### Риск 4: Ломается plugin архитектура
**Митигация:** Отдельные build targets, тестирование cellframe-node

---

## 🚀 СЛЕДУЮЩИЕ ШАГИ

1. **Немедленно:** Создать backup и начать Этап 1
2. **Сегодня:** Завершить Этап 2 (модификация build system)
3. **Завтра:** Этап 3-4 (enablement и debugging)
4. **Результат:** Готовая test suite для Phase 2 рефакторинга

---

## 📊 ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ

**До исправления:**
```
89 tests SKIPPED (100%)
0 tests PASSED
0 tests FAILED
```

**После исправления:**
```
75-80 tests PASSED (85-90%)
5-10 tests FAILED (5-10%) - с планом исправления
0-5 tests SKIPPED (0-5%) - только если действительно нужно
0 tests ERROR
```

**Время выполнения:** < 3 минут для всех тестов  
**Готовность к Phase 2:** 100%

---

*План подготовлен Smart Layered Context системой*  
*Версия: 4.1.0 | Приоритет: CRITICAL | ETA: 2-3 дня* 