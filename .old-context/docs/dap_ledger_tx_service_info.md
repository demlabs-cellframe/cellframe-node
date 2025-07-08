# dap_ledger_tx_service_info

**Категория:** Blockchain Operations  
**Модуль:** `cellframe-sdk/modules`  
**Приоритет:** 95

## Описание
Функция блокчейн операций. dap_ledger_tx_service_info управляет блоками и транзакциями.

## Сигнатура
```c
bool dap_ledger_tx_service_info(dap_ledger_t *a_ledger, dap_hash_fast_t *a_tx_hash, dap_chain_srv_uid_t *a_uid, char **a_service_name,  dap_chain_tx_tag_action_type_t *a_action) {
```

## Параметры
| Параметр | Тип | Описание |
|----------|-----|----------|
| a_ledger | `dap_ledger_t` |  |
| a_tx_hash | `dap_hash_fast_t` |  |
| a_uid | `dap_chain_srv_uid_t` |  |
| a_service_name | `char` |  |
| a_action | `dap_chain_tx_tag_action_type_t` |  |


## Возвращаемое значение
- **Тип:** `bool`
- **Описание:** Результат выполнения операции

## Примеры использования

### C/C++
```c
#include "cellframe_api.h"

int main() {
    // Инициализация
    if (dap_common_init("app") != 0) {
        return -1;
    }
    
    // Вызов dap_ledger_tx_service_info
    int result = dap_ledger_tx_service_info(/* параметры */);
    
    if (result == 0) {
        printf("Успешно выполнено\n");
    }
    
    dap_common_deinit();
    return result;
}
```

### Python
```python
import libCellFrame

def example_ledger_tx_service_info():
    try:
        result = libCellFrame.ledger.tx.service.info()
        if result is not None:
            print("Функция выполнена успешно")
            return result
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

# Использование
example_ledger_tx_service_info()
```

## Производительность
- **Категория сложности:** Сложная
- **Рекомендуемое использование:** Проверить состояние блокчейна

## История изменений
- **Версия API:** 1.0
- **Последнее обновление:** 2025-06-18

---
*Документация сгенерирована автоматически системой Simple Mass Generator v1.0*
