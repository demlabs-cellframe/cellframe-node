/*
 * Python DAP Crypto Implementation
 * Real bindings to DAP SDK crypto functions
 */

#include "python_cellframe_common.h"
#include "dap_enc.h"
#include "dap_hash.h"
#include "dap_sign.h"
#include "dap_enc_key.h"
#include "dap_cert.h"
#include <string.h>

// Crypto initialization functions  
int dap_crypto_init_py(void) {
    return dap_enc_init();
}

void dap_crypto_deinit_py(void) {
    dap_enc_deinit();
}

// Hash functions using real DAP SDK API
int dap_hash_fast_py(const void* a_data, size_t a_data_size, void* a_hash_out) {
    if (!a_data || a_data_size == 0 || !a_hash_out) {
        return -EINVAL;
    }
    
    dap_hash_fast_t l_hash;
    bool l_result = dap_hash_fast(a_data, a_data_size, &l_hash);
    if (l_result) {
        memcpy(a_hash_out, &l_hash, DAP_HASH_FAST_SIZE);
        return 0;
    }
    
    return -1;
}

size_t dap_hash_fast_get_size_py(void) {
    return DAP_HASH_FAST_SIZE;
}

int dap_hash_fast_compare_py(const void* a_hash1, const void* a_hash2) {
    if (!a_hash1 || !a_hash2) {
        return -EINVAL;
    }
    
    const dap_hash_fast_t* l_hash1 = (const dap_hash_fast_t*)a_hash1;
    const dap_hash_fast_t* l_hash2 = (const dap_hash_fast_t*)a_hash2;
    
    return dap_hash_fast_compare(l_hash1, l_hash2) ? 0 : 1;
}

int dap_hash_fast_from_str_py(const char* a_hash_str, void* a_hash_out) {
    if (!a_hash_str || !a_hash_out) {
        return -EINVAL;
    }
    
    dap_hash_fast_t l_hash;
    int l_result = dap_chain_hash_fast_from_str(a_hash_str, &l_hash);
    if (l_result == 0) {
        memcpy(a_hash_out, &l_hash, DAP_HASH_FAST_SIZE);
    }
    
    return l_result;
}

char* dap_hash_fast_to_str_py(const void* a_hash) {
    if (!a_hash) {
        return NULL;
    }
    
    const dap_hash_fast_t* l_hash = (const dap_hash_fast_t*)a_hash;
    return dap_chain_hash_fast_to_str_new(l_hash);
}

// Key management functions
void* dap_enc_key_new_generate_py(const char* a_key_type, const char* a_key_name, 
                                   const char* a_seed_str, size_t a_key_size) {
    if (!a_key_type) {
        return NULL;
    }
    
    dap_enc_key_type_t l_key_type;
    
    // Parse key type string to enum
    if (strcmp(a_key_type, "sig_bliss") == 0) {
        l_key_type = DAP_ENC_KEY_TYPE_SIG_BLISS;
    } else if (strcmp(a_key_type, "sig_tesla") == 0) {
        l_key_type = DAP_ENC_KEY_TYPE_SIG_TESLA;
    } else if (strcmp(a_key_type, "sig_picnic") == 0) {
        l_key_type = DAP_ENC_KEY_TYPE_SIG_PICNIC;
    } else if (strcmp(a_key_type, "sig_dilithium") == 0) {
        l_key_type = DAP_ENC_KEY_TYPE_SIG_DILITHIUM;
    } else if (strcmp(a_key_type, "sig_falcon") == 0) {
        l_key_type = DAP_ENC_KEY_TYPE_SIG_FALCON;
    } else if (strcmp(a_key_type, "sig_sphincs") == 0) {
        l_key_type = DAP_ENC_KEY_TYPE_SIG_SPHINCSPLUS;
    } else if (strcmp(a_key_type, "enc_kyber") == 0) {
        l_key_type = DAP_ENC_KEY_TYPE_KEM_KYBER512;
    } else {
        return NULL;
    }
    
    // Generate new key with proper parameters - no name field in struct
    dap_enc_key_t* l_key = dap_enc_key_new_generate(l_key_type, NULL, 0, a_seed_str, 0, a_key_size);
    
    return l_key;
}

void dap_enc_key_delete_py(void* a_key) {
    if (a_key) {
        dap_enc_key_delete((dap_enc_key_t*)a_key);
    }
}

// Signature functions  
int dap_sign_create_py(void* a_key, const void* a_data, size_t a_data_size, 
                       void** a_signature_out, size_t* a_signature_size_out) {
    if (!a_key || !a_data || a_data_size == 0 || !a_signature_out || !a_signature_size_out) {
        return -EINVAL;
    }
    
    dap_enc_key_t* l_key = (dap_enc_key_t*)a_key;
    dap_sign_t* l_sign = dap_sign_create(l_key, a_data, a_data_size);
    
    if (!l_sign) {
        return -1;
    }
    
    // Allocate memory for signature and copy data
    size_t l_sign_size = dap_sign_get_size(l_sign);
    void* l_signature_copy = DAP_NEW_SIZE(uint8_t, l_sign_size);
    if (!l_signature_copy) {
        DAP_DELETE(l_sign);
        return -ENOMEM;
    }
    
    memcpy(l_signature_copy, l_sign, l_sign_size);
    
    *a_signature_out = l_signature_copy;
    *a_signature_size_out = l_sign_size;
    
    DAP_DELETE(l_sign);
    return 0;
}

int dap_sign_verify_py(void* a_key, const void* a_data, size_t a_data_size,
                       const void* a_signature, size_t a_signature_size) {
    if (!a_signature || a_signature_size == 0 || !a_data || a_data_size == 0) {
        return -EINVAL;
    }
    
    const dap_sign_t* l_sign = (const dap_sign_t*)a_signature;
    
    int l_result = dap_sign_verify((dap_sign_t*)l_sign, a_data, a_data_size);
    return l_result;
}

// Certificate functions
void* dap_cert_generate_py(const char* a_cert_name, void* a_key) {
    if (!a_cert_name || !a_key) {
        return NULL;
    }
    
    dap_enc_key_t* l_key = (dap_enc_key_t*)a_key;
    
    // Get key type from the key structure
    dap_enc_key_type_t l_key_type = l_key->type;
    
    dap_cert_t* l_cert = dap_cert_generate(a_cert_name, NULL, l_key_type);
    
    return l_cert;
}

void dap_cert_delete_py(void* a_cert) {
    if (a_cert) {
        dap_cert_delete((dap_cert_t*)a_cert);
    }
}

int dap_cert_save_to_folder_py(void* a_cert, const char* a_folder_path) {
    if (!a_cert || !a_folder_path) {
        return -EINVAL;
    }
    
    dap_cert_t* l_cert = (dap_cert_t*)a_cert;
    int l_result = dap_cert_save_to_folder(l_cert, a_folder_path);
    
    return l_result;
}

void* dap_cert_load_from_folder_py(const char* a_folder_path, const char* a_cert_name) {
    if (!a_folder_path || !a_cert_name) {
        return NULL;
    }
    
    dap_cert_t* l_cert = dap_cert_find_by_name(a_cert_name);
    return l_cert;
} 