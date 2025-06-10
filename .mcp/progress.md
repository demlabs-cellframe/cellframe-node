# Прогресс исправления srv_stake invalidate с параметром -cert

## Проблема
Команда `srv_stake invalidate` с параметром `-cert` не работает, если не найдена в леджере условная транзакция делегации. Нужно изменить поведение, чтобы инвалидация декретом работала независимо от того, была ли найдена транзакция.

## Анализ кода

### Текущая логика (строки 2782-2787):
```c
HASH_FIND(hh, l_srv_stake->itemlist, &l_signing_addr.data.hash_fast, sizeof(dap_hash_fast_t), l_stake);
if (!l_stake) {
    dap_json_rpc_error_add(*a_json_arr_reply, DAP_CHAIN_NODE_CLI_SRV_STAKE_INVALIDATE_CERT_PKEY_ERR, 
                          "Specified certificate/pkey hash is not delegated nor this delegating is approved."
                          " Try to invalidate with tx hash instead");
    return DAP_CHAIN_NODE_CLI_SRV_STAKE_INVALIDATE_CERT_PKEY_ERR;
}
```

### Проблема:
- При использовании `-cert` код ищет stake в `itemlist` 
- Если stake не найден, возвращается ошибка
- Но при использовании `-poa_cert` (декрет) должна быть возможность инвалидации независимо от наличия stake в itemlist

### Решение:
Нужно разделить логику для случаев:
1. Инвалидация через wallet (`-w`) - требует наличие stake в itemlist
2. Инвалидация через PoA декрет (`-poa_cert`) - не требует наличие stake в itemlist

## Детальный план исправления:

### 1. Создать функцию поиска транзакции делегации по адресу подписи
```c
static dap_hash_fast_t s_find_delegation_tx_by_signing_addr(dap_ledger_t *a_ledger, dap_chain_addr_t *a_signing_addr)
```
Эта функция будет искать транзакцию делегации напрямую в леджере по адресу подписи.

### 2. Изменить логику в s_cli_srv_stake_invalidate
- Если используется `-poa_cert` и stake не найден в itemlist, попытаться найти транзакцию напрямую в леджере
- Только для `-w` (wallet) требовать обязательное наличие stake в itemlist

### 3. Добавить новую логику поиска
- Использовать `dap_ledger_tx_find_by_addr` для поиска транзакций по адресу
- Проверить каждую найденную транзакцию на наличие условного выхода типа `DAP_CHAIN_TX_OUT_COND_SUBTYPE_SRV_STAKE_POS_DELEGATE`
- Вернуть хеш подходящей транзакции

## Статус: В процессе реализации

### Исследование функций леджера:
- Изучена функция `dap_ledger_tx_find_by_addr()` в `cellframe-sdk/modules/net/dap_chain_ledger.c`
- Функция позволяет искать транзакции по адресу в выходах
- Можно использовать для поиска транзакций делегации по адресу подписи

### Техническая реализация:
1. Создать функцию `s_find_delegation_tx_by_signing_addr()` для поиска транзакции делегации
2. Изменить логику в `s_cli_srv_stake_invalidate()` для разделения случаев wallet и PoA
3. Добавить альтернативный путь поиска для случая PoA декрета

## Файлы для изменения:
- `cellframe-sdk/modules/service/stake/dap_chain_net_srv_stake_pos_delegate.c`

# Прогресс: Добавление метаданных в блок перед отправкой SUBMIT

## Задача ✅ ЗАВЕРШЕНА
Добавить в блок метаданные в виде сериализованного массива известной длины перед его отправкой SUBMIT в ESBOCS консенсусе.

## Уточненные требования ✅
- Массив содержит бинарные данные типа `uint8_t` с переменной длиной
- Массив и его длину возвращает специальная функция (черный ящик)
- Нужно добавить новый тип метаданных

## Реализация

### Этап 1: Определение нового типа метаданных ✅
- Добавлен `#define DAP_CHAIN_BLOCK_META_EVM_DATA 0x84` в `cellframe-sdk/modules/type/blocks/include/dap_chain_block.h`

### Этап 2: Обработка нового типа метаданных ✅
- Добавлена обработка в `s_meta_type_to_string()` в `cellframe-sdk/modules/type/blocks/dap_chain_block.c`
- Добавлена обработка в `s_meta_extract()` для переменной длины данных
- Добавлена обработка в CLI функциях для JSON вывода

### Этап 3: Колбэки и интеграция ✅
- Добавлены типы колбэков `dap_chain_esbocs_callback_set_custom_metadata_t` и `dap_chain_esbocs_callback_presign_t`
- Добавлены поля колбэков в структуру `dap_chain_esbocs_t`
- Модифицирована функция `s_session_candidate_submit()` для использования колбэков
- Добавлена проверка в `s_callback_block_verify()` с использованием presign колбэка

### Этап 4: Функции установки колбэков ✅ ЗАВЕРШЕНО
- Добавлены функции `dap_chain_esbocs_set_custom_metadata_callback()` и `dap_chain_esbocs_set_presign_callback()`
- Функции позволяют устанавливать и удалять колбэки для конкретной сети
- Добавлена валидация параметров и обработка ошибок
- Добавлено логирование операций установки/удаления колбэков

## Изменения в коде

### Новый тип метаданных:
```c
#define DAP_CHAIN_BLOCK_META_EVM_DATA        0x84
```

### Колбэки в структуре ESBOCS:
```c
typedef uint8_t *(*dap_chain_esbocs_callback_set_custom_metadata_t)(dap_chain_block_t *a_block, uint8_t *a_meta_type, size_t *a_data_size);
typedef bool (*dap_chain_esbocs_callback_presign_t)(dap_chain_block_t *a_block);

typedef struct dap_chain_esbocs {
    // ... existing fields ...
    dap_chain_esbocs_callback_set_custom_metadata_t callback_set_custom_metadata;
    dap_chain_esbocs_callback_presign_t callback_presign;
    void *_pvt;
} dap_chain_esbocs_t;
```

### Функции установки колбэков:
```c
int dap_chain_esbocs_set_custom_metadata_callback(dap_chain_net_id_t a_net_id, 
                                                  dap_chain_esbocs_callback_set_custom_metadata_t a_callback);
int dap_chain_esbocs_set_presign_callback(dap_chain_net_id_t a_net_id,
                                          dap_chain_esbocs_callback_presign_t a_callback);
```

### Интеграция в SUBMIT:
```c
// В функции s_session_candidate_submit()
if (l_candidate_size && a_session->esbocs->callback_set_custom_metadata) {
    size_t l_custom_data_size = 0;
    uint8_t l_meta_type = DAP_CHAIN_BLOCK_META_EVM_DATA;
    uint8_t *l_custom_data = a_session->esbocs->callback_set_custom_metadata(l_candidate, &l_meta_type, &l_custom_data_size);
    if (l_custom_data && l_custom_data_size) {
        l_candidate_size = dap_chain_block_meta_add(&l_candidate, l_candidate_size, l_meta_type, l_custom_data, l_custom_data_size);
        // Debug logging...
    }
}
```

### Интеграция в верификацию блоков:
```c
// В функции s_callback_block_verify()
if (l_esbocs->callback_presign && !l_esbocs->callback_presign(a_block)) {
    log_it(L_ERROR, "Block %s has invalid custom metadata", dap_hash_fast_to_str_static(a_block_hash));
    return -5;
}
```

## Использование API

### Установка колбэка для добавления метаданных:
```c
// Пример функции колбэка
uint8_t *my_custom_metadata_callback(dap_chain_block_t *a_block, uint8_t *a_meta_type, size_t *a_data_size) {
    // Ваша логика получения данных
    *a_meta_type = DAP_CHAIN_BLOCK_META_EVM_DATA; // или другой тип
    *a_data_size = my_data_size;
    return my_data_ptr;
}

// Установка колбэка
dap_chain_net_id_t net_id = {.uint64 = 0x123};
int result = dap_chain_esbocs_set_custom_metadata_callback(net_id, my_custom_metadata_callback);
```

### Установка колбэка для проверки метаданных:
```c
// Пример функции проверки
bool my_presign_callback(dap_chain_block_t *a_block) {
    // Ваша логика проверки блока
    return true; // или false если блок невалиден
}

// Установка колбэка
int result = dap_chain_esbocs_set_presign_callback(net_id, my_presign_callback);
```

## Статус: ✅ ПОЛНОСТЬЮ ЗАВЕРШЕНА
Реализация полностью завершена. Добавлена возможность установки пользовательских метаданных в блоки ESBOCS консенсуса через систему колбэков с полным API для управления.