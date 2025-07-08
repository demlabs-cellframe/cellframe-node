# dap_chain_node_cli_init

**Категория:** Critical Core  
**Модуль:** `cellframe-sdk/modules`  
**Приоритет:** 100

## Описание
Критическая функция ядра. dap_chain_node_cli_init выполняет базовые операции системы Cellframe. * * @brief dap_chain_node_cli_init * Initialization of the server side of the interaction * with the console kelvin-node-cli * init commands description * return 0 if OK, -1 error * @param g_config * @param a_server_enabled - if server and rpc enabled will be wrn inform * @return int

## Сигнатура
```c
int dap_chain_node_cli_init(dap_config_t * g_config) {
```

## Параметры
| Параметр | Тип | Описание |
|----------|-----|----------|
| g_config | `dap_config_t *` |  |


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
    
    // Вызов dap_chain_node_cli_init
    int result = dap_chain_node_cli_init(/* параметры */);
    
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

def example_chain_node_cli_init():
    try:
        result = libCellFrame.chain.node.cli.init()
        if result is not None:
            print("Функция выполнена успешно")
            return result
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

# Использование
example_chain_node_cli_init()
```

## Производительность
- **Категория сложности:** Простая
- **Рекомендуемое использование:** Использовать с осторожностью

## История изменений
- **Версия API:** 1.0
- **Последнее обновление:** 2025-06-18

---
*Документация сгенерирована автоматически системой Simple Mass Generator v1.0*
