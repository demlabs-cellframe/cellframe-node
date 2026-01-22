#include "FromTemplateCommand.h"
#include <stdexcept>
#include <filesystem>

#include "../build_config.h"
#include "../config/CellframeConfigFile.h"

namespace fs = std::filesystem;

CAbstractScriptCommand::Registrar<CFromTemplateCommand> tmplt_registrar("fromtemplate");

CFromTemplateCommand::CFromTemplateCommand(std::vector <std::string> cmd_tokens): CAbstractScriptCommand(cmd_tokens)
{   
 if (cmd_tokens.size() <= 2)
        throw std::invalid_argument("config command invalid numbers of arguments");
    
    this->cfg_name = cmd_tokens[1];

    //check if config name accetable
    fs::path net_cfg_template_path = config_path(this->cfg_name, CFG_GENERAL, CFG_TEMPLATE);
    if (this->cfg_name != "cellframe-node" && !fs::exists(net_cfg_template_path))
        throw std::invalid_argument("config_cmd: config  not exitst");

    this->action = cmd_tokens[2];
}


bool CFromTemplateCommand::execute(bool non_intercative, int flags)
{
    
    auto path_from =    config_path(this->cfg_name, CFG_GENERAL, CFG_TEMPLATE);
    auto path_to =      config_path(this->cfg_name, CFG_GENERAL, CFG_ON);

    if (this->action == "default")
    {
        if (fs::exists(path_to)) 
        {
            std::cout << "[C][fromtemplate default] " << " [" << this->cfg_name<<"]"
                    << " exists, skip altering"<<std::endl;
            return true;
        }

        std::cout <<"[C] [fromtemplate default] " 
        <<"copy "<<  path_from << " to "<<  path_to << std::endl;
        if (!(flags & F_DRYRUN)) fs::copy_file(path_from, path_to);
    }

    if (this->action == "ensure")
    {
        std::cout <<"[C] [fromtemplate ensure] " 
        <<"copy "<<  path_from << " to "<<  path_to << std::endl;
        if (!(flags & F_DRYRUN)) fs::copy_file(path_from, path_to, fs::copy_options::overwrite_existing);
    }
    
    //populate
    CellframeConfigurationFile cfg(path_to, flags);
    cfg.replace_placeholders(variable_storage);
    cfg.save();
    return true; 
}