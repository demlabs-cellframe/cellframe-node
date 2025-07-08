#include "wrapping_base64.h"

 PyObject *dap_encode_base64_py(PyObject *self, PyObject *args){
     PyObject *in_data;
     short int l_dap_enc_data_type;
     if (!PyArg_ParseTuple(args, "S|h", &in_data, &l_dap_enc_data_type)){
         return NULL;
     }
     if (l_dap_enc_data_type < 1 || l_dap_enc_data_type > 2){
         return NULL;
     }
     void *in_void = PyBytes_AsString((PyObject*)in_data);
     size_t pySize = (size_t)PyBytes_GET_SIZE(in_data);
     char result[DAP_ENC_BASE64_ENCODE_SIZE(pySize)];
     dap_enc_base64_encode(in_void, pySize, result, l_dap_enc_data_type);
     return Py_BuildValue("s", result);
}

 PyObject *dap_decode_base64_py(PyObject *self, PyObject *args){
     const char *in_str;
     short int l_dap_enc_data_type=1;
     if (!PyArg_ParseTuple(args, "s|h", &in_str, &l_dap_enc_data_type)) {
         return NULL;
     }
     if (l_dap_enc_data_type < 1 || l_dap_enc_data_type > 2){
         return NULL;
     }
     void *res = DAP_NEW_SIZE(void*, DAP_ENC_BASE64_ENCODE_SIZE(strlen(in_str)));
     size_t decrypted_size = dap_enc_base64_decode(in_str, strlen(in_str), res, l_dap_enc_data_type);
     PyBytesObject *return_object = (PyBytesObject*)PyBytes_FromStringAndSize(res, (Py_ssize_t)decrypted_size);
     return Py_BuildValue("O", return_object);
}
