import libTPO
import pickle
import sys

print ("Start test crypto base58")
s = """Test! I will crush Base58!"""
base_in = pickle.dumps(s)
print ("Input data: "+s)
print (base_in)
crypt = libTPO.Crypto.encodeBase58(base_in)
print ("Encrypted data: \t")
print(crypt)
decrypt = libTPO.Crypto.decodeBase58(crypt)
print ("Decoded data: \t")
print(decrypt)
out_data = pickle.loads(decrypt)
if s == out_data:
    print ("TEST 1. Encode/Decode base58 done")
else:
    print ("TEST 1. Encode/Decode base58 faild")
    sys.exit(1)

sys.exit(0)
