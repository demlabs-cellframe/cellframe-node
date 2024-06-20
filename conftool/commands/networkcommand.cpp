#include "networkcommand.h"
#include <stdexcept>
#include <filesystem>

#include "../build_config.h"
#include "../config/cellframeconfigfile.h"

namespace fs = std::filesystem;

CAbstractScriptCommand::Registrar<CNetworkCommand> registrar("network");

/*
Network Command syntax:

network {netname}   default      on 
network {netname}   default      off
network {netname}   ensure       off
network {netname}   ensure       on
*/

std::vector<std::string> allowed_states{"on", "off"};


CNetworkCommand::CNetworkCommand(std::vector <std::string> cmd_tokens): CAbstractScriptCommand(cmd_tokens)
{   
    //zero token is always a command (network)
    
    if (cmd_tokens.size() <= 2)
        throw std::invalid_argument("network command has no command arguments");
    
    this->net_name = cmd_tokens[1];
    
    //check such net is available: lookup for config files in share dir
    fs::path net_cfg_template_path = config_path(this->net_name, CFG_GENERAL, CFG_TEMPLATE);
    if (!fs::exists(net_cfg_template_path))
        throw std::invalid_argument("network_cmd: template not found in share config path");
    
    
    std::map <std::string, std::function<void ()>> actions;
    actions["default"] = [this, &cmd_tokens](){
        if (cmd_tokens.size() < 4 || allowed_states.end() == std::find(allowed_states.begin(), allowed_states.end(), cmd_tokens[3]))
            throw std::invalid_argument("network_cmd: [default] require 'on or off' state for net");
            
        this->default_val = cmd_tokens[3];
            
    };

    actions["ensure"] = [this, &cmd_tokens](){
        
        if (cmd_tokens.size() < 4 || allowed_states.end() == std::find(allowed_states.begin(), allowed_states.end(), cmd_tokens[3]))
            throw std::invalid_argument("network_cmd: [ensure] require 'on or off' state for net" );
        this->default_val = cmd_tokens[3];
    };
    
    this->action = cmd_tokens[2];
    if (actions.find(this->action) == actions.end())
        throw std::invalid_argument("network_cmd: unknown action for network_cmd");
    
    actions[this->action]();
}


bool CNetworkCommand::execute(bool non_intercative, int flags)
{   
    std::map <std::string, std::function<bool ()>> actions;
    
    //check for default net state
    actions["default"] = [&]() {
        //validity of default_value ensured by constructor 

        fs::path check_exist_path;
        fs::path template_copy_dest;
        fs::path template_path = config_path(this->net_name, CFG_GENERAL, CFG_TEMPLATE);

        if (fs::exists(config_path(this->net_name, CFG_GENERAL, CFG_OFF)) && 
            fs::exists(config_path(this->net_name, CFG_GENERAL, CFG_ON)) )
        {
            std::cout << "[C][network default] you have both enabled and disabled files for network [" << this->net_name << "], skip this step"<<std::endl;
            return false; 
        }

        //default requested net on
        if (this->default_val == "on")
        {   
            check_exist_path = config_path(this->net_name, CFG_GENERAL, CFG_OFF);
            template_copy_dest = config_path(this->net_name, CFG_GENERAL, CFG_ON);
        } else if (this->default_val == "off")
        {
            check_exist_path = config_path(this->net_name, CFG_GENERAL, CFG_ON);
            template_copy_dest = config_path(this->net_name, CFG_GENERAL, CFG_OFF);
        } else { std::cout << "wtf" << std::endl; return false; }

        //skip default if net already exists in any state
        if (fs::exists(template_copy_dest)) {
            std::cout << "[C][network default " << this->default_val<<"] Network [" << this->net_name << "] already "<< this->default_val << ", skip this step" <<std::endl;
            return true;
        }        
            
        if (fs::exists(check_exist_path)) 
        {
            if (flags & F_VERBOSE) std::cout << "[VE][network default] File " << check_exist_path << " exists, but default state requested [" << this->default_val << "]";
            std::cout << "Skip altering state for newtwork [" << this->net_name<<"] due to it was user-configured";
            return false;
        }

        // default on: net exists, not on, and not disabled -> copy network config as enabled 
        std::cout << "[C][network default] Set-up net [" << this->net_name << "] as ["<< (this->default_val == "on" ? "ENABLED" : "DISABLED")
                    << "] from template " << template_path <<  std::endl;
        
        if (flags & F_VERBOSE) std::cout << "[VE][network default] copy file from " << template_path << " to " << template_copy_dest << std::endl;
    
        if (!(flags & F_DRYRUN)) fs::copy(template_path, template_copy_dest);
    
        return true;
    
    };

    //force net state
    actions["ensure"] = [&]() {
        
        //check for disabled
        bool net_enabled = fs::exists(config_path(this->net_name, CFG_GENERAL, CFG_ON));

        if (this->default_val == "on" && net_enabled)
        {
            std::cout << "[C][network ensure on]: Network [" << this->net_name << "] already enabled"<<std::endl;
            return false;
        }
    
        if (this->default_val == "off" && !net_enabled && fs::exists(config_path(this->net_name, CFG_GENERAL, CFG_OFF)))
        {
            std::cout << "[C][network ensure off]: Network [" << this->net_name << "] already disabled"<<std::endl;
            return false;
        }
        
        ENetworkConfigState requested_state, oposite_state;
        if (this->default_val == "on") {
            requested_state = CFG_ON;
            oposite_state = CFG_OFF;
        }
        if (this->default_val == "off")
        {
            requested_state = CFG_OFF;
            oposite_state = CFG_ON;        
        }

        //move from oposite if exists
        if (fs::exists(config_path(this->net_name, CFG_GENERAL, oposite_state))){
            
            std::cout << "[C][network ensure " << this->default_val << "] move file from " 
                                            << config_path(this->net_name, CFG_GENERAL, oposite_state)
                                            << " to " << config_path(this->net_name, CFG_GENERAL, requested_state)
                                            << std::endl;
            if (!(flags & F_DRYRUN)) fs::rename(config_path(this->net_name, CFG_GENERAL, oposite_state), 
                                                config_path(this->net_name, CFG_GENERAL, requested_state));
        } else { //copy from template if oposite side of config not exits

            std::cout << "[C][network ensure "<<this->default_val << "] copy file from " 
                                            << config_path(this->net_name, CFG_GENERAL, CFG_TEMPLATE)
                                            << " to " << config_path(this->net_name, CFG_GENERAL, requested_state)
                                            << std::endl;
            if (!(flags & F_DRYRUN)) fs::copy(config_path(this->net_name, CFG_GENERAL, CFG_TEMPLATE), 
                                                config_path(this->net_name, CFG_GENERAL, requested_state));
        }
        return true;
    };
    
    
    return actions[this->action]();
}
