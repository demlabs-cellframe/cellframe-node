/*
 * Authors:
 * Dmitriy A. Gearasimov <kahovski@gmail.com>
 * DeM Labs Inc.   https://demlabs.net
 * DeM Labs Open source community https://github.com/demlabsinc
 * Copyright  (c) 2017-2019
 * All rights reserved.

 This file is part of DAP (Deus Applications Prototypes) the open source project

 DAP (Deus Applicaions Prototypes) is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 DAP is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with any DAP based project.  If not, see <http://www.gnu.org/licenses/>.
 */

//#include <dap_client.h>
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <sys/socket.h>
#include "dap_common.h"
#include "dap_chain_node_cli.h" // for UNIX_SOCKET_FILE
#include "main_node_cli_net.h"

/**
 * Add to one array another one
 *
 * memory - destination array of data
 * add_mem - source array of data
 * memory_len - memory array size
 * add_size - add_mem array size
 */
static int add_mem_data(uint8_t **memory, size_t *memory_len, char *add_mem, size_t add_size)
{
    *memory = (char*) realloc(*memory, *memory_len + add_size + 1);
    //out of memory!
    if(*memory == NULL) {
        //printf("not enough memory (realloc returned NULL)\n");
        return 0;
    }
    if(add_mem) {
        memcpy((*memory + *memory_len), add_mem, add_size);
        // increase the received bytes number
        *memory_len += add_size;
        // zero out the last byte
        *(*memory + *memory_len) = 0;
    }
    return add_size;
}

//callback functions to receive header
static size_t WriteHttpMemoryHeadCallback(void *contents, size_t size, size_t nmemb, cmd_state *cmd)
{
    if(!cmd)
        return 0;
    //printf("[header] %s len=%d\n", contents, size * nmemb);
    const char *head_str = "Content-Length:";
    int len_str = strlen(head_str);
    if(!strncasecmp(contents, head_str, len_str)) {
        cmd->cmd_res_len = atoi((contents + len_str));
        cmd->cmd_res_cur = 0;
        cmd->cmd_res = DAP_NEW_Z_SIZE(char, cmd->cmd_res_len + 1);
    }
    return size * nmemb;
}

// callback function to receive data
static size_t WriteHttpMemoryCallback(void *contents, size_t size, size_t nmemb, cmd_state *cmd)
{
    //printf("[data] %s len=%d\n", contents, size * nmemb);
    if(!cmd)
        return 0;
    // add received data to body
    memcpy(cmd->cmd_res + cmd->cmd_res_cur, contents, size * nmemb);
    cmd->cmd_res_cur += size * nmemb;
    return size * nmemb;
}

/**
 * Connect to node unix socket server
 *
 * return struct connect_param if connect established, else NULL
 */
connect_param* node_cli_connect(void)
{
    curl_global_init(CURL_GLOBAL_DEFAULT);
    connect_param *param = DAP_NEW_Z(connect_param);
    CURL *curl_handle = curl_easy_init();
    int ret = curl_easy_setopt(curl_handle, CURLOPT_UNIX_SOCKET_PATH, UNIX_SOCKET_FILE); // unix socket mode
    curl_easy_setopt(curl_handle, CURLOPT_TIMEOUT, 60L); // complete within 60 seconds
    ret = curl_easy_setopt(curl_handle, CURLOPT_CONNECT_ONLY, 1L); // connection only
    ret = curl_easy_setopt(curl_handle, CURLOPT_URL, "http:/localhost/connect");
// execute request
    ret = curl_easy_perform(curl_handle);
    if(!ret)
    {
        param->curl = curl_handle;
        curl_easy_setopt(curl_handle, CURLOPT_CONNECT_ONLY, 0L); // disable mode - connection only
    }
    else
    {
        curl_easy_cleanup(curl_handle);
        DAP_DELETE(param);
        param = NULL;
    }
    return param;
}

/**
 * Send request to kelvin-node
 *
 * return 0 if OK, else error code
 */
int node_cli_post_command(connect_param *conn, cmd_state *cmd)
{
    if(!conn || !conn->curl || !cmd || !cmd->cmd_name)
            {
        assert(0);
        return -1;
    }
    CURLcode ret;
    CURL *curl = conn->curl;

    ret = curl_easy_setopt(curl, CURLOPT_HEADER, 0L); // don't get header in the body
    //ret = curl_easy_setopt(curl, CURLOPT_ACCEPT_ENCODING, "gzip, deflate"); // allow receive of compressed data
    //callback functions to receive data
    ret = curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteHttpMemoryCallback); // callback for the data read
    //callback functions to receive header
    ret = curl_easy_setopt(curl, CURLOPT_HEADERFUNCTION, WriteHttpMemoryHeadCallback); // callback for the header read
    // passing a parameter to the callback function
    ret = curl_easy_setopt(curl, CURLOPT_WRITEDATA, (void * )cmd);
    ret = curl_easy_setopt(curl, CURLOPT_HEADERDATA, (void * )cmd);
    ret = curl_easy_setopt(curl, CURLOPT_USERAGENT, "kelvin-console 1.0");

    char *post_data = NULL;
    ret = curl_easy_setopt(curl, CURLOPT_POST, 1); // POST request - optional if CURLOPT_POSTFIELDS will be

    size_t post_data_len = 0;
    add_mem_data((uint8_t**) &post_data, &post_data_len, cmd->cmd_name, strlen(cmd->cmd_name));
    if(cmd->cmd_param) {
        for(int i = 0; i < cmd->cmd_param_count; i++) {
            if(cmd->cmd_param[i]) {
                add_mem_data((uint8_t**) &post_data, &post_data_len, "\r\n", 2);
                add_mem_data((uint8_t**) &post_data, &post_data_len, cmd->cmd_param[i], strlen(cmd->cmd_param[i]));
            }
        }
    }
        add_mem_data((uint8_t**) &post_data, &post_data_len, "\r\n\r\n", 4);
        if(post_data)
            ret = curl_easy_setopt(curl, CURLOPT_POSTFIELDS, post_data); // data for POST request
        if(post_data_len >= 0)
            ret = curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, (long )post_data_len); // if need a lot to send: CURLOPT_POSTFIELDSIZE_LARGE
        // sending request and receiving the http page (filling cmd)
        //printf("cmd='%s'\n", cmd->cmd_name);
        ret = curl_easy_perform(curl); // curl_easy_send
        //printf("res=%s(err_code=%d) ret='%s'\n", (!ret) ? "OK" : "Err", ret, (cmd->cmd_res) ? cmd->cmd_res : "-");
        if(ret != CURLE_OK)
            printf("Error (err_code=%d)\n", ret);
        printf("%s\n", (cmd->cmd_res) ? cmd->cmd_res : "no response");
        DAP_DELETE(post_data);
        return ret;
    //}
    //else
    //    printf("%s\n", "no parameters");
    return -1;
}

int node_cli_desconnect(connect_param *param)
{
    if(param) {
        if(param->curl)
            curl_easy_cleanup(param->curl);
        DAP_DELETE(param);
    }

    curl_global_cleanup();
}
