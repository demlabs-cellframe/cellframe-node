#pragma once

#include <stdint.h>
#include "dap_common.h"
#include "ldb.h"

typedef struct dap_store_obj {
    char    *section;
    char    *group;
    char    *key;
    uint8_t type;
    char    *value;
} DAP_ALIGN_PACKED dap_store_obj_t, *pdap_store_obj_t;

typedef struct dap_store_obj_pkt {
     uint8_t type;
     uint8_t sec_size;
     uint8_t grp_size;
     uint8_t name_size;
     uint8_t data[];
} __attribute__((packed)) dap_store_obj_pkt_t;

int dap_store_len = 0; // initialized only when reading from local db

char *dap_db_path = NULL;

static struct ldb_context *ldb  = NULL;
static TALLOC_CTX *mem_ctx      = NULL;

int     dap_db_init     (const char*);
void    dap_db_deinit   (void);

int dap_db_add_msg(struct ldb_message *);
int dap_db_merge(pdap_store_obj_t, int);

pdap_store_obj_t dap_db_read_data       (void);
pdap_store_obj_t dap_db_read_file_data  (const char *); // state of emergency only, if LDB database is inaccessible
dap_store_obj_pkt_t *dap_store_packet_single(pdap_store_obj_t);
dap_store_obj_pkt_t *dap_store_packet_multiple(pdap_store_obj_t);
