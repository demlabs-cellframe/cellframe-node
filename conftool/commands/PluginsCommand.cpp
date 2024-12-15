//
// Created by blus on 02.12.24.
//

#include <valarray>
#include "PluginsCommand.h"
#include "../config/CellframeConfigFile.h"
#include "zip.h"
#include "../rapidjson/rapidjson.h"
#include "../rapidjson/document.h"
#include "../rapidjson/filereadstream.h"
#include "../rapidjson/istreamwrapper.h"

namespace fs = std::filesystem;
namespace rj = rapidjson;

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

    if (this->action == "install") return actionInstallPlugin();

    if (this->action == "ensure") return actionEnsurePlugin();

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

bool CPluginsCommand::actionInstallPlugin() {
    if (this->params.size() == 0)
        throw  std::invalid_argument("Not enough arguments to execute the command to install the plugin.");
    std::string source_plugin = this->params[0];
    //Check git or zip
    fs::path l_path = source_plugin;
    bool isZip = l_path.extension() == ".zip";
    bool isGit = l_path.extension() == ".git";
//    if (!isGit) {
//    }
    if (isZip) {
        if (!UnpackZip(l_path, this->pathPlugin, l_path.filename().generic_string())) {
            std::cout << "Can't decompress archive '" << l_path << "'" << std::endl;
            return false;
        }
        std::cout << "Archive unpacking complete." << std::endl;
    }
    if (!CPluginsCommand::postInstallAction(this->pathPlugin/l_path.filename().generic_string())){
        std::cout << "Error in post install process" << std::endl;
        fs::remove_all(this->pathPlugin/l_path.filename().generic_string());
        return false;
    }
    std::cout << "Install plugin completed." << std::endl;
    return true;
}

bool CPluginsCommand::UnpackZip(std::filesystem::path archive_path, std::filesystem::path dist_path, std::string dir) {
    if (!fs::exists(archive_path)) return false;
    if (!fs::exists(dist_path)) return false;
    if (fs::exists(dist_path/dir)) return false;
    fs::create_directories(dist_path/dir);
    if (this->flags & F_VERBOSE)
        std::cout << "[VC] libzip version: " << zip_libzip_version() << std::endl;
    int err_code = 0;
    zip_t *zip = zip_open(archive_path.c_str(), ZIP_RDONLY, &err_code);
    if (!zip) {
        zip_error_t error;
        zip_error_init_with_code(&error, err_code);
        std::cout << "Can't open zip archive " << archive_path << "Error code:" << zip_error_strerror(&error);
        zip_error_fini(&error);
        return false;
    }
    zip_int64_t countFilesInArchive = zip_get_num_entries(zip, ZIP_FL_UNCHANGED);
    if (this->flags & F_VERBOSE)
        std::cout << "[VC] Count files in archive: " << countFilesInArchive << std::endl;
    for (zip_int64_t i = 0; i < countFilesInArchive;i++) {
        zip_file_t *zip_file = zip_fopen_index(zip, i, ZIP_FL_UNCHANGED);
        zip_stat_t fileinfo;
        int status = zip_stat_index(zip, i, ZIP_FL_ENC_GUESS, &fileinfo);
        if (status == 0)
        {
            if (!fileinfo.size) {
                fs::create_directory(dist_path/dir/fileinfo.name);
                continue;
            }
            char *buffer = (char*)malloc(fileinfo.size);
            zip_fread(zip_file, buffer, fileinfo.size);
            FILE *file = fopen((dist_path/dir/fileinfo.name).c_str(), "wb");
            fwrite(buffer, fileinfo.size, 1, file);
            fclose(file);
            if (this->flags & F_VERBOSE)
                std::cout << "[VC] Unpack file " << fileinfo.name << std::endl;
        }
        else
        {
            fs::remove_all(dist_path/dir);
            std::cout << "Error decompression: " << zip_error_strerror(zip_get_error(zip)) << std::endl;
            return false;
        }
    }
    zip_close(zip);
    return true;
}

bool CPluginsCommand::postInstallAction(std::filesystem::path plugin_path) {
    bool enabledInstallDep = true;
    if (this->params.size() == 2 && this->params[1] == "no_dep") {
        enabledInstallDep = false;
    }
    if (!fs::exists(plugin_path/"manifest.json")) {
        std::cout << "Manifest file not found in " << plugin_path << std::endl;
        return false;
    }
    std::ifstream manifestFile(plugin_path/"manifest.json");
    rapidjson::IStreamWrapper isw {manifestFile};
    rapidjson::Document manifest;
    manifest.ParseStream(isw);
    if (manifest.HasParseError()) {
        std::cout << "Error parsed manifest.json file";
        if (this->flags & F_VERBOSE)
            std::cout << "Error: " << manifest.GetParseError()  << std::endl <<
            "Offset: " << manifest.GetErrorOffset() << std::endl;
        return false;
    }
    const char *namePlugin = manifest["name"].GetString();
    const char *typePlugin = manifest["type"].GetString();
    fs::path newPath = plugin_path;
    newPath.remove_filename().append(namePlugin);
    fs::rename(plugin_path, newPath);

    if (!enabledInstallDep || (!fs::exists(newPath / "requirements.txt") || strcmp(typePlugin, "python") != 0)) return true;
    fs::path pathToPip = fs::path{variable_storage["CONFIGS_PATH"]}/"python"/"bin"/"pip3";
    std::string cmd = pathToPip.generic_string() + " install -r " + (newPath / "requirements.txt").generic_string();
    std::system(cmd.c_str());
    return true;
}

bool CPluginsCommand::actionEnsurePlugin() {
    if (this->params.size() == 0)
        throw  std::invalid_argument("Not enough arguments to execute the command enabling or disabling plugins.");
    bool activateWorkWithPlugin = false;
    if (this->params[0] == "on") {
        activateWorkWithPlugin = true;
    } else if (this->params[0] == "off") {
        activateWorkWithPlugin = false;
    } else {
        throw  std::invalid_argument("The activation status for working with plugins is not set, you can set it to on or off.");
    }
    CellframeConfigurationFile cfg(fs::path{variable_storage["CONFIGS_PATH"]}/"etc"/"cellframe-node.cfg", 0);
    if (!cfg.exists("plugins", "enabled", nullptr))
        throw std::invalid_argument("The configuration file does not have a plugins section or it does not have a enabled value.");
    if (!cfg.exists("plugins", "py_load", nullptr))
        throw std::invalid_argument("The configuration file does not have a plugins section or it does not have a py_load value.");
    if (activateWorkWithPlugin) {
        cfg.set("plugins", "enabled", "true");
        cfg.set("plugins", "py_load", "true");
    } else {
        cfg.set("plugins", "enabled", "false");
        cfg.set("plugins", "py_load", "false");
    }
    cfg.save();
    std::cout << "Work with plugins in the " << (activateWorkWithPlugin ? "activated" : "deactivated") << " states has been established." << std::endl;
    return true;
}