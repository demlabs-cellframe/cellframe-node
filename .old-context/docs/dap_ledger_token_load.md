# dap_ledger_token_load

**Категория:** Blockchain Operations  
**Модуль:** `cellframe-sdk/modules`  
**Приоритет:** 95

## Описание
Функция блокчейн операций. dap_ledger_token_load управляет блоками и транзакциями.

## Сигнатура
```c
int dap_ledger_token_load(dap_ledger_t *a_ledger, byte_t *a_token, size_t a_token_size) {
```

## Параметры
| Параметр | Тип | Описание |
|----------|-----|----------|
| a_ledger | `dap_ledger_t` |  |
| a_token | `byte_t` |  |
| a_token_size | `size_t` |  |


## Возвращаемое значение
- **Тип:** `int`
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
    
    // Вызов dap_ledger_token_load
    int result = dap_ledger_token_load(/* параметры */);
    
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

def example_ledger_token_load():
    try:
        result = libCellFrame.ledger.token.load()
        if result is not None:
            print("Функция выполнена успешно")
            return result
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

# Использование
example_ledger_token_load()
```

## Производительность
- **Категория сложности:** Средняя
- **Рекомендуемое использование:** Проверить состояние блокчейна

## История изменений
- **Версия API:** 1.0
- **Последнее обновление:** 2025-06-18

---
*Документация сгенерирована автоматически системой Simple Mass Generator v1.0*
