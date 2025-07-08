# dap_ledger_tx_purge

**Категория:** Blockchain Operations  
**Модуль:** `cellframe-sdk/modules`  
**Приоритет:** 95

## Описание
Функция блокчейн операций. dap_ledger_tx_purge управляет блоками и транзакциями.

## Сигнатура
```c
void dap_ledger_tx_purge(dap_ledger_t *a_ledger, bool a_preserve_db) {
```

## Параметры
| Параметр | Тип | Описание |
|----------|-----|----------|
| a_ledger | `dap_ledger_t` |  |
| a_preserve_db | `bool` |  |


## Возвращаемое значение
- **Тип:** `void`
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
    
    // Вызов dap_ledger_tx_purge
    int result = dap_ledger_tx_purge(/* параметры */);
    
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

def example_ledger_tx_purge():
    try:
        result = libCellFrame.ledger.tx.purge()
        if result is not None:
            print("Функция выполнена успешно")
            return result
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

# Использование
example_ledger_tx_purge()
```

## Производительность
- **Категория сложности:** Простая
- **Рекомендуемое использование:** Проверить состояние блокчейна

## История изменений
- **Версия API:** 1.0
- **Последнее обновление:** 2025-06-18

---
*Документация сгенерирована автоматически системой Simple Mass Generator v1.0*
