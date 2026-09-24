# cellframe-node

Cellframe Node — полноузловой сервер сетей Cellframe. Он отвечает за
синхронизацию сетей и цепочек, глобальную базу данных, кошельки,
валидацию транзакций и консенсус, а также предоставляет локальный CLI и
удалённый JSON-RPC интерфейс.

Актуальное описание установки, настройки и команд:
[Cellframe Node Wiki](https://wiki.cellframe.net/en/soft).

Этот файл описывает сборку и работу с репозиторием. Для типовых
операционных задач первичным источником остаётся Wiki; RPC-справочник
доступен непосредственно на запущенной ноде, как описано ниже.

## Сборка из исходных кодов

### Зависимости

Debian/Ubuntu:

```bash
sudo apt-get install \
  build-essential cmake dpkg-dev debconf-utils xsltproc git \
  libsqlite3-dev libz-dev libmagic-dev libpq-dev libcurl4-openssl-dev
```

macOS (Homebrew):

```bash
brew install cmake sqlite zlib
```

Для сборки можно использовать и другие дистрибутивы, при условии
наличия CMake, компилятора C, OpenSSL/libcrypto, SQLite, zlib и libmagic.
Имена пакетов при этом отличаются.

### Получение исходных кодов

Репозиторий использует сабмодули, поэтому их необходимо инициализировать:

```bash
git clone --recurse-submodules \
  https://gitlab.demlabs.net/cellframe/cellframe-node.git
cd cellframe-node
```

Если клон уже создан без сабмодулей:

```bash
git submodule update --init --recursive
```

### Сборка и запуск из дерева сборки

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
cd build
./cellframe-node
```

По умолчанию узел ищет `cellframe-node.cfg` относительно каталога
исполняемого файла. Для локальной сборки используйте конфигурацию,
установленную в `build/etc/cellframe-node.cfg`, или явно скопируйте
шаблон из `dist/share/configs/cellframe-node.cfg`. Перед выходом в сеть
проверьте выбранные сети, адреса прослушивания и пути к данным.

### Создание пакета

```bash
cmake --build build --target package
```

Пакет формируется средствами CPack в каталоге `build/`.

### Установка

Поддерживаются два основных способа:

- из официального репозитория Cellframe:
  `sudo apt-get install cellframe-node`;
- из локально собранного `.deb`-пакета:
  `sudo dpkg -i build/cellframe-node-<version>_<codename>-<arch>.deb`,
  при необходимости затем `sudo apt --fix-broken install`.

Точные версии пакета и поддерживаемые дистрибутивы смотрите в
установочных инструкциях Wiki. При установке пакет может создавать
собственного пользователя, systemd-юнит и служебные каталоги; после
установки типовой путь конфигурации:

```text
/opt/cellframe-node/etc/cellframe-node.cfg
```

После изменения конфигурации перезапустите службу:

```bash
sudo systemctl restart cellframe-node
sudo systemctl status cellframe-node
```

## RPC и CLI

У ноды есть два разных, но родственных входа для команд.

### Локальный CLI/RPC

Секция `[cli-server]` управляет локальным console/CLI-сервером. Он
слушает unix-сокет и/или TCP-адрес и принимает JSON-RPC-запросы.
В конфигурации это секция вида:

```ini
[cli-server]
enabled=true
version=1
#listen-path=[../var/run/node_cli]
#listen-address=[127.0.0.1:12345]
#http-index-path=../share/docs/rpc
```

Параметры секции:

- `enabled` — включить или отключить CLI/RPC-сервер;
- `version` — версия протокола `1` или `2`;
- `listen-path` — список unix-сокетов, например
  `../var/run/node_cli`;
- `listen-address` — TCP-адрес и порт вида `127.0.0.1:12345`;
- `http-index-path` — каталог HTML-документации RPC.

Помимо этих настроек в `dap-sdk/net/server/cli_server/dap_cli_server.c`
поддерживаются ограничительные параметры:

- `max_inflight` — максимальное число одновременных обычных запросов
  (по умолчанию `32`);
- `max_inflight_heavy` — лимит для тяжёлых операций, помеченных
  соответствующим флагом (по умолчанию `4`);
- `allowed_cmd` — белый список методов, разрешённых для не-локальных
  вызовов;
- `allowed_cmd_control` — включает проверку `allowed_cmd` (по умолчанию
  `false`);
- `rate_limit`, `rate_limit_rps` и `rate_limit_burst` — token-bucket
  ограничение частоты запросов на IPv4-/16 подсеть источника; по
  умолчанию `false`, `20` и `40`.

При перегрузке сервер отвечает `HTTP/1.1 429 Too Many Requests` вместо
неопределённо долгого удержания соединения, а после локального завершения
команды соединение закрывается.

Запрос к локальному порту:

```bash
curl -X POST http://127.0.0.1:12345/ \
  -H 'Content-Type: application/json' \
  --data '{"method":"version","params":[""],"id":1,"version":1}'
```

Текстовый режим CLI доступен через штатную утилиту `cellframe-node-cli`:

```bash
cellframe-node-cli wallet info -w my_wallet -net Backbone
cellframe-node-cli help
cellframe-node-cli help wallet
```

### Удалённый JSON-RPC через `/exec_cmd`

Секция `[server]` включает общий HTTP-сервер ноды. Для удалённых вызовов
зарегистрирован путь `/exec_cmd`:

```ini
[server]
enabled=true
listen-address=[0.0.0.0:8079]
#exec_cmd=[<authorized public-key hash>]
```

Для HTTP-сервера используется ключ `listen-address` (дефис в имени
параметра, как в `dap-sdk/io/include/dap_net.h`).
HTTP-запрос на `/exec_cmd` должен быть подписан; список доверенных
ключей задаётся параметром `exec_cmd`. Запросы к другим путям общего
HTTP-сервера не являются заменой CLI RPC.

### RPC-документация и self-help

Да, на актуальной сборке сервер сам отдаёт встроенную HTML-документацию:
при запуске вызывается `dap_cli_http_docs_init("cli-server")`, а
GET-запросы обрабатывает `dap_cli_http_docs_try_get()` в
`dap-sdk/net/server/cli_server/dap_cli_http_docs.c`.

Откройте корневой адрес CLI/RPC-сервера:

```bash
curl http://127.0.0.1:12345/
```

Например, `http://127.0.0.1:12345/` отдаёт индекс с доступными
модулями RPC. Страницы доступны и напрямую:

- `/help.html` — справочник вызова команды через RPC;
- `/wallet.html`, `/net.html`, `/block.html`, `/tx_history.html` и т.д.
  — документация по соответствующим RPC-командам;
- `/rpc-app.js` и `/rpc-theme.css` — интерфейс и оформление справочника.

Документация берётся из `http-index-path` относительно каталога, где
находится `cellframe-node.cfg`. Для типового пакетного пути
`/opt/cellframe-node/etc` и значения по умолчанию
`http-index-path=../share/docs/rpc` это означает
`/opt/cellframe-node/share/docs/rpc`.

Помимо HTML-справочника, команда `help` возвращает текстовую справку по
всем зарегистрированным RPC-командам:

```bash
cellframe-node-cli help
cellframe-node-cli help wallet
```

или эквивалентным JSON-RPC-запросом. Таким образом, актуальную справку
можно открыть прямо в браузере или получить через RPC, не обращаясь к
отдельному внешнему документу.

## Напоминание о безопасности

Не выставляйте RPC-порт без необходимости. По умолчанию используйте
loopback/ unix-сокет или reverse proxy; при включении TCP проверьте:

- список `allowed_cmd` для удалённых вызовов;
- привязку к нужному интерфейсу и файрвол;
- лимиты `max_inflight`, `max_inflight_heavy` и rate-limit;
- доступность и корректность локальной HTML-документации, если она
  включена на публичном узле.

## Удаление

```bash
sudo apt-get remove cellframe-node
```

Конфигурационные и рабочие каталоги могут сохраняться; при необходимости
удалите `/opt/cellframe-node` и связанные данные только после резервной
копии и проверки, что служба остановлена.
