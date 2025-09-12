# 💰 Basic Wallet - Простой кошелек для CellFrame

Этот пример демонстрирует создание базового криптовалютного кошелька с основными функциями управления токенами на платформе CellFrame.

## 🎯 Возможности

- ✅ **Создание нового кошелька** с автоматической генерацией ключей
- ✅ **Загрузка существующего кошелька** из файла
- ✅ **Просмотр баланса** токенов
- ✅ **Отправка токенов** другому адресу
- ✅ **История транзакций** кошелька
- ✅ **Экспорт/импорт** кошелька

## 📁 Структура проекта

```
basic-wallet/
├── CMakeLists.txt          # Конфигурация сборки
├── src/
│   ├── main.c             # Основное приложение
│   ├── wallet.c           # Логика кошелька
│   └── transaction.c      # Работа с транзакциями
├── include/
│   ├── wallet.h           # API кошелька
│   └── transaction.h      # API транзакций
├── config/
│   └── wallet.cfg         # Конфигурация
├── tests/
│   └── test_wallet.c      # Тесты
└── docs/
    ├── api.md             # API документация
    └── examples.md        # Примеры использования
```

## 🚀 Быстрый старт

### Сборка и запуск

```bash
# Переход в директорию примера
cd examples/basic/basic-wallet

# Сборка
mkdir build && cd build
cmake .. -DCMAKE_BUILD_TYPE=Release
make

# Создание нового кошелька
./basic-wallet create my_wallet

# Просмотр баланса
./basic-wallet balance my_wallet

# Отправка токенов
./basic-wallet send my_wallet <recipient_address> 100.0 KEL
```

## 💻 Основные компоненты

### Структура кошелька

```c
// include/wallet.h
typedef struct basic_wallet {
    char name[64];                    // Имя кошелька
    char address[128];                // Адрес кошелька
    dap_enc_key_t *private_key;       // Приватный ключ
    dap_pkey_t *public_key;           // Публичный ключ

    // Балансы по токенам
    GHashTable *balances;             // Таблица балансов

    // История транзакций
    GList *transactions;              // Список транзакций

    // Настройки
    bool encrypted;                   // Шифрование файла
    char *password;                   // Пароль (если зашифрован)
} basic_wallet_t;
```

### Операции с кошельком

#### Создание кошелька

```c
basic_wallet_t *wallet_create(const char *name, const char *password) {
    basic_wallet_t *wallet = calloc(1, sizeof(basic_wallet_t));
    strncpy(wallet->name, name, sizeof(wallet->name) - 1);

    // Генерация ключевой пары
    wallet->private_key = dap_enc_key_generate(DAP_ENC_KEY_TYPE_SIG_ECDSA, 256);
    wallet->public_key = dap_enc_key_get_pkey(wallet->private_key);

    // Получение адреса из публичного ключа
    size_t addr_size = 0;
    uint8_t *addr_bytes = dap_enc_key_get_address(wallet->public_key, &addr_size);
    dap_enc_base58_encode(addr_bytes, addr_size, wallet->address);

    // Инициализация структур данных
    wallet->balances = g_hash_table_new_full(g_str_hash, g_str_equal, free, free);
    wallet->transactions = NULL;

    // Настройки шифрования
    wallet->encrypted = (password != NULL);
    if (password) {
        wallet->password = strdup(password);
    }

    return wallet;
}
```

#### Загрузка кошелька

```c
basic_wallet_t *wallet_load(const char *filename, const char *password) {
    // Загрузка файла кошелька
    FILE *file = fopen(filename, "rb");
    if (!file) {
        return NULL;
    }

    // Чтение и расшифровка данных (если нужно)
    // ...

    // Восстановление структур данных
    basic_wallet_t *wallet = wallet_create_from_data(data);

    fclose(file);
    return wallet;
}
```

#### Сохранение кошелька

```c
int wallet_save(basic_wallet_t *wallet, const char *filename) {
    // Сериализация данных кошелька
    size_t data_size;
    uint8_t *data = wallet_serialize(wallet, &data_size);

    // Шифрование (если настроено)
    if (wallet->encrypted) {
        data = wallet_encrypt_data(data, &data_size, wallet->password);
    }

    // Сохранение в файл
    FILE *file = fopen(filename, "wb");
    if (!file) {
        free(data);
        return -1;
    }

    fwrite(data, 1, data_size, file);
    fclose(file);
    free(data);

    return 0;
}
```

## 💸 Работа с токенами

### Просмотр баланса

```c
void wallet_print_balance(basic_wallet_t *wallet) {
    printf("💰 Баланс кошелька %s:\n", wallet->name);
    printf("📍 Адрес: %s\n", wallet->address);
    printf("\n");

    if (g_hash_table_size(wallet->balances) == 0) {
        printf("📭 Кошелек пуст\n");
        return;
    }

    GHashTableIter iter;
    gpointer key, value;
    g_hash_table_iter_init(&iter, wallet->balances);

    while (g_hash_table_iter_next(&iter, &key, &value)) {
        const char *ticker = (const char *)key;
        uint256_t *balance = (uint256_t *)value;

        char balance_str[64];
        uint256_to_str(balance, balance_str, sizeof(balance_str));

        printf("🪙 %s: %s\n", ticker, balance_str);
    }
}
```

### Отправка токенов

```c
int wallet_send_tokens(basic_wallet_t *wallet,
                      const char *recipient_addr,
                      const char *ticker,
                      uint256_t amount,
                      const char *network) {

    // Проверка баланса
    uint256_t *current_balance = g_hash_table_lookup(wallet->balances, ticker);
    if (!current_balance || uint256_compare(amount, *current_balance) > 0) {
        fprintf(stderr, "❌ Недостаточно средств\n");
        return -1;
    }

    // Создание транзакции через Compose API
    compose_config_t config = {
        .net_name = network,
        .url_str = "http://rpc.cellframe.net",
        .port = 8081,
        .enc = false
    };

    json_object *tx = dap_tx_create_compose(
        network,           // сеть
        ticker,           // токен
        uint256_to_str(&amount), // сумма
        "0.001",         // комиссия
        recipient_addr,  // получатель
        &wallet->addr_from, // отправитель
        config.url_str,
        config.port,
        NULL
    );

    if (!tx) {
        fprintf(stderr, "❌ Ошибка создания транзакции\n");
        return -1;
    }

    // Подписание и отправка
    // ...

    // Обновление локального баланса
    uint256_sub(current_balance, current_balance, amount);

    return 0;
}
```

## 📊 История транзакций

### Структура транзакции

```c
typedef struct wallet_transaction {
    char tx_hash[128];               // Хэш транзакции
    char timestamp[32];              // Время транзакции
    char type[16];                   // Тип (send/receive)
    char ticker[16];                 // Токен
    uint256_t amount;                // Сумма
    char address[128];               // Адрес отправителя/получателя
    char network[32];                // Сеть
} wallet_transaction_t;
```

### Просмотр истории

```c
void wallet_print_history(basic_wallet_t *wallet) {
    printf("📜 История транзакций кошелька %s:\n", wallet->name);
    printf("%-20s %-10s %-8s %-15s %-25s %-15s\n",
           "Дата", "Тип", "Токен", "Сумма", "Адрес", "Хэш");

    for (GList *iter = wallet->transactions; iter; iter = iter->next) {
        wallet_transaction_t *tx = (wallet_transaction_t *)iter->data;

        char amount_str[32];
        uint256_to_str(&tx->amount, amount_str, sizeof(amount_str));

        printf("%-20s %-10s %-8s %-15s %-25s %-15.10s...\n",
               tx->timestamp, tx->type, tx->ticker, amount_str,
               tx->address, tx->tx_hash);
    }
}
```

## 🔧 Конфигурация

### Файл конфигурации (config/wallet.cfg)

```ini
[wallet]
# Основные настройки
default_network = KelVPN
auto_backup = true
backup_interval = 3600

# Настройки безопасности
encryption = true
key_derivation = argon2
password_min_length = 8

# Настройки сети
rpc_timeout = 30
max_retries = 3
confirmations_required = 6

# Настройки UI
show_fiat_values = true
fiat_currency = USD
update_rates_interval = 300
```

### Загрузка конфигурации

```c
typedef struct wallet_config {
    char *default_network;
    bool auto_backup;
    int backup_interval;
    bool encryption;
    char *key_derivation;
    int password_min_length;
    int rpc_timeout;
    int max_retries;
    int confirmations_required;
} wallet_config_t;

wallet_config_t *wallet_config_load(const char *filename) {
    wallet_config_t *config = calloc(1, sizeof(wallet_config_t));

    // Загрузка из INI файла
    // (упрощенная реализация)
    config->default_network = strdup("KelVPN");
    config->auto_backup = true;
    config->backup_interval = 3600;
    config->encryption = true;
    // ...

    return config;
}
```

## 🧪 Тестирование

### Unit-тесты

```c
// tests/test_wallet.c
#include "wallet.h"
#include "dap_test.h"

void test_wallet_creation() {
    basic_wallet_t *wallet = wallet_create("test_wallet", NULL);
    dap_assert(wallet != NULL, "Wallet creation should succeed");
    dap_assert(strlen(wallet->address) > 0, "Wallet should have address");
    dap_assert(wallet->private_key != NULL, "Wallet should have private key");

    wallet_free(wallet);
}

void test_wallet_save_load() {
    basic_wallet_t *original = wallet_create("test_wallet", "password");

    // Сохранение
    int save_result = wallet_save(original, "test_wallet.dat");
    dap_assert(save_result == 0, "Wallet save should succeed");

    // Загрузка
    basic_wallet_t *loaded = wallet_load("test_wallet.dat", "password");
    dap_assert(loaded != NULL, "Wallet load should succeed");
    dap_assert(strcmp(original->address, loaded->address) == 0,
               "Loaded wallet should have same address");

    wallet_free(original);
    wallet_free(loaded);

    // Очистка
    unlink("test_wallet.dat");
}

int main() {
    dap_print_module_name("Basic Wallet Tests");

    test_wallet_creation();
    test_wallet_save_load();

    return 0;
}
```

### Интеграционные тесты

```bash
#!/bin/bash
# tests/integration_test.sh

echo "Running wallet integration tests..."

# Создание тестового кошелька
./basic-wallet create test_wallet

# Проверка создания
if [ ! -f "test_wallet.dat" ]; then
    echo "Wallet file not created"
    exit 1
fi

# Проверка баланса
./basic-wallet balance test_wallet

# Тест отправки (с mock RPC)
# ...

echo "Integration tests passed!"
```

## 🔐 Безопасность

### Шифрование файла кошелька

```c
uint8_t *wallet_encrypt_data(uint8_t *data, size_t *size, const char *password) {
    // Генерация ключа из пароля
    uint8_t key[32];
    dap_enc_key_from_pass(password, key, sizeof(key));

    // Шифрование данных
    dap_enc_aes_key_t *aes_key = dap_enc_aes_key_from_data(key, sizeof(key));
    size_t encrypted_size = *size + 16; // Для padding
    uint8_t *encrypted = malloc(encrypted_size);

    dap_enc_aes_encrypt_cbc(aes_key, data, *size, encrypted);

    *size = encrypted_size;
    return encrypted;
}
```

### Валидация адресов

```c
bool wallet_validate_address(const char *address, const char *network) {
    // Проверка формата адреса
    if (strlen(address) < 30 || strlen(address) > 40) {
        return false;
    }

    // Проверка символов (base58)
    for (const char *p = address; *p; p++) {
        if (!strchr("123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz", *p)) {
            return false;
        }
    }

    // Проверка контрольной суммы
    // ...

    return true;
}
```

## 📊 Мониторинг и метрики

### Статистика кошелька

```c
typedef struct wallet_stats {
    int total_transactions;
    int successful_transactions;
    int failed_transactions;
    uint256_t total_sent;
    uint256_t total_received;
    time_t first_transaction;
    time_t last_transaction;
} wallet_stats_t;

wallet_stats_t *wallet_get_stats(basic_wallet_t *wallet) {
    wallet_stats_t *stats = calloc(1, sizeof(wallet_stats_t));

    for (GList *iter = wallet->transactions; iter; iter = iter->next) {
        wallet_transaction_t *tx = (wallet_transaction_t *)iter->data;

        stats->total_transactions++;

        if (strcmp(tx->type, "send") == 0) {
            uint256_add(&stats->total_sent, &stats->total_sent, &tx->amount);
        } else if (strcmp(tx->type, "receive") == 0) {
            uint256_add(&stats->total_received, &stats->total_received, &tx->amount);
        }

        // Обновление временных меток
        // ...
    }

    return stats;
}
```

## 🎨 Интерфейс командной строки

### Основные команды

```c
void print_usage() {
    printf("Basic Wallet for CellFrame DAP SDK\n");
    printf("Usage:\n");
    printf("  basic-wallet create <name> [password]    - Create new wallet\n");
    printf("  basic-wallet load <file> [password]      - Load wallet from file\n");
    printf("  basic-wallet balance <name>              - Show wallet balance\n");
    printf("  basic-wallet send <name> <address> <amount> <ticker> [network]\n");
    printf("                                           - Send tokens\n");
    printf("  basic-wallet history <name>              - Show transaction history\n");
    printf("  basic-wallet export <name> <file>        - Export wallet to file\n");
    printf("  basic-wallet import <file> <name>        - Import wallet from file\n");
    printf("  basic-wallet help                        - Show this help\n");
}
```

### Обработка аргументов командной строки

```c
int main(int argc, char *argv[]) {
    if (argc < 2) {
        print_usage();
        return 1;
    }

    const char *command = argv[1];

    if (strcmp(command, "create") == 0) {
        if (argc < 3) {
            fprintf(stderr, "Usage: basic-wallet create <name> [password]\n");
            return 1;
        }

        const char *password = (argc > 3) ? argv[3] : NULL;
        return cmd_create_wallet(argv[2], password);

    } else if (strcmp(command, "load") == 0) {
        // ...
    } else if (strcmp(command, "balance") == 0) {
        // ...
    }

    fprintf(stderr, "Unknown command: %s\n", command);
    print_usage();
    return 1;
}
```

## 🔧 Расширение функциональности

### Добавление поддержки NFT

```c
// Структура для NFT
typedef struct wallet_nft {
    char token_id[128];
    char collection[64];
    char metadata_uri[256];
    char image_uri[256];
    char description[512];
} wallet_nft_t;

// Методы для работы с NFT
GList *wallet_get_nfts(basic_wallet_t *wallet);
int wallet_send_nft(basic_wallet_t *wallet, const char *nft_id,
                   const char *recipient_addr, const char *network);
```

### Интеграция с exchanges

```c
// Структура для ордера на биржу
typedef struct exchange_order {
    char exchange_name[64];
    char pair[16];              // "KEL/CELL"
    char type[8];               // "buy"/"sell"
    uint256_t amount;
    uint256_t price;
    char status[16];            // "open"/"filled"/"cancelled"
} exchange_order_t;

// Методы для работы с биржами
int wallet_place_order(basic_wallet_t *wallet, exchange_order_t *order);
int wallet_cancel_order(basic_wallet_t *wallet, const char *order_id);
GList *wallet_get_orders(basic_wallet_t *wallet, const char *exchange);
```

### Многопользовательский режим

```c
// Структура для профиля пользователя
typedef struct user_profile {
    char username[64];
    basic_wallet_t *wallet;
    wallet_config_t *config;
    GList *sessions;            // Активные сессии
} user_profile_t;

// Методы для работы с профилями
user_profile_t *user_create(const char *username);
int user_add_wallet(user_profile_t *user, basic_wallet_t *wallet);
basic_wallet_t *user_get_wallet(user_profile_t *user, const char *wallet_name);
```

## 📚 Документация API

### Основные функции

- `wallet_create()` - Создание нового кошелька
- `wallet_load()` - Загрузка кошелька из файла
- `wallet_save()` - Сохранение кошелька в файл
- `wallet_get_balance()` - Получение баланса токена
- `wallet_send_tokens()` - Отправка токенов
- `wallet_get_history()` - Получение истории транзакций

### Детальная документация

См. [API документацию](docs/api.md) для подробного описания всех функций и структур данных.

## 🐛 Устранение неисправностей

### Распространенные проблемы

#### Проблема: "Failed to create wallet"
**Решение:** Проверьте права доступа к директории, убедитесь, что DAP SDK правильно инициализирован.

#### Проблема: "Invalid password"
**Решение:** Убедитесь, что пароль соответствует требованиям (минимум 8 символов).

#### Проблема: "Network connection failed"
**Решение:** Проверьте настройки сети и доступность RPC узла.

### Логирование

```bash
# Включение детального логирования
export DAP_LOG_LEVEL=DEBUG
./basic-wallet balance my_wallet

# Сохранение логов в файл
./basic-wallet balance my_wallet 2>&1 | tee wallet.log
```

## 🎯 Следующие шаги

1. **[Simple Transaction](../simple-transaction/)** - Изучение транзакций
2. **[Network Client](../network-client/)** - Работа с сетью
3. **[Advanced Wallet](../../advanced/advanced-wallet/)** - Продвинутые возможности

## 🤝 Вклад в развитие

Мы приветствуем вклад в развитие этого примера:

- **🐛 Исправления ошибок**
- **✨ Новые возможности**
- **📚 Улучшения документации**
- **🧪 Дополнительные тесты**

См. [CONTRIBUTING.md](https://github.com/cellframe/libdap/blob/master/CONTRIBUTING.md) для получения подробной информации.

---

## 📄 Лицензия

Этот пример распространяется под лицензией GNU General Public License v3.0.

**🎉 Готовы управлять своими токенами? Начните с создания первого кошелька!**



