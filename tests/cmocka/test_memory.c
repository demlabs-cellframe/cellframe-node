#include <stdarg.h>
#include <stddef.h>
#include <setjmp.h>
#include <cmocka.h>
#include <stdlib.h>
#include "cellframe/lib_memory.h"

static void test_memory_allocation(void **state) {
    (void)state;
    void *ptr = cellframe_malloc(100);
    assert_non_null(ptr);
    cellframe_free(ptr);
}

int main(void) {
    const struct CMUnitTest tests[] = {
        cmocka_unit_test(test_memory_allocation),
    };
    return cmocka_run_group_tests(tests, NULL, NULL);
}