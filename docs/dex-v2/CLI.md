# SRV_DEX (DEX v2) — CLI команды и параметры

Краткая справка по CLI сервиса DEX v2 (SRV_DEX), параметрам и инвариантам.

## Базовые требования
- Всегда указывать сеть: `-net <net_name>`
- Указывать кошелёк: `-w <wallet>` (путь/алиас)
- Денежные значения — строки, парсятся в `uint256` (поддерживаются десятичные):
  - `-value`, `-rate`, `-fee`, `-min_rate`, `-leftover_rate`

## Команды

### 1) Создание / удаление ордера продавца
- Создать ордер:
```
srv_dex order create \
  -net NET \
  -token_sell T_SELL \
  -token_buy T_BUY \
  -w WALLET \
  -value V_SELL \
  -rate RATE \
  -fee FEE
```
- Удалить (инвалидировать) ордер по корню/хвосту:
```
srv_dex order remove -net NET -order ORDER_HASH -w WALLET -fee FEE
```

### 1.1) Обновление ордера владельцем (1 TX)
- Всегда один транзакционный шаг: вход `IN_COND` по текущему хвосту ордера и один `OUT_COND(SRV_DEX)` с обновлёнными параметрами и тем же `order_root_hash`.
- Платежей продавцу в `buy_token` нет — это не сделка.
- Комиссии: только валидаторская (FEE item) и сетевая (native). Сервисная own‑fee при апдейте не используется.
- В случае гонки (хвост уже потрачен) транзакция будет отвергнута — это нормально: следует повторить апдейт по актуальному хвосту.

```
srv_dex order update \
  -net NET \
  -order ORDER_ROOT_HASH \
  -w WALLET \
  [-rate NEW_RATE] \
  [-value_new NEW_VALUE] \
  -fee FEE
```
- Менять можно любые параметры ордера (например, `rate`, `value`), кроме идентичности рынка/владельца.

### 2) Обзор ордеров и статусов
- Список ордеров по паре (канонический `BASE/QUOTE`):
```
srv_dex orders -net NET -pair BASE/QUOTE
```
- Краткий статус по паре (счётчик открытых):
```
srv_dex status -net NET -pair BASE/QUOTE
```
- История ордера:
```
srv_dex history -net NET -order ORDER_ROOT_HASH
```

### 3) Покупка против одного ордера
```
srv_dex purchase -net NET -order ORDER_HASH -w WALLET -value BUY_VALUE -fee FEE
```
- `BUY_VALUE` — платим в `buy_token`.
- Частичный случай поддерживается; остаток у продавца создаётся как единственный `OUT_COND(SRV_DEX)` в TX.

### 4) Покупка против набора ордеров (multi)
```
srv_dex purchase_multi \
  -net NET \
  -orders HASH1,HASH2,... \
  -w WALLET \
  -value BUY_VALUE \
  -fee FEE \
  [-create_leftover_order 0|1] \
  [-leftover_rate RATE]
```
- Распределяет `BUY_VALUE` по ордерам пары (сначала лучшая цена, затем FIFO).
- Если `-create_leftover_order 1` и НЕТ частичного входа — можно создать НОВЫЙ ордер покупателя на остаток:
  - `-leftover_rate` — курс leftover‑ордера (обязателен при создании leftover‑ордера).
  - Новый ордер покупателя имеет `order_root_hash = 0`, `seller_addr = buyer_addr`.

### 5) Автоподбор по паре (multi, cache-driven)
```
srv_dex purchase_auto \
  -net NET \
  -token_sell T_SELL \
  -token_buy T_BUY \
  -w WALLET \
  -value BUY_VALUE \
  [-min_rate RATE] \
  [-fee FEE] \
  [-create_leftover_order 0|1]
```
- Подбирает из локального кэша: `rate ASC`, затем FIFO по времени (`ts_created`).
- Если `-create_leftover_order 1` и нет частичных входов — для leftover‑ордера используется `-min_rate` как ставка.

## Инварианты и комиссии
- В одной TX — максимум один `OUT_COND(SRV_DEX)`.
  - Если есть частичный вход (`IN[0]`) — `OUT_COND` это остаток продавца (параметры идентичны исходному, кроме `value`).
  - Если частичных входов нет — допустим НОВЫЙ ордер покупателя (`order_root_hash = 0`).
- Комиссии: сетевая (native), сервисная (own/native, fixed/percent), валидаторская (FEE item).
  - При `sell == native` выплата покупателю в `sell_token` уменьшается на сумму нативных комиссий (network + service_native + validator).

## Примеры
- Создать ордер на продажу 100 SELL по курсу 2 BUY/SELL:
```
srv_dex order create -net main -token_sell SELL -token_buy BUY -w my.wallet -value 100 -rate 2 -fee 0.01
```
- Купить на 50 BUY из набора ордеров и создать leftover‑покупателя с курсом 1.8:
```
srv_dex purchase_multi -net main -orders 0xabc...,0xdef... -w my.wallet -value 50 -fee 0.01 -create_leftover_order 1 -leftover_rate 1.8
```
- Автопокупка (min_rate 1.9), создать leftover с этой ставкой:
```
srv_dex purchase_auto -net main -token_sell SELL -token_buy BUY -w my.wallet -value 200 -min_rate 1.9 -create_leftover_order 1
```

### 6) Рыночные метрики и данные
- Стакан (агрегация по уровням, опционально бинирование цены и кумулятивы):
```
srv_dex orderbook -net NET -pair BASE/QUOTE -depth N [-tick_price STEP] [-tick DECIMALS] [-cum 0|1]
```
  - В ответе: `asks[]`, `bids[]`, а также сводка `best_ask`, `best_bid`, `mid`, `spread` и объект `summary` с теми же полями.
- Рыночный курс и динамика (on‑demand скан):
```
srv_dex market_rate -net NET -pair BASE/QUOTE [-from T0] [-to T1] [-bucket SEC]
```
  - Верхний уровень: `spot`, `vwap`, `volume_base`, `volume_quote`, `trades`.
  - При `-bucket`: массив `ohlc[]` с полями `ts`, `first_ts`, `last_ts`, `open`, `high`, `low`, `close`, `volume_base`, `volume_quote`, `trades`.
- TVL по токену:
```
srv_dex tvl -net NET -token T
```
- Спред по паре:
```
srv_dex spread -net NET -pair BASE/QUOTE
```
- Объём торгов (on‑demand):
```
srv_dex volume -net NET -pair BASE/QUOTE [-from T0] [-to T1] [-bucket SEC]
```
  - Верхний уровень: `volume_base`, `volume_quote`, `trades`.
  - При `-bucket`: массив `buckets[]` с полями `ts`, `first_ts`, `last_ts`, `volume_base`, `volume_quote`, `trades`.

- Slippage (оценка исполнения и просадки цены):
```
srv_dex slippage -net NET -pair BASE/QUOTE -value AMOUNT [-side buy|sell]
```
  - Параметры: `-side` (по умолчанию `buy`).
  - Ответ: `effective_price`, `best_ask|best_bid`, `slippage`, `slippage_pct`, `filled_base`, `spent_quote`, `fully_filled`.

