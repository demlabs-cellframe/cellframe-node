## Анализ системы биллинга сервисов (dap_stream_ch_chain_net_srv.c)

Документ описывает логику биллинга сервисов, взаимодействие с клиентом через Stream Channel, работу с блокчейном/леджером/мемпулом и персистентные аспекты (GDB, банлисты, статистика). Основано на анализе файла `cellframe-sdk/modules/channel/chain-net-srv/dap_stream_ch_chain_net_srv.c`.

### 1. Состав системы и основные сущности
- **Stream Channel NET SRV**: канал `DAP_STREAM_CH_NET_SRV_ID`, обработчики: `s_stream_ch_new`, `s_stream_ch_delete`, `s_stream_ch_packet_in`, `s_stream_ch_packet_out`.
- **Session/Inheritor**: при создании канала создаётся `dap_chain_net_srv_stream_session` (см. `dap_chain_net_srv_stream_session_create`). В `usage_active` хранится текущий контекст обслуживания.
- **Service (VPN)**: в текущей реализации используется прайс-лист, извлекаемый по order hash и имени сервиса `"srv_vpn"` (`dap_chain_net_srv_get_price_from_order`). Флаг `allow_free_srv` разрешает бесплатный режим.
- **Usage**: состояние обслуживания клиента, включает:
  - `service_state`: IDLE | GRACE | NORMAL
  - `service_substate`: IDLE | WAITING_FIRST_RECEIPT_SIGN | WAITING_NEXT_RECEIPT_SIGN | WAITING_TX_FOR_PAYING | WAITING_NEW_TX_FROM_CLIENT | WAITING_NEW_TX_IN_LEDGER | WAITING_RECEIPT_FOR_NEW_TX_FROM_CLIENT | NORMAL | ERROR
  - `price`, `net`, `service`, `client` (включая worker/ch), `tx_cond_hash`/`tx_cond`, `receipt`/`receipt_next`, `token_ticker`, `last_err_code`, счётчики байтов и т.п.
- **Grace**: структура ожидания с таймером и хеш-таблицей `grace_hash_tab` в сервисе (под мьютексом).
- **GDB**: группы `local.srv_statistic`, `local.srv_pay`, `local.receipts`, а также динамические группы банлистов вида `local.<net_prefix>.0x<srv_uid>.ban_list.<cert_pkey_hash>`.
- **Callbacks сервиса**: `response_success`, `response_error`, `custom_data`, `get_remain_service`, `save_remain_service`.

### 2. Протокол взаимодействия по Stream
- Входящие типы пакетов (обрабатываются в `s_stream_ch_packet_in`):
  - `CHECK_REQUEST` → проверка доступности и целостности payload, ответ `CHECK_RESPONSE` с (возможной) заменой данных.
  - `REQUEST` → запуск обслуживания: создаётся `usage`, выбирается `price` по `order_hash`, проверяется сеть/роль, выбирается режим оплаты (free/grace/pay). Успех → `RESPONSE_SUCCESS`; ошибки → `RESPONSE_ERROR`.
  - `SIGN_RESPONSE` → клиент возвращает подписанную квитанцию (`dap_chain_datum_tx_receipt_t`, version=2), сервер валидирует и инициирует оплату через мемпул.
  - `DATA` → пользовательский payload: отдаётся в `callbacks.custom_data`, ответ `RESPONSE_DATA` при наличии выходных данных.
  - `RESPONSE_ERROR` → лог уведомления об ошибке на стороне удалённого узла (в клиентском режиме; сервер здесь в основном логирует).
  - `NEW_TX_COND_RESPONSE` → клиент присылает новый `tx_cond` для оплаты (когда предыдущий не найден/нехватает средств).

Отправляемые сервером пакеты:
- `RESPONSE_SUCCESS` с `usage_id/net_id/srv_uid` (иногда с доп. данными).
- `RESPONSE_ERROR` с `code` и контекстом.
- `SIGN_REQUEST` — квитанция на подпись клиентом (`receipt` или `receipt_next`).
- `RESPONSE_DATA` — результат обработки пользовательского `DATA`.

Таймеры и ретраи:
- Таймер ожидания подписи квитанции: 10 сек, до `RECEIPT_SIGN_MAX_ATTEMPT` попыток, затем ошибка `RECEIPT_NO_SIGN`.
- Таймер grace: `service->grace_period` секунд; по истечении — либо переход к оплате, либо ошибка `TX_COND_NOT_FOUND`.

### 3. Запуск обслуживания (REQUEST) и выбор режима
Функция: `s_service_start(a_ch, a_request, a_request_size)`
1) Валидация входа: наличие `order_hash`, `tx_cond`, сети `net`, роли узла (требование роли не ниже master; при несоответствии → `SERVICE_NODE_ROLE_ERROR`).
2) Создание `usage`, привязка клиента/worker/сеанса, установка `tx_cond_hash` и пр.
3) Получение прайса: `dap_chain_net_srv_get_price_from_order(srv, "srv_vpn", order_hash)`.
   - Если цена нулевая и `allow_free_srv`: режим FREE → `RESPONSE_SUCCESS` и `service_state=FREE`.
   - Иначе — платный режим:
     - Если сеть OFFLINE → ошибка `NETWORK_IS_OFFLINE`.
     - Сохранить `static_order_hash` для сверки.
     - Найти `tx_cond` в леджере по `tx_cond_hash`:
       - Найден → `s_unban_client()`, `usage->tx_cond = tx`, переход к оплате `s_service_substate_pay_service()`.
       - Не найден → проверить банлист. Если клиент забанен до `t_end` → ошибка `RECEIPT_BANNED_PKEY_HASH`. Иначе запустить grace: `s_service_state_go_to_grace()`.

### 4. Оплата услуги (pay flow)
Первичный ход (`s_service_substate_pay_service`):
1) Если есть остатки у клиента (`callbacks.get_remain_service`) для совпадающей единицы измерения (SEC/B):
   - Применить лимиты в сессии (`limits_ts/limits_bytes`), ответить `RESPONSE_SUCCESS` и сгенерировать стартовую квитанцию `receipt`, перейти в `service_state=NORMAL`.
2) Иначе:
   - Сформировать первую квитанцию `receipt = dap_chain_net_srv_issue_receipt(...)`.
   - Отправить `SIGN_REQUEST` клиенту, перейти в `WAITING_FIRST_RECEIPT_SIGN`, запустить таймер ожидания подписи.

Ответ клиента (`SIGN_RESPONSE`):
1) Валидации: размер ≥ `sizeof(dap_chain_receipt_info_t)`, `receipt_info.version==2`, состояние ожидания подписи.
2) Отмена таймера ожидания подписи.
3) Сеть должна быть ONLINE.
4) Сопоставление полученной квитанции с ожидаемой (`receipt`/`receipt_next` в зависимости от сабстейта). При несоответствии → ошибка `RECEIPT_CANT_FIND`.
5) Проверка `tx_cond` и извлечение `out_cond` типа `SRV_PAY`; проверка совпадения `pkey_hash` клиента.
6) Обновление актуальной квитанции в `usage` (копия payload клиента).
7) Вызов оплаты: `s_pay_service(usage, receipt_or_next)`.

`s_pay_service` выполняет:
- Поиск `tx_cond` в леджере. Если не найден → `PAY_SERVICE_STATUS_TX_CANT_FIND`.
- `s_check_tx_params`:
  - Наличие `out_cond` `SRV_PAY` и соответствие `srv_uid` сервиса.
  - Получение `token_ticker` по `tx_cond_hash` и его совпадение с `price.token`.
  - Совпадение единиц измерения (SEC/B) и ограничение `unit_price_max_datoshi`.
  - Ненулевые `units` в прайсе.
- Попытка создать входную транзакцию через мемпул:
  `dap_chain_mempool_tx_create_cond_input(net, tx_cond_hash, price.wallet_addr, price.receipt_sign_cert->enc_key, receipt, ...)`.
  - SUCCESS → обновить `tx_cond_hash` на хеш созданного входа, сохранить квитанцию в `local.receipts`, переход в `NORMAL` (или в сабстейт `NORMAL` при следующем цикле).
  - CANT_FIND_FINAL_TX_HASH / NO_COND_OUT → попытка найти предыдущий `out_cond`; при успехе → `NOT_ENOUGH`, иначе → `TX_ERROR`.
  - NOT_ENOUGH → недостаточно средств в `tx_cond`.
  - Прочие → `TX_ERROR`.

Реакция на статусы в `s_service_substate_pay_service`:
- SUCCESS → сохранить квитанцию в GDB `local.receipts`, перейти в `NORMAL`/`NORMAL` сабстейт.
- TX_CANT_FIND →
  - Если ожидали новый `tx_cond` от клиента → `WAITING_NEW_TX_IN_LEDGER`.
  - Если были `NORMAL` без ожиданий → перейти в ожидание прежнего `tx_cond` (`WAITING_TX_FOR_PAYING`) через `s_service_substate_go_to_waiting_prev_tx`.
  - Если были `IDLE` → запустить grace `s_service_state_go_to_grace`.
  - Иначе установить соответствующий `last_err_code` и перейти в ошибку.
- NOT_ENOUGH →
  - Из `IDLE` → запустить grace `s_service_state_go_to_grace`.
  - Иначе → запросить новый `tx_cond` у клиента `s_service_substate_go_to_waiting_new_tx` (с отправкой `RESPONSE_ERROR` `TX_COND_NOT_ENOUGH`).
- MEMALLOC / TX_ERROR → очистка `receipt_next` и переход в ошибку (с кодом `TX_CREATION_ERROR`, если не установлен).

### 5. Grace-период: ветки и завершение
Варианты запуска:
- `s_service_state_go_to_grace` из `IDLE` (tx не найден) → `WAITING_TX_FOR_PAYING` и ответ `RESPONSE_SUCCESS` клиенту (услуга ещё не начата).
- `s_service_state_go_to_grace` из `WAITING_FIRST_RECEIPT_SIGN` (недостаточно средств) → `WAITING_NEW_TX_FROM_CLIENT`.

Технически:
- Создаётся объект `grace` с таймером на `grace_period` секунд, запись добавляется в `service->grace_hash_tab` под мьютексом.
- По истечении таймера `s_grace_period_finish` проверяет наличие `tx_cond` в леджере:
  - Нет → устанавливает `TX_COND_NOT_FOUND`, переход в ошибку.
  - Есть → повторная попытка оплаты `s_service_substate_pay_service`.

Обработка события из леджера:
- Callback `dap_stream_ch_chain_net_srv_tx_cond_added_cb` вызывается при добавлении tx.
- Если tx соответствует ожидаемому `tx_cond_hash` в `grace_hash_tab`, перенос обработки на нужный worker (`dap_worker_exec_callback_on`).
- В `dap_stream_ch_chain_net_srv_tx_cond_added_cb_mt`:
  - Удаляется объект из `grace_hash_tab`, таймер останавливается.
  - Если ждали новый `tx_cond` (`WAITING_NEW_TX_IN_LEDGER`): формируется новая квитанция (`receipt`/`receipt_next`) на новый `tx_cond`, сабстейт → `WAITING_RECEIPT_FOR_NEW_TX_FROM_CLIENT`, запускается таймер ожидания подписи и отсылается `SIGN_REQUEST`.
  - Иначе — обычная оплата через `s_service_substate_pay_service`.

Обработка `NEW_TX_COND_RESPONSE` от клиента:
- Если текущий сабстейт `WAITING_NEW_TX_FROM_CLIENT` и пришёл `tx_cond`:
  - Если новый `tx_cond` уже в леджере → удалить grace-запись, сформировать новую квитанцию, сабстейт → `WAITING_RECEIPT_FOR_NEW_TX_FROM_CLIENT`, отправить `SIGN_REQUEST` и запустить таймер.
  - Если ещё не в леджере → сабстейт → `WAITING_NEW_TX_IN_LEDGER`, grace-запись переносится под ожидание нового хеша.
- Если `tx_cond` пустой → завершить grace и перейти в ошибку `TX_COND_NO_NEW_COND`.

### 6. Таймаут ожидания подписи
`s_start_receipt_timeout_timer` запускает таймер на 10 секунд; `s_receipt_timeout_handler`:
- До `RECEIPT_SIGN_MAX_ATTEMPT-1` повторно шлёт `SIGN_REQUEST` (в зависимости от сабстейта — первую или следующую квитанцию).
- При исчерпании попыток → `last_err_code = RECEIPT_NO_SIGN`, переход в ошибку.

Замечание: в ветке `WAITING_RECEIPT_FOR_NEW_TX_FROM_CLIENT` в текущем коде отправка квитанций, вероятно, перепутана местами (при наличии `receipt_next` отправляется `receipt`, и наоборот). Это кандидат на баг и юнит-тест.

### 7. Ошибки, завершение, банлисты
- `s_service_substate_go_to_error`:
  - Если `service_state==NORMAL` → фиксирует ошибку, очищает `receipt_next`, переводит сабстейт в `ERROR`, отправляет `RESPONSE_ERROR`, ждёт окончания услуги (не выключает usage).
  - Иначе → `s_service_state_go_to_error`.
- `s_service_state_go_to_error`:
  - Помечает usage неактивным, отправляет `RESPONSE_ERROR` и вызывает `callbacks.response_error`.
  - Если было в GRACE → добавляет клиента в банлист на `grace_period * 50` секунд по ключу группы, зависящему от `srv_uid` и хеша публичного ключа сертификата прайса.
  - Иначе удаляет `usage_active` из сессии.
- При новом входе в платный режим, если `tx_cond` не найден, проверяется банлист (`s_check_client_is_banned`) и при активном бане возвращается `RECEIPT_BANNED_PKEY_HASH`.

### 8. Статистика и персистентность
- `s_set_usage_data_to_gdb` агрегирует статистику по ключу `"0x<srv_uid_hex>" + <client_pkey_hash>` в группу `local.srv_statistic`:
  - Секции: `payed`, `free`, `grace` — поля `using_time`, `bytes_received/sent`, `units`, `datoshi_value` и счётчик `using_count` для grace.
  - Денежная оценка вычисляется `s_calc_datoshi` с учётом прошедшего времени/байтов и тарифов.
- Квитанции последней успешной оплаты сохраняются в `local.receipts` по ключу `client_pkey_hash`.
- При удалении канала (`s_stream_ch_delete`) текущая статистика usage сохраняется в GDB и вызывается `save_remain_service`.

### 9. Расчёт стоимости и единицы тарификации
- `units_uid.enm` в прайсе: `SERV_UNIT_SEC` (секунды) или `SERV_UNIT_B` (байты суммарно `bytes_received + bytes_sent`).
- `s_calc_datoshi` вычисляет стоимость: `datoshi = (price.value_datoshi * used) / price.units` + предыдущие накопления.
- Валидации `s_check_tx_params`:
  - Соответствие `srv_uid`, `token_ticker`, единицы измерения, ограничение `unit_price_max_datoshi`, ненулевые `units`.

### 10. Требования к роли узла и состоянию сети
- Узел должен иметь роль не ниже `master` (в коде проверка `dap_chain_net_get_role(net).enums > NODE_ROLE_MASTER` ведёт к ошибке; требуется подтвердить порядок сравнения ролей).
- Сеть должна быть ONLINE при оплате и обработке подписи.

### 11. План юнит‑тестов и точки моков
Моки/заглушки:
- Ledger: `dap_ledger_tx_find_by_hash`, `dap_ledger_tx_get_token_ticker_by_hash`.
- Mempool: `dap_chain_mempool_tx_create_cond_input` (возврат всех статусов).
- Global DB: `dap_global_db_get/set/del`, `dap_global_db_get_all_sync`.
- Таймеры/воркеры: `dap_timerfd_start_on_worker/delete`, `dap_worker_exec_callback_on` (синхронная эмуляция).
- Stream I/O: перехват `dap_stream_ch_pkt_write_unsafe` для проверки отправляемых пакетов.
- Service callbacks: `get_remain_service`, `response_success`, `response_error`, `custom_data`, `save_remain_service`.

Наборы сценариев:
1) REQUEST: free‑mode (`allow_free_srv`, нулевая цена) → `RESPONSE_SUCCESS`, `service_state=FREE`.
2) REQUEST: платный, сеть OFFLINE → ошибка `NETWORK_IS_OFFLINE`.
3) REQUEST: платный, `tx_cond` есть, `get_remain_service` вернул лимиты → старт без оплаты, `NORMAL`.
4) REQUEST: платный, `tx_cond` нет, не забанен → запуск grace (`WAITING_TX_FOR_PAYING`), `RESPONSE_SUCCESS`.
5) GRACE: по таймауту `tx_cond` не появился → ошибка `TX_COND_NOT_FOUND`, бан клиента.
6) GRACE: событие леджера добавило ожидаемый `tx_cond` → формирование новой квитанции и `SIGN_REQUEST` (ветка `WAITING_NEW_TX_IN_LEDGER`).
7) SIGN_RESPONSE: неверный размер/версия/несовпадение с ожидаемой квитанцией → соответствующие ошибки.
8) SIGN_RESPONSE: неверный `pkey_hash` в `out_cond` → `RECEIPT_WRONG_PKEY_HASH`.
9) PAY: mempool SUCCESS → переход в `NORMAL`, сохранение квитанции, проверки отправляемых `RESPONSE_SUCCESS`.
10) PAY: mempool NOT_ENOUGH → из `IDLE` → grace; из `NORMAL` → запрос нового `tx_cond` (`WAITING_NEW_TX_FROM_CLIENT` + ошибка `TX_COND_NOT_ENOUGH`).
11) PAY: mempool CANT_FIND_FINAL_TX_HASH/NO_COND_OUT → ветки `NOT_ENOUGH` или `TX_ERROR` согласно поиску предыдущего `out_cond`.
12) NEW_TX_COND_RESPONSE: пустой `tx_cond` → ошибка `TX_COND_NO_NEW_COND`; валидный `tx_cond` в леджере → новая квитанция и ожидание подписи; валидный вне леджера → `WAITING_NEW_TX_IN_LEDGER`.
13) Таймаут подписи: ретраи до лимита, затем `RECEIPT_NO_SIGN` и переход в ошибку. Отдельный тест на потенциальную инверсию квитанций в ветке `WAITING_RECEIPT_FOR_NEW_TX_FROM_CLIENT`.
14) Банлист: попадание в бан после неуспеха в grace; отказ в запуске, если бан активен; удаление записи после истечения.
15) Статистика: корректное накопление `using_time/bytes/units/datoshi` по режимам `payed/free/grace` и запись в GDB.

### 12. Известные риски/наблюдения
- Возможная ошибка в `s_receipt_timeout_handler` при `WAITING_RECEIPT_FOR_NEW_TX_FROM_CLIENT`: перепутана отправка `receipt`/`receipt_next`.
- Проверка роли (`enums > NODE_ROLE_MASTER`) может требовать ревизии с учётом порядка значений enum.
- Многопоточность: доступ к `grace_hash_tab` под мьютексом; callbacks исполняются на конкретном worker. Тесты должны либо сериализовать вызовы, либо тщательно мокать worker API.

### 13. Краткий глоссарий
- `tx_cond` — условная транзакция для оплаты сервиса (тип `SRV_PAY`).
- `receipt` — квитанция (версия 2), подписывается сервером и клиентом, прикладывается к входу в мемпуле.
- `grace_period` — окно времени для появления/замены `tx_cond`.
- `remain service` — остатки предоплаченного сервиса, выдаются без мгновенной оплаты.

### 14. Быстрая карта функций (по назначению)
- Инициализация/удаление канала: `dap_stream_ch_chain_net_srv_init`, `s_stream_ch_new`, `s_stream_ch_delete`.
- Обработка входящих пакетов: `s_stream_ch_packet_in` (+ обработчики веток).
- Запуск и биллинг: `s_service_start`, `s_service_substate_pay_service`, `s_pay_service`, `s_check_tx_params`.
- Grace: `s_service_state_go_to_grace`, `s_service_substate_go_to_waiting_prev_tx`, `s_service_substate_go_to_waiting_new_tx`, `s_grace_period_finish`, `dap_stream_ch_chain_net_srv_tx_cond_added_cb(_mt)`.
- Подписи/таймеры: `s_start_receipt_timeout_timer`, `s_receipt_timeout_handler`.
- Завершение/ошибки: `s_service_state_go_to_normal`, `s_service_state_go_to_error`, `s_service_substate_go_to_normal`, `s_service_substate_go_to_error`.
- Персистентность/банлист/статистика: `s_get_ban_group`, `s_ban_client`, `s_unban_client`, `s_set_usage_data_to_gdb`, `s_calc_datoshi`.

Этот документ содержит достаточный контекст для проектирования и реализации юнит‑тестов, а также для быстрой навигации по ключевым сценариям биллинга.


