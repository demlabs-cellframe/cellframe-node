# 📋 Фаза 1: Анализ и проектирование
## Документация результатов анализа

### 🔍 Субфаза 1.1: Анализ UTXO модели Cellframe

#### ✅ ЗАВЕРШЕНО: Детальный анализ структур

**1. Структура dap_ledger_tx_item_t** (dap_chain_ledger.c:168-186)
```c
typedef struct dap_ledger_tx_item {
    dap_chain_hash_fast_t tx_hash_fast;          // TX hash идентификатор
    dap_chain_datum_tx_t *tx;                    // Указатель на саму транзакцию
    dap_nanotime_t ts_added;                     // Timestamp добавления
    UT_hash_handle hh;                           // Hash table handle
    struct {
        dap_time_t ts_created;                   // TX datum timestamp
        uint32_t n_outs;                         // Количество выходов
        uint32_t n_outs_used;                    // Сколько выходов потрачено
        char token_ticker[DAP_CHAIN_TICKER_SIZE_MAX];
        byte_t padding[6];
        byte_t multichannel;
        dap_time_t ts_spent;                     // Когда потрачено
        byte_t pad[7];
        dap_chain_net_srv_uid_t tag;
        dap_chain_tx_tag_action_type_t action;
        dap_chain_hash_fast_t tx_hash_spent_fast[]; // ⭐ МАССИВ ХЕШЕЙ потративших TX
    } DAP_ALIGN_PACKED cache_data;
} dap_ledger_tx_item_t;
```

**Ключевые выводы:**
- UTXO tracking через массив `tx_hash_spent_fast[]`
- Размер массива = `n_outs` (по одному элементу на каждый выход)
- Если выход не потрачен: `tx_hash_spent_fast[idx]` содержит нулевой хеш
- Если потрачен: содержит хеш транзакции, которая его потратила

**2. Структура dap_ledger_token_item_t** (dap_chain_ledger.c:127-165)
```c
typedef struct dap_ledger_token_item {
    char ticker[DAP_CHAIN_TICKER_SIZE_MAX];
    // ... поля эмиссии, supply ...
    
    pthread_rwlock_t token_emissions_rwlock;     // ⭐ Thread-safety pattern
    pthread_rwlock_t token_ts_updated_rwlock;
    
    // Auth & permissions
    dap_pkey_t ** auth_pkeys;
    size_t auth_signs_valid;
    uint32_t flags;                              // ⭐ СЮДА добавим BIT(16-19)
    
    // Address-based permissions
    struct spec_address *tx_recv_allow;
    size_t tx_recv_allow_size;
    struct spec_address *tx_recv_block;
    size_t tx_recv_block_size;
    struct spec_address *tx_send_allow;
    size_t tx_send_allow_size;
    struct spec_address *tx_send_block;
    size_t tx_send_block_size;
    
    UT_hash_handle hh;
} dap_ledger_token_item_t;
```

**Ключевые выводы:**
- Использует `pthread_rwlock_t` для thread-safety
- Поле `flags` (uint32_t) для флагов токена
- Уже имеет address-based permissions (tx_send/recv_allow/block)
- **План:** Добавить сюда UTXO blocklist hash table и rwlock для него

**3. Критическая точка валидации транзакций**

**Файл:** `cellframe-sdk/modules/net/dap_chain_ledger.c`  
**Функция:** `s_ledger_tx_add_check()` (строка 3367)  
**Критическая проверка:** строка 3785

```c
// 2. Check if out in previous transaction has spent
dap_hash_fast_t l_spender = {};
if (s_ledger_tx_hash_is_used_out_item(l_item_out, l_tx_prev_out_idx, &l_spender) 
    && !a_check_for_removing) {
    l_err_num = DAP_LEDGER_TX_CHECK_OUT_ITEM_ALREADY_USED;
    debug_if(s_debug_more, L_INFO, 
        "'Out' item %u of previous tx %s already spent by %s", 
        l_tx_prev_out_idx, l_tx_prev_hash_str, l_hash);
    break;
}
```

**🎯 МЕСТО ДЛЯ ВСТАВКИ ПРОВЕРКИ UTXO BLOCKLIST:**
**После строки 3791** (после break, в следующей итерации после успешной spent check)

**Псевдокод будущей проверки:**
```c
// 2.5. Check if UTXO is blocked (NEW CHECK)
if (!a_check_for_removing) {
    // Get token item
    dap_ledger_token_item_t *l_token_item = s_ledger_find_token(a_ledger, l_token);
    if (l_token_item && (l_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_UTXO_BLOCKING_ENABLED)) {
        // Check if UTXO is in blocklist
        if (s_ledger_utxo_is_blocked(l_token_item, &l_tx_prev_hash, l_tx_prev_out_idx)) {
            l_err_num = DAP_LEDGER_TX_CHECK_OUT_ITEM_BLOCKED; // NEW ERROR CODE
            debug_if(s_debug_more, L_WARNING, 
                "UTXO %s:%u is blocked by token %s policy",
                l_tx_prev_hash_str, l_tx_prev_out_idx, l_token);
            break;
        }
    }
}
```

**4. UTXO Identification Model**

UTXO однозначно идентифицируется парой:
- `tx_hash` (dap_chain_hash_fast_t) - хеш транзакции
- `out_idx` (uint32_t) - индекс выхода в транзакции

**5. Thread-Safety Pattern**

Cellframe SDK использует `pthread_rwlock_t` для read-write locks:
- Множественные читатели одновременно
- Эксклюзивный доступ для писателей
- **План:** Добавить `pthread_rwlock_t utxo_blocklist_rwlock` в `dap_ledger_token_item_t`

---

### 📊 Статус Фазы 1.1: ✅ ЗАВЕРШЕНА

**Deliverable:** Документ архитектуры UTXO tracking - СОЗДАН

**Ключевые находки для следующих фаз:**
1. Точное место вставки проверки UTXO blocking (строка 3791)
2. Структура для расширения (dap_ledger_token_item_t)
3. Pattern thread-safety (pthread_rwlock_t)
4. UTXO identification model (tx_hash + out_idx)
5. Error handling pattern (enum + debug logging)

---

### 🔄 Переход к Субфазе 1.2

**Следующий шаг:** Анализ существующих механизмов блокировки (address-based permissions)


---

### 🔐 Субфаза 1.2: Анализ существующих механизмов блокировки

#### ✅ ЗАВЕРШЕНО: Детальный анализ address-based permissions

**1. Функция s_ledger_permissions_check()** (dap_chain_ledger.c:2586-2613)

```c
static bool s_ledger_permissions_check(dap_ledger_t *a_ledger, 
                                       dap_ledger_token_item_t *a_token_item, 
                                       enum ledger_permissions a_permission_id, 
                                       dap_chain_addr_t *a_addr)
{
    struct spec_address *l_addrs = NULL;
    size_t l_addrs_count = 0;
    
    // Выбор соответствующего списка
    switch (a_permission_id) {
    case LEDGER_PERMISSION_RECEIVER_ALLOWED:  // Whitelist получателей
        l_addrs = a_token_item->tx_recv_allow;
        l_addrs_count = a_token_item->tx_recv_allow_size;
        break;
    case LEDGER_PERMISSION_RECEIVER_BLOCKED:  // Blacklist получателей
        l_addrs = a_token_item->tx_recv_block;
        l_addrs_count = a_token_item->tx_recv_block_size;
        break;
    case LEDGER_PERMISSION_SENDER_ALLOWED:    // Whitelist отправителей
        l_addrs = a_token_item->tx_send_allow;
        l_addrs_count = a_token_item->tx_send_allow_size;
        break;
    case LEDGER_PERMISSION_SENDER_BLOCKED:    // Blacklist отправителей
        l_addrs = a_token_item->tx_send_block;
        l_addrs_count = a_token_item->tx_send_block_size;
        break;
    }
    
    // Поиск адреса в списке
    for (size_t n = 0; n < l_addrs_count; n++)
        if (dap_chain_addr_compare(&l_addrs[n].addr, a_addr) &&
                l_addrs[n].becomes_effective <= dap_ledger_get_blockchain_time(a_ledger))
            return true;
    return false;
}
```

**2. Функция s_ledger_addr_check()** (dap_chain_ledger.c:2615-2646)

```c
dap_ledger_check_error_t s_ledger_addr_check(dap_ledger_t *a_ledger, 
                                              dap_ledger_token_item_t *a_token_item, 
                                              dap_chain_addr_t *a_addr, 
                                              bool a_receive)
{
    if (a_receive) {
        // RECEIVER CHECKS
        if ((a_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_ALL_RECEIVER_BLOCKED) ||
            (a_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_ALL_RECEIVER_FROZEN)) {
            // Все получатели заблокированы - проверяем whitelist
            if (!s_ledger_permissions_check(a_ledger, a_token_item, 
                                           LEDGER_PERMISSION_RECEIVER_ALLOWED, a_addr))
                return DAP_LEDGER_CHECK_ADDR_FORBIDDEN;
        } else if ((a_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_ALL_RECEIVER_ALLOWED) ||
                   (a_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_ALL_RECEIVER_UNFROZEN)) {
            // Все получатели разрешены - проверяем blacklist
            if (s_ledger_permissions_check(a_ledger, a_token_item, 
                                          LEDGER_PERMISSION_RECEIVER_BLOCKED, a_addr))
                return DAP_LEDGER_CHECK_ADDR_FORBIDDEN;
        }
    } else {
        // SENDER CHECKS
        if ((a_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_ALL_SENDER_BLOCKED) ||
            (a_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_ALL_SENDER_FROZEN)) {
            // Все отправители заблокированы - проверяем whitelist
            if (!s_ledger_permissions_check(a_ledger, a_token_item, 
                                           LEDGER_PERMISSION_SENDER_ALLOWED, a_addr))
                return DAP_LEDGER_CHECK_ADDR_FORBIDDEN;
        } else if ((a_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_ALL_SENDER_ALLOWED) ||
                   (a_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_ALL_SENDER_UNFROZEN)) {
            // Все отправители разрешены - проверяем blacklist
            if (s_ledger_permissions_check(a_ledger, a_token_item, 
                                          LEDGER_PERMISSION_SENDER_BLOCKED, a_addr))
                return DAP_LEDGER_CHECK_ADDR_FORBIDDEN;
        }
    }
    return DAP_LEDGER_CHECK_OK;
}
```

**3. Структура spec_address** (dap_chain_ledger.c:122-125)

```c
struct spec_address {
    dap_chain_addr_t addr;              // Адрес
    dap_time_t becomes_effective;       // Когда вступает в силу (time-based activation)
};
```

**4. Используемые флаги токена**

| Флаг | BIT | Описание |
|------|-----|----------|
| ALL_SENDER_BLOCKED | BIT(1) | Все отправители заблокированы |
| ALL_SENDER_ALLOWED | BIT(2) | Все отправители разрешены |
| ALL_SENDER_FROZEN | BIT(3) | Все отправители заморожены |
| ALL_SENDER_UNFROZEN | BIT(4) | Все отправители разморожены |
| ALL_RECEIVER_BLOCKED | BIT(5) | Все получатели заблокированы |
| ALL_RECEIVER_ALLOWED | BIT(6) | Все получатели разрешены |
| ALL_RECEIVER_FROZEN | BIT(7) | Все получатели заморожены |
| ALL_RECEIVER_UNFROZEN | BIT(8) | Все получатели разморожены |

**5. Логика работы address-based permissions**

```
Модель работы: BLOCKED flag → whitelist, ALLOWED flag → blacklist

RECEIVER BLOCKED (BIT 5):
  ├─ Все получатели заблокированы по умолчанию
  └─ Проверяется tx_recv_allow (whitelist) - только эти адреса могут получать

RECEIVER ALLOWED (BIT 6):
  ├─ Все получатели разрешены по умолчанию
  └─ Проверяется tx_recv_block (blacklist) - эти адреса НЕ могут получать

SENDER BLOCKED (BIT 1):
  ├─ Все отправители заблокированы по умолчанию
  └─ Проверяется tx_send_allow (whitelist) - только эти адреса могут отправлять

SENDER ALLOWED (BIT 2):
  ├─ Все отправители разрешены по умолчанию
  └─ Проверяется tx_send_block (blacklist) - эти адреса НЕ могут отправлять
```

**6. 🎯 План модификации для DISABLE_ADDRESS_*_BLOCKING флагов**

```c
dap_ledger_check_error_t s_ledger_addr_check(dap_ledger_t *a_ledger, 
                                              dap_ledger_token_item_t *a_token_item, 
                                              dap_chain_addr_t *a_addr, 
                                              bool a_receive)
{
    dap_return_val_if_fail(a_token_item && a_addr, DAP_LEDGER_CHECK_INVALID_ARGS);
    if (dap_chain_addr_is_blank(a_addr))
        return DAP_LEDGER_CHECK_OK;
        
    if (a_receive) {
        // ⭐ NEW: Early exit if address-based receiver blocking is disabled
        if (a_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_DISABLE_ADDRESS_RECEIVER_BLOCKING) {
            return DAP_LEDGER_CHECK_OK;
        }
        
        // Existing receiver checks...
        if ((a_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_ALL_RECEIVER_BLOCKED) ||
            (a_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_ALL_RECEIVER_FROZEN)) {
            if (!s_ledger_permissions_check(a_ledger, a_token_item, 
                                           LEDGER_PERMISSION_RECEIVER_ALLOWED, a_addr))
                return DAP_LEDGER_CHECK_ADDR_FORBIDDEN;
        } else if ((a_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_ALL_RECEIVER_ALLOWED) ||
                   (a_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_ALL_RECEIVER_UNFROZEN)) {
            if (s_ledger_permissions_check(a_ledger, a_token_item, 
                                          LEDGER_PERMISSION_RECEIVER_BLOCKED, a_addr))
                return DAP_LEDGER_CHECK_ADDR_FORBIDDEN;
        }
    } else {
        // ⭐ NEW: Early exit if address-based sender blocking is disabled
        if (a_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_DISABLE_ADDRESS_SENDER_BLOCKING) {
            return DAP_LEDGER_CHECK_OK;
        }
        
        // Existing sender checks...
        if ((a_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_ALL_SENDER_BLOCKED) ||
            (a_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_ALL_SENDER_FROZEN)) {
            if (!s_ledger_permissions_check(a_ledger, a_token_item, 
                                           LEDGER_PERMISSION_SENDER_ALLOWED, a_addr))
                return DAP_LEDGER_CHECK_ADDR_FORBIDDEN;
        } else if ((a_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_ALL_SENDER_ALLOWED) ||
                   (a_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_ALL_SENDER_UNFROZEN)) {
            if (s_ledger_permissions_check(a_ledger, a_token_item, 
                                          LEDGER_PERMISSION_SENDER_BLOCKED, a_addr))
                return DAP_LEDGER_CHECK_ADDR_FORBIDDEN;
        }
    }
    return DAP_LEDGER_CHECK_OK;
}
```

---

### 📊 Статус Фазы 1.2: ✅ ЗАВЕРШЕНА

**Deliverable:** Схема существующих permissions механизмов - СОЗДАНА

**Ключевые находки:**
1. Address-based permissions через 4 списка (allow/block для sender/receiver)
2. Флаги токена управляют режимом (whitelist vs blacklist)
3. Time-based activation через `becomes_effective`
4. Единая точка проверки: `s_ledger_addr_check()`
5. **Место для модификации:** Начало функции `s_ledger_addr_check()` - добавить early exit при установленных DISABLE флагах

---

### 🔄 Переход к Субфазе 1.3

**Следующий шаг:** Проектирование UTXO blocklist структуры


---

### 🏗️ Субфаза 1.3: Проектирование UTXO blocklist структуры

#### ✅ ЗАВЕРШЕНО: Детальный дизайн структур данных

**1. Ключ для UTXO (hash table key)**

```c
/**
 * @brief UTXO blocklist key
 * @details Composite key for UTXO identification: transaction hash + output index
 */
typedef struct dap_ledger_utxo_block_key {
    dap_chain_hash_fast_t tx_hash;  // Transaction hash (32 bytes)
    uint32_t out_idx;                // Output index in transaction
} DAP_ALIGN_PACKED dap_ledger_utxo_block_key_t;
```

**Размер:** `sizeof(dap_chain_hash_fast_t) + sizeof(uint32_t)` = 32 + 4 = 36 байт

**Обоснование:**
- Минимальный размер для однозначной идентификации UTXO
- DAP_ALIGN_PACKED для экономии памяти в hash table
- Соответствует модели UTXO tracking в dap_ledger_tx_item_t

**2. Элемент UTXO blocklist**

```c
/**
 * @brief UTXO blocklist item
 * @details Represents a blocked UTXO with metadata
 */
typedef struct dap_ledger_utxo_block_item {
    dap_ledger_utxo_block_key_t key;  // Composite key (tx_hash + out_idx)
    dap_time_t blocked_time;           // When UTXO was blocked (timestamp)
    char *reason;                      // Optional: reason for blocking (can be NULL)
    UT_hash_handle hh;                 // uthash handle for hash table
} dap_ledger_utxo_block_item_t;
```

**Поля:**
- `key` - композитный ключ для поиска
- `blocked_time` - метка времени блокировки (для audit trail)
- `reason` - опциональная причина (может быть NULL, управляется через token_update)
- `hh` - стандартный uthash handle

**Memory management:**
- `reason` выделяется через `dap_strdup()` если предоставлен
- При удалении элемента: `DAP_DELETE(item->reason)` затем `DAP_DELETE(item)`

**3. Расширение dap_ledger_token_item_t**

```c
typedef struct dap_ledger_token_item {
    // ... existing fields ...
    
    uint32_t flags;
    struct spec_address *tx_recv_allow;
    size_t tx_recv_allow_size;
    // ... other permission lists ...
    
    // ⭐ NEW: UTXO blocklist fields
    pthread_rwlock_t utxo_blocklist_rwlock;        // Thread-safety for blocklist
    dap_ledger_utxo_block_item_t *utxo_blocklist; // Hash table of blocked UTXOs
    size_t utxo_blocklist_count;                   // Number of blocked UTXOs
    
    // ... existing fields ...
    UT_hash_handle hh;
} dap_ledger_token_item_t;
```

**Новые поля:**
- `utxo_blocklist_rwlock` - pthread rwlock для thread-safe доступа
- `utxo_blocklist` - указатель на hash table (uthash)
- `utxo_blocklist_count` - количество заблокированных UTXO (для быстрой статистики)

**Инициализация (в dap_ledger_token_add):**
```c
pthread_rwlock_init(&l_token_item->utxo_blocklist_rwlock, NULL);
l_token_item->utxo_blocklist = NULL;
l_token_item->utxo_blocklist_count = 0;
```

**Очистка (в dap_ledger_token_delete):**
```c
pthread_rwlock_wrlock(&l_token_item->utxo_blocklist_rwlock);
dap_ledger_utxo_block_item_t *l_item, *l_tmp;
HASH_ITER(hh, l_token_item->utxo_blocklist, l_item, l_tmp) {
    HASH_DEL(l_token_item->utxo_blocklist, l_item);
    if (l_item->reason)
        DAP_DELETE(l_item->reason);
    DAP_DELETE(l_item);
}
pthread_rwlock_unlock(&l_token_item->utxo_blocklist_rwlock);
pthread_rwlock_destroy(&l_token_item->utxo_blocklist_rwlock);
```

**4. Новые флаги токена (dap_chain_datum_token.h)**

```c
// Existing flags BIT(1) through BIT(15) ...

// ⭐ NEW: UTXO blocking flags
#define DAP_CHAIN_DATUM_TOKEN_FLAG_UTXO_BLOCKING_ENABLED         BIT(16)
#define DAP_CHAIN_DATUM_TOKEN_FLAG_STATIC_UTXO_BLOCKLIST         BIT(17)

// ⭐ NEW: Address blocking disable flags
#define DAP_CHAIN_DATUM_TOKEN_FLAG_DISABLE_ADDRESS_SENDER_BLOCKING    BIT(18)
#define DAP_CHAIN_DATUM_TOKEN_FLAG_DISABLE_ADDRESS_RECEIVER_BLOCKING  BIT(19)
```

**Семантика флагов:**

| Флаг | BIT | Действие |
|------|-----|----------|
| UTXO_BLOCKING_ENABLED | 16 | Включает механизм блокировки UTXO для данного токена |
| STATIC_UTXO_BLOCKLIST | 17 | Запрещает изменение UTXO blocklist после установки (immutable) |
| DISABLE_ADDRESS_SENDER_BLOCKING | 18 | Отключает проверки tx_send_allow/tx_send_block |
| DISABLE_ADDRESS_RECEIVER_BLOCKING | 19 | Отключает проверки tx_recv_allow/tx_recv_block |

**5. Новые TSD types для token_update**

```c
// Existing TSD types ...
#define DAP_CHAIN_DATUM_TOKEN_TSD_TYPE_TX_RECEIVER_BLOCKED_REMOVE  0x0018
#define DAP_CHAIN_DATUM_TOKEN_TSD_TYPE_TX_RECEIVER_FEE             0x0019
// ...

// ⭐ NEW: UTXO blocklist TSD types
#define DAP_CHAIN_DATUM_TOKEN_TSD_TYPE_UTXO_BLOCKED_ADD      0x0029
#define DAP_CHAIN_DATUM_TOKEN_TSD_TYPE_UTXO_BLOCKED_REMOVE   0x002A
#define DAP_CHAIN_DATUM_TOKEN_TSD_TYPE_UTXO_BLOCKED_CLEAR    0x002B
```

**TSD section format для UTXO operations:**

```c
// ADD/REMOVE: multiple UTXOs in one TSD section
struct {
    uint16_t type;           // 0x0029 (ADD) или 0x002A (REMOVE)
    uint16_t size;           // Размер данных
    struct {
        dap_chain_hash_fast_t tx_hash;
        uint32_t out_idx;
        // Optional: char reason[] для ADD operation
    }[] utxos;               // Массив UTXO для блокировки/разблокировки
};

// CLEAR: empty data section
struct {
    uint16_t type;           // 0x002B (CLEAR)
    uint16_t size;           // 0 (no data)
};
```

**6. Новый error code**

```c
// Existing error codes in dap_chain_ledger.h ...
DAP_LEDGER_TX_CHECK_PREV_OUT_ITEM_LOCKED,
DAP_LEDGER_TX_CHECK_PKEY_HASHES_DONT_MATCH,
// ...

// ⭐ NEW: UTXO blocking error code
DAP_LEDGER_TX_CHECK_OUT_ITEM_BLOCKED,  // UTXO is in token's blocklist
```

**Error message:**
```c
case DAP_LEDGER_TX_CHECK_OUT_ITEM_BLOCKED:
    return "Previous transaction output is blocked by token policy";
```

**7. Thread-Safety Design**

**Pattern:** Read-Write Lock для UTXO blocklist

```c
// Read operation (checking if UTXO is blocked) - множественные читатели
pthread_rwlock_rdlock(&l_token_item->utxo_blocklist_rwlock);
dap_ledger_utxo_block_item_t *l_blocked = NULL;
HASH_FIND(hh, l_token_item->utxo_blocklist, &l_key, 
          sizeof(dap_ledger_utxo_block_key_t), l_blocked);
bool l_is_blocked = (l_blocked != NULL);
pthread_rwlock_unlock(&l_token_item->utxo_blocklist_rwlock);

// Write operation (adding/removing from blocklist) - эксклюзивный доступ
pthread_rwlock_wrlock(&l_token_item->utxo_blocklist_rwlock);
HASH_ADD(hh, l_token_item->utxo_blocklist, key, 
         sizeof(dap_ledger_utxo_block_key_t), l_new_item);
l_token_item->utxo_blocklist_count++;
pthread_rwlock_unlock(&l_token_item->utxo_blocklist_rwlock);
```

**Обоснование:**
- Чтения (проверка блокировки) частые - multiple readers allowed
- Записи (изменение blocklist) редкие - exclusive writer access
- Соответствует паттерну остальных rwlock в dap_ledger_token_item_t

**8. Memory Footprint Analysis**

**Per token overhead:**
- `pthread_rwlock_t`: ~56 bytes (Linux x86_64)
- `size_t utxo_blocklist_count`: 8 bytes
- `*utxo_blocklist`: 8 bytes (pointer)
- **Total:** ~72 bytes per token (empty blocklist)

**Per blocked UTXO:**
- `dap_ledger_utxo_block_key_t`: 36 bytes
- `dap_time_t`: 8 bytes
- `char *reason`: 8 bytes (pointer)
- `UT_hash_handle`: ~32 bytes
- **Total:** ~84 bytes + strlen(reason) если есть

**Оценка для токена с 1000 заблокированных UTXO:**
- Token overhead: 72 bytes
- 1000 UTXOs: 84KB (без reason strings)
- **Total:** ~84KB per token

**Приемлемо для памяти:** Даже 10,000 блокированных UTXO = ~840KB per token

---

### 📊 Статус Фазы 1.3: ✅ ЗАВЕРШЕНА

**Deliverable:** Детальный дизайн структур данных - СОЗДАН

**Ключевые решения:**
1. Composite key (tx_hash + out_idx) для однозначной идентификации UTXO
2. Hash table (uthash) для O(1) lookup performance
3. pthread_rwlock_t для thread-safety (read-optimized)
4. 4 новых флага токена (BIT 16-19)
5. 3 новых TSD типа для token_update (0x0029-0x002B)
6. Опциональное поле `reason` для audit trail
7. Минимальный memory footprint (~84 bytes per blocked UTXO)

---

### 🔄 Переход к Субфазе 1.4

**Следующий шаг:** Проектирование API и CLI


---

### 🎯 Субфаза 1.4: Проектирование API и CLI

#### ✅ ЗАВЕРШЕНО: Детальный дизайн API и CLI интерфейсов

**1. Internal API Functions (dap_chain_ledger.c)**

Все функции static, префикс `s_ledger_utxo_blocklist_*`

```c
/**
 * @brief Initialize UTXO blocklist for a token
 * @param a_token_item Token item
 * @return 0 on success, negative error code on failure
 */
static int s_ledger_utxo_blocklist_init(dap_ledger_token_item_t *a_token_item);

/**
 * @brief Deinitialize and free UTXO blocklist for a token
 * @param a_token_item Token item
 */
static void s_ledger_utxo_blocklist_deinit(dap_ledger_token_item_t *a_token_item);

/**
 * @brief Add UTXO to blocklist
 * @param a_token_item Token item
 * @param a_tx_hash Transaction hash
 * @param a_out_idx Output index
 * @param a_reason Optional reason string (can be NULL)
 * @return 0 on success, negative error code on failure
 */
static int s_ledger_utxo_blocklist_add(dap_ledger_token_item_t *a_token_item,
                                        const dap_chain_hash_fast_t *a_tx_hash,
                                        uint32_t a_out_idx,
                                        const char *a_reason);

/**
 * @brief Remove UTXO from blocklist
 * @param a_token_item Token item
 * @param a_tx_hash Transaction hash
 * @param a_out_idx Output index
 * @return 0 on success, -ENOENT if not found
 */
static int s_ledger_utxo_blocklist_remove(dap_ledger_token_item_t *a_token_item,
                                           const dap_chain_hash_fast_t *a_tx_hash,
                                           uint32_t a_out_idx);

/**
 * @brief Clear all UTXOs from blocklist
 * @param a_token_item Token item
 * @return Number of UTXOs removed
 */
static size_t s_ledger_utxo_blocklist_clear(dap_ledger_token_item_t *a_token_item);

/**
 * @brief Check if UTXO is blocked
 * @param a_token_item Token item
 * @param a_tx_hash Transaction hash
 * @param a_out_idx Output index
 * @return true if blocked, false otherwise
 */
static bool s_ledger_utxo_is_blocked(dap_ledger_token_item_t *a_token_item,
                                      const dap_chain_hash_fast_t *a_tx_hash,
                                      uint32_t a_out_idx);

/**
 * @brief Get blocklist item with details
 * @param a_token_item Token item
 * @param a_tx_hash Transaction hash
 * @param a_out_idx Output index
 * @return Pointer to item or NULL if not blocked
 */
static dap_ledger_utxo_block_item_t* s_ledger_utxo_blocklist_get(
                                      dap_ledger_token_item_t *a_token_item,
                                      const dap_chain_hash_fast_t *a_tx_hash,
                                      uint32_t a_out_idx);
```

**Implementation notes:**
- Все функции thread-safe (используют rwlock)
- Return codes: 0 = success, negative errno-style codes for errors
- Memory management: caller не владеет возвращенными указателями
- Логирование через log_it() с уровнями L_DEBUG, L_WARNING, L_ERROR

**2. Token Update Integration (dap_chain_ledger.c)**

Модификация функции обработки TSD sections в `s_token_add_check()`:

```c
/**
 * @brief Process UTXO blocklist TSD sections in token_update
 * @param a_ledger Ledger
 * @param a_token_item Token item
 * @param a_tsd TSD section
 * @return 0 on success, error code on failure
 */
static int s_token_tsd_process_utxo_blocklist(dap_ledger_t *a_ledger,
                                                dap_ledger_token_item_t *a_token_item,
                                                dap_tsd_t *a_tsd)
{
    // Check UTXO_BLOCKING_ENABLED flag
    if (!(a_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_UTXO_BLOCKING_ENABLED)) {
        log_it(L_WARNING, "UTXO blocking is not enabled for token %s", a_token_item->ticker);
        return -EACCES;
    }
    
    // Check STATIC_UTXO_BLOCKLIST flag
    if (a_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_STATIC_UTXO_BLOCKLIST) {
        log_it(L_WARNING, "UTXO blocklist is static for token %s", a_token_item->ticker);
        return -EPERM;
    }
    
    switch (a_tsd->type) {
    case DAP_CHAIN_DATUM_TOKEN_TSD_TYPE_UTXO_BLOCKED_ADD: {
        // Parse TSD data: array of (tx_hash, out_idx) pairs
        // For each pair: call s_ledger_utxo_blocklist_add()
        break;
    }
    case DAP_CHAIN_DATUM_TOKEN_TSD_TYPE_UTXO_BLOCKED_REMOVE: {
        // Parse TSD data: array of (tx_hash, out_idx) pairs
        // For each pair: call s_ledger_utxo_blocklist_remove()
        break;
    }
    case DAP_CHAIN_DATUM_TOKEN_TSD_TYPE_UTXO_BLOCKED_CLEAR: {
        // Call s_ledger_utxo_blocklist_clear()
        break;
    }
    }
    return 0;
}
```

**3. CLI: token_update расширение**

**Файл:** `cellframe-sdk/modules/net/dap_chain_node_cli_cmd.c`  
**Функция:** `com_token_update()` (строка ~5149)

**Новые параметры:**

```bash
# Add UTXO(s) to blocklist
token_update -net <net> -chain <chain> -token <ticker> \
    -utxo_blocked_add <tx_hash>:<out_idx>[,<tx_hash>:<out_idx>...] \
    [-signs <cert1>,<cert2>...]

# Remove UTXO(s) from blocklist
token_update -net <net> -chain <chain> -token <ticker> \
    -utxo_blocked_remove <tx_hash>:<out_idx>[,<tx_hash>:<out_idx>...] \
    [-signs <cert1>,<cert2>...]

# Clear entire blocklist
token_update -net <net> -chain <chain> -token <ticker> \
    -utxo_blocked_clear \
    [-signs <cert1>,<cert2>...]
```

**Parsing logic:**

```c
// In com_token_update()
dap_cli_server_cmd_find_option_val(a_argv, arg_index, a_argc, "-utxo_blocked_add", &l_utxo_add_str);
if (l_utxo_add_str) {
    // Parse comma-separated list: "hash1:idx1,hash2:idx2,..."
    // For each: parse hash (dap_chain_hash_fast_from_str)
    // Add TSD section with type 0x0029
}

dap_cli_server_cmd_find_option_val(a_argv, arg_index, a_argc, "-utxo_blocked_remove", &l_utxo_remove_str);
// Similar parsing...

dap_cli_server_cmd_check_option(a_argv, arg_index, a_argc, "-utxo_blocked_clear");
if (l_utxo_clear_flag) {
    // Add TSD section with type 0x002B (no data)
}
```

**4. CLI: Новая команда token_utxo_list**

**Файл:** `cellframe-sdk/modules/net/dap_chain_node_cli_cmd.c`

**Syntax:**
```bash
token_utxo_list -net <net> -token <ticker> [-blocked] [-offset N] [-limit M] [-json]
```

**Description:**
- Показывает список UTXO для токена
- `-blocked` - показывать только заблокированные UTXO
- `-offset N` - пагинация (начать с N-го элемента)
- `-limit M` - показать максимум M элементов
- `-json` - вывод в JSON формате

**Function signature:**
```c
static int com_token_utxo_list(int a_argc, char **a_argv, void **a_str_reply)
{
    // Parse parameters
    const char *l_net_name = NULL;
    const char *l_token_ticker = NULL;
    bool l_blocked_only = false;
    size_t l_offset = 0, l_limit = 100;  // Default limit
    bool l_json_output = false;
    
    // Find token_item
    dap_ledger_t *l_ledger = ...;
    dap_ledger_token_item_t *l_token_item = s_ledger_find_token(l_ledger, l_token_ticker);
    
    // If -blocked flag: iterate through utxo_blocklist
    if (l_blocked_only) {
        pthread_rwlock_rdlock(&l_token_item->utxo_blocklist_rwlock);
        dap_ledger_utxo_block_item_t *l_item, *l_tmp;
        size_t l_count = 0;
        
        HASH_ITER(hh, l_token_item->utxo_blocklist, l_item, l_tmp) {
            if (l_count >= l_offset && l_count < l_offset + l_limit) {
                // Format output
                char l_hash_str[DAP_CHAIN_HASH_FAST_STR_SIZE];
                dap_chain_hash_fast_to_str(&l_item->key.tx_hash, l_hash_str, sizeof(l_hash_str));
                
                if (l_json_output) {
                    // JSON format
                } else {
                    // Human-readable format
                    dap_cli_server_cmd_set_reply_text(a_str_reply,
                        "%s:%u | Blocked: %s | Reason: %s\n",
                        l_hash_str, l_item->key.out_idx,
                        dap_time_to_str_rfc822(l_item->blocked_time),
                        l_item->reason ? l_item->reason : "N/A");
                }
            }
            l_count++;
        }
        pthread_rwlock_unlock(&l_token_item->utxo_blocklist_rwlock);
    } else {
        // Iterate through all UTXOs (ledger_items)
        // Check if blocked and mark accordingly
    }
    
    return 0;
}
```

**Output format (human-readable):**
```
UTXO List for token: MYCOIN on network: mynet
Total UTXOs: 150 | Blocked: 15

TX Hash                                                        :Idx | Status    | Blocked Time        | Reason
================================================================================================================================
0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890:0    | BLOCKED   | 2025-10-16 12:00:00 | Suspicious activity
0x2345678901bcdef02345678901bcdef02345678901bcdef023456789012:5    | BLOCKED   | 2025-10-16 13:30:00 | Compliance issue
0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef12345:2    | AVAILABLE | -                   | -
```

**Output format (JSON):**
```json
{
  "token": "MYCOIN",
  "network": "mynet",
  "total_utxos": 150,
  "blocked_count": 15,
  "utxos": [
    {
      "tx_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
      "out_idx": 0,
      "status": "BLOCKED",
      "blocked_time": "2025-10-16T12:00:00Z",
      "reason": "Suspicious activity"
    },
    ...
  ]
}
```

**5. CLI: token_info расширение**

**Файл:** `cellframe-sdk/modules/net/dap_chain_node_cli_cmd.c`  
**Функция:** `com_token_list()` (показывает token_info)

**Добавить секцию в вывод:**
```
Token: MYCOIN
Type: CF20
...
Flags: UTXO_BLOCKING_ENABLED
Permissions:
  - UTXO Blocking: ENABLED
  - UTXO Blocklist: 15 items
  - Address Sender Blocking: DISABLED (flag set)
  - Address Receiver Blocking: ENABLED
```

**Code modification:**
```c
// In com_token_list() or related info function
if (l_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_UTXO_BLOCKING_ENABLED) {
    dap_cli_server_cmd_set_reply_text(a_str_reply,
        "UTXO Blocking: ENABLED\n");
    dap_cli_server_cmd_set_reply_text(a_str_reply,
        "UTXO Blocklist: %zu items\n", l_token_item->utxo_blocklist_count);
    
    if (l_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_STATIC_UTXO_BLOCKLIST)
        dap_cli_server_cmd_set_reply_text(a_str_reply, "UTXO Blocklist: STATIC (immutable)\n");
}

if (l_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_DISABLE_ADDRESS_SENDER_BLOCKING)
    dap_cli_server_cmd_set_reply_text(a_str_reply, "Address Sender Blocking: DISABLED\n");

if (l_token_item->flags & DAP_CHAIN_DATUM_TOKEN_FLAG_DISABLE_ADDRESS_RECEIVER_BLOCKING)
    dap_cli_server_cmd_set_reply_text(a_str_reply, "Address Receiver Blocking: DISABLED\n");
```

**6. Help Text Updates**

**token_update help:**
```
...
UTXO Blocklist Management:
  -utxo_blocked_add <tx_hash>:<out_idx>[,...]  Add UTXO(s) to blocklist
  -utxo_blocked_remove <tx_hash>:<out_idx>[,...] Remove UTXO(s) from blocklist
  -utxo_blocked_clear                          Clear entire blocklist

Note: Requires UTXO_BLOCKING_ENABLED flag and valid signatures.
      Cannot modify if STATIC_UTXO_BLOCKLIST flag is set.
```

**token_utxo_list help:**
```
token_utxo_list - List UTXOs for a token with blocking status

Usage:
  token_utxo_list -net <network> -token <ticker> [options]

Parameters:
  -net <network>     Network name
  -token <ticker>    Token ticker
  -blocked           Show only blocked UTXOs
  -offset <N>        Start from Nth item (pagination)
  -limit <M>         Show max M items (default: 100)
  -json              Output in JSON format

Examples:
  token_utxo_list -net mynet -token MYCOIN
  token_utxo_list -net mynet -token MYCOIN -blocked
  token_utxo_list -net mynet -token MYCOIN -blocked -limit 50 -json
```

---

### 📊 Статус Фазы 1.4: ✅ ЗАВЕРШЕНА

**Deliverable:** API спецификация и CLI дизайн - СОЗДАНЫ

**Ключевые решения:**
1. 7 внутренних API функций (`s_ledger_utxo_blocklist_*`)
2. Token update integration через TSD processing
3. 3 новых параметра для token_update CLI
4. Новая команда `token_utxo_list` с пагинацией и JSON support
5. Расширение `token_info` для показа UTXO blocking status
6. Детальные help messages для всех команд

---

### 🎉 ФАЗА 1: АНАЛИЗ И ПРОЕКТИРОВАНИЕ - ПОЛНОСТЬЮ ЗАВЕРШЕНА

**Все deliverables созданы:**
1. ✅ Документ архитектуры UTXO tracking
2. ✅ Схема существующих permissions механизмов  
3. ✅ Детальный дизайн структур данных
4. ✅ API спецификация и CLI дизайн

**Следующая фаза:** Фаза 2 - Инфраструктура тестирования

