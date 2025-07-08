/*
 * Authors:
 * Alexey V. Stratulat <alexey.stratulat@demlabs.net>
 * DeM Labs Inc.   https://demlabs.net
 * CellFrame       https://cellframe.net
 * Sources         https://gitlab.demlabs.net/cellframe
 * Copyright  (c) 2017-2024
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
#include "Python.h"
#include "dap_chain_datum_tx_voting.h"

typedef struct PyDapChainTXVoting{
    PyObject_HEAD
    dap_chain_datum_tx_voting_params_t *voting;
}PyDapChainTXVotingObject;

PyObject *wrapping_dap_chain_tx_voting_get_question(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_tx_voting_get_answers(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_tx_voting_get_max_count(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_tx_voting_get_expire(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_tx_voting_get_is_delegate_key_required(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_tx_voting_get_is_vote_changing_allowed(PyObject *self, void *closure);

extern PyTypeObject PyDapChainTxVotingObjectType;

typedef struct PyDapChainTXVote{
    PyObject_HEAD
    dap_chain_tx_vote_t *vote;
}PyDapChainTXVoteObject;

PyObject *wrapping_dap_chain_tx_vote_get_hash(PyObject *self, void *closure);
PyObject *wrapping_dap_chain_tx_vote_get_answer_idx(PyObject *self, void *closure);

extern PyTypeObject PyDapChainTXVoteObjectType;
