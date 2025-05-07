#include <stdarg.h>
#include <stddef.h>
#include <setjmp.h>
#include <cmocka.h>

static void test_sample(void **state) {
    (void) state; // Не используется
    assert_int_equal(1, 1);
}

int main(void) {
    const struct CMUnitTest tests[] = {
        cmocka_unit_test(test_sample),
    };
    return cmocka_run_group_tests(tests, NULL, NULL);
}
