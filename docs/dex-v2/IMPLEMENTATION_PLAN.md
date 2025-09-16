# DEX v2 (SRV_DEX) — План реализации

Этот документ фиксирует архитектуру и пошаговый план работ по внедрению SRV_DEX (новый сервис условных обменов) с поддержкой частичных исполнений, мульти-исполнений и инвалидации хвоста ордера.

## 0. Архитектурные положения
- Новый подтип условного выхода: DAP_CHAIN_TX_OUT_COND_SUBTYPE_SRV_DEX (не конфликтует с существующими).
- OUT_COND(SRV_DEX), храним в union во всех остатках ордера: `sell_net_id`, `buy_net_id`, `buy_token`, `rate`, `seller_addr`, `order_root_hash`, `min_fill`, `fill_policy`, `version`, `flags`. `header.value` — остаток sell.
- Частичное исполнение: допускается несколько IN_COND, из них максимум один частичный. Ровно один остаточный OUT_COND (или ни одного).
- Мульти-исполнение: N полных входов + 0/1 частичный IN[0]. Вариант «все продавцы закрыты, у покупателя есть остаток» — создание нового OUT_COND для покупателя (новый ордер). Исторические данные не кэшируются — on‑demand скан.
- Инвалидация: всегда потребляет «хвост» (tail) цепочки ордера, найденный через dap_ledger_get_final_chain_tx_hash.
- Ончейн TSD — только для не‑критичных метаданных; всё, что влияет на валидность (включая `order_root_hash`, `min_fill`, `fill_policy`), хранится в union и валидируется.
- Ограничения DoS: лимиты на количество IN_COND в TX и на размер TX.
- Выборка ордеров: детерминированный матчинг (сначала лучшая цена, затем FIFO по времени ts_created). Только внутри одной пары (sell_token, buy_token).
- Представление rate/сумм: фиксированная точность uint256, явный порядок вычислений и округлений (вниз) для предсказуемости.
- Канонизация пар: рынки представлены как BASE/QUOTE; у ордера хранится `side` (ASK — продаёт BASE, BID — продаёт QUOTE), `rate` хранится в каноне QUOTE/BASE. Индекс по паре ведёт подсписки `asks`/`bids` (упорядочены по цене ASC, для UX bids выводятся DESC).
- Горячий кэш хранит только активные ордера; исторические рыночные метрики (market_rate/volume) считаются on‑demand сканом леджера.

## 1. Подготовка типов
- Добавить SRV_DEX в enum подтипов (modules/common/include/dap_chain_datum_tx_out_cond.h).
- Реализовать фабрику out_cond: dap_chain_datum_tx_item_out_cond_create_srv_dex(...) (modules/common/dap_chain_datum_tx_items.c).
- Обновить строковые функции *_to_str / *_to_str_short при необходимости.

## 2. Новый модуль сервиса
- Создать modules/service/dex/
  - dap_chain_net_srv_dex.h — API, enum ошибок, статусы, типы TX.
  - dap_chain_net_srv_dex.c — init/deinit, CLI, verificator, кэш, билдеры TX.
- Регистрация: dap_cli_server_cmd_add("srv_dex", ...), dap_ledger_verificator_add(SRV_DEX, s_dex_verificator_callback, ...).

## 3. API и билдеры TX
- Структуры сборки ордера/покупки: dap_chain_net_srv_dex_order_t.
- Функции:
  - dap_chain_net_srv_dex_create(net, token_sell, token_buy, V_sell, rate, fee, wallet, out_hash)
  - dap_chain_net_srv_dex_purchase(net, order_root_hash или список ордеров, request_value, fee, wallet, out_hash, options)
    - M:1: множество IN_COND, максимум один частичный IN[0], один остаточный OUT_COND.
    - При L_buy>0 — опционально создать новый ордер покупателя.
  - dap_chain_net_srv_dex_remove(net, order_root_hash, fee, wallet, out_hash) — найти tail и инвалидировать.
- Опции: max_orders, min_rate, allow_new_buyer_order, fee_policy.

## 4. Верификатор SRV_DEX
- s_dex_verificator_callback(ledger, a_tx_out_cond, a_tx_in, a_owner):
  - Если a_owner (инвалидация) — проверка подписи владельца (seller_addr) и возврат V_prev.
  - Иначе: собрать все IN_COND → найти предыдущие OUT_COND(SRV_DEX).
  - Инварианты:
    - Частичных входов 0 или 1; остаточных OUT_COND 0 или 1.
    - Для каждого i: S_i + L_i = V_prev_i (L_i=0 для full; для partial L_0=V_prev0−S0).
    - Выплаты продавцам: Σ(S_i*rate_i) в соответствующих buy_token_i на соответствующие seller_addr_i.
    - Покупатель получает ΣS_i (либо S' с вычетом native fee, если она берётся из sell).
    - Комиссии соответствуют политике (сеть/валидатор/сервис) и типу (fixed/percent, native/own).
    - Политики исполнения:
      - PARTIAL_OK (по умолчанию): частичные допустимы.
      - AON (All-or-None): частичные запрещены, требуется S == V_prev.
      - MIN_FILL: если создаётся остаток (L>0), тогда S ≥ min_fill.
      - EXPIRY (через header.ts_expires): после истечения — использование не владельцем запрещено.
    - Остаточный OUT_COND параметрами равен исходному (кроме value). Корень сверяется как `first_tx_hash` цепочки.
    - Обновление ордера владельцем (1 TX): 1 IN_COND (текущий tail) + 1 OUT_COND(SRV_DEX) с тем же `order_root_hash` и `seller_addr`; выплат продавцу в `buy_token` нет; запрещён own‑fee сервиса (в `buy_token`), разрешены только нативные комиссии (network/validator). Один SRV_DEX OUT на TX.
  - Лимиты: число IN_COND, общий размер TX.

## 5. Кэш DEX
- Основная таблица: `s_dex_orders_cache` по `root` (order_root_hash).
- Индекс по хвосту: `s_dex_index_by_tail` для O(1) доступа.
- Индекс по паре (канон): `s_dex_pair_index[key(BASE,QUOTE)]` c подтаблицами `asks` и `bids` (uthash), упорядоченными по цене (ASC), тай‑брейк — `ts_created`, затем `root`.
- Индекс по продавцу: `s_dex_seller_index[seller_addr]` (uthash), упорядочен по `ts_created`, затем `root`.
- `ts_created` из blockchain time для FIFO.
- Ledger‑нотификации: при `a` учитываем partial/residual, при `d` восстанавливаем прошлое состояние и удаляем созданные покупательские остатки.
- Реорг‑защита: восстановление из леджера по `d`.

## 6. CLI/RPC (минимум)
- Команды: srv_dex order create | remove | update | status | orders | orders_by_seller | status_by_seller | history | history_by_seller | cancel_all_by_seller | purchase | purchase_multi | purchase_auto | orderbook | market_rate | tvl | spread | volume
- Пары задаются `-pair BASE/QUOTE` (ввод канонизируется).
- Рыночные команды:
  - orderbook: агрегация + бинирование цен (`-tick_price` или `-tick`) и кумулятивы; сводка `best_ask`, `best_bid`, `mid`, `spread`, и объект `summary`.
  - market_rate: SPOT, VWAP, при `-bucket` — `ohlc[]` (open/high/low/close, volume_base/volume_quote, trades, first_ts/last_ts).
  - volume: суммарные объёмы и, при `-bucket`, бакеты `buckets[]` с ts/first_ts/last_ts/volume/trades.
  - slippage: моделирование исполнения по стакану, вывод `effective_price`, `best_ask|best_bid`, `slippage`, `slippage_pct`, `filled_base`, `spent_quote`, `fully_filled`.

## 7. Комиссии
- Наследовать политику сети/валидатора (как в xchange) + сервисная комиссия DEX (fixed/percent, native/own), конфигурируемая.
- Для сделок (exchange): если `sell == native`, выплата покупателю в `sell_token` уменьшается на сумму фактических native‑комиссий (network + validator + service_native); если `sell != native` — выплата равна ΣS; при отдельном наборе fee‑входов сдача из native возвращается (cashback).
- Service fee: списывается в `native` (native‑fixed/percent) или в `buy_token` (own‑fixed/percent).
- Для update (1 TX): сервисная own‑fee не применяется; допускаются только validator и network (native).

## 8. Ограничения/безопасность
- Лимит IN_COND на TX (напр. 16 по умолчанию), лимит размера TX.
- Запрет N:M остаточных OUT_COND — только 1:1 (один partial → один остаток).
- Валидация входных параметров (нулевые значения, переполнения, диапазоны rate).

## 9. Тесты
- Unit: create (валид/невалид), purchase single (full/partial), multi (all-full/one-partial), wrong payouts, double residual, лимиты, комиссии, rounding.
- Invalidate: после частичных, поиск tail, возврат V_prev, подпись владельца.
- Кэш: индексы, обновление, реорг.
- Интеграция: mempool-accept, CLI сценарии.

## 10. Порядок внедрения (итерации)
1) Типы/фабрика OUT_COND(SRV_DEX)
2) Каркас модуля + регистрация CLI/верификатора
3) Билдеры TX (create/purchase/remove) с M:1 логикой
4) Верификатор (полный набор проверок)
5) Кэш и индексы + нотификации
6) CLI/RPC минимально достаточный
7) Тесты unit+integration
8) Документация и примеры

## 11. Критерии готовности
- Все сценарии из диаграмм проходят верификацию и тесты.
- Инвалидация хвоста доступна владельцу в любой момент при открытом остатке.
- Лимиты и проверки защищают от DoS.
- Документация и CLI зафиксированы.
