//
// Created by dpuzyrkov on 9/17/24.
//

#ifndef NODE_CELLFRAME_NODE_CONFIG_H
#define NODE_CELLFRAME_NODE_CONFIG_H
#include "commands/AbstractCommand.h"

namespace conftool {

    void populate_variables(std::string basepath);//must be specificly called befor init_configs
    int init_configs(std::string init_file_name, int flags, int non_interactive);
    std::unique_ptr<CAbstractScriptCommand> parse_line_to_cmd(std::string line, int line_no, int flags);
    bool run_commands(std::vector <std::unique_ptr<CAbstractScriptCommand>> &commands, int interactive, int flags);
}
#endif //NODE_CELLFRAME_NODE_CONFIG_H
