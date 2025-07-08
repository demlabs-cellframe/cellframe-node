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
#pragma once
#define PY_SSIZE_T_CLEAN

#include <Python.h>
#include "dap_enc.h"
#include "dap_enc_key.h"
#include "dap_common.h"
#include "wrapping_cert.h"
#include "wrapping_base58.h"
#include "wrapping_base64.h"
#include "wrapping_dap_enc_key.h"
#include "wrapping_dap_enc_iaes.h"
#include "wrapping_dap_enc_oaes.h"

#ifdef __cplusplus
extern "C" {
#endif


typedef struct PyCryptoAlgo{
    PyObject_HEAD
}PyCryptoAlgoObject;

int dap_crypto_init(void);

void dap_crypto_deinit(void);

extern PyTypeObject DapCryptoAlgoObjectType;

#ifdef  __cplusplus
}
#endif
