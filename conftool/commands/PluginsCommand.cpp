//
// Created by blus on 02.12.24.
//

#include "PluginsCommand.h"
#include "../config/CellframeConfigFile.h"

namespace fs = std::filesystem;

CAbstractScriptCommand::Registrar<CPluginsCommand> plugins_registrar("plugins");

CPluginsCommand::CPluginsCommand(std::vector <std::string> a_cmd_tokens) : CAbstractScriptCommand(a_cmd_tokens) {
    if (a_cmd_tokens.size() < 2)
        throw std::invalid_argument("plugins command require action argument");

    std::string l_command = a_cmd_tokens[1];
    if (l_command == "install") {
        this->action = CPluginsActions::INSTALL;
    } else if (l_command == "ensure") {
        this->action = CPluginsActions::ENSURE;
    } else if (l_command == "update") {
        this->action = CPluginsActions::UPDATE;
    } else if (l_command == "remove") {
        this->action = CPluginsActions::REMOVE;
    } else if (l_command == "list") {
        this->action = CPluginsActions::LIST;
    } else {
        this->action = CPluginsActions::UNDEFINED;
    }
//    if (CellframeConfigurationFile::exists("",""))
//    this->
}

bool CPluginsCommand::execute(bool non_interactive, int flags) {
    CellframeConfigurationFile cfg(fs::path{variable_storage["CONFIGS_PATH"]}/"etc"/"cellframe-node.cfg", flags);

    std::string l_path_plugins;
    if (!cfg.exists("plugins", "py_path", &l_path_plugins))
        throw std::invalid_argument("The configuration file does not have a plugins section or it does not have a py_path value.");
    if (flags & F_VERBOSE) std::cout << "[VC] Path to the directory with plugins '" << l_path_plugins << "'" << std::endl;
    switch (this->action) {
        case LIST: {
            if (!fs::exists(l_path_plugins)) {
                std::cout << "The directory with plugins is missing, try to activate work with plugins again."
                          << std::endl;
                return false;
            }
            std::cout << "List plugins: " << std::endl;
            fs::directory_iterator l_plugins_dir(l_path_plugins);
            for (const fs::directory_entry &entry : l_plugins_dir) {
                if (entry.is_directory()) {
                    fs::path l_plugin_path = entry.path();
                    fs::path l_manifest_file_path = fs::path{l_plugin_path}/"manifest.json";
                    if (!fs::exists(l_manifest_file_path)) {
                        std::cout << "In directory plugin '" << l_plugin_path << "' absent manifest plugin" << std::endl;
                    }
                    std::cout << "\t " << entry.path().filename().generic_string() << std::endl;
                }
            }
        } break;
        default: {
            throw std::invalid_argument("Undefined action for command plugins");
        }break;
    }
    return false;
}
