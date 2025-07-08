import libTPO
import sys

print ("Start test crypto OAES")
s = "Test! I will crush OAES!"
kex_buff = bytes("114151400014314485131FGXVGHcJFIH", "utf-8")
size_kex_buff = len(kex_buff)
seed = bytes(112771128)
seed_size = len(seed)
libTPO.init()
key = libTPO.Crypto.generateNewKey(libTPO.CryptoKeyType.DAP_ENC_KEY_TYPE_OAES(), kex_buff, size_kex_buff, seed, seed_size, 32)
source = bytes(s, "utf-8")
enc = libTPO.Crypto.encryptOAESFast(key, source, len(source), 2048)
decrypt = libTPO.Crypto.decryptOAESFast(key, enc, len(enc), 2048)

if bytes(s, "utf-8") == decrypt:
    print ("TEST 1. Encode/Decode OAES FAST done")
else:
    print ("TEST 1. Encode/Decode OAES CBC FAST faild")
    sys.exit(1)

sys.exit(0)

