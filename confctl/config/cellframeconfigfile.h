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
#include "../commands/abstractcommand.h"
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

fs::path config_path(const std::string &netname, ENetworkConfigType type, ENetworkConfigState state = CFG_ON); 

struct CellframeConfigurationFile {
    CellframeConfigurationFile(fs::path filepath, int flags = 0);
    
    bool exists(const std::string & group, const std::string & param, std::string *value = nullptr, int *line_no = nullptr);
    std::string set(const std::string & group, const std::string & param, const std::string &value);
    bool save();


    private:
        fs::path path;
        std::vector<std::string> lines;
        int flags;
};