#include "AbstractCommand.h"

enum CPluginsActions{
        ENSURE,
        INSTALL,
        UPDATE,
        LIST,
        REMOVE,
        UNDEFINED
};


class CPluginsCommand : public CAbstractScriptCommand{
public:
    CPluginsCommand(std::vector <std::string> a_cmd_tokens);
    static std::unique_ptr<CAbstractScriptCommand> create(std::vector <std::string> cmd_tokens) { return std::make_unique<CPluginsCommand>(cmd_tokens); }
    bool execute(bool non_interactive, int flags);
private:
    CPluginsActions action;
    union {
        struct {
            char *source_path;
            bool enabled_install_dependencies;
            bool l2;
        } install;
        struct {
            bool binary;
        } ensure;
        struct {} update;
        struct {} remove;
    };
    std::string python_plugin_path;
    std::string binary_plugin_path;
};