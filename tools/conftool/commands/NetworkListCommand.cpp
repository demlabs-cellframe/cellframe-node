#include "NetworkListCommand.h"
#include <stdexcept>
#include <filesystem>

#include "../build_config.h"
#include "../config/CellframeConfigFile.h"

namespace fs = std::filesystem;

CAbstractScriptCommand::Registrar<CNetworkListCommand> net_list_registrar("net_list");

CNetworkListCommand::CNetworkListCommand(std::vector <std::string> cmd_tokens)
    : CAbstractScriptCommand(cmd_tokens)
{   
    if (cmd_tokens.size() >= 2)
        if(cmd_tokens[1] == "on")
        {
            m_state = ON;
        }
        else if(cmd_tokens[1] == "off")
        {
            m_state = OFF;
        }
}


bool CNetworkListCommand::execute(bool non_intercative, int flags)
{
    fs::path directoryPath = get_config_path();
    if(!fs::exists(directoryPath))
    {
        std::cout << "The catalog was not found." << std::endl;
        return false;
    }

    if (!fs::is_directory(directoryPath)) {
        std::cout << "The specified path is not a directory." << std::endl;
        return false;
    }

    std::vector<NetworkInfo> configs;
    const std::string dis = ".dis";
    const std::string cfg = ".cfg";
    for (const auto& entry : fs::directory_iterator(directoryPath))
    {
        if(fs::is_regular_file(entry.status()))
        {
            std::string name = entry.path().filename().string();

            auto removeSubstring = [](std::string& str, const std::string& tuRemove)
            {
                size_t pos = 0;

                while ((pos = str.find(tuRemove, pos)) != std::string::npos) {
                    str.erase(pos, tuRemove.length());
                }
            };

            bool isDis = name.find(dis) != std::string::npos;
            bool isCfg = name.find(cfg) != std::string::npos;

            if((isDis && isCfg)
                && (m_state == ALL || m_state == OFF) )
            {
                removeSubstring(name, cfg + dis);
                configs.push_back({name, "off"});
            }
            else if((!isDis && isCfg)
                     && (m_state == ALL || m_state == ON))
            {
                removeSubstring(name, cfg);
                configs.push_back({name, "on"});
            }
            else if((!isDis && !isCfg)
                     && m_state == ALL)
            {
                configs.push_back({name, "unknown"});
            }
        }
    }

    if(configs.empty())
    {
        std::cout << "No networks were found.";
    }
    else
    {
        for (const auto& item : configs) {
            std::cout << "name: " <<item.networkName << "\t state:" << item.state << std::endl;
        }
    }

    return true; 
}
