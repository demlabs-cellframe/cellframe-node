# dap_ledger_pvt_cache_gdb_load_tokens_callback

**Категория:** Blockchain Operations  
**Модуль:** `cellframe-sdk/modules`  
**Приоритет:** 95

## Описание
Функция блокчейн операций. dap_ledger_pvt_cache_gdb_load_tokens_callback управляет блоками и транзакциями. * @param a_global_db_context * @param a_rc * @param a_group * @param a_key * @param a_values_total * @param a_values_shift * @param a_values_count * @param a_values * @param a_arg

## Сигнатура
```c
bool dap_ledger_pvt_cache_gdb_load_tokens_callback(dap_global_db_instance_t *a_dbi, int a_rc, const char *a_group, const size_t a_values_total, const size_t a_values_count, dap_global_db_obj_t *a_values, void *a_arg) {
```

## Параметры
| Параметр | Тип | Описание |
|----------|-----|----------|
| a_dbi | `dap_global_db_instance_t` |  |
| a_rc | `int` |  |
| a_group | `const char` |  |
| a_values_total | `const size_t` |  |
| a_values_count | `const size_t` |  |
| a_values | `dap_global_db_obj_t` |  |
| a_arg | `void` |  |


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
    
    // Вызов dap_ledger_pvt_cache_gdb_load_tokens_callback
    int result = dap_ledger_pvt_cache_gdb_load_tokens_callback(/* параметры */);
    
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

def example_ledger_pvt_cache_gdb_load_tokens_callback():
    try:
        result = libCellFrame.ledger.pvt.cache.gdb.load.tokens.callback()
        if result is not None:
            print("Функция выполнена успешно")
            return result
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

# Использование
example_ledger_pvt_cache_gdb_load_tokens_callback()
```

## Производительность
- **Категория сложности:** Сложная
- **Рекомендуемое использование:** Проверить состояние блокчейна

## История изменений
- **Версия API:** 1.0
- **Последнее обновление:** 2025-06-18

---
*Документация сгенерирована автоматически системой Simple Mass Generator v1.0*
