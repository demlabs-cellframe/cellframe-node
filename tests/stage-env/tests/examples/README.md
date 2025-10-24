# Test Examples

Эта директория содержит **примеры** тестовых сценариев, демонстрирующие возможности stage-env.

## ⚠️ Важно

Примеры **НЕ запускаются автоматически** при выполнении `./tests/run.sh`.

Они предназначены для:
- 📚 Обучения и документации
- 🔬 Экспериментов с новыми возможностями
- 📋 Шаблонов для создания собственных тестов
- 🧪 Ручного запуска для демонстрации функций

## Запуск примеров

### Запуск конкретного примера:
```bash
cd tests/stage-env
./stage_env.py run-tests tests/examples/test_vpn_node.yml
```

### Запуск всех примеров:
```bash
cd tests/stage-env
./stage_env.py run-tests tests/examples/
```

## Доступные примеры

### 1. `test_vpn_node.yml`
**Демонстрация:** Docker customizations для VPN тестирования
- ✅ NET_ADMIN capabilities
- ✅ TUN/TAP устройство
- ✅ Sysctls (IP forwarding)
- ✅ Custom packages (WireGuard, OpenVPN)
- ✅ Asymmetric topology (сервер + клиент)

**Возможности:**
- Создание VPN интерфейсов внутри контейнеров
- Проверка сетевых capabilities
- Тестирование туннелирования

### 2. `test_version_compatibility.yml`
**Демонстрация:** Per-node package sources
- ✅ Разные версии на разных нодах
- ✅ URL, local, repository источники
- ✅ Тестирование совместимости версий
- ✅ Смешанные сборки (debug + release)

**Возможности:**
- Проверка обратной совместимости
- Тестирование миграций между версиями
- Симуляция гетерогенной сети

### 3. `test_defaults_and_groups.yml`
**Демонстрация:** Hierarchical defaults и step grouping
- ✅ Global defaults
- ✅ Section-level defaults
- ✅ Group-level defaults
- ✅ Nested groups
- ✅ Defaults inheritance and override

**Возможности:**
- Минимизация дублирования кода
- Логическая группировка шагов
- Гибкое переопределение параметров

## Создание собственных тестов

Используйте примеры как шаблоны:

1. **Скопируйте** подходящий пример
2. **Адаптируйте** под ваши нужды
3. **Разместите** в соответствующей директории:
   - `tests/e2e/` - сквозные интеграционные тесты
   - `tests/functional/` - функциональные тесты
   - `tests/stage-env/tests/base/` - базовые тесты окружения

## Структура примера

```yaml
name: "Test Name"
description: "What this test does"

network:
  topology: minimal
  nodes:
    - name: node1
      role: root
      # Customizations here

defaults:
  node: node1
  wait: 2s

setup:
  - cli: "version"

test:
  - group:
      description: "Test group"
      steps:
        - cli: "command"

check:
  - cli: "stats"
    expect: success
```

## Полезные ссылки

- [Scenario Language Guide](../../docs/ru/scenarios/Glossary.md)
- [Defaults & Groups](../../docs/ru/scenarios/Defaults-And-Groups.md)
- [Per-Node Packages](../../docs/en/Per-Node-Packages.md)
- [Docker Customizations](../../config/stage-env.cfg.default#L340)

## Вопросы?

Если что-то непонятно или нужны дополнительные примеры:
1. Изучите существующие тесты в `tests/e2e/` и `tests/functional/`
2. Прочитайте документацию в `tests/stage-env/docs/`
3. Экспериментируйте с примерами!

