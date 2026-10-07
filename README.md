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
#max_request_size=16777216
```

Для HTTP-сервера используется ключ `listen-address` (дефис в имени
параметра, как в `dap-sdk/io/include/dap_net.h`).
HTTP-запрос на `/exec_cmd` должен быть подписан; список доверенных
ключей задаётся параметром `exec_cmd`. Запросы к другим путям общего
HTTP-сервера не являются заменой CLI RPC.

`max_request_size` — верхняя граница тела HTTP-запроса в байтах
(по умолчанию 16 МБ, диапазон 1 КБ–16 МБ); всё, что больше, получает
`413 Payload Too Large` вместо аллокации.

### Требование метаданных комитета (ESBOCS)

В конфигурации сети (`etc/<net>.cfg`, секция `[esbocs]`) доступен ключ:

```ini
[esbocs]
#require_signs_meta_since=0
```

Блоки, созданные после указанного unix-времени, обязаны нести метаданные
комитета (`SYNC_ATTEMPT` и др.); без них они отклоняются. `0` (по умолчанию)
проверку отключает — исторические блоки и смешанные версии сети работают
как раньше. Включайте после того, как все сабмиттеры сети обновились до
сборки, штампующей метаданные всегда.

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

### Working with the RPC interface

Besides the `cellframe-node-cli` command line tool, the node exposes a **JSON-RPC 2.0**
interface over HTTP. Both share the same command set (wallet, tx_create, token, net,
memPool, block, version, etc.): every CLI command is available as an RPC `method`, and its
positional arguments are passed as the `params` array.

The interface is provided by the `[cli-server]` section of
`/opt/cellframe-node/etc/cellframe-node.cfg`.

#### Configuration

```
[cli-server]
enabled=true
# Protocol version of the RPC/CLI command layer (default 1)
version=1
# Unix domain socket used by cellframe-node-cli by default
listen-path=[../var/run/node_cli]
# HTTP address:port to serve JSON-RPC and the built-in docs.
# Loopback by default; bind 0.0.0.0 to expose it to your LAN.
listen-address=[127.0.0.1:12345]
# Uncomment to serve the unix socket only (no HTTP/TCP listener)
#unix-only
# Static RPC documentation directory (relative to the config dir). See below.
http-index-path=../share/docs/rpc
# Optional: restrict which RPC methods remote (non-loopback) clients may call.
# A space/comma separated list of method names, e.g.:
#allowed_cmd=[version,net,block,tx_create_json]
# Extra logging
#debug_more=false
```

After editing the config, restart the node: `sudo service cellframe-node restart`.

#### Security model

- Connections coming from a **unix socket or from loopback (127.0.0.1 / ::1)** are trusted
  and can call every method.
- Connections from any **other address** are restricted: only the methods listed in
  `allowed_cmd` are accepted, everything else returns a `Command "..." is restricted` error.
- If you don't need HTTP at all, set `unix-only` (or leave `listen-address` commented) so
  only the local unix socket is served.
- Binding `listen-address` to `0.0.0.0`/a public IP exposes node management to the network —
  always set `allowed_cmd` in that case, or keep it loopback-only and reach it via an
  authenticated reverse proxy.

#### Built-in self-documented interface (open it in a browser)

The RPC endpoint doubles as a small web documentation server. Point a browser at the HTTP
`listen-address` (e.g. **http://127.0.0.1:12345/**) and you get an interactive HTML
reference generated from the docs in `http-index-path` (installed at
`/opt/cellframe-node/share/docs/rpc`): a method list grouped per module (block, wallet,
token, mempool, net, net_srv, srv_xchange, stake_lock, tx_create_json, tx_history,
version, …) with a **Try-it-out** form that issues the JSON-RPC request for you.

Notes on the docs server:
- `GET /` (or `/index.html`) returns the auto-generated index; each module is also served
  at `/<module>.html`.
- Only modules allowed by `allowed_cmd` are shown for the corresponding audience; if
  `allowed_cmd` is unset, all present docs are served.
- If `http-index-path` doesn't exist on disk, the server falls back to a minimal stub page
  (application name, `DAP_VERSION` and build hash) instead of erroring.
- CORS is enabled (`Access-Control-Allow-Origin: *`, `GET`/`POST`/`OPTIONS`), so the UI can
  call the RPC from a browser on another origin. Symlinks and path traversal are rejected.

#### Making raw JSON-RPC requests

Send a JSON-RPC 2.0 object with the `method` and the `params` array via HTTP POST:

```
curl -s -X POST http://127.0.0.1:12345/ \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"version","params":[],"id":1}'
```

A call that returns a value, e.g. listing wallets:

```
curl -s -X POST http://127.0.0.1:12345/ \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"wallet","params":["list"],"id":2}'
```

Transactions can also be built from a JSON body using the dedicated
`tx_create_json` method (see the `tx_create_json` module in the web docs for its schema):

```
curl -s -X POST http://127.0.0.1:12345/ \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"tx_create_json","params":["{\"net\":\"minkowski\", ... }"],"id":3}'
```

Successful calls return `{"result": ... ,"id":N}`; errors return `{"error":{"code":...,"message":...}}`.
To discover every method and its exact parameters without reading code, open the web docs
at the `listen-address` — that is the intended, always-up-to-date reference for the RPC.

### How to publish service in network 


#### Obtain node address
First you need to publish you public IPv4 and/or IPv6 addresses (for current moment we support only IPv4)

```
sudo /opt/cellframe-node/bin/cellframe-node-cli net -net minkowski get status
```

It should print smth like this
```
Network "minkowski" has state NET_STATE_SYNC_CHAINS (target state NET_STATE_ONLINE), active links 3 from 4, cur node address 374C::CEB5::6740::D93B
```

#### Publish IP address in nodelist

Look at the end of address, thats you node address, ```374C::CEB5::6740::D93B``` use it to update information about your node, as in example below:
```
sudo /opt/cellframe-node/bin/cellframe-node-cli node add -net minkowski -addr 374C::CEB5::6740::D93B -cell 0x0000000000000001 -ipv4 5.89.17.176
```

Here is cell `0x0000000000000001` used by default until we haven't finished cell autoselection. Then ipv4 address is `5.89.17.176` replace it with your public IPv4 address. Same could be added ipv6 address with argument `-ipv6`


#### Create order for VPN service 

To say world that you have VPN service you need to place order. First lets see the market, what orders are already present:
```
sudo /opt/cellframe-node/bin/cellframe-node-cli net_srv -net KelVPN order find -srv_uid 0x0000000000000001 -direction sell
```

It should print list if you've syncronized well before (should happens automatically by default)
Anyway, lets create our order, changing price in it if you see in list thats market changed and you need to change prices as well.
Here is exmaple based on our pricelist in previous examples:
```sudo /opt/cellframe-node/bin/cellframe-node-cli net_srv -net KelVPN order create -direction sell -srv_uid 1 -price_unit SEC -price_token KEL -price 100 -units 3600 -node_addr 374C::CEB5::6740::D93B -cert my_awesome_cert -region Russia -continent Europe```

And then you just wait some for network synchronisation and your order will see everybody. Next restart your node. Provide the hash of your order to the network administrator so that your node appears in the clients list of servers.


Description of arguments
* ```-direction``` buy or sell, for VPN service publishing it must be ```sell```
* ```-srv_uid``` Service UID, for VPN service set ```1```
* ```-price_unit``` Set SEC for Seconds
* ```-price_token``` Token ticker
* ```-units``` The number of units in one portion of the service, in this example 3600 seconds
* ```-price``` Price for the number of units specified in the parameter -units. In this example 100 datoshi for 3600 seconds of service. To share VPN service for free set this field to 0.
* ```-node_addr``` Address of node
* ```-cert``` Certificate of master node
* ```-region``` The region in which the node is located
* ```-continent```  The continent in which the node is located

More details about order operations you could find with call ```sudo /opt/cellframe-node/bin/cellframe-node-cli help net_srv```
More details about cellframe node commands in call ```sudo /opt/cellframe-node/bin/cellframe-node-cli help```

# SubZero testnet

## Create wallet and token request

1. Install node according instructions above.
2. Create wallet
   
```
    cellframe-node-cli wallet new -w subzero_wallet
    Wallet 'subzero_wallet' (type=sig_dil) successfully created
```

3. Get wallet address:
   
```
cellframe-node-cli wallet info -w subzero_wallet -net subzero 
addr: mJUUJk6Yk2gBSTjcDHXxAerggncSK7DP8ZViVG2zrtbuW6uiCtTvXXn9kdcoBadGeBiujC7VsfemGv5BLbq2zcxoCR8GVRKfCmLtaedd
network: subzero
balance: 0
```

4. Send wallet address and request for tCELL amount of money to telegram channel: t.me/cellframe_dev_en
5. Waiting for answer from admin and execute command for network chains and gdb syncronization:

```cellframe-node-cli net sync all -net subzero```

6. See wallet balance:
   
```
cellframe-node-cli wallet info -w subzero_wallet -net subzero 
wallet: subzero_wallet
addr: mJUUJk6Yk2gBSTjcDHXxAerggncSK7DP8ZViVG2zrtbuW6uiCtTvXXn9kdcoBadGeBiujC7VsfemGv5BLbq2zcxoCR8GVRKfCmLtaedd
network: subzero
balance:
	5500000.000000000 (5500000000000000) tCELL
```

## Balance replenishment 

If you want increase amount of tCell on your wallet, you can wrote about it to SubZero admin.

## Tokens transfer

1. You can transfer tokens from your wallet to other wallet. For doing this you need to know address of 2nd wallet. Execute command

```
cellframe-node-cli tx_create -net subzero -chain support -from_wallet subzero_wallet -to_addr rTDbDdeStfpodpLUevvYaxJBh2k739fjwusqtmAU72VoUCm88ERPw555jHXtrkoEGJfYEZ7Mmwssc3ajijG9eEqEZxV2FmZvYcvnAVZz -value 32100000
        transfer=Ok
        tx_hash=0x4E6D540F86CD46CBFA551F219A04BA2248FF474BB795EB5B2C524299458AD709
```

- to_addr - address of 2nd wallet (you can see it using command ```cellframe-node-cli wallet info -w <wallet_name> -net subzero ```)
- value - amount of tokens

2. Execute command for database syncing

```cellframe-node-cli net sync all -net subzero```

3. Waiting for a while root node have processed you request
4. Don't create more then one request on balance changing, until you get confirmation about processing current request. That requests will not be processed (it can be fixed in future)
      
and see your updated balance

```cellframe-node-cli wallet info -w subzero_wallet -net subzero``` 

# Node notes

1. Token declaration operations, executing on node client (token_decl command) will be approved manually.
2. Token emission operations (token_emit command) will be processing automatically only for token owners.
3. Transactions (tx_create command) will be automatically processing as usual.

#### Remove cellframe-node

In order to remove cellframe-node, use the following command
```
sudo apt-get remove cellframe-node
```
