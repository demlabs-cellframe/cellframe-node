/*
 * Authors:
 * Alexey Stratulat <alexey.stratulat@demlabs.net>
 * Dmitriy A. Gearasimov <gerasimov.dmitriy@demlabs.net>
 * DeM Labs Inc.   https://demlabs.net
 * CellFrame       https://cellframe.net
 * Sources         https://gitlab.demlabs.net/cellframe
 * Copyright  (c) 2017-2020
 * All rights reserved.

 This file is part of DAP (Distributed Applications Platform) the open source project

    DAP (Distributed Applications Platform) is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    DAP is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with any DAP based project.  If not, see <http://www.gnu.org/licenses/>.
*/

#include "libdap-python.h"
#include "libdap-crypto-python.h"

#define LOG_TAG "dap_crypto_python"

static PyMethodDef PyDapCryptoMethods[] = {
        {"encodeBase58", dap_encode_base58_py, METH_VARARGS | METH_STATIC, "Encrypts information using the base58 algorithm from the DAP crypto library"},
        {"decodeBase58", dap_decode_base58_py, METH_VARARGS | METH_STATIC, "Dencrypts information using the base58 algorithm from the DAP crypto library"},
        {"encodeBase64", dap_encode_base64_py, METH_VARARGS | METH_STATIC, "Encrypts information using the base64 algorithm from the DAP crypto library"},
        {"decodeBase64", dap_decode_base64_py, METH_VARARGS | METH_STATIC, "Dencrypts information using the base64 algorithm from the DAP crypto library"},
        {"newKey", dap_enc_key_new_py, METH_VARARGS | METH_STATIC, "The function creates a new key, and returns it with PyObject."},
        {"generateNewKey", dap_enc_key_new_generate_py, METH_VARARGS | METH_STATIC, ""},
        {"getEncSizeKey", dap_enc_key_get_enc_size_py, METH_VARARGS | METH_STATIC, ""},
        {"getDecSizeKey", dap_enc_key_get_dec_size_py, METH_VARARGS | METH_STATIC, ""},
        /*IAES256*/
        {"newKeyIAES", dap_enc_iaes_key_new_py, METH_VARARGS | METH_STATIC, ""},
        {"deleteKeyIAES", dap_enc_iaes_key_delete_py, METH_VARARGS | METH_STATIC, ""},
        {"generateKeyIAES", dap_enc_iaes_key_generate_py, METH_VARARGS | METH_STATIC, ""},
        {"encodeSizeIAES256", dap_enc_iaes256_calc_encode_size_py, METH_VARARGS | METH_STATIC, ""},
        {"decodeSizeIAES256", dap_enc_iaes256_calc_decode_size_py, METH_VARARGS | METH_STATIC, ""},
        {"encryptIAES256CBCFast", dap_enc_iaes256_cbc_encrypt_fast_py, METH_VARARGS | METH_STATIC, ""},
        {"decryptIAES256CBCFast", dap_enc_iaes256_cbc_decrypt_fast_py, METH_VARARGS | METH_STATIC, ""},
        /*OAES*/
        {"newKeyOAES", dap_enc_oaes_key_new_py, METH_VARARGS | METH_STATIC, ""},
        {"deleteKeyOAES", dap_enc_oaes_key_delete_py, METH_VARARGS | METH_STATIC, ""},
        {"generateKeyOAES", dap_enc_oaes_key_generate_py, METH_VARARGS | METH_STATIC, ""},
        {"encodeSizeOAES", dap_enc_oaes_calc_encode_size_py, METH_VARARGS | METH_STATIC, ""},
        {"decodeSizeOAES", dap_enc_oaes_calc_decode_size_py, METH_VARARGS | METH_STATIC, ""},
        {"encryptOAESFast", dap_enc_oaes_encrypt_fast_py, METH_VARARGS | METH_STATIC, ""},
        {"decryptOAESFast", dap_enc_oaes_decrypt_fast_py, METH_VARARGS | METH_STATIC, ""},
        {}
};

PyTypeObject DapCryptoAlgoObjectType = DAP_PY_TYPE_OBJECT(
        "DAP.Crypto.Algo", sizeof(PyCryptoAlgoObject),
        "Crypto algorithms",
        .tp_methods = PyDapCryptoMethods);

int dap_crypto_init(void){
    if(dap_enc_init()!=0){
        log_it(L_CRITICAL,"Can't init encryption module");
        return -1;
    }
    if(dap_enc_key_init()!=0){
        log_it(L_CRITICAL,"Can't init encryption key module");
        return -2;
    }
    PyCryptoKeyObjectType.tp_new = PyType_GenericNew;
    return 0;
}

void dap_crypto_deinit(void){
    dap_enc_key_deinit();
    dap_enc_deinit();
}
