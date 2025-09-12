# 🔐 Руководство по безопасности CellFrame DAP SDK

Это всеобъемлющее руководство по обеспечению безопасности приложений, разработанных с использованием CellFrame DAP SDK. Безопасность является фундаментальным аспектом блокчейн технологий и криптовалютных систем.

## 📋 Содержание

- [Введение в безопасность](#введение-в-безопасность)
- [Криптографическая безопасность](#криптографическая-безопасность)
- [Безопасность приложений](#безопасность-приложений)
- [Сетевая безопасность](#сетевая-безопасность)
- [Безопасность хранения данных](#безопасность-хранения-данных)
- [Аутентификация и авторизация](#аутентификация-и-авторизация)
- [Защита от распространенных атак](#защита-от-распространенных-атак)
- [Аудит безопасности](#аудит-безопасности)
- [Мониторинг и реагирование](#мониторинг-и-реагирование)
- [Лучшие практики](#лучшие-практики)

## 🔐 Введение в безопасность

### Основные принципы безопасности

**CIA Triad** - фундаментальная модель безопасности:
- **Confidentiality (Конфиденциальность)** - защита информации от несанкционированного доступа
- **Integrity (Целостность)** - обеспечение неизменности данных
- **Availability (Доступность)** - обеспечение доступности системы

### Специфика блокчейн безопасности

```c
// Блокчейн-специфичные угрозы
typedef enum blockchain_threats {
    THREAT_DOUBLE_SPENDING,      // Двойная трата
    THREAT_51_PERCENT_ATTACK,    // Атака 51%
    THREAT_SYBIL_ATTACK,         // Sybil атака
    THREAT_ECLIPSE_ATTACK,       // Eclipse атака
    THREAT_REPLAY_ATTACK,        // Replay атака
    THREAT_FRONT_RUNNING,        // Front-running
    THREAT_SANDBOX_ESCAPE,       // Escape из sandbox
    THREAT_SUPPLY_CHAIN_ATTACK,  // Атака цепочки поставок
} blockchain_threats_t;
```

### Zero Trust модель

```c
// Принципы Zero Trust
#define ZERO_TRUST_PRINCIPLES \
    "Never trust, always verify", \
    "Assume breach", \
    "Verify explicitly", \
    "Use least privilege", \
    "Log everything"

// Реализация в коде
bool zero_trust_verify(dap_stream_node_addr_t *node_addr,
                      dap_sign_t *signature,
                      const void *data, size_t data_size) {
    // Всегда проверять, никогда не доверять
    if (!node_addr || !signature || !data) {
        return false;
    }

    // Явная верификация
    return dap_sign_verify(signature, data, data_size);
}
```

## 🔑 Криптографическая безопасность

### Управление ключами

#### Генерация ключей

```c
// Безопасная генерация ключей
dap_enc_key_t *generate_secure_key(dap_enc_key_type_t key_type,
                                  size_t key_size) {
    // Использование криптографически безопасного RNG
    dap_enc_key_t *key = dap_enc_key_new_generate(key_type, key_size, NULL);

    // Валидация ключа
    if (!dap_enc_key_is_valid(key)) {
        dap_enc_key_delete(key);
        return NULL;
    }

    return key;
}
```

#### Безопасное хранение ключей

```c
// Шифрование ключей с использованием мастер-пароля
typedef struct secure_key_storage {
    uint8_t salt[32];           // Salt для PBKDF2
    uint8_t iv[16];             // IV для AES
    uint8_t encrypted_key[64];  // Зашифрованный ключ
    uint32_t iterations;        // Количество итераций PBKDF2
} secure_key_storage_t;

bool store_key_securely(dap_enc_key_t *key, const char *password,
                       secure_key_storage_t *storage) {

    // Генерация salt
    if (RAND_bytes(storage->salt, sizeof(storage->salt)) != 1) {
        return false;
    }

    // PBKDF2 для генерации ключа шифрования
    uint8_t derived_key[32];
    if (!PKCS5_PBKDF2_HMAC(password, strlen(password),
                          storage->salt, sizeof(storage->salt),
                          storage->iterations, EVP_sha256(),
                          sizeof(derived_key), derived_key)) {
        return false;
    }

    // Шифрование приватного ключа
    // ...

    return true;
}
```

#### Ротация ключей

```c
// Автоматическая ротация ключей
typedef struct key_rotation_policy {
    time_t rotation_interval;   // Интервал ротации
    time_t last_rotation;       // Последняя ротация
    size_t max_keys;           // Максимум активных ключей
    bool emergency_rotation;   // Экстренная ротация
} key_rotation_policy_t;

bool should_rotate_keys(key_rotation_policy_t *policy) {
    time_t now = time(NULL);
    return (now - policy->last_rotation) > policy->rotation_interval ||
           policy->emergency_rotation;
}

int rotate_keys(dap_enc_key_t **old_key, dap_enc_key_t **new_key) {
    // Генерация нового ключа
    *new_key = generate_secure_key(DAP_ENC_KEY_TYPE_SIG_ECDSA, 256);
    if (!*new_key) return -1;

    // Переходный период для использования обоих ключей
    // ...

    // Безопасное удаление старого ключа
    dap_enc_key_delete(*old_key);
    *old_key = *new_key;

    return 0;
}
```

### Цифровые подписи

#### Создание подписей

```c
// Безопасное создание подписи
dap_sign_t *create_secure_signature(dap_enc_key_t *private_key,
                                  const void *data, size_t data_size) {

    if (!private_key || !data || data_size == 0) {
        return NULL;
    }

    // Вычисление хэша данных
    uint8_t hash[32];
    if (dap_hash_fast(data, data_size, hash) != 0) {
        return NULL;
    }

    // Создание подписи
    return dap_sign_create(private_key, hash, sizeof(hash));
}
```

#### Верификация подписей

```c
// Комплексная верификация подписи
typedef struct signature_verification_result {
    bool is_valid;
    const char *error_message;
    time_t verification_time;
    const char *algorithm_used;
} signature_verification_result_t;

signature_verification_result_t verify_signature_comprehensive(
    dap_sign_t *signature, const void *data, size_t data_size,
    dap_pkey_t *public_key) {

    signature_verification_result_t result = {0};

    result.verification_time = time(NULL);

    // Проверка входных параметров
    if (!signature || !data || !public_key) {
        result.error_message = "Invalid parameters";
        return result;
    }

    // Верификация подписи
    result.is_valid = dap_sign_verify(signature, data, data_size);

    // Определение алгоритма
    result.algorithm_used = dap_sign_get_algorithm_name(signature);

    if (!result.is_valid) {
        result.error_message = "Signature verification failed";
    }

    return result;
}
```

## 🛡️ Безопасность приложений

### Input Validation

#### Валидация входных данных

```c
// Комплексная валидация входных данных
typedef struct input_validation_rules {
    size_t min_length;
    size_t max_length;
    const char *allowed_chars;
    bool allow_null;
    bool trim_whitespace;
} input_validation_rules_t;

bool validate_input_string(const char *input,
                          input_validation_rules_t *rules) {

    if (!input && !rules->allow_null) {
        return false;
    }

    if (!input) return true;

    size_t length = strlen(input);

    // Проверка длины
    if (length < rules->min_length || length > rules->max_length) {
        return false;
    }

    // Проверка символов
    if (rules->allowed_chars) {
        for (size_t i = 0; i < length; i++) {
            if (!strchr(rules->allowed_chars, input[i])) {
                return false;
            }
        }
    }

    return true;
}

// Применение валидации
bool process_user_input(const char *user_input) {
    input_validation_rules_t rules = {
        .min_length = 1,
        .max_length = 256,
        .allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-.",
        .allow_null = false,
        .trim_whitespace = true
    };

    if (!validate_input_string(user_input, &rules)) {
        log_security_event("Invalid user input detected", user_input);
        return false;
    }

    return true;
}
```

#### Защита от SQL Injection

```c
// Безопасные запросы к базе данных
typedef struct safe_query_builder {
    GString *query;
    GPtrArray *parameters;
} safe_query_builder_t;

safe_query_builder_t *query_builder_new(const char *base_query) {
    safe_query_builder_t *builder = g_new(safe_query_builder_t, 1);
    builder->query = g_string_new(base_query);
    builder->parameters = g_ptr_array_new_with_free_func(g_free);
    return builder;
}

void query_builder_add_param(safe_query_builder_t *builder,
                           const char *param_name, const char *param_value) {

    // Экранирование специальных символов
    char *escaped_value = g_strescape(param_value, NULL);

    // Добавление параметра
    g_string_append_printf(builder->query, " %s = '%s'",
                          param_name, escaped_value);

    g_free(escaped_value);
}

char *query_builder_get_query(safe_query_builder_t *builder) {
    return g_string_free(builder->query, FALSE);
}
```

### Memory Safety

#### Безопасное управление памятью

```c
// RAII паттерн для C
typedef struct safe_buffer {
    uint8_t *data;
    size_t size;
    size_t capacity;
    bool owns_memory;
} safe_buffer_t;

safe_buffer_t *safe_buffer_new(size_t initial_capacity) {
    safe_buffer_t *buffer = calloc(1, sizeof(safe_buffer_t));
    if (!buffer) return NULL;

    buffer->data = calloc(1, initial_capacity);
    if (!buffer->data) {
        free(buffer);
        return NULL;
    }

    buffer->size = 0;
    buffer->capacity = initial_capacity;
    buffer->owns_memory = true;

    return buffer;
}

void safe_buffer_free(safe_buffer_t *buffer) {
    if (!buffer) return;

    if (buffer->owns_memory && buffer->data) {
        // Безопасная очистка чувствительных данных
        memset(buffer->data, 0, buffer->capacity);
        free(buffer->data);
    }

    free(buffer);
}

// Использование
void process_sensitive_data() {
    safe_buffer_t *buffer = safe_buffer_new(1024);
    if (!buffer) return;

    // Работа с данными
    // ...

    // Автоматическая безопасная очистка
    safe_buffer_free(buffer);
}
```

#### Защита от buffer overflow

```c
// Безопасные строковые операции
bool safe_strncpy(char *dest, size_t dest_size,
                 const char *src, size_t src_size) {

    if (!dest || !src || dest_size == 0) {
        return false;
    }

    size_t copy_size = (src_size < dest_size) ? src_size : dest_size - 1;
    memcpy(dest, src, copy_size);
    dest[copy_size] = '\0';

    return true;
}

// Безопасная конкатенация строк
bool safe_strncat(char *dest, size_t dest_size,
                 const char *src, size_t src_size) {

    size_t dest_len = strnlen(dest, dest_size);
    if (dest_len >= dest_size) {
        return false; // dest уже переполнен
    }

    size_t remaining = dest_size - dest_len;
    size_t copy_size = (src_size < remaining) ? src_size : remaining - 1;

    memcpy(dest + dest_len, src, copy_size);
    dest[dest_len + copy_size] = '\0';

    return true;
}
```

## 🌐 Сетевая безопасность

### TLS/SSL шифрование

#### Настройка защищенного соединения

```c
// Конфигурация TLS
typedef struct tls_config {
    const char *certificate_file;
    const char *private_key_file;
    const char *ca_certificate_file;
    const char *cipher_list;
    bool require_client_cert;
    int min_tls_version;
    bool enable_hsts;
} tls_config_t;

dap_ssl_context_t *create_secure_ssl_context(tls_config_t *config) {

    // Инициализация OpenSSL
    SSL_library_init();
    OpenSSL_add_all_algorithms();
    SSL_load_error_strings();

    // Создание контекста
    const SSL_METHOD *method = TLS_server_method();
    SSL_CTX *ctx = SSL_CTX_new(method);

    if (!ctx) {
        log_ssl_error("Failed to create SSL context");
        return NULL;
    }

    // Загрузка сертификата
    if (SSL_CTX_use_certificate_file(ctx, config->certificate_file,
                                   SSL_FILETYPE_PEM) <= 0) {
        log_ssl_error("Failed to load certificate");
        SSL_CTX_free(ctx);
        return NULL;
    }

    // Загрузка приватного ключа
    if (SSL_CTX_use_PrivateKey_file(ctx, config->private_key_file,
                                  SSL_FILETYPE_PEM) <= 0) {
        log_ssl_error("Failed to load private key");
        SSL_CTX_free(ctx);
        return NULL;
    }

    // Настройка шифров
    if (!SSL_CTX_set_cipher_list(ctx, config->cipher_list)) {
        log_ssl_error("Failed to set cipher list");
        SSL_CTX_free(ctx);
        return NULL;
    }

    // Настройка минимальной версии TLS
    SSL_CTX_set_min_proto_version(ctx, config->min_tls_version);

    return ctx;
}
```

#### Защита от сетевых атак

```c
// Rate limiting
typedef struct rate_limiter {
    uint32_t max_requests_per_minute;
    uint32_t current_requests;
    time_t window_start;
    GHashTable *client_requests; // IP -> request_count
} rate_limiter_t;

bool check_rate_limit(rate_limiter_t *limiter,
                     const char *client_ip,
                     time_t current_time) {

    // Проверка окна времени
    if (current_time - limiter->window_start >= 60) {
        // Сброс счетчиков
        limiter->current_requests = 0;
        limiter->window_start = current_time;
        g_hash_table_remove_all(limiter->client_requests);
    }

    // Проверка индивидуального лимита клиента
    uint32_t *client_count = g_hash_table_lookup(limiter->client_requests,
                                                client_ip);
    if (!client_count) {
        client_count = g_new(uint32_t, 1);
        *client_count = 0;
        g_hash_table_insert(limiter->client_requests, g_strdup(client_ip),
                           client_count);
    }

    if (*client_count >= limiter->max_requests_per_minute) {
        return false; // Превышен лимит
    }

    (*client_count)++;
    limiter->current_requests++;

    return limiter->current_requests < limiter->max_requests_per_minute;
}
```

#### Защита от DDoS

```c
// DDoS mitigation
typedef struct ddos_protection {
    rate_limiter_t *rate_limiter;
    GHashTable *blacklist;       // Заблокированные IP
    GHashTable *whitelist;       // Доверенные IP
    uint32_t max_connections;
    uint32_t current_connections;
    pthread_mutex_t mutex;
} ddos_protection_t;

connection_result_t check_connection_allowed(ddos_protection_t *ddos,
                                          const char *client_ip,
                                          const char *user_agent) {

    pthread_mutex_lock(&ddos->mutex);

    // Проверка blacklist
    if (g_hash_table_contains(ddos->blacklist, client_ip)) {
        pthread_mutex_unlock(&ddos->mutex);
        return CONNECTION_BLOCKED;
    }

    // Проверка whitelist
    if (g_hash_table_contains(ddos->whitelist, client_ip)) {
        pthread_mutex_unlock(&ddos->mutex);
        return CONNECTION_ALLOWED;
    }

    // Проверка rate limit
    if (!check_rate_limit(ddos->rate_limiter, client_ip, time(NULL))) {
        // Автоматическое добавление в blacklist
        g_hash_table_add(ddos->blacklist, g_strdup(client_ip));
        pthread_mutex_unlock(&ddos->mutex);
        return CONNECTION_BLOCKED;
    }

    // Проверка количества соединений
    if (ddos->current_connections >= ddos->max_connections) {
        pthread_mutex_unlock(&ddos->mutex);
        return CONNECTION_REJECTED;
    }

    ddos->current_connections++;
    pthread_mutex_unlock(&ddos->mutex);

    return CONNECTION_ALLOWED;
}
```

## 💾 Безопасность хранения данных

### Шифрование данных

```c
// Шифрование базы данных
typedef struct encrypted_database {
    const char *db_path;
    uint8_t master_key[32];
    uint8_t salt[16];
    bool use_hardware_encryption;
} encrypted_database_t;

int encrypt_database_record(const void *plaintext, size_t plaintext_size,
                           void **ciphertext, size_t *ciphertext_size,
                           encrypted_database_t *db) {

    // Генерация IV
    uint8_t iv[16];
    if (RAND_bytes(iv, sizeof(iv)) != 1) {
        return -1;
    }

    // Шифрование AES-256-GCM
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) return -1;

    if (EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(),
                          NULL, db->master_key, iv) != 1) {
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }

    *ciphertext_size = plaintext_size + 16 + 12; // data + tag + iv
    *ciphertext = malloc(*ciphertext_size);
    if (!*ciphertext) {
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }

    int len;
    if (EVP_EncryptUpdate(ctx, *ciphertext, &len,
                         plaintext, plaintext_size) != 1) {
        free(*ciphertext);
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }

    if (EVP_EncryptFinal_ex(ctx, *ciphertext + len, &len) != 1) {
        free(*ciphertext);
        EVP_CIPHER_CTX_free(ctx);
        return -1;
    }

    EVP_CIPHER_CTX_free(ctx);
    return 0;
}
```

### Secure Delete

```c
// Безопасное удаление файлов
int secure_delete_file(const char *filepath, int passes) {
    struct stat st;

    if (stat(filepath, &st) != 0) {
        return -1; // Файл не существует
    }

    int fd = open(filepath, O_WRONLY);
    if (fd == -1) {
        return -1;
    }

    // Несколько проходов перезаписи
    for (int pass = 0; pass < passes; pass++) {
        uint8_t pattern;

        switch (pass) {
            case 0: pattern = 0x00; break; // Все нули
            case 1: pattern = 0xFF; break; // Все единицы
            default: pattern = rand() % 256; break; // Случайные данные
        }

        if (lseek(fd, 0, SEEK_SET) == -1) {
            close(fd);
            return -1;
        }

        // Перезапись файла
        for (off_t offset = 0; offset < st.st_size; ) {
            size_t chunk_size = (st.st_size - offset > 4096) ?
                               4096 : st.st_size - offset;

            uint8_t buffer[4096];
            memset(buffer, pattern, chunk_size);

            if (write(fd, buffer, chunk_size) != chunk_size) {
                close(fd);
                return -1;
            }

            offset += chunk_size;
        }

        // Синхронизация
        if (fsync(fd) != 0) {
            close(fd);
            return -1;
        }
    }

    close(fd);

    // Физическое удаление
    if (unlink(filepath) != 0) {
        return -1;
    }

    return 0;
}
```

## 🔒 Аутентификация и авторизация

### Multi-factor Authentication

```c
// MFA система
typedef struct mfa_context {
    const char *username;
    uint8_t secret[32];         // TOTP secret
    time_t last_auth_time;
    uint32_t failed_attempts;
    bool is_locked;
    time_t lock_until;
} mfa_context_t;

typedef enum mfa_result {
    MFA_SUCCESS,
    MFA_INVALID_CODE,
    MFA_EXPIRED_CODE,
    MFA_ACCOUNT_LOCKED,
    MFA_SYSTEM_ERROR
} mfa_result_t;

mfa_result_t verify_totp_code(mfa_context_t *context,
                             const char *user_code,
                             time_t current_time) {

    if (context->is_locked) {
        if (current_time < context->lock_until) {
            return MFA_ACCOUNT_LOCKED;
        } else {
            // Сброс блокировки
            context->is_locked = false;
            context->failed_attempts = 0;
        }
    }

    // Генерация ожидаемого кода
    uint32_t expected_code = generate_totp_code(context->secret,
                                               current_time / 30);

    char expected_str[7];
    snprintf(expected_str, sizeof(expected_str), "%06u", expected_code);

    if (strcmp(user_code, expected_str) == 0) {
        context->last_auth_time = current_time;
        context->failed_attempts = 0;
        return MFA_SUCCESS;
    }

    // Неудачная попытка
    context->failed_attempts++;

    if (context->failed_attempts >= 5) {
        context->is_locked = true;
        context->lock_until = current_time + 900; // 15 минут
    }

    return MFA_INVALID_CODE;
}
```

### Role-Based Access Control

```c
// RBAC система
typedef enum user_role {
    ROLE_GUEST,
    ROLE_USER,
    ROLE_MODERATOR,
    ROLE_ADMIN,
    ROLE_SUPER_ADMIN
} user_role_t;

typedef struct permission {
    const char *resource;
    const char *action;
    user_role_t min_role;
} permission_t;

// Таблица разрешений
static const permission_t permissions[] = {
    {"wallet", "read", ROLE_USER},
    {"wallet", "send", ROLE_USER},
    {"wallet", "create", ROLE_USER},
    {"network", "read", ROLE_GUEST},
    {"network", "configure", ROLE_ADMIN},
    {"system", "shutdown", ROLE_SUPER_ADMIN},
    {NULL, NULL, 0}
};

bool check_permission(user_role_t user_role,
                     const char *resource,
                     const char *action) {

    for (const permission_t *perm = permissions; perm->resource; perm++) {
        if (strcmp(perm->resource, resource) == 0 &&
            strcmp(perm->action, action) == 0) {

            return user_role >= perm->min_role;
        }
    }

    return false; // Разрешение не найдено
}
```

## 🛡️ Защита от распространенных атак

### Защита от SQL Injection

```c
// Параметризованные запросы
typedef struct safe_sql_query {
    GString *query_template;
    GPtrArray *parameters;
    GHashTable *param_types;
} safe_sql_query_t;

safe_sql_query_t *safe_sql_query_new(const char *template) {
    safe_sql_query_t *query = g_new(safe_sql_query_t, 1);
    query->query_template = g_string_new(template);
    query->parameters = g_ptr_array_new();
    query->param_types = g_hash_table_new(g_str_hash, g_str_equal);
    return query;
}

void safe_sql_query_add_param(safe_sql_query_t *query,
                             const char *name, const void *value,
                             const char *type) {

    g_ptr_array_add(query->parameters, g_strdup(name));
    g_hash_table_insert(query->param_types, g_strdup(name), g_strdup(type));

    // Замена плейсхолдера на безопасный параметр
    char *placeholder = g_strdup_printf(":%s", name);
    g_string_replace(query->query_template, placeholder, "?", 0);
    g_free(placeholder);
}

char *safe_sql_query_execute(safe_sql_query_t *query,
                           sqlite3 *db) {

    sqlite3_stmt *stmt;
    const char *sql = query->query_template->str;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK) {
        return NULL;
    }

    // Привязка параметров
    for (guint i = 0; i < query->parameters->len; i++) {
        const char *param_name = g_ptr_array_index(query->parameters, i);
        const char *param_type = g_hash_table_lookup(query->param_types, param_name);

        // Безопасная привязка в зависимости от типа
        // ...
    }

    // Выполнение запроса
    // ...

    sqlite3_finalize(stmt);
    return result;
}
```

### Защита от XSS

```c
// HTML escaping
char *html_escape(const char *input) {
    GString *escaped = g_string_new("");

    for (const char *p = input; *p; p++) {
        switch (*p) {
            case '<': g_string_append(escaped, "&lt;"); break;
            case '>': g_string_append(escaped, "&gt;"); break;
            case '&': g_string_append(escaped, "&amp;"); break;
            case '"': g_string_append(escaped, "&quot;"); break;
            case '\'': g_string_append(escaped, "&#x27;"); break;
            case '/': g_string_append(escaped, "&#x2F;"); break;
            default: g_string_append_c(escaped, *p); break;
        }
    }

    return g_string_free(escaped, FALSE);
}

// CSP (Content Security Policy) headers
const char *get_csp_header() {
    return "default-src 'self'; "
           "script-src 'self' 'unsafe-inline'; "
           "style-src 'self' 'unsafe-inline'; "
           "img-src 'self' data: https:; "
           "font-src 'self'; "
           "connect-src 'self'; "
           "media-src 'self'; "
           "object-src 'none'; "
           "frame-ancestors 'none';";
}

// Безопасная генерация HTML
char *generate_safe_html(const char *user_input) {
    char *escaped = html_escape(user_input);

    char *html = g_markup_printf_escaped(
        "<div class=\"user-content\">%s</div>",
        escaped
    );

    g_free(escaped);
    return html;
}
```

### Защита от CSRF

```c
// CSRF токены
typedef struct csrf_protection {
    GHashTable *tokens;         // session_id -> token
    time_t token_lifetime;      // Время жизни токена
    pthread_mutex_t mutex;
} csrf_protection_t;

char *generate_csrf_token(csrf_protection_t *csrf,
                         const char *session_id) {

    pthread_mutex_lock(&csrf->mutex);

    // Генерация случайного токена
    uint8_t random_bytes[32];
    if (RAND_bytes(random_bytes, sizeof(random_bytes)) != 1) {
        pthread_mutex_unlock(&csrf->mutex);
        return NULL;
    }

    char *token = g_base64_encode(random_bytes, sizeof(random_bytes));

    // Сохранение токена
    g_hash_table_insert(csrf->tokens,
                       g_strdup(session_id),
                       g_strdup(token));

    pthread_mutex_unlock(&csrf->mutex);
    return token;
}

bool validate_csrf_token(csrf_protection_t *csrf,
                        const char *session_id,
                        const char *token) {

    pthread_mutex_lock(&csrf->mutex);

    const char *stored_token = g_hash_table_lookup(csrf->tokens, session_id);

    bool is_valid = stored_token && strcmp(stored_token, token) == 0;

    if (is_valid) {
        // Одноразовый токен - удаляем после использования
        g_hash_table_remove(csrf->tokens, session_id);
    }

    pthread_mutex_unlock(&csrf->mutex);
    return is_valid;
}
```

## 🔍 Аудит безопасности

### Логирование событий безопасности

```c
// Структурированное логирование безопасности
typedef struct security_event {
    time_t timestamp;
    const char *event_type;
    const char *severity;
    const char *source_ip;
    const char *user_id;
    const char *resource;
    const char *action;
    const char *result;
    const char *details;
} security_event_t;

void log_security_event(security_event_t *event) {
    // JSON формат для структурированного логирования
    printf("{\"timestamp\":%ld,\"event_type\":\"%s\",\"severity\":\"%s\","
           "\"source_ip\":\"%s\",\"user_id\":\"%s\",\"resource\":\"%s\","
           "\"action\":\"%s\",\"result\":\"%s\",\"details\":\"%s\"}\n",
           event->timestamp, event->event_type, event->severity,
           event->source_ip, event->user_id, event->resource,
           event->action, event->result, event->details);

    // Также пишем в syslog
    syslog(LOG_AUTH | LOG_INFO, "Security event: %s from %s",
           event->event_type, event->source_ip);
}

// Макросы для удобного логирования
#define LOG_AUTH_SUCCESS(user, ip, action) \
    do { \
        security_event_t event = { \
            .timestamp = time(NULL), \
            .event_type = "authentication", \
            .severity = "info", \
            .source_ip = ip, \
            .user_id = user, \
            .action = action, \
            .result = "success" \
        }; \
        log_security_event(&event); \
    } while(0)

#define LOG_AUTH_FAILURE(user, ip, reason) \
    do { \
        security_event_t event = { \
            .timestamp = time(NULL), \
            .event_type = "authentication", \
            .severity = "warning", \
            .source_ip = ip, \
            .user_id = user, \
            .action = "login", \
            .result = "failure", \
            .details = reason \
        }; \
        log_security_event(&event); \
    } while(0)
```

### Автоматический аудит

```c
// Сканер уязвимостей
typedef struct vulnerability_scan {
    const char *target;
    GPtrArray *vulnerabilities;
    time_t scan_start;
    time_t scan_end;
    bool scan_completed;
} vulnerability_scan_t;

typedef struct vulnerability {
    const char *cve_id;
    const char *severity;
    const char *description;
    const char *affected_component;
    const char *remediation;
    bool exploitable;
} vulnerability_t;

vulnerability_scan_t *run_security_audit(const char *target_system) {
    vulnerability_scan_t *scan = g_new(vulnerability_scan_t, 1);
    scan->target = g_strdup(target_system);
    scan->vulnerabilities = g_ptr_array_new();
    scan->scan_start = time(NULL);

    // Проверка конфигурации
    check_configuration_vulnerabilities(scan);

    // Проверка зависимостей
    check_dependency_vulnerabilities(scan);

    // Проверка кода
    check_code_vulnerabilities(scan);

    // Проверка инфраструктуры
    check_infrastructure_vulnerabilities(scan);

    scan->scan_end = time(NULL);
    scan->scan_completed = true;

    return scan;
}

void check_configuration_vulnerabilities(vulnerability_scan_t *scan) {
    // Проверка слабых паролей
    if (has_weak_passwords()) {
        vulnerability_t *vuln = g_new(vulnerability_t, 1);
        vuln->cve_id = "CONFIG-001";
        vuln->severity = "high";
        vuln->description = "Weak password policy detected";
        vuln->remediation = "Implement strong password requirements";
        vuln->exploitable = true;
        g_ptr_array_add(scan->vulnerabilities, vuln);
    }

    // Проверка открытых портов
    // ...

    // Проверка прав доступа к файлам
    // ...
}
```

## 📊 Мониторинг и реагирование

### Security Information and Event Management

```c
// SIEM интеграция
typedef struct siem_integration {
    const char *siem_endpoint;
    const char *api_key;
    GQueue *event_queue;
    pthread_t worker_thread;
    bool running;
    pthread_mutex_t queue_mutex;
    pthread_cond_t queue_cond;
} siem_integration_t;

void siem_send_event(siem_integration_t *siem,
                    security_event_t *event) {

    pthread_mutex_lock(&siem->queue_mutex);

    // Добавление события в очередь
    security_event_t *event_copy = g_memdup(event, sizeof(security_event_t));
    g_queue_push_tail(siem->event_queue, event_copy);

    // Уведомление рабочего потока
    pthread_cond_signal(&siem->queue_cond);

    pthread_mutex_unlock(&siem->queue_mutex);
}

void *siem_worker_thread(void *arg) {
    siem_integration_t *siem = (siem_integration_t *)arg;

    while (siem->running) {
        pthread_mutex_lock(&siem->queue_mutex);

        // Ожидание событий
        while (g_queue_is_empty(siem->event_queue) && siem->running) {
            pthread_cond_wait(&siem->queue_cond, &siem->queue_mutex);
        }

        if (!siem->running) {
            pthread_mutex_unlock(&siem->queue_mutex);
            break;
        }

        // Извлечение события из очереди
        security_event_t *event = g_queue_pop_head(siem->event_queue);
        pthread_mutex_unlock(&siem->queue_mutex);

        // Отправка в SIEM
        send_to_siem(siem, event);
        g_free(event);
    }

    return NULL;
}
```

### Incident Response

```c
// Система реагирования на инциденты
typedef struct incident_response {
    GHashTable *active_incidents;
    GPtrArray *response_playbooks;
    GHashTable *escalation_matrix;
    pthread_mutex_t mutex;
} incident_response_t;

typedef struct incident {
    const char *id;
    const char *type;
    const char *severity;
    time_t detected_time;
    const char *description;
    GPtrArray *affected_systems;
    const char *assigned_to;
    const char *status;
    GPtrArray *actions_taken;
} incident_t;

void handle_security_incident(incident_response_t *ir,
                             const char *incident_type,
                             const char *description,
                             const char *severity) {

    // Создание инцидента
    incident_t *incident = g_new(incident_t, 1);
    incident->id = generate_incident_id();
    incident->type = g_strdup(incident_type);
    incident->severity = g_strdup(severity);
    incident->detected_time = time(NULL);
    incident->description = g_strdup(description);
    incident->status = "investigating";
    incident->actions_taken = g_ptr_array_new();

    // Регистрация инцидента
    pthread_mutex_lock(&ir->mutex);
    g_hash_table_insert(ir->active_incidents,
                       g_strdup(incident->id), incident);
    pthread_mutex_unlock(&ir->mutex);

    // Автоматическое реагирование
    execute_response_playbook(ir, incident);

    // Эскалация при необходимости
    if (strcmp(severity, "critical") == 0) {
        escalate_incident(ir, incident);
    }

    // Уведомление
    notify_security_team(incident);
}

void execute_response_playbook(incident_response_t *ir,
                              incident_t *incident) {

    // Поиск подходящего playbook
    for (guint i = 0; i < ir->response_playbooks->len; i++) {
        response_playbook_t *playbook = g_ptr_array_index(ir->response_playbooks, i);

        if (strcmp(playbook->incident_type, incident->type) == 0) {
            execute_playbook_actions(playbook, incident);
            break;
        }
    }
}
```

## ✨ Лучшие практики

### 1. Defense in Depth

```c
// Многоуровневая защита
typedef struct defense_layers {
    input_validation_t *input_layer;
    authentication_t *auth_layer;
    authorization_t *access_layer;
    encryption_t *crypto_layer;
    monitoring_t *audit_layer;
} defense_layers_t;

bool process_secure_request(defense_layers_t *defense,
                           const char *request_data,
                           size_t request_size,
                           const char *client_ip,
                           const char *session_token) {

    // Слой 1: Валидация входных данных
    if (!validate_input(defense->input_layer, request_data, request_size)) {
        log_security_event("Invalid input detected", client_ip);
        return false;
    }

    // Слой 2: Аутентификация
    if (!authenticate_user(defense->auth_layer, session_token)) {
        log_security_event("Authentication failed", client_ip);
        return false;
    }

    // Слой 3: Авторизация
    if (!authorize_action(defense->access_layer, request_data)) {
        log_security_event("Authorization failed", client_ip);
        return false;
    }

    // Слой 4: Шифрование (если нужно)
    char *encrypted_request = encrypt_request(defense->crypto_layer, request_data);
    if (!encrypted_request) {
        log_security_event("Encryption failed", client_ip);
        return false;
    }

    // Обработка запроса
    bool result = process_request_securely(encrypted_request);

    // Слой 5: Аудит
    audit_request(defense->audit_layer, request_data, result, client_ip);

    free(encrypted_request);
    return result;
}
```

### 2. Secure Coding Standards

```c
// Безопасные макросы
#define SAFE_FREE(ptr) \
    do { \
        if (ptr) { \
            memset(ptr, 0, malloc_usable_size(ptr)); \
            free(ptr); \
            ptr = NULL; \
        } \
    } while(0)

#define SAFE_STRCPY(dest, src, dest_size) \
    do { \
        if (dest && src && dest_size > 0) { \
            size_t copy_len = strnlen(src, dest_size - 1); \
            memcpy(dest, src, copy_len); \
            dest[copy_len] = '\0'; \
        } \
    } while(0)

#define VALIDATE_PTR(ptr) \
    ((ptr) && ((uintptr_t)(ptr) >= 0x1000) && ((uintptr_t)(ptr) < UINTPTR_MAX))

// Безопасные арифметические операции
bool safe_add(size_t a, size_t b, size_t *result) {
    if (a > SIZE_MAX - b) {
        return false; // Переполнение
    }
    *result = a + b;
    return true;
}

bool safe_mul(size_t a, size_t b, size_t *result) {
    if (a != 0 && b > SIZE_MAX / a) {
        return false; // Переполнение
    }
    *result = a * b;
    return true;
}
```

### 3. Regular Security Audits

```c
// Автоматизированный аудит
typedef struct security_audit_schedule {
    time_t next_audit_time;
    uint32_t audit_interval_days;
    GPtrArray *audit_checks;
    audit_report_t *last_report;
} security_audit_schedule_t;

void run_scheduled_security_audit(security_audit_schedule_t *schedule) {
    time_t now = time(NULL);

    if (now >= schedule->next_audit_time) {
        audit_report_t *report = perform_comprehensive_audit(schedule->audit_checks);

        if (report->critical_findings > 0) {
            send_security_alert("Critical security findings detected", report);
        }

        // Сохранение отчета
        if (schedule->last_report) {
            free_audit_report(schedule->last_report);
        }
        schedule->last_report = report;

        // Планирование следующего аудита
        schedule->next_audit_time = now + (schedule->audit_interval_days * 24 * 3600);
    }
}

audit_report_t *perform_comprehensive_audit(GPtrArray *checks) {
    audit_report_t *report = g_new(audit_report_t, 1);
    report->start_time = time(NULL);
    report->findings = g_ptr_array_new();

    for (guint i = 0; i < checks->len; i++) {
        audit_check_t *check = g_ptr_array_index(checks, i);

        audit_finding_t *finding = run_audit_check(check);
        if (finding) {
            g_ptr_array_add(report->findings, finding);

            if (strcmp(finding->severity, "critical") == 0) {
                report->critical_findings++;
            }
        }
    }

    report->end_time = time(NULL);
    report->duration = report->end_time - report->start_time;

    return report;
}
```

---

## 🎯 Заключение

Безопасность - это непрерывный процесс, требующий комплексного подхода на всех уровнях приложения. Следуя принципам, описанным в этом руководстве, вы сможете создать надежные и защищенные приложения на базе CellFrame DAP SDK.

**🔐 Помните:** "Безопасность не является продуктом, а процессом!"

**📞 Нужна помощь?** Обратитесь в нашу [службу безопасности](https://cellframe.net/security) или сообщество разработчиков.

**🔒 Хотите узнать больше?** Изучите наши [рекомендации по безопасности](https://docs.cellframe.net/security/best-practices)!


