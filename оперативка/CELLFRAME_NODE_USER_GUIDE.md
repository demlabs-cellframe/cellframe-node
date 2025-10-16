# 📖 Cellframe Node - Краткий User Guide

**Создано на основе**: QA_SPECIFICATION_LINUX.md (1985 строк)  
**Дата**: 16.10.2025  
**Версия ноды**: 5.5-3

---

## 🎯 Что такое Cellframe Node?

Cellframe Node - это нода блокчейн платформы Cellframe, поддерживающая:
- **Backbone** (Mainnet) - основная сеть с токеном CELL
- **KelVPN** - VPN сеть с токеном KEL
- Quantum-safe криптография
- Full/Light/Master/Root режимы работы

---

## 🚀 Быстрый старт

### 1. Установка (Debian/Ubuntu)

```bash
# Добавить репозиторий
wget https://cellframe.net/cellframe-node.deb
sudo dpkg -i cellframe-node.deb
sudo apt-get install -f
```

### 2. Запуск сервиса

```bash
# Запустить
sudo systemctl start cellframe-node

# Проверить статус
sudo systemctl status cellframe-node

# Включить автозапуск
sudo systemctl enable cellframe-node
```

### 3. Первые команды

```bash
# Версия
cellframe-node-cli version

# Список сетей
cellframe-node-cli net list

# Статус сети Backbone
cellframe-node-cli net -net Backbone get status
```

---

## 📂 Структура файлов

```
/opt/cellframe-node/
├── bin/
│   ├── cellframe-node          # Главный процесс
│   ├── cellframe-node-cli      # CLI инструмент
│   ├── cellframe-node-tool     # Утилиты
│   └── cellframe-node-config   # Конфигуратор
│
├── etc/
│   ├── cellframe-node.cfg      # Главный конфиг
│   └── network/                # Конфиги сетей
│       ├── Backbone/
│       └── KelVPN/
│
├── var/
│   ├── log/                    # Логи
│   ├── lib/
│   │   ├── wallet/             # Кошельки
│   │   ├── global_db/          # Глобальная БД
│   │   └── network/            # Данные сетей
│   └── run/
│       └── node_cli            # CLI socket
│
└── share/
    ├── ca/                     # Сертификаты
    └── configs/                # Дефолтные конфиги
```

---

## 🔧 Основные команды CLI

### Информация о ноде

```bash
# Версия
cellframe-node-cli version

# Информация о ноде
cellframe-node-cli node dump

# Подключения
cellframe-node-cli node connections
```

### Работа с сетями

```bash
# Список сетей
cellframe-node-cli net list

# Статус сети
cellframe-node-cli net -net Backbone get status

# Перейти онлайн
cellframe-node-cli net -net Backbone go online

# Перейти оффлайн
cellframe-node-cli net -net Backbone go offline

# Синхронизация
cellframe-node-cli net -net Backbone sync all

# Статистика
cellframe-node-cli net -net Backbone stats tx
cellframe-node-cli net -net Backbone stats tps
```

### Работа с кошельками

```bash
# Список кошельков
cellframe-node-cli wallet list

# Создать кошелек
cellframe-node-cli wallet new -w my_wallet

# С квантово-устойчивой подписью
cellframe-node-cli wallet new -w secure_wallet -sign sig_dil

# С паролем
cellframe-node-cli wallet new -w secure_wallet -password mypass123

# Информация о кошельке
cellframe-node-cli wallet info -w my_wallet -net Backbone

# Баланс
cellframe-node-cli wallet info -addr [ADDRESS] -net Backbone

# Активировать (если с паролем)
cellframe-node-cli wallet activate -w secure_wallet -password mypass123
```

### Транзакции

```bash
# Отправить токены
cellframe-node-cli tx_create \
  -net Backbone \
  -chain main \
  -from_wallet my_wallet \
  -to_addr [RECIPIENT_ADDRESS] \
  -token CELL \
  -value 10.5

# История по кошельку
cellframe-node-cli tx_history -w my_wallet -net Backbone

# История по адресу
cellframe-node-cli tx_history -addr [ADDRESS] -net Backbone

# Проверить транзакцию
cellframe-node-cli tx_verify -net Backbone -tx [TX_HASH]

# Количество транзакций
cellframe-node-cli tx_history -count -net Backbone
```

### Токены

```bash
# Список токенов
cellframe-node-cli token list -net Backbone

# С деталями
cellframe-node-cli token list -net Backbone -full

# Информация о токене
cellframe-node-cli token info -net Backbone -name CELL
```

---

## ⚙️ Конфигурация

### Главный файл: `/opt/cellframe-node/etc/cellframe-node.cfg`

#### Секция [general]
```ini
debug_mode=false          # Режим отладки
auto_online=true          # Автоматически онлайн при старте
```

#### Секция [server]
```ini
enabled=false             # Серверный режим (для мастернод)
listen_address=[0.0.0.0:8079]
```

#### Секция [cli-server]
```ini
enabled=true              # CLI сервер (всегда включен)
listen-path=[../var/run/node_cli]  # Unix socket
```

#### Секция [resources]
```ini
threads_cnt=0             # 0 = автоопределение (кол-во ядер)
log_file=../var/log/cellframe-node.log
wallets_path=../var/lib/wallet
```

#### Секция [global_db]
```ini
path=../var/lib/global_db
driver=mdbx               # MDBX драйвер БД
```

### Конфиги сетей

#### Backbone: `/opt/cellframe-node/etc/network/Backbone/main.cfg`
```ini
[general]
network_name=Backbone
native_ticker=CELL
node-role=full            # full, light, master, root, archive
```

#### KelVPN: `/opt/cellframe-node/etc/network/KelVPN/main.cfg`
```ini
[general]
network_name=KelVPN
native_ticker=KEL
node-role=full
```

---

## 📊 Логи и мониторинг

### Основной лог файл

```bash
# Просмотр логов
tail -f /opt/cellframe-node/var/log/cellframe-node.log

# Последние 100 строк
tail -100 /opt/cellframe-node/var/log/cellframe-node.log

# Поиск ошибок
grep "ERR" /opt/cellframe-node/var/log/cellframe-node.log

# Поиск критичных проблем
grep "CRITICAL" /opt/cellframe-node/var/log/cellframe-node.log
```

### Уровни логов

- `[DBG]` - Debug (отладка)
- `[INFO]` - Информация
- `[NOTICE]` - Уведомления
- `[MSG]` - Сообщения
- `[DAP]` - DAP протокол
- `[WRN]` - Предупреждения
- `[ATT]` - Важные события
- `[ERR]` - Ошибки
- `[CRITICAL]` - Критичные проблемы

### Мониторинг процесса

```bash
# PID процесса
cat /opt/cellframe-node/var/run/cellframe-node.pid

# Проверка что запущен
pgrep -x cellframe-node

# Использование ресурсов
ps aux | grep cellframe-node

# Детальная информация
top -p $(cat /opt/cellframe-node/var/run/cellframe-node.pid)
```

---

## 🔐 Типы криптографических подписей

| Тип | Описание | Quantum-safe |
|-----|----------|--------------|
| `sig_dil` | Dilithium | ✅ Да (default) |
| `sig_bliss` | BLISS | ✅ Да |
| `sig_tesla` | TESLA | ✅ Да |
| `sig_picnic` | Picnic | ✅ Да |

**Рекомендация**: Используйте `sig_dil` (Dilithium) - это дефолтный quantum-safe алгоритм.

---

## 🌐 Сети

### Backbone (Mainnet)
- **ID**: `0x53c0rp10n`
- **Токен**: CELL
- **Decimals**: 18
- **Seed nodes**: 5 root нод
- **Consensus**: ESbocs (для основной цепи main)

### KelVPN
- **ID**: `0x4b656c56504e`
- **Токен**: KEL
- **Decimals**: 18
- **Seed nodes**: 3 root ноды
- **Назначение**: VPN сервисы

---

## ❓ FAQ

### Как проверить что нода работает?

```bash
# 1. Проверить сервис
sudo systemctl status cellframe-node

# 2. Проверить процесс
pgrep -x cellframe-node

# 3. Проверить CLI
cellframe-node-cli version

# 4. Проверить статус сети
cellframe-node-cli net -net Backbone get status
```

### Как посмотреть баланс?

```bash
# По кошельку
cellframe-node-cli wallet info -w my_wallet -net Backbone

# По адресу
cellframe-node-cli wallet info -addr [YOUR_ADDRESS] -net Backbone
```

### Как отправить токены?

```bash
cellframe-node-cli tx_create \
  -net Backbone \
  -chain main \
  -from_wallet my_wallet \
  -to_addr [RECIPIENT_ADDRESS] \
  -token CELL \
  -value 100
```

### Нода не синхронизируется?

```bash
# 1. Проверить онлайн статус
cellframe-node-cli net -net Backbone get status

# 2. Перейти онлайн если оффлайн
cellframe-node-cli net -net Backbone go online

# 3. Принудительная синхронизация
cellframe-node-cli net -net Backbone sync all

# 4. Проверить подключения
cellframe-node-cli node connections

# 5. Проверить логи
tail -100 /opt/cellframe-node/var/log/cellframe-node.log | grep "ERR"
```

### Как создать безопасный кошелек?

```bash
# С quantum-safe подписью и паролем
cellframe-node-cli wallet new \
  -w secure_wallet \
  -sign sig_dil \
  -password your_strong_password_here

# Активировать для использования
cellframe-node-cli wallet activate \
  -w secure_wallet \
  -password your_strong_password_here \
  -ttl 60  # Активен 60 минут
```

### Где хранятся приватные ключи?

```
/opt/cellframe-node/var/lib/wallet/
```

**⚠️ ВАЖНО**: Создавайте бэкапы этой директории!

### Как обновить ноду?

```bash
# Скачать новую версию
wget https://cellframe.net/cellframe-node-latest.deb

# Остановить старую
sudo systemctl stop cellframe-node

# Установить новую
sudo dpkg -i cellframe-node-latest.deb
sudo apt-get install -f

# Запустить
sudo systemctl start cellframe-node

# Проверить версию
cellframe-node-cli version
```

---

## 🛠️ Troubleshooting

### Проблема: CLI не отвечает

```bash
# Проверить что процесс запущен
pgrep -x cellframe-node

# Проверить CLI socket
ls -la /opt/cellframe-node/var/run/node_cli

# Перезапустить
sudo systemctl restart cellframe-node
```

### Проблема: Нода занимает много памяти

```bash
# Проверить использование
ps aux | grep cellframe-node

# В конфиге можно ограничить потоки
# /opt/cellframe-node/etc/cellframe-node.cfg
[resources]
threads_cnt=4  # Вместо 0 (auto)
```

### Проблема: Логи переполняют диск

```bash
# Настроить ротацию логов
# Уже настроена по умолчанию:
# - Ротация каждые 120 минут
# - Максимальный размер файла: 2048 MB
# - Старые логи сжимаются

# Проверить размер
du -h /opt/cellframe-node/var/log/

# Очистить старые логи вручную
find /opt/cellframe-node/var/log/ -name "*.gz" -mtime +7 -delete
```

---

## 📚 Дополнительные ресурсы

- **Официальный сайт**: https://cellframe.net
- **GitHub**: https://github.com/demlabs-cellframe
- **GitLab**: https://gitlab.demlabs.net/cellframe/cellframe-node
- **Telegram**: @cellframechat
- **FAQ**: https://cellframe.net/faq

---

## 💡 Best Practices

### Безопасность

1. **Всегда** используйте пароли для кошельков
2. **Регулярно** делайте бэкапы `/opt/cellframe-node/var/lib/wallet/`
3. **Не храните** большие суммы на hot wallet (онлайн нода)
4. **Используйте** quantum-safe подписи (sig_dil)

### Мониторинг

1. **Настройте** автоматический мониторинг логов
2. **Проверяйте** статус сети раз в день
3. **Следите** за использованием диска
4. **Обновляйте** ноду регулярно

### Производительность

1. **Оставьте** `threads_cnt=0` для автоопределения
2. **Не запускайте** ноду на маломощных серверах (мин. 2GB RAM)
3. **Используйте** SSD для БД
4. **Проверяйте** что нода в online режиме

---

*Руководство создано на основе QA_SPECIFICATION_LINUX.md*  
*Версия: 1.0*  
*Дата: 16.10.2025*

