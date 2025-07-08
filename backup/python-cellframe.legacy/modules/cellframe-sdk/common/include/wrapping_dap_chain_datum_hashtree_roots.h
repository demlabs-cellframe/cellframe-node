#ifndef _WRAPPING_DAP_CHAIN_DATUM_HASHTREE_ROOTS_
#define _WRAPPING_DAP_CHAIN_DATUM_HASHTREE_ROOTS_
#include <Python.h>

typedef struct PyDapChainBlockRootsV1{
    PyObject_HEAD
}PyDapChainBlockRootsV1Object;

static PyTypeObject DapChainBlockRootsV1Object_DapChainBlockRootsV1Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "CellFrame.ChainBlockRootsV1Object",             /* tp_name */
    sizeof(PyDapChainBlockRootsV1Object),      /* tp_basicsize */
    0,                                               /* tp_itemsize */
    0,                                               /* tp_dealloc */
    0,                                               /* tp_print */
    0,                                               /* tp_getattr */
    0,                                               /* tp_setattr */
    0,                                               /* tp_reserved */
    0,                                               /* tp_repr */
    0,                                               /* tp_as_number */
    0,                                               /* tp_as_sequence */
    0,                                               /* tp_as_mapping */
    0,                                               /* tp_hash  */
    0,                                               /* tp_call */
    0,                                               /* tp_str */
    0,                                               /* tp_getattro */
    0,                                               /* tp_setattro */
    0,                                               /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT |
        Py_TPFLAGS_BASETYPE,                         /* tp_flags */
    "Chain block roots v1 object",           /* tp_doc */
    0,		                                         /* tp_traverse */
    0,		                                         /* tp_clear */
    0,		                                         /* tp_richcompare */
    0,                                               /* tp_weaklistoffset */
    0,		                                         /* tp_iter */
    0,		                                         /* tp_iternext */
    0,                                               /* tp_methods */
    0,                                               /* tp_members */
    0,                                               /* tp_getset */
    0,                                               /* tp_base */
    0,                                               /* tp_dict */
    0,                                               /* tp_descr_get */
    0,                                               /* tp_descr_set */
    0,                                               /* tp_dictoffset */
    0,                                               /* tp_init */
    0,                                               /* tp_alloc */
    PyType_GenericNew,                               /* tp_new */
};

typedef struct PyDapChainBlockRootsV2{
    PyObject_HEAD
}PyDapChainBlockRootsV2Object;

static PyTypeObject DapChainBlockRootsV2Object_DapChainBlockRootsV2Type = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "CellFrame.ChainBlockRootsV2Object",             /* tp_name */
    sizeof(PyDapChainBlockRootsV2Object),      /* tp_basicsize */
    0,                                               /* tp_itemsize */
    0,                                               /* tp_dealloc */
    0,                                               /* tp_print */
    0,                                               /* tp_getattr */
    0,                                               /* tp_setattr */
    0,                                               /* tp_reserved */
    0,                                               /* tp_repr */
    0,                                               /* tp_as_number */
    0,                                               /* tp_as_sequence */
    0,                                               /* tp_as_mapping */
    0,                                               /* tp_hash  */
    0,                                               /* tp_call */
    0,                                               /* tp_str */
    0,                                               /* tp_getattro */
    0,                                               /* tp_setattro */
    0,                                               /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT |
        Py_TPFLAGS_BASETYPE,                         /* tp_flags */
    "Chain block roots v2 object",           /* tp_doc */
    0,		                                         /* tp_traverse */
    0,		                                         /* tp_clear */
    0,		                                         /* tp_richcompare */
    0,                                               /* tp_weaklistoffset */
    0,		                                         /* tp_iter */
    0,		                                         /* tp_iternext */
    0,                                               /* tp_methods */
    0,                                               /* tp_members */
    0,                                               /* tp_getset */
    0,                                               /* tp_base */
    0,                                               /* tp_dict */
    0,                                               /* tp_descr_get */
    0,                                               /* tp_descr_set */
    0,                                               /* tp_dictoffset */
    0,                                               /* tp_init */
    0,                                               /* tp_alloc */
    PyType_GenericNew,                               /* tp_new */
};


#endif //_WRAPPING_DAP_CHAIN_DATUM_HASHTREE_ROOTS_
