import libTPO
import sys

print ("Start test crypto iaes256 CBC")
s = "Test! I will crush iaes256!"
kex_buff = bytes("123", "utf-8")
size_kex_buff = len(kex_buff)
seed = bytes(112771128)
seed_size = len(seed)
libTPO.init()
key_id = libTPO.Crypto.generateNewKey(0, kex_buff, size_kex_buff, seed, seed_size, 0)
source = bytes(s, "utf-8")
enc = libTPO.Crypto.encryptIAES256CBCFast(key_id, source, len(source), 2048)
decrypt = libTPO.Crypto.decryptIAES256CBCFast(key_id, enc, len(enc), 2048)

if bytes(s, "utf-8") == decrypt:
    print ("TEST 1. Encode/Decode IAES256 CBC FAST done")
else:
    print ("TEST 1. Encode/Decode IAES256 CBC FAST faild")
    sys.exit(1)


sys.exit(0)

