# dap_chain_ledger_tx_add

## Описание
Добавляет транзакцию в ledger блокчейна. Эта функция является основной для записи транзакций в распределенный реестр Cellframe и обеспечивает целостность данных блокчейна.

## Сигнатура
```c
int dap_chain_ledger_tx_add(dap_chain_ledger_t *a_ledger, 
                           dap_chain_datum_tx_t *a_tx,
                           dap_chain_hash_fast_t *a_tx_hash,
                           bool a_from_threshold);
```

## Параметры
| Параметр | Тип | Описание | Обязательный |
|----------|-----|----------|--------------|
| a_ledger | `dap_chain_ledger_t*` | Указатель на объект ledger | Да |
| a_tx | `dap_chain_datum_tx_t*` | Указатель на транзакцию для добавления | Да |
| a_tx_hash | `dap_chain_hash_fast_t*` | Хеш транзакции для верификации | Да |
| a_from_threshold | `bool` | Флаг: добавляется ли из threshold consensus | Нет |

## Возвращаемое значение
- **Тип:** `int`
- **Описание:** Код результата операции
- **Возможные значения:**
  - `0` - Успешное добавление транзакции
  - `-1` - Ошибка: недопустимые параметры
  - `-2` - Ошибка: транзакция уже существует
  - `-3` - Ошибка: недостаточно средств
  - `-4` - Ошибка: недопустимая подпись
  - `-5` - Ошибка: превышен лимит размера

## Коды ошибок
| Код | Константа | Описание |
|-----|-----------|----------|
| 0   | DAP_CHAIN_LEDGER_TX_ADD_SUCCESS | Транзакция успешно добавлена |
| -1  | DAP_CHAIN_LEDGER_TX_ADD_ERROR_INVALID_PARAMS | Недопустимые входные параметры |
| -2  | DAP_CHAIN_LEDGER_TX_ADD_ERROR_DUPLICATE | Транзакция уже существует в ledger |
| -3  | DAP_CHAIN_LEDGER_TX_ADD_ERROR_INSUFFICIENT_FUNDS | Недостаточно средств для выполнения |
| -4  | DAP_CHAIN_LEDGER_TX_ADD_ERROR_INVALID_SIGNATURE | Недопустимая криптографическая подпись |
| -5  | DAP_CHAIN_LEDGER_TX_ADD_ERROR_SIZE_LIMIT | Превышен максимальный размер транзакции |

## Пример использования

### C/C++
```c
#include "dap_chain_ledger.h"
#include "dap_chain_datum_tx.h"

int main() {
    // Инициализация ledger
    dap_chain_ledger_t *ledger = dap_chain_ledger_create();
    if (!ledger) {
        printf("Ошибка создания ledger\n");
        return -1;
    }
    
    // Создание транзакции (упрощенный пример)
    dap_chain_datum_tx_t *tx = dap_chain_datum_tx_create();
    if (!tx) {
        printf("Ошибка создания транзакции\n");
        dap_chain_ledger_delete(ledger);
        return -1;
    }
    
    // Вычисление хеша транзакции
    dap_chain_hash_fast_t tx_hash;
    dap_hash_fast(tx, dap_chain_datum_tx_get_size(tx), &tx_hash);
    
    // Добавление транзакции в ledger
    int result = dap_chain_ledger_tx_add(ledger, tx, &tx_hash, false);
    
    switch (result) {
        case 0:
            printf("Транзакция успешно добавлена\n");
            break;
        case -1:
            printf("Ошибка: недопустимые параметры\n");
            break;
        case -2:
            printf("Ошибка: транзакция уже существует\n");
            break;
        case -3:
            printf("Ошибка: недостаточно средств\n");
            break;
        case -4:
            printf("Ошибка: недопустимая подпись\n");
            break;
        default:
            printf("Неизвестная ошибка: %d\n", result);
    }
    
    // Очистка ресурсов
    dap_chain_datum_tx_delete(tx);
    dap_chain_ledger_delete(ledger);
    
    return result;
}
```

### Python
```python
import libCellFrame

def add_transaction_to_ledger():
    """Пример добавления транзакции в ledger через Python API"""
    
    try:
        # Создание ledger
        ledger = libCellFrame.ChainLedger()
        
        # Создание транзакции
        tx = libCellFrame.ChainDatumTx()
        tx.create_simple_transfer(
            from_addr="mNXGWtYTDjbRgQskLjBJKAKsKtKXDABdwBD",
            to_addr="mQNGWtYTDjbRgQskLjBJKAKsKtKXDABdwBE", 
            amount=1000000,  # В минимальных единицах
            fee=1000
        )
        
        # Подписание транзакции
        private_key = libCellFrame.CryptoKey.load_from_file("wallet.key")
        tx.sign(private_key)
        
        # Добавление в ledger
        result = ledger.tx_add(tx, from_threshold=False)
        
        if result == 0:
            print("Транзакция успешно добавлена")
            print(f"Hash: {tx.get_hash()}")
        else:
            print(f"Ошибка добавления транзакции: {result}")
            
    except Exception as e:
        print(f"Исключение: {e}")
        return -1
        
    return result

# Использование
if __name__ == "__main__":
    add_transaction_to_ledger()
```

## Связанные функции
- `dap_chain_ledger_tx_remove()` - удаление транзакции из ledger
- `dap_chain_ledger_tx_find_by_hash()` - поиск транзакции по хешу
- `dap_chain_ledger_balance_get()` - получение баланса адреса
- `dap_chain_datum_tx_create()` - создание новой транзакции
- `dap_chain_datum_tx_sign()` - подписание транзакции

## Примечания

### Важные замечания
- **Атомарность:** Функция обеспечивает атомарность операции - транзакция либо добавляется полностью, либо не добавляется вообще
- **Валидация:** Перед добавлением выполняется полная валидация транзакции, включая проверку подписей и балансов
- **Производительность:** Операция может быть ресурсоемкой для больших транзакций или при высокой нагрузке
- **Потокобезопасность:** Функция потокобезопасна при использовании различных ledger объектов

### Ограничения и предупреждения
- Максимальный размер транзакции ограничен константой `DAP_CHAIN_DATUM_TX_MAX_SIZE`
- При работе с threshold consensus необходимо соблюдать дополнительные требования
- Функция может блокироваться при синхронизации с сетью
- Рекомендуется проверять возвращаемое значение для обработки ошибок

### Производительность
- **Время выполнения:** O(log n) где n - количество транзакций в ledger
- **Память:** Дополнительные ~1KB на транзакцию для индексации
- **Диск:** Транзакция сохраняется на диск асинхронно

## Диагностика и отладка

### Логирование
```c
// Включение детального логирования
dap_log_level_set(L_DEBUG);
dap_chain_ledger_set_debug_mode(ledger, true);
```

### Проверка состояния
```c
// Проверка состояния ledger перед добавлением
if (!dap_chain_ledger_is_valid(ledger)) {
    printf("Ledger в недопустимом состоянии\n");
    return -1;
}

// Проверка размера транзакции
size_t tx_size = dap_chain_datum_tx_get_size(tx);
if (tx_size > DAP_CHAIN_DATUM_TX_MAX_SIZE) {
    printf("Транзакция слишком большая: %zu bytes\n", tx_size);
    return -5;
}
```

## Тестирование

### Модульные тесты
```c
// Тест успешного добавления
void test_tx_add_success() {
    dap_chain_ledger_t *ledger = create_test_ledger();
    dap_chain_datum_tx_t *tx = create_test_tx();
    dap_chain_hash_fast_t hash;
    
    dap_hash_fast(tx, dap_chain_datum_tx_get_size(tx), &hash);
    
    int result = dap_chain_ledger_tx_add(ledger, tx, &hash, false);
    assert(result == 0);
    
    cleanup_test_data(ledger, tx);
}

// Тест дублирования транзакции
void test_tx_add_duplicate() {
    // Реализация теста на дублирование
}
```

## История изменений
| Версия | Дата | Изменения |
|--------|------|-----------|
| 1.0 | 2024-01-01 | Первая версия функции |
| 1.1 | 2024-06-01 | Добавлена поддержка threshold consensus |
| 1.2 | 2024-12-01 | Улучшена производительность и добавлены новые коды ошибок |

## См. также
- [Cellframe Ledger Architecture](../architecture/ledger.md)
- [Transaction Format Specification](../specs/transaction-format.md)
- [Consensus Mechanisms](../consensus/overview.md)
- [Python API Reference](../python/api-reference.md) 