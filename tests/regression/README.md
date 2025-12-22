# Regression Test Scenarios for Stage Environment

Этот каталог содержит production-like регрессионные тесты для багов, выполняемые в Docker-based stage environment.

## Созданные сценарии

### Bug #20138: Signature Validation Issue
**Файл**: `bug_20138_signature_validation.yml`

**Описание**: Arbitrage транзакция не авторизуется несмотря на правильный сертификат

**Симптомы**:
- TX создается успешно
- TX застревает в mempool со status='hole'  
- Ошибка: "invalid owner signature or arbitrage disabled for token"
- Тот же сертификат используется для token_decl И arbitrage

**Сценарии**:
1. Arbitrage без -cert → ожидаемая ошибка (TSD sanity check)
2. Arbitrage с -cert → воспроизведение бага (TX stuck in mempool)

**Запуск**:
```bash
./stage-env scenarios/regression/bug_20138_signature_validation.yml
```

---

### Bug #20273: Balance Zeroing After UTXO Blocking  
**Файл**: `bug_20273_balance_zeroing.yml`

**Описание**: Arbitrage игнорирует -value и обнуляет баланс отправителя ПОСЛЕ token_update

**Критический триггер**: 🔴 Баг возникает ТОЛЬКО ПОСЛЕ token_update (UTXO blocking)

**Симптомы**:
- -value флаг игнорируется
- Весь баланс отправителя обнуляется
- Вместо создания change output, все средства уходят на fee address

**Сценарии**:
1. Arbitrage БЕЗ token_update → baseline (работает корректно)
2. Arbitrage С token_update → воспроизведение бага (balance = 0)

**Запуск**:
```bash
./stage-env scenarios/regression/bug_20273_balance_zeroing.yml
```

---

## Особенности stage-env тестов

### Отличия от synthetic tests

| Аспект | Synthetic Tests | Stage-Env Tests |
|--------|----------------|-----------------|
| Окружение | In-memory, single process | Docker containers, multi-node |
| Consensus | Simplified (DAG PoA mock) | Real DAG PoA with validators |
| Chains | zerochain + main (same chain) | zerochain + main (separate) |
| Network | Synthetic | Production-like stagenet |
| Execution | C code, direct API calls | CLI commands via Docker exec |
| Isolation | Per-test process | Per-scenario containers |

### Преимущества

1. **Production-like conditions**: Реальные Docker контейнеры, как в production
2. **Real consensus**: DAG PoA с несколькими валидаторами, требует подписей
3. **CLI-based**: Тестирует CLI commands, как используют пользователи
4. **Network latency**: Реальные сетевые задержки между нодами
5. **Multi-node**: Проверяет синхронизацию и consensus между нодами

## Структура сценариев

### Общий формат:

```yaml
name: Test Name
description: Detailed description

includes:
  - common/network_full.yml  # Network setup
  - common/set_net_default.yml

network:
  topology: default
  name: stagenet
  consensus: dag-poa

setup:
  - docker_op: start
    services: [root-1, validator-1, validator-2]
  - wait_network: online
    timeout: 120

test:
  - group: Test Group Name
    steps:
      - cli: "command"
        save_hash: variable_name
      - wait_for_datum: "{{hash}}"
        chain: main
      - python: |
          # Validation logic
          ...

cleanup:
  - docker_op: stop
```

## Запуск всех regression тестов

```bash
# Все regression сценарии:
cd /home/naeper/work/cellframe-node/tests/stage-env
./stage-env scenarios/regression/*.yml

# Только bugs 20138 и 20273:
./stage-env scenarios/regression/bug_20138_signature_validation.yml
./stage-env scenarios/regression/bug_20273_balance_zeroing.yml
```

## Интеграция с CI/CD

Эти сценарии готовы к интеграции в CI/CD pipeline для автоматического регрессионного тестирования после каждого изменения в arbitrage или token_update модулях.

## См. также

- Synthetic tests: `cellframe-sdk/tests/regression/test_bug_20138.c`, `test_bug_20273.c`
- Documentation: `.context/tasks/bug/20138.json`, `20273.json`
- Investigation report: `.context/tasks/bug/INVESTIGATION_REPORT.md`

