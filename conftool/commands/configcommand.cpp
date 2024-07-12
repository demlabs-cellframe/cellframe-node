#include "configcommand.h"
#include "../config/cellframeconfigfile.h"

CAbstractScriptCommand::Registrar<CConfigCommand> cfg_registrar("config");

/*
config  cellframe-node  general         auto_online         default     true
config  cellframe-node  general         debug_mode          default     false
config  cellframe-node  server          enabled             default     false
config  cellframe-node  server          listen_address      default     127.0.0.1
config  cellframe-node  server          listen_port_tcp     default     8079
config  cellframe-node  notify_server   listen_address      default     127.0.0.1
config  cellframe-node  notify_server   listen_port         default     8080

if MacOS == $HOST_OS
    config cellframe-node  global_db       driver          ensure     $DB_DRIVER
endif

config  Backbone     general     node-role   default     full
config  KelVPN       general     node-role   default     full
config  raiden       general     node-role   default     full
config  riemann      general     node-role   default     full
config  mileena      general     node-role   default     full
config  subzero      general     node-role   default     full
 */

std::vector<std::string> allowed_actions{"default", "ensure", "get"};

CConfigCommand::CConfigCommand(std::vector <std::string> cmd_tokens):CAbstractScriptCommand(cmd_tokens)
{   
    //zero token is always a command (config)
    
    if (cmd_tokens.size() <= 4)
        throw std::invalid_argument("config command invalid numbers of arguments");
    
    this->cfg_name = cmd_tokens[1];

    //check if config name accetable
    //net should exist
    fs::path net_cfg_template_path = config_path(this->cfg_name, CFG_GENERAL, CFG_TEMPLATE);
    if (this->cfg_name != "cellframe-node" && !fs::exists(net_cfg_template_path))
        throw std::invalid_argument(string_format("config_cmd: config for [%s] not exitst", 
                                                    this->cfg_name.c_str()));

    this->group = cmd_tokens[2];
    this->param = cmd_tokens[3];
    this->action = cmd_tokens[4];

    if (allowed_actions.end() == std::find(allowed_actions.begin(), allowed_actions.end(), this->action))
    {
        throw std::invalid_argument(string_format("config_cmd: allowed actions are get|ensure|default, not %s", 
                                                    this->action.c_str()));
    }

    if (cmd_tokens.size() > 5)
        this->value = cmd_tokens[5];
}

bool is_placeholder(const std::string &val)
{
    if (val.empty()) return true;
    return val[0]=='$' && val[val.size()-1]=='}';
}

bool CConfigCommand::execute(bool non_intercative, int flags)
{   
    //can't do this in ctr, cause storage-cmds can be not executed yet.  
    this->value = substitute_variables(this->value);
    
    auto cfg_on_path = config_path(this->cfg_name, CFG_GENERAL, CFG_ON );
    auto cfg_off_path = config_path(this->cfg_name, CFG_GENERAL, CFG_OFF );
    
    fs::path cfg_path = cfg_on_path;
    
    if (this->cfg_name != "cellframe-node")
    {
        if (fs::exists(cfg_off_path))
            cfg_path = cfg_off_path;
            
        if (fs::exists(cfg_on_path))
            cfg_path = cfg_on_path;
            
        if (fs::exists(cfg_on_path) && fs::exists(cfg_off_path))
        {
            std::cout << "[C][config] " << "cfg " << this->cfg_name 
                        << " is in both on&off states, use enabled cfg for modifications" << std::endl;
        }
    }

    std::map <std::string, std::function<bool ()>> actions;
    CellframeConfigurationFile cfg(cfg_path, flags);

    //check for default net state
    //default means 
    //set if - no parameter defined
    //set if value is placeholder ({CFG})
    //if exists - skip

    actions["default"] = [*this, &cfg]() {
        std::string cfg_val;
        bool param_exists = cfg.exists(this->group, this->param, &cfg_val);
        if (param_exists && !is_placeholder(cfg_val)){
            //skip
            std::cout << "[C][config default] " << "[" << this->cfg_name<<"] "
                            << "[" << this->group<<"] " 
                            << this->param << "==" <<cfg_val
                            << ", skip altering"<<std::endl;
            return false;
        }

        std::cout << "[C][config default] " << "[" << this->cfg_name<<"]"
                            << " [" << this->group<<"] set " 
                            << this->param << "=" <<this->value
                            << std::endl;

        cfg.set(this->group, this->param, this->value);
        return true;
    };

    //force net state
    actions["ensure"] = [*this, &cfg]() {
        std::cout << "[C][config ensure] " << "[" << this->cfg_name<<"] "
                            << "[" << this->group<<"] set " 
                            << this->param << "=" <<this->value
                            << std::endl;

        cfg.set(this->group, this->param, this->value);
        return true;
    };

    actions["get"] = [*this, &cfg]() {
        std::string cfg_val;
        bool param_exists = cfg.exists(this->group, this->param, &cfg_val);
        std::cout << this->cfg_name << ": ["<<this->group<<"] " << this->param+"="+cfg_val<<std::endl;
        return true;
    };
    
    //actions return true if config was altered and need to be saved
    bool res =  actions[this->action]();
    if (res) cfg.save();
    return res;
}
