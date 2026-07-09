# План: Динамический consensus_section в stage-env

## Проблема
В stage-env `consensus_type` полностью мёртв — он декларируется в `stage-env.cfg` и передаётся в Jinja2 топологию, но **нигде не используется для выбора имени секции конфигурации**. Результат:
- Jinja2 шаблоны `main.cfg.j2` и `network.cfg.j2` всегда пишут `[esbocs]`
- `generator.py` всегда пишет `[chipchain]` в node snippet
- `genesis_config.py` всегда ищет `[chipchain]` при парсинге
- SDK читает секцию `[consensus=xxx]` — т.е. `consensus=esbocs` → ищет `[esbocs]`, `consensus=chipchain` → ищет `[chipchain]`

## Решение: Ввести `consensus_section` как Jinja2 переменную

### Шаг 1: generator.py — добавить `consensus_section` в контекст шаблонов
- В `_generate_network_configs()`: вычислить `consensus_section` из `topology.consensus.type`
- Карта: `'chipchain' → 'chipchain'`, `'esbocs' → 'esbocs'`, `'pos' → 'esbocs'` (для обратной совместимости)
- Передать `consensus_section` в `base_chain_context` и `network_context`
- В `_generate_node_snippet()`: использовать `consensus_section` вместо хардкода `[chipchain]`

### Шаг 2: Jinja2 шаблоны — использовать `{{ consensus_section }}`
- `config/templates/chains/main.cfg.j2`: 
  - `[chain]` → `consensus={{ consensus_section }}`
  - `[esbocs]` → `[{{ consensus_section }}]`
- `config/templates/network.cfg.j2`:
  - `[esbocs]` → `[{{ consensus_section }}]`
  - Комментарии обновить

### Шаг 3: v5.7, v5.8, v6.x базовые шаблоны
- `config/templates/v6.x/cellframe-node.cfg.j2`:
  - `[esbocs]` → `[{{ consensus_section | default('chipchain') }}]`
  - `allowed_cmd` — оставить `esbocs, chipchain` в списке (для CLI доступности обоих)
- Аналогично для v5.7 и v5.8

### Шаг 4: genesis_config.py — динамическое определение секции
- Создать helper-метод `_get_consensus_section(config_file)` который:
  1. Загружает chain config
  2. Читает `config['chain']['consensus']` 
  3. Возвращает это значение как имя секции
- Заменить все `'chipchain' not in config` на `_get_consensus_section(config) not in config`
- 7 мест: строки 521, 645, 651, 656, 662, 664, 667, 696, 701, 931, 934, 937

### Шаг 5: Конфигурация по умолчанию
- `config/stage-env.cfg.default`: `consensus_type = chipchain` (дефолт)
- `config/topologies/default.json.tpl`: обновить описания узлов (убрать "ESBocs" из описаний)
- Комментарий: `# Consensus type: chipchain (recommended) or esbocs (legacy)`

### Шаг 6: Обратная совместимость
- Когда `consensus_type = esbocs`:
  - `default.json.tpl` → `consensus.type = 'esbocs'`
  - `generator.py` → `consensus_section = 'esbocs'`
  - `main.cfg.j2` → `consensus=esbocs`, `[esbocs]`
  - `genesis_config.py` → ищет `[esbocs]`
  - SDK загружает модуль esbocs (если скомпилирован с cs-esbocs)
- Когда `consensus_type = chipchain` (дефолт):
  - Всё работает через `[chipchain]` секции

### Шаг 7: Тестирование
1. Остановить текущие контейнеры
2. Запустить с `consensus_type = chipchain` → проверить что `[chipchain]` секции генерируются
3. Проверить что genesis_config.py парсит `[chipchain]` секцию
4. Опционально: проверить с `consensus_type = esbocs` что `[esbocs]` генерируются

## Файлы для изменения:
1. `tools/stage-env/src/config/generator.py` — добавить `consensus_section`
2. `tools/stage-env/config/templates/chains/main.cfg.j2` — динамическая секция
3. `tools/stage-env/config/templates/network.cfg.j2` — динамическая секция
4. `tools/stage-env/config/templates/v6.x/cellframe-node.cfg.j2` — динамическая секция
5. `tools/stage-env/config/templates/v5.7/cellframe-node.cfg.j2` — аналогично
6. `tools/stage-env/config/templates/v5.8/cellframe-node.cfg.j2` — аналогично
7. `tools/stage-env/src/network/genesis_config.py` — динамическое чтение секции
8. `tools/stage-env/config/stage-env.cfg.default` — дефолт chipchain
9. `tools/stage-env/config/topologies/default.json.tpl` — обновить описания
10. `tests/stage-env.cfg` — убедиться что consensus_type = chipchain

## Ключевые ограничения (НЕ СЛОМАТЬ):
- `zerochain` всегда `consensus=dag_poa` + `[dag-poa]` — НЕ ТРОГАТЬ
- `dag-poa` шаблоны `zerochain.cfg.j2` — НЕ ТРОГАТЬ
- SDK C-код (cellframe-sdk) — НЕ ТРОГАТЬ
- CLI команды `allowed_cmd` — оставить оба `esbocs, chipchain`
- `esbocs_waiters.py` уже удалён, `chipchain_waiters.py` на месте — ОК