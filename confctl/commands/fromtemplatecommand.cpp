#include "fromtemplatecommand.h"
#include <stdexcept>
#include <filesystem>
#include <format>
#include "../build_config.h"
#include "../config/cellframeconfigfile.h"

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
        throw std::invalid_argument(string_format("config_cmd: config for [%s] not exitst", 
                                                    this->cfg_name.c_str()));

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
            std::cout << "[E][fromtemplate default] " << " [" << this->cfg_name<<"]"
                    << " exists, skip altering"<<std::endl;
            return true;
        }

        std::cout <<"[E] [fromtemplate default] " 
        <<"copy "<<  path_from << " to "<<  path_to;
        if (!(flags & F_DRYRUN)) fs::copy(path_from, path_to);
    }

    if (this->action == "ensure")
    {
        std::cout <<"[E] [fromtemplate default] " 
        <<"copy "<<  path_from << " to "<<  path_to;
        if (!(flags & F_DRYRUN)) fs::copy(path_from, path_to);
    }
    
    //populate
    return true; 
}