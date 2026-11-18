# Cellframe Node в Docker

Два образа: **builder** (сборка/тесты/отладочный запуск, исходники через mount) и
**deploy** (прод-образ без сорцов — только собранные артефакты и runtime-данные).

## 1. Builder (сборка, тесты, отладка)

```bash
docker build -t cellframe-node-builder -f Dockerfile.build .

# сборка: рабочее дерево в ./docker-artifacts/build, выкладка для деплой-образа
# в ./docker-artifacts/{bin,python-lib}
docker run --rm -v "$PWD:/src" -v "$PWD/docker-artifacts:/out" \
    -e BUILDER_UID=$(id -u) -e BUILDER_GID=$(id -g) cellframe-node-builder

# сборка + тесты sdk (ctest)
docker run --rm -v "$PWD:/src" -v "$PWD/docker-artifacts:/out" -e BUILD_TESTS=1 cellframe-node-builder

# отладочный запуск ноды (конфиг в ./docker-artifacts/node-base, исходники монтируются)
docker run --rm -it -v "$PWD:/src" -v "$PWD/docker-artifacts:/out" -e RUN_NODE=1 \
    -p 127.0.0.1:12345:12345 cellframe-node-builder
```

Исходники не копируются в образ — монтируются. Пересборка после правок — просто
повторный `docker run` (слой с тулчейном закэширован). Дерево исходников не
записывается.

## 2. Deploy-образ (без сорцов)

```bash
# после сборки билдером:
docker build -t cellframe-node:local .

docker run -d --name cellframe-node \
    -v cellframe-var:/opt/cellframe-node/var \
    -v cellframe-etc:/opt/cellframe-node/etc \
    -p 127.0.0.1:12345:12345 \
    cellframe-node:local
```

или `docker compose up -d`.

## Конфигурация

При первом старте entrypoint генерирует `/opt/cellframe-node/etc/cellframe-node.cfg`
из шаблона (`dist/share/configs/`) и включает сети из `CELLFRAME_NETWORKS`
(по умолчанию `Backbone`, роль `CELLFRAME_NODE_ROLE=full`). Существующий конфиг
никогда не перезаписывается — смонтируйте свой `etc/` целиком, чтобы управлять
конфигурацией полностью вручную.

| Переменная | По умолчанию | Что делает |
|---|---|---|
| `CELLFRAME_NETWORKS` | `Backbone` | встроенные сети для включения, через запятую (шаблоны из `dist/share/configs/network/`) |
| `CELLFRAME_NODE_ROLE` | `full` | роль ноды (light/full/archive/master/root) |
| `CELLFRAME_DEBUG_MODE` | `false` | debug_mode в general-секции |

## Оверлеи конфигурации (без правки базового cfg)

- `etc/cellframe-node.cfg.d/*.cfg` — drop-in фрагменты; dap_config сливает их
  нативно (alphasort, поздние ключи побеждают). Файлы читаются при каждом
  старте ноды.
- `etc/patches.d/*.cfg` — «патчи»: entrypoint копирует их в `cfg.d/` при старте
  (то же имя заменяет прежнюю копию) — рабочий процесс confctl-патчей.
- Свои сети: положите `<net>.cfg` в `etc/network/` (и шаблоны цепей при
  необходимости) — entrypoint включает только встроенные из
  `CELLFRAME_NETWORKS` и существующее не трогает.
- Плагины: `/opt/cellframe-node/var/lib/plugins` (внутри тома `var`).
- Кошельки: `/opt/cellframe-node/var/lib/wallet`; сертификаты: встроенные в
  образе `/opt/cellframe-node/share/ca`, пользовательские —
  `/opt/cellframe-node/var/lib/ca` (оба пути уже в `ca_folders` конфига;
  можно bind-mount: `./my-certs:/opt/cellframe-node/var/lib/ca:ro`).

## Эксплуатация

- CLI: `docker exec cellframe-node ./bin/cellframe-node-cli net list`
- Health (для балансировщика): `curl http://<host>:12345/health` — 200, когда все
  сети ONLINE и wallet-cache прогрет; 503 + Retry-After с причиной иначе.
- p2p-порт: добавьте `-e CELLFRAME_SERVER_ENABLED=true` нет — публикуйте `8079`
  и откройте `[server]` в конфиге (см. шаблон); для приватной ноды достаточно
  исходящих соединений.
- State: том `var` — цепь/global_db/кошельки; том `etc` — конфиги.
