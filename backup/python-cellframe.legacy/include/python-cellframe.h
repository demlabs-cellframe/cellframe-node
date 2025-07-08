#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "libdap-python.h"
#include "math_python.h"
#include "node_address.h"
#include "libdap-crypto-python.h"
#include "wrapping_dap_enc_key_type.h"
#include "wrapping_dap_crypto_key_types.h"
#include "libdap_crypto_data_type.h"
#include "wrapping_dap_sign.h"
#include "wrapping_guuid.h"
// === GlobalDB ==
#include "wrapping_dap_global_db.h"
#include "wrapping_dap_global_db_obj.h"
#include "wrapping_dap_global_db_instance.h"
#include "wrapping_dap_global_db_role.h"
#include "wrapping_dap_global_db_cluster.h"
// === CHAIN ==
#include "libdap-chain-python.h"
#include "libdap_chain_type_python.h"
#include "libdap_chain_atom_iter_python.h"
#include "wrapping_dap_chain_cell.h"
#include "wrapping_dap_chain_common.h"
#include "wrapping_dap_chain_cs.h"
#include "wrapping_dap_chain_datum.h"
#include "wrapping_dap_chain_datum_decree.h"
#include "wrapping_dap_chain_datum_anchor.h"
#include "wrapping_dap_chain_datum_token.h"
#include "wrapping_dap_chain_tx_token_ext.h"
#include "wrapping_dap_chain_datum_tx.h"
#include "wrapping_dap_chain_ledger.h"
#include "wrapping_dap_chain_datum_tx.h"
#include "wrapping_dap_chain_tx_in.h"
#include "wrapping_dap_chain_tx_in_cond.h"
#include "wrapping_dap_chain_tx_out.h"
#include "wrapping_dap_chain_tx_out_cond.h"
#include "wrapping_dap_chain_tx_out_cond_subtype_srv_pay.h"
#include "wrapping_dap_chain_tx_out_cond_subtype_srv_stake.h"
#include "wrapping_dap_chain_tx_out_cond_subtype_srv_stake_lock.h"
#include "wrapping_dap_chain_tx_out_cond_subtype_srv_xchange.h"
#include "wrapping_dap_chain_tx_pkey.h"
#include "wrapping_dap_chain_tx_receipt.h"
#include "wrapping_dap_chain_tx_out_ext.h"
#include "wrapping_dap_chain_tx_tsd.h"
#include "wrapping_dap_chain_datum_tx_voting.h"
#include "wrapping_dap_chain_tx_out_std.h"
// ============
// === Chain net ===
#include "libdap_chain_net_python.h"
#include "wrapping_dap_chain_net_node.h"
#include "wrapping_dap_chain_net_node_client.h"
#include "wrapping_dap_chain_net_node_info.h"
#include "wrapping_dap_chain_net_state.h"
// ============
// === Chain net channel ===
#include "wrapping_dap_stream_ch_chain_validator_test.h"
// ============
// === Chain net srv ===
#include "wrapping_dap_chain_net_srv.h"
#include "wrapping_dap_chain_net_srv_client.h"
#include "wrapping_dap_chain_net_srv_common.h"
#include "wrapping_dap_chain_net_srv_order.h"
// ============
// === Chain cs dag poa ===
#include "wrapping_dap_chain_cs_dag_poa.h"
// ============
// === Chain cs block ===
#include "wrapping_dap_chain_cs_block.h"
// ============

#include "dap_events_python.h"
#include "wrapping_http.h"
#include "wrapping_dap_enc_http.h"
#include "wrapping_dap_stream.h"
#include "wrapping_dap_stream_ctl.h"
#include "wrapping_dap_mempool.h"
#include "wrapping_dap_http_folder.h"
#include "dap_chain_wallet_python.h"
#include "wrapping_dap_stream_cluster_role.h"
#include "wrapping_dap_cluster_member.h"

//#include "dap_http_client_simple.h"
//#include "dap_chain_wallet.h"
#include "dap_chain_cs.h"
#include "wrapping_dap_chain_atom_ptr.h"
//#include "dap_chain_cs_dag.h"
//#include "dap_chain_cs_dag_poa.h"
//#include "dap_chain_cs_dag_pos.h"
#include "dap_chain_net_srv.h"
#include "dap_http_simple.h"
#include "dap_chain_net_ch.h"
#include "dap_chain_net_srv_ch.h"
#include "dap_enc_ks.h"
#include "dap_chain_cs_none.h"
#include "libdap_chain_net_python.h"

#include "dap_app_cli.h"
#include "libdap-app-cli-python.h"
#include "wrapping_dap_app_cli_server.h"

#include "dap_file_utils.h"
#include "dap_string.h"

#include "dap_common.h"
#include "dap_server.h"
#include "wrapping_json_rpc_request.h"
#include "wrapping_json_rpc_response.h"
#include "wrapping_dap_chain_cs_dag_round.h"
#ifdef _WIN32
#include "Windows.h"
BOOL WINAPI consoleHandler(DWORD);
#else
#include "signal.h"
#include "wrapping_http_status_code.h"
#include "wrapping_dap_http_simple.h"
#include "wrapping_dap_http_header.h"
#include "wrapping_dap_client_http.h"
#include "wrapping_dap_chain_net_srv_stake_pos_delegate.h"
#include "wrapping_dap_chain_net_srv_xchange.h"
#include "wrapping_dap_chain_net_srv_xchange_price.h"
#include "wrapping_dap_chain_net_srv_vote.h"
#include "wrapping_dap_chain_net_srv_vote_info.h"
#ifdef DAP_SUPPORT_PYTHON_PLUGINS
    #include "../modules/plugins/include/dap_plugins_python_app_context.h"
#endif // DAP_SUPPORT_PYTHON_PLUGINS
void sigfunc(int sig);
#endif // _WIN32

PyObject *python_dap_init(PyObject *self, PyObject *args);
PyObject *python_cellframe_init(PyObject *self, PyObject *args);

void deinit_modules(void);

PyObject *python_dap_deinit(PyObject *self, PyObject *args);

PyMODINIT_FUNC PyInit_libDAP();
PyMODINIT_FUNC PyInit_libCellFrame(void);
