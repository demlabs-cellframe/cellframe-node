/*
 Copyright (c) 2017-2018 (c) Project "DeM Labs Inc" https://github.com/demlabsinc
  All rights reserved.

 This file is part of DAP (Deus Applications Prototypes) the open source project

    DAP (Deus Applicaions Prototypes) is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    DAP is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with any DAP based project.  If not, see <http://www.gnu.org/licenses/>.
*/

#include "node_manager.h"
#include "dap_enc_http.h"
#include "dap_http.h"
#include "dap_http_simple.h"
#include "stream.h"
#include "stream_ch_pkt.h"

#define LOG_TAG "node_manager"


void channel_new(struct stream_ch* ch,void* arg)
{
    log_it(L_INFO,"Channel new");
}


void channel_delete(struct stream_ch* ch,void* arg)
{
    log_it(L_INFO,"Channel delete");
}

void channel_packet_in(struct stream_ch* ch,void* arg)
{
    stream_ch_pkt_t * ch_pkt = arg;
    char* data = (char*)malloc(ch_pkt->hdr.size);
    memcpy(data,ch_pkt->data,ch_pkt->hdr.size);
    log_it(L_DEBUG,"Income data: %s from %s \n",data,itoa(ch->stream->conn_udp->host_key));
    stream_ch_set_ready_to_write(ch,false);
    stream_ch_pkt_write_f(ch, 1, "ping");
    stream_ch_set_ready_to_write(ch,true);
}

void channel_packet_out(struct stream_ch* ch,void* arg)
{
    stream_ch_set_ready_to_write(ch,false);
}


void client_new(dap_server_client_t *client,void * arg){
    log_it(L_INFO,"Client connected");
}

void client_read(dap_server_client_t *client,void * arg){
    log_it(L_INFO,"Client read %u",client->buf_in_size);
    unsigned char* data = (char*)malloc(client->buf_in_size);
    data[client->buf_in_size] = 0;
    if(client->_ready_to_read)
    {        
        dap_client_read(client,data,client->buf_in_size);
    }
    char outbox[] = "ping";
    dap_client_write(client,outbox,strlen(outbox));
    dap_udp_client_ready_to_write(client,true);
    free(data);
}

void client_write(dap_server_client_t *client,void * arg)
{
    log_it(L_DEBUG,"Client write");
}

void client_disconnect(dap_server_client_t *client,void * arg)
{
    log_it(L_DEBUG,"Client disconnect");
}

/**
 * @brief node_manager_init Init all modules
 * @return Zero if ok or error code
 */
int node_manager_init(){
    if(dap_common_init("build/log.txt")!=0){
        log_it(L_CRITICAL,"Can't init common functions module");
        return -2;
    }
    if(dap_config_init("build/config")!=0){
        log_it(L_CRITICAL,"Can't init configurations module");
        return -1;
    }
    if(dap_enc_init()!=0){
        log_it(L_CRITICAL,"Can't init encryption module");
        return -56;
    }
    if(dap_enc_key_init()!=0){
        log_it(L_CRITICAL,"Can't init encryption key module");
        return -57;
    }
    if(dap_server_init(0)!=0){
        log_it(L_CRITICAL,"Can't init udp server module");
        return -4;
    }

    stream_init();
    stream_session_init();
    dap_http_init();
    dap_http_simple_module_init();
    return 0;
}

/**
 * @brief dap_server_deinit Deinit modules
 */
void node_manager_deinit(){
    stream_session_deinit();
    dap_server_deinit();
    dap_server_client_deinit();
    dap_enc_key_deinit();
    dap_enc_deinit();
    dap_common_deinit();
    dap_config_deinit();
}

/**
 * @brief new_node_manager Create node manager structure
 * @return Manager instance
 */
node_manager_t* new_node_manager(char* config_file){
    node_manager_t* manager = (node_manager_t*)malloc(sizeof(node_manager_t));
    manager->l_config = dap_config_open(config_file);
    return manager;
}

/**
 * @brief node_manager_start Start node work
 * @param manager Manager instance
 */
void node_manager_start(node_manager_t* manager){
    int port = 0;
    if (manager->l_config)
        port = atoi(dap_config_get_item_str(manager->l_config, "general", "port"));
    else{
        log_it(L_CRITICAL,"Unable to find config file");
        return;
    }
    if(port == 0){
        log_it(L_CRITICAL,"Unable to read port value");
        return;
    }
    dap_server_t* sh = manager->sh;
    sh = dap_udp_server_listen(port);
    sh->client_read_callback = *client_read;
    sh->client_write_callback = *client_write;
    sh->client_new_callback = *client_new;
    sh->client_delete_callback = *client_disconnect;
    dap_udp_server_loop(sh);
    dap_udp_server_delete(sh);

}

void node_manager_start_stream(){
    dap_server_t* server = dap_server_listen("localhost",56001,DAP_SERVER_TCP);
    dap_http_new(server,"KelvinNode");
    enc_http_add_proc(DAP_HTTP(server),"/handshake");
    dap_server_loop(server);
}

