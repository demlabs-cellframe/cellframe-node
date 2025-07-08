#include "dap_common.h"
#include "dap_strfuncs.h"
#include "json-c/json_object.h"
#include "json-c/json_util.h"
#include "dap_list.h"

#include "dap_chain_plugins_manifest.h"

#define LOG_TAG "dap_chain_plugins_manifest"

dap_chain_plugins_list_manifest_t* s_manifests = NULL;

void dap_chain_plugins_list_char_delete_all(dap_chain_plugins_list_char_t *a_list){
    dap_chain_plugins_list_char_t *l_element;
    dap_chain_plugins_list_char_t *l_tmp;
    LL_FOREACH_SAFE(a_list, l_element, l_tmp){
        DAP_FREE(l_element->value);
        LL_DELETE(a_list, l_element);
    }
}

dap_chain_plugins_list_manifest_t *dap_chain_plugins_manifest_new(const char *a_name, const char *a_version,
                                                                  const dap_chain_plugins_list_char_t *a_dep,
                                                                  const char *a_author,
                                                                  const char *a_description){
    dap_chain_plugins_list_manifest_t *l_man = (dap_chain_plugins_list_manifest_t*)DAP_NEW(dap_chain_plugins_list_manifest_t);
    if (!l_man) {
        log_it(L_CRITICAL, "Memory allocation error");
        return NULL;
    }
    l_man->name = dap_strdup(a_name);
    l_man->author = dap_strdup(a_author);
    l_man->version = dap_strdup(a_version);
    l_man->description = dap_strdup(a_description);
    l_man->dependencies = NULL;
    //copy informantion from dep to man->dependencies
    int l_len_dep;
    dap_chain_plugins_list_char_t *l_char_t;
    LL_COUNT((dap_chain_plugins_list_char_t*)a_dep, l_char_t, l_len_dep);
    LL_FOREACH((dap_chain_plugins_list_char_t*)a_dep, l_char_t){
        LL_APPEND(l_man->dependencies, l_char_t);
    }
    l_man->dependencies = (dap_chain_plugins_list_char_t*)a_dep;
    return l_man;
}

static dap_chain_plugins_list_char_t* JSON_array_to_dap_list_char(json_object *a_j_obj){
    dap_chain_plugins_list_char_t *l_list = NULL;
    dap_chain_plugins_list_char_t *l_element = NULL;
    for (size_t i = 0; i < (size_t)json_object_array_length(a_j_obj); i++){
        l_element = (dap_chain_plugins_list_char_t*)DAP_NEW(dap_chain_plugins_list_char_t);
        if (!l_element) {
            log_it(L_CRITICAL, "Memory allocation error");
            return l_list;
        }
        l_element->value = dap_strdup(json_object_get_string(json_object_array_get_idx(a_j_obj, i)));
        LL_APPEND(l_list, l_element);
    }
    return l_list;
}

void dap_chain_plugins_manifest_list_create(){
    s_manifests = NULL;
}

int dap_chain_plugins_manifest_name_cmp(dap_chain_plugins_list_manifest_t *man, const char *name){
    return dap_strcmp(man->name, name);
}

dap_chain_plugins_list_manifest_t* dap_chain_plugins_add_manifest_from_file(const char *file_path){
    
    // Open json file_path
    struct json_object *l_json = json_object_from_file(file_path);
    if(!l_json) {
        log_it(L_ERROR, "Can't open manifest file on path: %s", file_path);
        return NULL;
    }
    if(!json_object_is_type(l_json, json_type_object)) {
        log_it(L_ERROR, "Invalid manifest structure, shoud be a json object: %s", file_path);
        DAP_DELETE(l_json);
        return NULL;
    }

    json_object *j_name = json_object_object_get(l_json, "name");
    json_object *j_version = json_object_object_get(l_json, "version");;
    json_object *j_dependencies = json_object_object_get(l_json, "dependencies");
    json_object *j_author = json_object_object_get(l_json, "author");
    json_object *j_description = json_object_object_get(l_json, "description");

    const char *name, *version, *author, *description;    
    name = json_object_get_string(j_name);
    version = json_object_get_string(j_version);
    author = json_object_get_string(j_author);
    description = json_object_get_string(j_description);
    
    if (!name || !version || !author || !description)
    {
        log_it(L_ERROR, "Invalid manifest structure, insuficient fields %s", file_path);
        return NULL;
    }

    dap_chain_plugins_list_char_t *dep = JSON_array_to_dap_list_char(j_dependencies);
    dap_chain_plugins_list_manifest_t *manifest = dap_chain_plugins_manifest_new(name, version, dep, author, description);
    dap_chain_plugins_list_char_delete_all(dep);
    return manifest;
}

void dap_chain_plugins_manifest_list_add_manifest(dap_chain_plugins_list_manifest_t *man){
    LL_APPEND(s_manifests, man);
}

dap_chain_plugins_list_manifest_t* dap_chain_plugins_manifests_get_list(){
    return s_manifests;
}

dap_chain_plugins_list_manifest_t *dap_chain_plugins_manifest_list_get_name(const char *a_name){
    dap_chain_plugins_list_manifest_t *l_element;
    LL_SEARCH(s_manifests, l_element, a_name, dap_chain_plugins_manifest_name_cmp);
    return l_element;
}

char* dap_chain_plugins_manifests_get_list_dependencyes(dap_chain_plugins_list_manifest_t *a_element){
    if (a_element->dependencies == NULL) {
        return NULL;
    } else {
        char *l_result = "";
        dap_chain_plugins_list_char_t *l_el;
        int l_max_count_list = 0;
        LL_COUNT(a_element->dependencies, l_el, l_max_count_list);
        int l_count_list = 1;
        LL_FOREACH(a_element->dependencies, l_el){
            if (l_count_list != l_max_count_list)
                l_result = dap_strjoin(NULL, l_result, l_el->value, ", ", NULL);
            else
                l_result = dap_strjoin(NULL, l_result, l_el->value, NULL);
        }
        return l_result;
    }
}

bool dap_chain_plugins_manifest_list_add_from_file(const char *a_file_path){
    dap_chain_plugins_list_manifest_t *l_manifest = dap_chain_plugins_add_manifest_from_file(a_file_path);
    if (l_manifest == NULL)
        return false;
    dap_chain_plugins_manifest_list_add_manifest(l_manifest);
    return true;
}

bool dap_chain_plugins_manifest_list_delete_name(const char *a_name){
    dap_chain_plugins_list_manifest_t *l_element;
    LL_SEARCH(s_manifests, l_element, a_name, dap_chain_plugins_manifest_name_cmp);
    if (l_element == NULL)
        return false;
    DAP_FREE(l_element->name);
    DAP_FREE(l_element->version);
    DAP_FREE(l_element->author);
    DAP_FREE(l_element->description);
    dap_chain_plugins_list_char_delete_all(l_element->dependencies);
    LL_DELETE(s_manifests, l_element);
    return true;
}
void dap_chain_plugins_manifest_list_delete_all(void){
    dap_chain_plugins_list_manifest_t *l_element;
    dap_chain_plugins_list_manifest_t *tmp;
    LL_FOREACH_SAFE(s_manifests, l_element, tmp){
        DAP_FREE(l_element->name);
        DAP_FREE(l_element->version);
        DAP_FREE(l_element->author);
        DAP_FREE(l_element->description);
        dap_chain_plugins_list_char_delete_all(l_element->dependencies);
        LL_DELETE(s_manifests, l_element);
    }
}
