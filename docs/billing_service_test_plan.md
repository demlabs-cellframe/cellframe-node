## Тест‑план: биллинг сервисов (dap_stream_ch_chain_net_srv.c)

Документ описывает перечень тестируемых сценариев с ожидаемым поведением, покрытия по состояниям, а также список необходимых моков и их API‑поведение. Основано на анализе `docs/billing_service_system_analysis.md`.

### 1. Цели тестирования
- Проверить корректность запуска обслуживания по пакету REQUEST и разветвления (free/pay/grace).
- Валидировать flow квитанций, таймеров и ретраев при подписи клиентом.
- Подтвердить корректность интеграции с Ledger/Mempool/GDB при всех статусах.
- Проверить машину состояний (state + substate) и переходы, включая ошибки и банлист.

### 2. Область покрытия (функции/кейсы)
- Запуск: `s_service_start`
- Подписи и отправка квитанций: `s_service_substate_pay_service`, `s_start_receipt_timeout_timer`, `s_receipt_timeout_handler`
- Оплата: `s_pay_service`, `s_check_tx_params`
- Grace: `s_service_state_go_to_grace`, `s_service_substate_go_to_waiting_prev_tx`, `s_service_substate_go_to_waiting_new_tx`, `s_grace_period_finish`, `dap_stream_ch_chain_net_srv_tx_cond_added_cb(_mt)`
- Ошибки/завершение: `s_service_state_go_to_error`, `s_service_substate_go_to_error`, `s_service_state_go_to_normal`, `s_service_substate_go_to_normal`
- Персистентность/банлист/статистика: `s_get_ban_group`, `s_ban_client`, `s_unban_client`, `s_set_usage_data_to_gdb`, `s_calc_datoshi`

### 3. Список тестов (подробные сценарии)

1) REQUEST: Free‑mode
   - Условия: `allow_free_srv=true`, `price.value_datoshi==0`.
   - Действия: прислать `REQUEST` с валидным `order_hash`/`tx_cond`.
   - Ожидание: `RESPONSE_SUCCESS`, `service_state=FREE`, статистика → секция `free`.

2) REQUEST: Net offline
   - Условия: сеть OFFLINE.
   - Действия: прислать платный `REQUEST`.
   - Ожидание: `RESPONSE_ERROR=NETWORK_IS_OFFLINE`.

3) REQUEST: Платный, tx_cond присутствует, есть остаток услуги
   - Условия: ledger вернёт `tx_cond`, `get_remain_service` выдаёт лимиты для нужной единицы.
   - Ожидание: старт без оплаты, `RESPONSE_SUCCESS`, `service_state=NORMAL`, создан `receipt`, лимиты в сессии выставлены.

4) REQUEST: Платный, tx_cond отсутствует, не забанен
   - Условия: ledger не находит `tx_cond`, банлист пуст.
   - Ожидание: запуск grace → `service_state=GRACE`, substate= `WAITING_TX_FOR_PAYING`, отправлен `RESPONSE_SUCCESS`, старт таймера grace.

5) REQUEST: Платный, tx_cond отсутствует, клиент в бане
   - Условия: s_check_client_is_banned возвращает будущее время.
   - Ожидание: `RESPONSE_ERROR=RECEIPT_BANNED_PKEY_HASH`.

6) SIGN_RESPONSE: happy‑path оплаты через mempool
   - Условия: находили `tx_cond`, отправили `SIGN_REQUEST`, клиент вернул валидную квитанцию v2; mempool возвращает SUCCESS.
   - Ожидание: переход в `NORMAL` (или `substate NORMAL` при следующем цикле), сохранение квитанции в `local.receipts`, отправка `RESPONSE_SUCCESS`.

7) SIGN_RESPONSE: неверная версия/размер/несовпадение квитанции
   - Условия: версия!=2 или payload не совпал с ожидаемым.
   - Ожидание: `RECEIPT_WRONG_VERSION` или `RECEIPT_CANT_FIND`, переход в ошибку.

8) SIGN_RESPONSE: неверный pkey_hash в out_cond
   - Условия: сравнение с `l_tx_out_cond->subtype.srv_pay.pkey_hash` не проходит.
   - Ожидание: `RECEIPT_WRONG_PKEY_HASH`, переход в ошибку.

9) PAY: mempool NOT_ENOUGH
   - Ветка из `IDLE`: запуск grace (→ `WAITING_NEW_TX_FROM_CLIENT`).
   - Ветка из `NORMAL`: `s_service_substate_go_to_waiting_new_tx`, отправка `RESPONSE_ERROR=TX_COND_NOT_ENOUGH`.

10) PAY: mempool CANT_FIND_FINAL_TX_HASH/NO_COND_OUT
    - При наличии предшествующего out_cond SRV_PAY → трактовать как `NOT_ENOUGH`.
    - При отсутствии → ошибка создания входа, переход в ошибку.

11) NEW_TX_COND_RESPONSE: пустой tx_cond
    - Условия: substate=`WAITING_NEW_TX_FROM_CLIENT`.
    - Ожидание: завершение grace, `RESPONSE_ERROR=TX_COND_NO_NEW_COND`.

12) NEW_TX_COND_RESPONSE: валидный tx_cond уже в леджере
    - Ожидание: удалить текущую grace‑запись, сгенерировать новую квитанцию, substate=`WAITING_RECEIPT_FOR_NEW_TX_FROM_CLIENT`, отправить `SIGN_REQUEST`, стартовать таймер подписи.

13) NEW_TX_COND_RESPONSE: валидный tx_cond ещё не в леджере
    - Ожидание: substate= `WAITING_NEW_TX_IN_LEDGER`, перенос grace‑записи на ожидание нового хеша.

14) GRACE таймаут: tx_cond не появился
    - Ожидание: `TX_COND_NOT_FOUND`, переход в ошибку и добавление клиента в банлист.

15) GRACE: уведомление леджера о добавлении tx_cond
    - Ожидание: ветка `_cb_mt`: остановка таймера, перегенерация квитанции (для NEW_TX_IN_LEDGER) и `SIGN_REQUEST`; иначе — повтор платежа.

16) Таймаут подписи квитанции
    - Условия: `RECEIPT_SIGN_MAX_ATTEMPT` попыток.
    - Ожидание: повторные `SIGN_REQUEST`; по исчерпании → `RECEIPT_NO_SIGN`, переход в ошибку.

17) Статистика GDB
    - Условия: имитировать трафик и время, режимы FREE/GRACE/NORMAL.
    - Ожидание: корректное накопление полей и `datoshi_value` через `s_calc_datoshi`, запись в `local.srv_statistic`.

18) Банлист: добавление и снятие
    - Ошибка в GRACE → клиент попадает в банлист на `grace_period*50`.
    - По истечении — снятие через `s_unban_client`.

19) Ошибки роли/сети
    - Роль ниже требуемой → `SERVICE_NODE_ROLE_ERROR`.
    - Сеть OFFLINE во время SIGN_RESPONSE → `NETWORK_IS_OFFLINE`.

20) DATA/RESPONSE_DATA
    - При наличии `callbacks.custom_data` корректно оборачивается ответ `RESPONSE_DATA`.

21) Удаление канала
    - Ожидание: запись статистики usage в GDB и вызов `save_remain_service`.

22) Потенциальная инверсия квитанций в `WAITING_RECEIPT_FOR_NEW_TX_FROM_CLIENT`
    - Репродукция ветки `s_receipt_timeout_handler`: проверить, что правильная квитанция уходит клиенту; если воспроизводится инверсия — зафиксировать как багтест.

### 4. Матрица трассируемости
- REQUEST → тесты 1–5
- SIGN_RESPONSE → тесты 6–8, 16, 19
- PAY/mempool → тесты 6, 9–10
- GRACE/timers/ledger cb → тесты 4, 14–15, 11–13
- Статистика/банлист → тесты 17–18
- Stream data → тест 20
- Teardown → тест 21

### 5. Необходимые моки и ожидаемое поведение
- Ledger API:
  - `dap_ledger_tx_find_by_hash(net->pub.ledger, hash)` → сценарии: найден/не найден; возвращать преднастроенные tx структуры.
  - `dap_ledger_tx_get_token_ticker_by_hash(ledger, hash)` → вернуть корректный тикер/NULL.
  - Уведомления: триггер `dap_stream_ch_chain_net_srv_tx_cond_added_cb` с параметрами (tx, hash, ADDED).
- Mempool API:
  - `dap_chain_mempool_tx_create_cond_input(net, tx_cond_hash, wallet_addr, enc_key, receipt, fmt, ret_status)` → сценарии SUCCESS, NOT_ENOUGH, CANT_FIND_FINAL_TX_HASH, NO_COND_OUT, WRONG_ADDR, CANT_ADD_SIGN и т.д.; при SUCCESS возвращать строку хеша входа.
- Global DB:
  - `dap_global_db_get/set/del/get_all_sync` → in‑memory имитация KV‑хранилища, поддержка групп, проверка размеров.
- Таймеры/воркеры:
  - `dap_timerfd_start_on_worker(cb,arg)`/`dap_timerfd_delete[_unsafe/_mt]` → эмуляция немедленного/отложенного вызова; контроль идентификаторов таймеров.
  - `dap_worker_exec_callback_on(worker, cb, arg)` → синхронный вызов.
- Stream:
  - Перехват `dap_stream_ch_pkt_write_unsafe(a_ch, type, data, size)` → лог/буфер для ассертов отправляемых пакетов.
- Сервис/прайс/сертификаты:
  - `dap_chain_net_srv_get`, `dap_chain_net_srv_get_price_from_order` → возврат поддельного сервиса/прайса по `order_hash`.
  - `get_remain_service`, `response_success`, `response_error`, `custom_data`, `save_remain_service` → controllable callbacks.
  - Сертификат `receipt_sign_cert->enc_key` → заглушка ключа.
- Время/рандом/хеши:
  - `dap_time_now`, `dap_nanotime_now` → контролируемые значения.
  - `dap_hash_fast`, `dap_chain_hash_fast_to_str_static/new`, сравнения/конверсии → стабилизация для предсказуемых тестов.

### 6. Организация тестов
- Фреймворк: CMake/CTest (как в проекте), имена файлов: `*_test.c`, функции `test_*`.
- Группировка по сценариям (request_signing_pay, grace_flow, mempool_statuses, gdb_stats, banlist, stream_data, teardown).
- Проверки: состояние usage (state/substate), отправленные пакеты, записи в GDB, вызовы callbacks, изменения tx_cond_hash.

### 7. Нефункциональные проверки
- Идемпотентность некоторых переходов при повторных входящих пакетах.
- Отсутствие «утечек» состояния при ошибках и корректная очистка.

Документ готов служить источником правды для реализации тестов и моков.


