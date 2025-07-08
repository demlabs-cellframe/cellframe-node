import libdap_crypto_python_module as crypto
import unittest

class TestLibdapCryptoPythonModule(unittest.TestCase):
    def test_ini(self):
        self.assertTrue(crypto.init() == 0, "Failed init libdap crypto python")
    def test_deinit(self):
        self.assertTrue(crypto.deinit() == 0, "Failed deinit libdap crypto python")
    def test_b58(self):
        s = "REvgshguqwt76thuioh1`lwi0-8i-d0hjwpeocnpgh89efty7ug"
        crypt = crypto.encodeBase58(s)
        decrypt = crypto.decodeBase58(crypt)
        self.assertTrue(s == decrypt, "Encoding and decoded information using the base58 algorithm does not match the original")
    def test_b64(self):
        s = "LindyfekrngFHJFGR23356fer"
        crypt = crypto.encodeBase64(bytes(s, "utf-8"), 1)
        decrypt = crypto.decodeBase64(crypt, 1)
        self.assertTrue(bytes(s, "utf-8") == decrypt, "Encoding and decoded information using the base64 algorithm does not match the original")

if __name__ == '__main__':
    unittest.main()
