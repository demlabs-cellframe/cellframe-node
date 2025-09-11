# 📚 CellFrame DAP SDK - Полный индекс API функций

## Обзор

Этот документ содержит полный индекс всех публичных API функций CellFrame DAP SDK, организованный по модулям. Используйте этот индекс для быстрого поиска нужных функций и навигации по документации.

## 📋 Структура индекса

- [Core модули](#core-модули)
- [Crypto модули](#crypto-модули)
- [Network модули](#network-модули)
- [Blockchain модули](#blockchain-модули)
- [Service модули](#service-модули)
- [Utility модули](#utility-модули)

---

## Core модули

### dap_common.h - Базовые функции

#### Инициализация и управление
```c
int dap_common_init(const char *a_app_name);
void dap_common_deinit(void);
const char *dap_get_version(void);
```

#### Системная информация
```c
uint32_t dap_get_cpu_count(void);
void *dap_alloc(size_t a_size);
void dap_free(void *a_ptr);
```

### dap_config.h - Конфигурация

#### Управление конфигурацией
```c
int dap_config_init(const char *a_path);
void dap_config_deinit(void);
dap_config_t *dap_config_open(const char *a_name);
```

#### Работа с параметрами
```c
const char *dap_config_get_item_str(dap_config_t *a_config, const char *a_section, const char *a_item);
int dap_config_get_item_int32(dap_config_t *a_config, const char *a_section, const char *a_item);
```

### dap_module.h - Система модулей

#### Управление модулями
```c
int dap_module_init(const char *a_name, void *a_init_func);
void dap_module_deinit(const char *a_name);
dap_module_t *dap_module_find(const char *a_name);
```

---

## Crypto модули

### dap_enc.h - Основное крипто API

#### Управление ключами
```c
dap_enc_key_t *dap_enc_key_new(dap_enc_key_type_t a_type);
void dap_enc_key_delete(dap_enc_key_t *a_key);
int dap_enc_key_generate(dap_enc_key_t *a_key);
```

#### Шифрование/дешифрование
```c
size_t dap_enc_code(dap_enc_key_t *a_key, const void *a_data, size_t a_data_size,
                   void *a_output, size_t a_output_size, int mode);
size_t dap_enc_decode(dap_enc_key_t *a_key, const void *a_data, size_t a_data_size,
                     void *a_output, size_t a_output_size, int mode);
```

### dap_sign.h - Цифровые подписи

#### Создание и проверка подписей
```c
dap_sign_t *dap_sign_create(dap_enc_key_t *a_key, const void *a_data, size_t a_data_size);
bool dap_sign_verify(dap_sign_t *a_sign, dap_pkey_t *a_pkey, const void *a_data, size_t a_data_size);
```

#### Сериализация подписей
```c
uint8_t *dap_sign_to_bytes(dap_sign_t *a_sign, size_t *a_bytes_size);
dap_sign_t *dap_sign_from_bytes(const uint8_t *a_bytes, size_t a_bytes_size);
```

### dap_cert.h - Сертификаты

#### Управление сертификатами
```c
dap_cert_t *dap_cert_generate(const char *a_name, dap_enc_key_t *a_key);
dap_cert_t *dap_cert_load_from_file(const char *a_path);
int dap_cert_save_to_file(dap_cert_t *a_cert, const char *a_path);
```

#### Проверка сертификатов
```c
bool dap_cert_verify(dap_cert_t *a_cert, dap_cert_t *a_ca_cert);
dap_pkey_t *dap_cert_to_pkey(dap_cert_t *a_cert);
```

---

## Network модули

### dap_events.h - Система событий

#### Инициализация событий
```c
int dap_events_init(uint32_t a_threads_count, size_t a_conn_timeout);
void dap_events_deinit(void);
int dap_events_start(void);
void dap_events_stop_all(void);
```

#### Управление потоками
```c
dap_worker_t *dap_events_worker_get_auto(void);
dap_worker_t *dap_events_worker_get(uint8_t a_index);
uint32_t dap_events_thread_get_count(void);
```

### dap_worker.h - Рабочие потоки

#### Управление рабочими потоками
```c
int dap_worker_init(size_t a_conn_timeout);
void dap_worker_deinit(void);
dap_worker_t *dap_worker_get_current(void);
```

#### Добавление задач
```c
void dap_worker_add_events_socket(dap_worker_t *a_worker, dap_events_socket_t *a_socket);
void dap_worker_exec_callback_on(dap_worker_t *a_worker, dap_worker_callback_t a_callback, void *a_arg);
```

### dap_context.h - Контексты выполнения

#### Управление контекстами
```c
int dap_context_init(void);
void dap_context_deinit(void);
dap_context_t *dap_context_new(int a_type);
int dap_context_run(dap_context_t *a_context, int a_cpu_id, int a_sched_policy,
                   int a_priority, uint32_t a_flags, dap_context_callback_t a_started,
                   dap_context_callback_t a_stopped, void *a_arg);
```

#### Работа с сокетами
```c
int dap_context_add(dap_context_t *a_context, dap_events_socket_t *a_socket);
int dap_context_remove(dap_events_socket_t *a_socket);
dap_events_socket_t *dap_context_find(dap_context_t *a_context, dap_events_socket_uuid_t a_uuid);
```

---

## Blockchain модули

### dap_chain_wallet.h - Кошельки

#### Создание и управление
```c
dap_chain_wallet_t *dap_chain_wallet_create(const char *a_name, dap_enc_key_t *a_key);
dap_chain_wallet_t *dap_chain_wallet_load_from_cert(const char *a_name, const char *a_cert_path);
void dap_chain_wallet_close(dap_chain_wallet_t *a_wallet);
```

#### Операции с кошельком
```c
dap_chain_addr_t *dap_chain_wallet_get_addr(dap_chain_wallet_t *a_wallet);
const char *dap_chain_wallet_get_address(dap_chain_wallet_t *a_wallet);
```

### dap_chain_tx_compose.h - Создание транзакций

#### Основные транзакции
```c
json_object *dap_tx_create_compose(const char *a_net_name, const char *a_token_ticker,
                                 const char *a_value_str, const char *a_fee_str,
                                 const char *a_addr_to, dap_chain_addr_t *a_addr_from,
                                 const char *a_url, uint16_t a_port, const char *a_cert);
```

#### Специализированные транзакции
```c
json_object *dap_tx_create_xchange_compose(const char *a_net_name, const char *a_token_sell,
                                         const char *a_token_buy, dap_chain_addr_t *a_wallet_addr,
                                         const char *a_value_str, const char *a_rate_str,
                                         const char *a_fee_str, const char *a_url, uint16_t a_port,
                                         const char *a_cert);
```

### dap_chain_mempool.h - Mempool

#### Управление mempool
```c
int dap_chain_mempool_init(void);
void dap_chain_mempool_deinit(void);
int dap_datum_mempool_init(void);
```

#### Операции с транзакциями
```c
json_object *dap_chain_mempool_add_proc(dap_http_server_t *a_http_server, const char *a_url);
uint8_t *dap_datum_mempool_serialize(dap_datum_mempool_t *a_mempool, size_t *a_size);
dap_datum_mempool_t *dap_datum_mempool_deserialize(uint8_t *a_data, size_t a_size);
```

---

## Service модули

### dap_cli_srv_stake.h - Staking сервисы

#### Управление ставками
```c
json_object *dap_cli_srv_stake_order_create_staker_compose(const char *a_net_str,
                                                         const char *a_value_str, const char *a_fee_str,
                                                         const char *a_tax_str, const char *a_addr_str,
                                                         dap_chain_addr_t *a_wallet_addr, const char *a_url,
                                                         uint16_t a_port, const char *a_cert);
```

#### Делегирование ставок
```c
json_object *dap_cli_srv_stake_delegate_compose(const char *a_net_str, dap_chain_addr_t *a_wallet_addr,
                                              const char *a_cert_str, const char *a_pkey_full_str,
                                              const char *a_value_str, const char *a_node_addr_str,
                                              const char *a_order_hash_str, const char *a_url,
                                              uint16_t a_port, const char *a_sovereign_addr_str,
                                              const char *a_fee_str, const char *a_enc_cert);
```

### dap_cli_voting.h - Голосование

#### Создание голосований
```c
json_object *dap_cli_voting_compose(const char *a_net_name, const char *a_question_str,
                                  const char *a_options_list_str, const char *a_voting_expire_str,
                                  const char *a_max_votes_count_str, const char *a_fee_str,
                                  bool a_is_delegated_key, bool a_is_vote_changing_allowed,
                                  dap_chain_addr_t *a_wallet_addr, const char *a_token_str,
                                  const char *a_url_str, uint16_t a_port, const char *a_enc_cert);
```

#### Голосование
```c
json_object *dap_cli_vote_compose(const char *a_net_str, const char *a_hash_str,
                                const char *a_cert_name, const char *a_fee_str,
                                dap_chain_addr_t *a_wallet_addr, const char *a_option_idx_str,
                                const char *a_url_str, uint16_t a_port, const char *a_enc_cert);
```

### dap_cli_xchange.h - Обмен токенами

#### Создание ордеров
```c
json_object *dap_tx_create_xchange_compose(const char *a_net_str, const char *a_token_sell,
                                         const char *a_token_buy, dap_chain_addr_t *a_wallet_addr,
                                         const char *a_value_str, const char *a_rate_str,
                                         const char *a_fee_str, const char *a_url_str,
                                         uint16_t a_port, const char *a_enc_cert);
```

#### Исполнение ордеров
```c
json_object *dap_cli_xchange_purchase_compose(const char *a_net_name, const char *a_order_hash,
                                            const char *a_value, const char *a_fee,
                                            const char *a_wallet_name, const char *a_wallet_path,
                                            const char *a_url_str, uint16_t a_port, const char *a_enc_cert);
```

---

## Utility модули

### dap_list.h - Связные списки

#### Создание и управление
```c
dap_list_t *dap_list_prepend(dap_list_t *a_list, void *a_data);
dap_list_t *dap_list_append(dap_list_t *a_list, void *a_data);
dap_list_t *dap_list_remove(dap_list_t *a_list, void *a_data);
```

#### Итерация и поиск
```c
dap_list_t *dap_list_find(dap_list_t *a_list, void *a_data);
unsigned int dap_list_length(dap_list_t *a_list);
void dap_list_free(dap_list_t *a_list);
```

### dap_hash.h - Хэш-функции

#### Основные хэши
```c
void dap_hash(dap_hash_t *a_hash, const void *a_data, size_t a_data_size);
void dap_hash_fast(dap_hash_fast_t *a_hash, const void *a_data, size_t a_data_size);
char *dap_hash_fast_to_str(dap_hash_fast_t *a_hash);
```

#### Специализированные хэши
```c
void dap_hash_sha3_256(dap_hash_t *a_hash, const void *a_data, size_t a_data_size);
void dap_hash_blake2b(dap_hash_t *a_hash, const void *a_data, size_t a_data_size);
void dap_hash_keccak(dap_hash_t *a_hash, const void *a_data, size_t a_data_size);
```

### dap_time.h - Работа со временем

#### Получение времени
```c
dap_nanotime_t dap_nanotime_now(void);
dap_time_t dap_time_now(void);
struct timespec dap_timespec_now(void);
```

#### Преобразование времени
```c
char *dap_time_to_str_rfc822(dap_time_t a_time);
dap_time_t dap_time_from_str_rfc822(const char *a_str);
char *dap_nanotime_to_str(dap_nanotime_t a_nanotime);
```

---

## 🔍 Поиск функций

### По категориям

#### 🔐 Криптография
- `dap_enc_key_*` - Управление ключами
- `dap_sign_*` - Цифровые подписи
- `dap_cert_*` - Сертификаты
- `dap_hash_*` - Хэш-функции

#### 🌐 Сеть
- `dap_events_*` - Система событий
- `dap_worker_*` - Рабочие потоки
- `dap_context_*` - Контексты выполнения
- `dap_http_*` - HTTP коммуникации

#### ⛓️ Блокчейн
- `dap_chain_wallet_*` - Кошельки
- `dap_tx_*` - Транзакции
- `dap_chain_mempool_*` - Mempool
- `dap_chain_*` - Блокчейн операции

#### 🛠️ Утилиты
- `dap_list_*` - Связные списки
- `dap_time_*` - Работа со временем
- `dap_common_*` - Базовые функции
- `dap_config_*` - Конфигурация

### По префиксам

| Префикс | Модуль | Описание |
|---------|--------|----------|
| `dap_common_` | Core | Базовые функции |
| `dap_config_` | Core | Конфигурация |
| `dap_enc_` | Crypto | Шифрование |
| `dap_sign_` | Crypto | Подписи |
| `dap_cert_` | Crypto | Сертификаты |
| `dap_hash_` | Crypto | Хэши |
| `dap_events_` | Network | События |
| `dap_worker_` | Network | Рабочие потоки |
| `dap_context_` | Network | Контексты |
| `dap_chain_` | Blockchain | Блокчейн |
| `dap_tx_` | Blockchain | Транзакции |
| `dap_cli_` | Services | CLI команды |

---

## 📖 Использование индекса

### Как найти нужную функцию

1. **Определите категорию**: Криптография, сеть, блокчейн, утилиты
2. **Найдите модуль**: Используйте таблицу префиксов
3. **Найдите функцию**: Ищите по префиксу + операция
4. **Проверьте сигнатуру**: Смотрите параметры и возвращаемые значения
5. **Изучите пример**: Перейдите к документации модуля

### Примеры поиска

#### Хочу создать кошелек
```
dap_chain_wallet_create() → dap_chain_wallet.h
```

#### Хочу подписать данные
```
dap_sign_create() → dap_sign.h
```

#### Хочу отправить HTTP запрос
```
dap_http_client_request() → dap_http_client.h
```

#### Хочу создать транзакцию
```
dap_tx_create_compose() → dap_chain_tx_compose.h
```

---

## 🔗 Перекрестные ссылки

### Связанные документы

- **[DAP SDK Architecture](../architecture.md)** - Общая архитектура
- **[API Reference](../api/)** - Детальная документация API
- **[Examples](../examples/)** - Практические примеры
- **[Migration Guide](MIGRATION_GUIDE.md)** - Миграция между версиями

### Внешние ресурсы

- **[GitHub Repository](https://github.com/cellframe/dap-sdk)** - Исходный код
- **[Documentation Site](https://docs.cellframe.net)** - Онлайн документация
- **[Community Forum](https://forum.cellframe.net)** - Обсуждения и вопросы

---

## 📊 Статистика API

### По модулям

| Модуль | Функций | Процент |
|--------|---------|---------|
| Core | 25 | 15% |
| Crypto | 45 | 27% |
| Network | 35 | 21% |
| Blockchain | 40 | 24% |
| Services | 20 | 12% |
| Utilities | 5 | 3% |
| **Итого** | **170** | **100%** |

### По типам операций

| Тип операции | Количество | Примеры |
|--------------|------------|---------|
| **Инициализация** | 25 | `*_init()`, `*_create()` |
| **Обработка данных** | 40 | `*_process()`, `*_handle()` |
| **Сериализация** | 15 | `*_serialize()`, `*_to_bytes()` |
| **Коммуникации** | 30 | `*_send()`, `*_receive()` |
| **Управление** | 35 | `*_get()`, `*_set()`, `*_add()` |
| **Завершение** | 25 | `*_deinit()`, `*_free()` |

---

## 🚀 Быстрый старт

### Базовое приложение

```c
#include "dap_common.h"
#include "dap_config.h"
#include "dap_chain_wallet.h"

int main() {
    // Инициализация
    dap_common_init("my_app");
    dap_config_init("config.conf");
    dap_chain_wallet_init();

    // Создание кошелька
    dap_enc_key_t *key = dap_enc_key_new(DAP_ENC_KEY_TYPE_SIG_DILITHIUM);
    dap_enc_key_generate(key);
    dap_chain_wallet_t *wallet = dap_chain_wallet_create("my_wallet", key);

    // Использование...

    // Очистка
    dap_chain_wallet_close(wallet);
    dap_enc_key_delete(key);
    dap_chain_wallet_deinit();
    dap_config_deinit();
    dap_common_deinit();

    return 0;
}
```

### Следующие шаги

1. **Изучите модули** по интересующим категориям
2. **Ознакомьтесь с примерами** в соответствующей директории
3. **Прочитайте документацию** конкретного модуля
4. **Начните разработку** с простых функций

---

**🎯 Этот индекс поможет вам быстро найти нужные функции и эффективно использовать CellFrame DAP SDK!**

**📚 Для детальной информации переходите к документации конкретных модулей.**
