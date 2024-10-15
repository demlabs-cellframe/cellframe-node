//
// Created by dpuzyrkov on 9/17/24.
//


#ifndef NODE_CELLFRAME_NODE_H
#define NODE_CELLFRAME_NODE_H
extern "C"
{

int main( int argc, const char **argv );
void set_global_sys_dir(const char *dir);
typedef bool (*dap_notify_data_user_callback_t)(const char *data);
void dap_notify_data_set_user_callback(dap_notify_data_user_callback_t callback);
char *dap_cli_exec(int argc, char **argv);

};
#endif //NODE_CELLFRAME_NODE_H
