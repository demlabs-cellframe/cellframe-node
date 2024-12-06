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

    this->action = a_cmd_tokens[1];
    //Exchange Params
    for (int i = 2; i < a_cmd_tokens.size(); i++) {
        this->params.push_back(a_cmd_tokens[i]);
    }
//    std::iterator<std::string> iter = a_cmd_tokens.begin(), a_cmd_tokens.end()

//    this->params = std::rotate_copy(a_cmd_tokens.begin(), a_cmd_tokens.end(),)

}

bool CPluginsCommand::execute(bool non_interactive, int flags) {
    this->flags = flags;
    CellframeConfigurationFile cfg(fs::path{variable_storage["CONFIGS_PATH"]}/"etc"/"cellframe-node.cfg", flags);

    std::string l_path_plugins;
    if (!cfg.exists("plugins", "py_path", &l_path_plugins))
        throw std::invalid_argument("The configuration file does not have a plugins section or it does not have a py_path value.");
    this->pathPlugin = l_path_plugins;
    if (flags & F_VERBOSE) std::cout << "[VC] Path to the directory with plugins '" << l_path_plugins << "'" << std::endl;
    if (this->action == "install") {
    } else if (this->action == "ensure") {
    } else if (this->action == "update") {
    } else if (this->action == "remove") {
        if (this->params.size() == 0)
            throw  std::invalid_argument("Not enough arguments to execute the command to remove the plugin.");
        return actionRemovePlugin(params[0]);
    } else if (this->action == "list") {
        std::vector<std::string> listPlugins = getListPlugins(l_path_plugins);
        std::cout << "List plugins (" << listPlugins.size() <<"):" << std::endl;
        for (auto &entry : listPlugins){
            std::cout << "\t" << entry << "\n";
        }
        return true;
    } else {
        throw std::invalid_argument("Undefined action for command plugins");
    }
    return false;
}


std::vector<std::string> CPluginsCommand::getListPlugins() {
    return getListPlugins(this->pathPlugin);
}

std::vector<std::string> CPluginsCommand::getListPlugins(std::filesystem::path path) {
    std::vector<std::string> ret;
    fs::directory_iterator l_plugins_dir(path);
    for (const fs::directory_entry &entry : l_plugins_dir) {
        if (entry.is_directory()) {
            fs::path l_plugin_path = entry.path();
            fs::path l_manifest_file_path = fs::path{l_plugin_path}/"manifest.json";
            if (fs::exists(l_manifest_file_path)) {
                ret.push_back(entry.path().filename().generic_string());
            }
        }
    }
    return ret;
}

bool CPluginsCommand::actionRemovePlugin(std::string a_name_plugin) {
    std::vector<std::string> listPlugins = getListPlugins();
    for (std::string l_name_plugin : listPlugins) {
        if (l_name_plugin == a_name_plugin) {
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
    }
    std::cout << "Can't find '" << a_name_plugin << "' plugin." << std::endl;
    return false;
}