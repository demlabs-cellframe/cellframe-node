#ifndef _DAP_CHAIN_WALLET_PYTHON_
#define _DAP_CHAIN_WALLET_PYTHON_

#include <Python.h>
#include "dap_common.h"
#include "dap_chain_wallet.h"
#include "wrapping_dap_chain_common.h"
#include "libdap_crypto_key_python.h"
#include "wrapping_dap_sign.h"
#include "wrapping_dap_pkey.h"
#include "wrapping_cert.h"

#ifdef __cplusplus
extern "C"{
#endif


typedef struct PyDapChainWallet{
    PyObject_HEAD
    dap_chain_wallet_t *wallet;
}PyDapChainWalletObject;

int dap_chain_wallet_init_py(void);
void dap_chain_wallet_deinit_py(void);

PyObject *dap_chain_wallet_get_path_py(PyObject *self, PyObject *argv);

PyObject *dap_chain_wallet_create_with_seed_py(PyObject *self, PyObject *argv);
PyObject *dap_chain_wallet_create_py(PyTypeObject *type, PyObject *argv, PyObject *kwds);
PyObject *dap_chain_wallet_open_file_py(PyObject *self, PyObject *argv);
PyObject *dap_chain_wallet_open_py(PyObject *self, PyObject *argv);
PyObject *dap_chain_wallet_save_py(PyObject *self, PyObject *argv);

void dap_chain_wallet_close_py(PyDapChainWalletObject *self);

PyObject *dap_cert_to_addr_py(PyObject *self, PyObject *argv);

PyObject *dap_chain_wallet_get_addr_py(PyObject *self, PyObject *argv);
PyObject *dap_chain_wallet_get_certs_number_py(PyObject *self, PyObject *argv);
PyObject *dap_chain_wallet_get_pkey_py(PyObject *self, PyObject *argv);
PyObject *dap_chain_wallet_get_key_py(PyObject *self, PyObject *argv);

//PyObject *dap_chain_wallet_save_file_py(PyObject *self, PyObject *argv);

extern PyTypeObject DapChainWalletObjectType;

static bool PyDapChainWalletObject_Check(PyObject *self) {
    return PyObject_TypeCheck(self, &DapChainWalletObjectType);
}


#ifdef __cplusplus
}
#endif


#endif // _DAP_CHAIN_WALLET_PYTHON_
