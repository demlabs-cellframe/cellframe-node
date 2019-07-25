#include "dap_global_db_test.h"
#include "dap_tx_test.h"
#include "dap_common.h"


int main(void) {
    // switch off debug info from library
     dap_log_level_set(L_CRITICAL);
    // dap_global_db_tests_run();
    dap_tx_tests_run();
    return 0;
}
