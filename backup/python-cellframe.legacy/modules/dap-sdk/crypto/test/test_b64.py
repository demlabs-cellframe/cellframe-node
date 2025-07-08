import libTPO
import sys

print ("Start test crypto b64")
s = "Test! I will crush Base64!"
print ("Input data: "+s)
crypt = libTPO.Crypto.encodeBase64(bytes(s, "utf-8"), libTPO.CryptoDataType.DAP_ENC_DATA_TYPE_B64())
print ("Encrypted data: \t")
print(crypt)
decrypt = libTPO.Crypto.decodeBase64(crypt, libTPO.CryptoDataType.DAP_ENC_DATA_TYPE_B64())
print ("Decoded data: \t")
print(decrypt)
if bytes(s, "utf-8") == decrypt:
    print ("TEST 1. Encode/Decode base64 done")
else:
    print ("TEST 1. Encode/Decode base64 faild")
    sys.exit(1)

print ("Test Base64 URLSAFE")
u = "http://kelvin.foundation/"
crypt_u = libTPO.Crypto.encodeBase64(bytes(u, "utf-8"), libTPO.CryptoDataType.DAP_ENC_DATA_TYPE_B64_URLSAFE())
decrypt_u = libTPO.Crypto.decodeBase64(crypt_u, libTPO.CryptoDataType.DAP_ENC_DATA_TYPE_B64_URLSAFE())
if bytes(u, "utf-8") == decrypt_u:
     print ("TEST 2. Encode/Decode base64 urlsafe done")
else:
     print ("TEST 2. Encode/Decode base64 urlsafe faild")
     sys.exit(2)

sys.exit(0)

