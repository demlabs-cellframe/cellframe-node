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
    CellframeConfigurationFile cfg(fs::path{variable_storage["CONFIGS_PATH"]}/"etc"/"cellframe-node.cfg", 0);

    std::string l_path_plugins;
    if (!cfg.exists("plugins", "py_path", &l_path_plugins))
        throw std::invalid_argument("The configuration file does not have a plugins section or it does not have a py_path value.");
    this->pathPlugin = l_path_plugins;

    this->action = a_cmd_tokens[1];
    //Exchange Params
    for (int i = 2; i < a_cmd_tokens.size(); i++) {
        this->params.push_back(a_cmd_tokens[i]);
    }

}

bool CPluginsCommand::execute(bool non_interactive, int flags) {
    this->flags = flags;

    if (flags & F_VERBOSE) std::cout << "[VC] Path to the directory with plugins '" << this->pathPlugin << "'" << std::endl;

    if (this->action == "install") {
    }

    if (this->action == "ensure") {
    }

    if (this->action == "update") {
    }

    if (this->action == "remove") return actionRemovePlugin();

    if (this->action == "list") return actionListPlugin();

    throw std::invalid_argument("Undefined action for command plugins");
}


std::vector<std::string> CPluginsCommand::getListPlugins() {
    return getListPlugins(this->pathPlugin);
}

std::vector<std::string> CPluginsCommand::getListPlugins(std::filesystem::path path) {
    std::vector<std::string> ret;
    fs::directory_iterator l_plugins_dir(path);
    for (const fs::directory_entry &entry : l_plugins_dir) {
        if (!entry.is_directory()) continue;
        fs::path l_plugin_path = entry.path();
        fs::path l_manifest_file_path = fs::path{l_plugin_path}/"manifest.json";
        if (!fs::exists(l_manifest_file_path)) continue;
        ret.push_back(entry.path().filename().generic_string());

    }
    return ret;
}

bool CPluginsCommand::actionListPlugin() {
    std::vector<std::string> listPlugins = getListPlugins(this->pathPlugin);
    std::cout << "List plugins (" << listPlugins.size() <<"):" << std::endl;
    for (auto &entry : listPlugins){
        std::cout << "\t" << entry << "\n";
    }
    return true;
}

bool CPluginsCommand::actionRemovePlugin() {
    if (this->params.size() == 0)
        throw  std::invalid_argument("Not enough arguments to execute the command to remove the plugin.");
    std::string  a_name_plugin = this->params[0];
    std::vector<std::string> listPlugins = getListPlugins();
    for (std::string &l_name_plugin : listPlugins) {
        if (l_name_plugin != a_name_plugin) continue;
        std::error_code err;
        const std::uintmax_t n(fs::remove_all(this->pathPlugin/a_name_plugin, err));
        if (!err){
            std::cout << "Plugin '" << a_name_plugin << "' plugin removed. Removed: " << n << " elements." << std::endl;
            return true;
        } else {
            std::cout << "Can't remove '" << a_name_plugin << "' plugin. Error: " << err.message() << std::endl;
            return false;
        }
    }
    std::cout << "Can't find '" << a_name_plugin << "' plugin." << std::endl;
    return false;
}