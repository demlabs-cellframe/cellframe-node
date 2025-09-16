## SRV_DEX: план новых команд и реализация

### Цели

- Удобные рыночные метрики и операции поверх DEX v2:
  1) Обновление ордера владельцем (изменение параметров)
  2) Стакан (order book) с заданной глубиной
  3) Рыночный курс по паре с динамикой за период
  4) TVL (сумма коинов на открытых ордерах по токену)
  5) Спред по паре
  6) Объём торгов по паре за период
  7) Тема: slippage — обсуждение применимости и расчёта

### Базовые источники данных

- Активные ордера (горячий кэш SRV_DEX):
  - Индекс по паре: `s_dex_pair_index` → подтаблица `entries`, упорядоченная (rate ASC → ts_created ASC → root)
  - Индекс по продавцу: `s_dex_seller_index` → подтаблица `entries`, упорядоченная (ts_created ASC → root)
  - Индекс по хвосту: `s_dex_index_by_tail` (O(1) доступ)
- Исторические сделки: on‑demand сканирование леджера по TX типа EXCHANGE
  - Без удержания исторических данных в горячем кэше
  - Реорг‑устойчивость обеспечивается самим леджером (чтение актуальной ветки)

### Команда 1: Обновление ордера владельцем

- CLI: `srv_dex order update -net NET -order <root_hash> -w <wallet> [-rate R] [-value_new V] [-fee F]`
- Семантика: атомарное "invalidate + create" в одной TX (если возможно), иначе — две TX:
  - IN_COND (tail, owner) + новый OUT_COND(SRV_DEX) с желаемыми параметрами
  - Защита: изменение только владельцем (ядро уже проверяет owner), параметры — любые валидные
- Обработка кэша (notify 'a'):
  - Считать как INVALIDATE старого + ORDER нового (без buyer leftover логики)
  - Реализация: детектировать `a_owner==true` и наличие SRV_DEX OUT_COND → пометить тип UPDATE, удалять старый корень и добавлять новый как ORDER
- Верификатор: при `a_owner==true` мы уже пропускаем (валидируется ядром). Ограничить максимум один OUT_COND.

### Команда 2: Стакан (order book)

- CLI: `srv_dex orderbook -net NET -pair BASE/QUOTE -depth N`
- Вывод: топ-N уровней: asks (продают BASE) по возрастанию цены (QUOTE/BASE), bids (покупают BASE) по убыванию
- Реализация: итерация по `s_dex_pair_index[key(BASE,QUOTE)]->asks/bids`, суммирование по уровням цены
- Сложность: O(N) с N = depth

### Команда 3: Рыночный курс и динамика (on‑demand)

- CLI: `srv_dex market_rate -net NET -token_sell A -token_buy B [-from T0] [-to T1] [-bucket SEC]`
- Метрики:
  - Spot: последняя цена сделки по паре (A/B)
  - VWAP за период [T0,T1]
  - OHLC по бакетам (если задан `-bucket`)
- Реализация:
  - Скан EXCHANGE TX в окне [T0,T1] с фильтром по паре; для multi-TX учитывать каждую долю с её rate
  - Агрегировать в памяти ответа команды; без накопителя в горячем кэше
- Сложность: O(M) по числу трейдов в окне; приемлемо для on‑demand

### Команда 4: TVL

- CLI: `srv_dex tvl -net NET -token T`
- Семантика: сумма `value_sell` всех активных ордеров, где sell_token == T
- Реализация:
  - Итерировать все пары в `s_dex_pair_index`, фильтровать по sell_token==T, суммировать
  - Опционально: поддержать быстрый индекс по sell_token (не требуется на старте)
- Сложность: O(K) по числу пар и ордеров — для редких запросов приемлемо

### Команда 5: Спред

- CLI: `srv_dex spread -net NET -pair A/B`
- Определения:
  - Ask (в B за 1 A): минимальный rate среди A→B
  - Bid (в B за 1 A): максимум по (B→A) инвертированным в B/A: bid = max(1 / rate_{B→A}) = 1 / min(rate_{B→A})
  - Spread = Ask - Bid (в тех же единицах B/A)
- Реализация: взять top-1 в A→B и top-1 в B→A, корректно инвертировать
- Сложность: O(1)

### Команда 6: Объём торгов (on‑demand)

- CLI: `srv_dex volume -net NET -pair A/B [-from T0] [-to T1] [-bucket SEC]`
- Метрики: общий объём (в sell/buy), и/или серия по бакетам
- Реализация: скан EXCHANGE TX за период, агрегирование; как в market_rate
- Сложность: O(M) по числу трейдов в окне; без накопителей в кэше

### Команда 7: Slippage (реализовано)

- В DEX ордеры дискретны, slippage релевантен: при крупной покупке средневзвешенный курс хуже лучшего
- Расчёт: пройти стакан (A→B) по возрастанию rate, исполняя бюджет покупателя; `effective_price` = VWAP, `slippage` = |VWAP - best|, `slippage_pct` = (VWAP/best - 1)*100%
- CLI: `srv_dex slippage -net NET -pair A/B -value AMOUNT [-side buy|sell]`
- Вывод: `effective_price`, `best_ask|best_bid`, `slippage`, `slippage_pct`, `filled_base`, `spent_quote`, `fully_filled`

### API/CLI спецификации (обновлено)

```
srv_dex order update -net NET -order ROOT -w WALLET [-rate R] [-value_new V] [-fee F]
srv_dex orderbook -net NET -pair A/B -depth N
srv_dex market_rate -net NET -pair A/B [-from T0] [-to T1] [-bucket SEC]
srv_dex tvl -net NET -token T
srv_dex spread -net NET -pair A/B
srv_dex volume -net NET -pair A/B [-from T0] [-to T1] [-bucket SEC]
```

Форматы времени: UNIX epoch (сек). Значения rate/value — в строковом fixed-precision (как в существующем CLI).

### Интеграция с кэшем и реоргами

- Все вычисления по активным ордерам — только из кэша (pair/seller/tail индексы)
- Исторические метрики — on‑demand через обход леджера с фильтрами по паре и интервалу

### Ограничения и валидации

- Обновление ордера — только владельцем (owner), максимум один OUT_COND
- При расчётах избегать истекших ордеров: проверка `ts_expires`
- При спреде аккуратно обращать курс B→A → в B/A (инверсия)

### Оценка трудозатрат (высокоуровнево)

- Update order: билдер TX + распознавание в notify как UPDATE (удалить старый, добавить новый)
- Orderbook: 1–2 дня (агрегация уровней, CLI формат)
- Market rate & Volume: 2–3 дня (скан, фильтры, бакетирование в пределах ответа)
- TVL / Spread: 0.5–1 день
- Slippage (расчёт): 0.5 дня (после согласования формализма)


