#include "AbstractCommand.h"
//#include "../miniz/miniz.h"

class CPluginsCommand : public CAbstractScriptCommand{
public:
    CPluginsCommand(std::vector <std::string> a_cmd_tokens);
    static std::unique_ptr<CAbstractScriptCommand> create(std::vector <std::string> cmd_tokens) { return std::make_unique<CPluginsCommand>(cmd_tokens); }
    bool execute(bool non_interactive, int flags);
private:
    std::string action;
    std::vector<std::string> params;
    int flags;
    std::filesystem::path pathPlugin;
    std::vector<std::string> getListPlugins();
    std::vector<std::string> getListPlugins(std::filesystem::path path);
    bool actionListPlugin();
    bool actionRemovePlugin();
    bool actionInstallPlugin();
    bool UnpackZip(std::filesystem::path archive_path, std::filesystem::path dist_path, std::string dir);
};