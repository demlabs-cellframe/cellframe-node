# Полноценная поддержка chipmunk_ring в wallet и crypto factory

## Исправления в dap-sdk/module/crypto/src/dap_sign.c
1. **Исправить баг маппинга** (строка 374-375): `sig_chipmunk_ring` → `SIG_TYPE_CHIPMUNK_RING` (0x010C) вместо `SIG_TYPE_CHIPMUNK_MRING` (0x0108)
2. **Добавить маппинг** `sig_chipmunk_ring` для `dap_sign_type_to_str` (обратное преобразование)

## Регистрация chipmunk_ring в crypto key factory
3. Найти `dap_enc_key_gen()` или эквивалентную функцию генерации ключей по sign_type
4. Добавить кейс `SIG_TYPE_CHIPMUNK_RING` → вызов chipmunk_ring keypair generation (аналогично `SIG_TYPE_CHIPMUNK`)
5. Убедиться что `dap_enc_key_type` правильно маппится на sign type для chipmunk_ring

## Поддержка в wallet module
6. Проверить что wallet CLI корректно передаёт sign_type в key generation
7. Убедиться что wallet new -sign sig_chipmunk_ring создаёт chipmunk_ring ключ (type 0x010C)

## Исправление бага логирования UTXO
8. В `dap_chain_ledger.c` исправить double-use static buffer в логе "Insufficient UTXO"

## Сборка и тесты
9. Пересобрать SDK
10. Запустить chipchain E2E тесты