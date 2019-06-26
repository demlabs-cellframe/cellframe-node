#ifndef DAP_TX_TEST_H
#define DAP_TX_TEST_H

#include "dap_test.h"

typedef enum scenario {
    VAIN    = 0,
    EMIT    = 1,
    TX      = 2,
    CHECK   = 3
} scenario_t;

void dap_tx_tests_run();
int dap_node_run_action(scenario_t);
int dap_node_init();
int dap_node_deinit();

#endif // DAP_TX_TEST_H
