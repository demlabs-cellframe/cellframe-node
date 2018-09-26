#include <string.h>
#include <stdio.h>
//#include "talloc.h"
#include "dap_chain_global_db.h"

#define LOG_TAG "dap_global_db"
#define TDB_PREFIX_LEN 7

/* add single entry which is not supposed to be an array
    e.g.: dap_db_add_record(&store_obj)
*/
#define CALL2(a, b, ...) (a), (b)
#define dap_db_add_record(...) dap_db_merge(CALL2(__VA_ARGS__, 0))

int dap_db_init(const char *path) {
    mem_ctx = talloc_new(NULL);
    if (ldb_global_init() != 0) {
        log_it(L_ERROR, "Couldn't initialize LDB's global information");
        return -1;
    };
    if ((ldb = ldb_init(mem_ctx, NULL)) != LDB_SUCCESS) {
        log_it(L_INFO, "ldb context initialized");
        char tdb_path[strlen(path) + TDB_PREFIX_LEN];
        memset(tdb_path, '\0', strlen(path) + TDB_PREFIX_LEN);
        strcat(tdb_path, "tdb://"); // using tdb for simplicity, no need for separate LDAP server
        strcat(tdb_path, path);
        struct ldb_result *data_message;
        if (ldb_connect(ldb, tdb_path, 0, NULL) != LDB_SUCCESS) {
            log_it(L_ERROR, "Couldn't connect to database");
            return 1;
        }
        dap_db_path = strdup(tdb_path);
        const char *query = "(dn=*)";
        if (ldb_search(ldb, mem_ctx, &data_message, NULL, LDB_SCOPE_DEFAULT, NULL, query) != LDB_SUCCESS) {
            log_it(L_ERROR, "Database querying failed");
            return 2;
        }
        struct ldb_message *msg;
        if (data_message->count == 0) {
            // level 1: section record
            msg = ldb_msg_new(ldb);
            msg->dn = ldb_dn_new(mem_ctx, ldb,      "dc=kelvin_nodes");
            ldb_msg_add_string(msg, "dc",           "kelvin_nodes");
            ldb_msg_add_string(msg, "objectClass",  "top");
            ldb_msg_add_string(msg, "objectClass",  "section");
            dap_db_add_msg(msg);
            talloc_free(msg->dn);
            talloc_free(msg);

            // level 2: group record
            msg = ldb_msg_new(ldb);
            msg->dn = ldb_dn_new(mem_ctx, ldb,      "ou=addrs_leased,dc=kelvin_nodes");
            ldb_msg_add_string(msg, "ou",           "addrs_leased");
            ldb_msg_add_string(msg, "objectClass",  "group");
            ldb_msg_add_string(msg, "description",  "Whitelist of Kelvin blockchain nodes");
            dap_db_add_msg(msg);
            talloc_free(msg->dn);
            talloc_free(msg);
        }
        talloc_free(data_message);
        return 0;
    }
    else {
        log_it(L_ERROR, "Couldn't initialize LDB context");
        return -2;
    }
}

int dap_db_add_msg(struct ldb_message *msg) {
    if (ldb_msg_sanity_check(ldb, msg) != LDB_SUCCESS) {
        log_it(L_ERROR, "LDB message is inconsistent: %s", ldb_errstring(ldb) );
        return -1;
    }
    ldb_transaction_start(ldb);
    int status = ldb_add(ldb, msg);
    if (status != LDB_SUCCESS) {
        if (status == LDB_ERR_ENTRY_ALREADY_EXISTS) {
            log_it(L_INFO, "Entry %s already present, skipped", ldb_dn_get_linearized(msg->dn) );
        }
        else {
            log_it(L_ERROR, "LDB adding error: %s", ldb_errstring(ldb) );
        }
        ldb_transaction_cancel(ldb);
        return -2;
    }
    else {
        ldb_transaction_commit(ldb);
        log_it(L_INFO, "Entry %s added", ldb_dn_get_linearized(msg->dn) );
        return 0;
    }
}

/* path is supposed to have been obtained by smth like
    dap_config_get_item_str(g_config, "resources", "dap_global_db_path");
*/
pdap_store_obj_t dap_db_read_data(void) {
    struct ldb_result *data_message;
    const char *query = "(objectClass=addr_leased)";
    if (ldb_connect(ldb, dap_db_path, LDB_FLG_RDONLY, NULL) != LDB_SUCCESS) {
        log_it(L_ERROR, "Couldn't connect to database");
        return NULL;
    }
    if (ldb_search(ldb, NULL, &data_message, NULL, LDB_SCOPE_DEFAULT, NULL, query) != LDB_SUCCESS) {
        log_it(L_ERROR, "Database querying failed");
        return NULL;
    }
    log_it(L_INFO, "Obtained binary data, %d entries", data_message->count);

    pdap_store_obj_t store_data = (pdap_store_obj_t)malloc(data_message->count * sizeof(struct dap_store_obj));
    if (store_data != NULL) {
        log_it(L_INFO, "We're about to put entries into store objects");
    }
    else {
        log_it(L_ERROR, "Couldn't allocate memory, store objects unobtained");
        talloc_free(data_message);
        return NULL;
    }
    dap_store_len = data_message->count;
    int q;
    for (q = 0; q < dap_store_len; ++q) {
        store_data[q].section = "kelvin_nodes";
        store_data[q].group = "addrs_leased";
        store_data[q].type = 1;
        store_data[q].key = ldb_msg_find_attr_as_string(data_message->msgs[q], "cn", NULL);
        store_data[q].value = ldb_msg_find_attr_as_string(data_message->msgs[q], "time", NULL);
        log_it(L_INFO, "Record %s stored successfully", ldb_dn_get_linearized(data_message->msgs[q]->dn) );
    }
    talloc_free(data_message);
    return store_data;
}

/* Get the entire content without using query expression
 * This function is highly dissuaded from being used
 * */
pdap_store_obj_t dap_db_read_file_data(const char *path) {
    struct ldb_ldif *ldif_msg;
    FILE *fs = fopen(path, "r");
    if (!fs) {
        log_it(L_ERROR, "Can't open file %s", path);
        return NULL;
    }
    pdap_store_obj_t store_data = (pdap_store_obj_t)malloc(256 * sizeof(dap_store_obj_t));
    if (store_data != NULL) {
        log_it(L_INFO, "We're about to put entries in store objects");
    }
    else {
        log_it(L_ERROR, "Couldn't allocate memory, store objects unobtained");
        return NULL;
    }

    int q = 0;
    for (ldif_msg = ldb_ldif_read_file(ldb, fs); ldif_msg; ldif_msg = ldb_ldif_read_file(ldb, fs), q++) {
        if (q % 256 == 0) {
            store_data = (pdap_store_obj_t)realloc(store_data, (q + 256) * sizeof(dap_store_obj_t));
        }
        /* if (ldif_msg->changetype == LDB_CHANGETYPE_ADD) {
          / ... /
        } */ // in case we gonna use extra LDIF functionality
        char *key = ldb_msg_find_attr_as_string(ldif_msg->msg, "cn", NULL);
        if (key != NULL) {
            store_data[q].section = "kelvin_nodes";
            store_data[q].group = "addrs_leased";
            store_data[q].type = 1;
            store_data[q].key = key;
            store_data[q].value = ldb_msg_find_attr_as_string(ldif_msg->msg, "time", NULL);
            log_it(L_INFO, "Record %s stored successfully", ldb_dn_get_linearized(ldif_msg->msg->dn) );
        }
        ldb_ldif_read_free(ldb, ldif_msg);
    }
    return store_data;
}

/*
 * Add multiple entries received from remote node to local database.
 * Since we don't know the size, it must be supplied too
 */
int dap_db_merge(pdap_store_obj_t store_obj, int dap_store_size) {
    if (store_obj == NULL) {
        log_it(L_ERROR, "Invalid Dap store objects passed");
        return -1;
    }
    if (ldb_connect(ldb, dap_db_path, NULL, NULL) != LDB_SUCCESS) {
        log_it(L_ERROR, "Couldn't connect to database");
        return -2;
    }
    log_it(L_INFO, "We're about to put %d records into database", dap_store_size);
    struct ldb_message *msg;
    int q;
    if (dap_store_size == 0) {
        dap_store_size = 1;
    }
    for (q = 0; q < dap_store_size; q++) {
        // level 3: leased address, single whitelist entity
        msg = ldb_msg_new(ldb);
        char dn[128];
        memset(dn, '\0', 128);
        strcat(dn, "cn=");
        strcat(dn, store_obj[q].key);
        strcat(dn, ",ou=addrs_leased,dc=kelvin_nodes");
        msg->dn = ldb_dn_new(mem_ctx, ldb, dn);
        ldb_msg_add_string(msg, "cn", store_obj[q].key);
        ldb_msg_add_string(msg, "objectClass", "addr_leased");
        ldb_msg_add_string(msg, "description", "Approved Kelvin node");
        ldb_msg_add_string(msg, "time", store_obj[q].value);
        dap_db_add_msg(msg);
        talloc_free(msg->dn);
        talloc_free(msg);
    }
    return 0;
}

/* serialization */
dap_store_obj_pkt_t *dap_store_packet_single(pdap_store_obj_t store_obj) {
    dap_store_obj_pkt_t *pkt =
            (dap_store_obj_pkt_t*)calloc(1, sizeof(int) + 4 + strlen(store_obj->group) + strlen(store_obj->key) + strlen(store_obj->section) + strlen(store_obj->value));
    pkt->grp_size = strlen(store_obj->group) + 1;
    pkt->name_size = strlen(store_obj->key) + 1;
    pkt->sec_size = strlen(store_obj->section) + 1;
    pkt->type = store_obj->type;
    memcpy(pkt->data, &store_obj->section, pkt->sec_size);
    memcpy(pkt->data+pkt->sec_size, &store_obj->group, pkt->grp_size);
    memcpy(pkt->data+pkt->sec_size+pkt->grp_size, &store_obj->key, pkt->name_size);
    memcpy(pkt->data+pkt->sec_size+pkt->grp_size+pkt->name_size, &store_obj->value, strlen(store_obj->value)+1);
    return pkt;
}

dap_store_obj_pkt_t *dap_store_packet_multiple(pdap_store_obj_t store_obj) {
    dap_store_obj_pkt_t *pkt =
            (dap_store_obj_pkt_t*)calloc(1, sizeof(int) + 2 + strlen(store_obj->group) + dap_store_len*(1+strlen(store_obj->key)) + strlen(store_obj->section) + dap_store_len*(1+strlen(store_obj->value)));
    pkt->grp_size = strlen(store_obj[0].group) + 1;
    pkt->name_size = strlen(store_obj[0].key) + 1; // useless here since it can differ from one store_obj to another
    pkt->sec_size = strlen(store_obj[0].section) + 1;
    pkt->type = store_obj[0].type;
    memcpy(pkt->data, &store_obj[0].section, pkt->sec_size);
    memcpy(pkt->data+pkt->sec_size, &store_obj[0].group, pkt->grp_size);
    uint64_t offset = pkt->sec_size+pkt->grp_size;
    int q;
    for (q = 0; q < dap_store_len; ++q) {
        memcpy(pkt->data + offset, &store_obj[q].key, strlen(store_obj[q].key) + 1);
        offset += strlen(store_obj[q].key) + 1;
        memcpy(pkt->data + offset, &store_obj[q].value, strlen(store_obj[q].value) + 1);
        offset += strlen(store_obj[q].value) + 1;
    }
    return pkt;
}

void dap_db_deinit() {
    talloc_free(ldb);
    talloc_free(mem_ctx);
    free(dap_db_path);
}
