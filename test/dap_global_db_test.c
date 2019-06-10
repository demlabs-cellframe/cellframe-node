#include <time.h>
#include <unistd.h>

#include "dap_common.h"
#include "dap_strfuncs.h"
#include "dap_file_utils.h"
//#include "dap_list.h"
#include "dap_chain_global_db.h"
#include "dap_chain_global_db_driver.h"
#include "dap_global_db_test.h"

#define DB_FILE "./base.tmp"

static void test_create_db(const char *db_type)
{
    if(dap_dir_test(DB_FILE)) {
        rmdir(DB_FILE);
        char *l_cmd = dap_strdup_printf("rm -rf %s", DB_FILE);
        system(l_cmd);
        DAP_DELETE(l_cmd);

    }
    else
        unlink(DB_FILE);
    int res = dap_db_driver_init(db_type, DB_FILE);
    char *l_str = dap_strdup_printf("Test init %s global_db", db_type);
    dap_assert(!res, l_str);
    DAP_DELETE(l_str);
}
static void test_write_read_one(void)
{
    dap_store_obj_t *l_store_obj = DAP_NEW_Z(dap_store_obj_t);
    size_t l_store_count = 1;
    l_store_obj->type = 'a';
    l_store_obj->key = dap_strdup("key");
    l_store_obj->group = dap_strdup("section.1");
    l_store_obj->timestamp = time(NULL);
    l_store_obj->value_len = rand() % 100;
    l_store_obj->value = DAP_NEW_SIZE(uint8_t, l_store_obj->value_len);
    for(size_t i = 0; i < l_store_obj->value_len; i++) {
        l_store_obj->value[i] = rand();
    }
    int ret = dap_chain_global_db_driver_add(l_store_obj, l_store_count);

    dap_store_obj_t *l_store_obj2 = dap_chain_global_db_driver_read(l_store_obj->group, l_store_obj->key, NULL);

    dap_assert_PIF(l_store_obj2, "Read global_db entry");

    // compare l_store_obj and l_store_obj
    if(l_store_obj->timestamp == l_store_obj2->timestamp &&
            l_store_obj->value_len == l_store_obj2->value_len &&
            l_store_obj->value && l_store_obj2->value &&
            !memcmp(l_store_obj->value, l_store_obj2->value, l_store_obj->value_len)) {
        dap_assert_PIF(1, "Check read entry");
    }
    else {
        dap_assert_PIF(0, "Check read entry");
    }

    dap_store_obj_free(l_store_obj, 1);
    dap_store_obj_free(l_store_obj2, 1);

    dap_assert(1, "Test dap_global_db one record");

}

static void test_close_db(void)
{
    dap_db_driver_deinit(); //dap_chain_global_db_deinit();
    dap_assert(1, "Test close global_db");
}

static void test_write_db_count(void)
{
    int a_count = 20000;
    dap_store_obj_t *l_store_obj = DAP_NEW_Z_SIZE(dap_store_obj_t, sizeof(dap_store_obj_t) * a_count);
    size_t l_store_count = 1;
    for(size_t n = 0; n < a_count; n++) {
        dap_store_obj_t *l_store_obj_cur = l_store_obj + n;
        l_store_obj_cur->type = 'a';
        l_store_obj_cur->key = dap_strdup_printf("key_%d", rand());
        l_store_obj_cur->group = dap_strdup("section.1");
        l_store_obj_cur->timestamp = time(NULL);
        l_store_obj_cur->value_len = 10 + rand() % 100;
        l_store_obj_cur->value = DAP_NEW_SIZE(uint8_t, l_store_obj_cur->value_len);
        for(size_t i = 0; i < l_store_obj_cur->value_len; i++) {
            l_store_obj_cur->value[i] = rand();
        }
    }
    //dap_test_msg("Start test write dap_global_db %d record", a_count);
    int ret = dap_chain_global_db_driver_add(l_store_obj, a_count);

    //dap_test_msg("Read first record");
    dap_store_obj_t *l_store_obj2 = dap_chain_global_db_driver_read(l_store_obj->group, l_store_obj->key, NULL);
    dap_store_obj_free(l_store_obj2, 1);
    //dap_test_msg("Start test read dap_global_db %d record", a_count);
    for(size_t n = 1; n < a_count; n++) {
        dap_store_obj_t *l_store_obj2 = dap_chain_global_db_driver_read(l_store_obj->group, l_store_obj->key, NULL);
        dap_assert_PIF(l_store_obj2, "Read data");
        // compare l_store_obj and l_store_obj
        if(l_store_obj->timestamp == l_store_obj2->timestamp &&
                l_store_obj->value_len == l_store_obj2->value_len &&
                l_store_obj->value && l_store_obj2->value &&
                !memcmp(l_store_obj->value, l_store_obj2->value, l_store_obj->value_len)) {
            ;
        }
        else {
            dap_assert_PIF(0, "Check read entry");
        }
        dap_store_obj_free(l_store_obj2, 1);
    }
    //dap_assert_PIF(1, "Read global_db entry");

    dap_store_obj_free(l_store_obj, a_count);

    //dap_usleep(5 * DAP_USEC_PER_SEC);
    //dap_assert(1, "Test dap_global_db");

}

void dap_global_db_tests_run(void)
{
    dap_print_module_name("dap_global_db");

    // cdb
    test_create_db("cdb");
    test_write_read_one();
    benchmark_mgs_time("Read and Write in cdb 20000 records",
            benchmark_test_time(test_write_db_count, 1));

    // sqlite
    test_create_db("sqlite");
    test_write_read_one();
//    test_write_db_count(1000000);

    benchmark_mgs_time("Read and Write in sqlite 20000 records",
            benchmark_test_time(test_write_db_count, 1));



    //test_close_db();



    //dap_assert(1, "Test dap_global_db: write and read 20000 records");

    /*
     benchmark_mgs_time("Read and Write in global_db 100 times",
     benchmark_test_time(test_write_db_count, 1));
     dap_assert(1, "Test dap_global_db 100 records");
     */

//        benchmark_mgs_rate("Read and Write in global_db",
//                benchmark_test_rate(test_write_db_count, 2000));
    //dap_usleep(2 * DAP_USEC_PER_SEC);
    test_close_db();
}
