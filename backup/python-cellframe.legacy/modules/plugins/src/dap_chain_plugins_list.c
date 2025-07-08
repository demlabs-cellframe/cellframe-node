#include "dap_chain_plugins_list.h"

#undef LOG_TAG
#define LOG_TAG "dap_chain_plugins_list"

void dap_chain_plugins_list_init(){
    s_dap_chain_plugins_module_list = NULL;
}

void dap_chain_plugins_list_add(PyObject *a_module, const char *a_name){
    dap_chain_plugin_list_module_t *elemnet = (dap_chain_plugin_list_module_t*)DAP_NEW(dap_chain_plugin_list_module_t);
    if (!elemnet) {
        log_it(L_CRITICAL, "Memory allocation error");
        return;
    }
    elemnet->name = dap_strdup(a_name);
    elemnet->obj_module = a_module;
    LL_APPEND(s_dap_chain_plugins_module_list, elemnet);
}

dap_chain_plugin_list_module_t* dap_chain_plugins_list_get(){
    return s_dap_chain_plugins_module_list;
}

int dap_chain_plugins_list_cmp(dap_chain_plugin_list_module_t *e1, dap_chain_plugin_list_module_t *e2){
    return strcmp(e1->name, e2->name);
}

bool dap_chain_plugins_list_check_load_plugins(dap_chain_plugins_list_char_t *a_list){
    dap_chain_plugins_list_char_t *l_value_from_list = NULL;
    dap_chain_plugin_list_module_t *l_element_from_list_module;
    dap_chain_plugin_list_module_t *l_element_lnk = (dap_chain_plugin_list_module_t*)DAP_NEW(
                dap_chain_plugin_list_module_t);
    if (!l_element_lnk) {
        log_it(L_CRITICAL, "Memory allocation error");
        return false;
    }
    int lenght;
    LL_COUNT(s_dap_chain_plugins_module_list, l_element_from_list_module, lenght);
    if (lenght == 0){
        DAP_FREE(l_element_lnk);
        return false;
    }
    LL_FOREACH(a_list, l_value_from_list){
        l_element_lnk->name = l_value_from_list->value;
        LL_SEARCH(s_dap_chain_plugins_module_list, l_element_from_list_module, l_element_lnk, dap_chain_plugins_list_cmp);
        if (!l_element_from_list_module){
            DAP_FREE(l_element_lnk);
            return false;
        }
    }
    DAP_FREE(l_element_lnk);
    return true;
}

void dap_chain_plugins_list_name_del(const char *a_name){
    dap_chain_plugin_list_module_t *l_plugin;
    dap_chain_plugin_list_module_t *l_tmp;
    bool plugin_searcging = false;
    LL_FOREACH_SAFE(s_dap_chain_plugins_module_list, l_plugin, l_tmp){
        if (strcmp(l_plugin->name, a_name) == 0){
            DAP_FREE(l_plugin->name);
            Py_XDECREF(l_plugin->obj_module);
            LL_DELETE(s_dap_chain_plugins_module_list, l_plugin);
            plugin_searcging = true;
        }
    }
    if (!plugin_searcging){
        log_it(L_WARNING, "Can't find \"%s\" plugin", a_name);
    }
}

int dap_chain_plugins_list_name_cmp(dap_chain_plugin_list_module_t *a_element, const char *a_name){
    return strcmp(a_element->name, a_name);
}

