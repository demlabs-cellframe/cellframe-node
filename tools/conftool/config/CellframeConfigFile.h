#pragma once

#include <algorithm>
#include <string>
#include <iostream>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <vector>
#include <regex>
#include <unordered_map>

#include <memory>
#include <string>
#include <stdexcept>
#include <sstream>
#include <iostream>
#include <iterator>
#include <numeric>
#include "../commands/AbstractCommand.h"
#include "../build_config.h"

namespace fs = std::filesystem;

enum ENetworkConfigType{
    CFG_GENERAL,
    CFG_MAINCHAIN,
    CFG_ZEROCHAIN
};

enum ENetworkConfigState{
    CFG_ON = 1,
    CFG_OFF = 1 << 2,
    CFG_TEMPLATE = 1 << 3,
};

enum EPathConfigType{
    CFG_NODE = 0,
    CFG_NODE_TEMPLATE,
    CFG_NETWORK,
    CFG_NETWORK_TEMPLATE
};

fs::path config_path(const std::string &netname, ENetworkConfigType type, ENetworkConfigState state = CFG_ON); 
fs::path get_config_path(EPathConfigType pathType = CFG_NETWORK); 

struct CellframeConfigurationFile {
    CellframeConfigurationFile(fs::path filepath, int flags = 0);
    
    bool exists(const std::string & group, const std::string & param, std::string *value = nullptr, int *line_no = nullptr, bool *group_exists = nullptr);
    std::string set(const std::string & group, const std::string & param, const std::string &value);
    void replace_placeholders(std::map<std::string, std::string> data);
    bool save();


private:
    fs::path path;
    std::vector<std::string> lines;
    int flags;
};

std::string substitute_variables(const std::string &string);
