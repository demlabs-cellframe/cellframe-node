import libdap_crypto_python_module as crypto

print ("Start dap_enc_key_test")
print ("Crypto init")
crypto.init()
print ("Create KEY")
key = crypto.newKey(1)
print ("Dellete key")
crypto.delKey(key)
print ("Crypto deinit")
crypto.deinit
