/*
Cellframe-Node Configuration controll tool.
2024 dmitry.puzrkov@demlabs.net

confctl tool uses .setup files with basic command and scripting capabilities to 
initial setup of cellframe-node as intended by developers. 

It will not alter any user settings if they exists. 

//  cellframe-node-config --init /path/to/cellframe-node.setup [-v | --verbose]

// .setup file syntax:
command param1 param2 param3 ....


*/


#include <algorithm>
#include <map>
#include <string>
#include <iostream>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <vector>
#include "commands/AbstractCommand.h"
#include <stdexcept>


#ifdef __linux__
#include <unistd.h>       //Linux
#endif

#ifdef __APPLE__
#include <unistd.h>       //Apple
#endif


#ifdef _WIN32
#include <winsock.h>      //Windows
#include <windows.h>
#endif 

std::string getHostName(void)
{
    std::string res = "unknown";
    char tmp[0x100];
    if( gethostname(tmp, sizeof(tmp)) == 0 )
    {
        res = tmp;
    }
    return res;
}

#ifdef WIN32

LONG GetDWORDRegKey(HKEY hKey, const std::wstring &strValueName, DWORD &nValue, DWORD nDefaultValue)
{
    nValue = nDefaultValue;
    DWORD dwBufferSize(sizeof(DWORD));
    DWORD nResult(0);
    LONG nError = ::RegQueryValueExW(hKey,
        strValueName.c_str(),
        0,
        NULL,
        reinterpret_cast<LPBYTE>(&nResult),
        &dwBufferSize);
    if (ERROR_SUCCESS == nError)
    {
        nValue = nResult;
    }
    return nError;
}


LONG GetBoolRegKey(HKEY hKey, const std::wstring &strValueName, bool &bValue, bool bDefaultValue)
{
    DWORD nDefValue((bDefaultValue) ? 1 : 0);
    DWORD nResult(nDefValue);
    LONG nError = GetDWORDRegKey(hKey, strValueName.c_str(), nResult, nDefValue);
    if (ERROR_SUCCESS == nError)
    {
        bValue = (nResult != 0) ? true : false;
    }
    return nError;
}


LONG GetStringRegKey(HKEY hKey, const std::wstring &strValueName, std::wstring &strValue, const std::wstring &strDefaultValue)
{
    strValue = strDefaultValue;
    WCHAR szBuffer[512];
    DWORD dwBufferSize = sizeof(szBuffer);
    ULONG nError;
    nError = RegQueryValueExW(hKey, strValueName.c_str(), 0, NULL, (LPBYTE)szBuffer, &dwBufferSize);
    if (ERROR_SUCCESS == nError)
    {
        strValue = szBuffer;
    }
    return nError;
}

#endif

namespace fs = std::filesystem;

std::string getNodeConfigPath(){
    #ifdef __linux__ 
        return "/opt/cellframe-node/";
    #endif
    
    #ifdef __APPLE__ 
        return  "/Applications/CellframeNode.app/Contents/Resources/";
    #endif

    #ifdef WIN32 
        HKEY hKey;
        LONG lRes = RegOpenKeyExW(HKEY_LOCAL_MACHINE, L"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders", 0, KEY_READ, &hKey);
        bool bExistsAndSuccess (lRes == ERROR_SUCCESS);
        bool bDoesNotExistsSpecifically (lRes == ERROR_FILE_NOT_FOUND);
        std::wstring path;
        GetStringRegKey(hKey, L"Common Documents", path, L"");
        std::string stdpath(path.begin(),path.end());
        return (std::filesystem::path{stdpath}/"cellframe-node/").string();
    #endif
}

std::string getNodeBinaryPath(){
    #ifdef __linux__ 
        return "/opt/cellframe-node/bin/";
    #endif
    
    #ifdef __APPLE__ 
        return  "/Applications/CellframeNode.app/Contents/MacOS/";
    #endif

    #ifdef WIN32 
        //HKLM "Software\${APP_NAME}" "Path"
        HKEY hKey;
        LONG lRes = RegOpenKeyExW(HKEY_LOCAL_MACHINE, L"SOFTWARE\\cellframe-node\\", 0, KEY_READ, &hKey);
        bool bExistsAndSuccess (lRes == ERROR_SUCCESS);
        bool bDoesNotExistsSpecifically (lRes == ERROR_FILE_NOT_FOUND);
        std::wstring path;
        GetStringRegKey(hKey, L"Path", path, L"");
        std::string stdpath(path.begin(),path.end());
        return (std::filesystem::path{stdpath}).string();
    #endif
}

bool cmdOptionExists(char** begin, char** end, const std::string& option)
{
    return std::find(begin, end, option) != end;
}

std::string getCmdOption(char ** begin, char ** end, const std::string & option_long, const std::string & option_short )
{
    std::string option = option_long;
    if (!cmdOptionExists(begin, end, option))
        option = option_short;

    char ** itr = std::find(begin, end, option);
    if (itr != end && ++itr != end)
    {
        return std::string(*itr);
    }
    return std::string();
}

void print_help()
{
    std::cout << "cellframe-node-config -h | --help" << std::endl;
    std::cout << "\t prints this help message" << std::endl;
    std::cout << "cellframe-node-config -s | --vars" << std::endl;
    std::cout << "\t prints installation config variables." << std::endl;
    std::cout << "cellframe-node-config -v | --verbose" << std::endl;
    std::cout << "\t enable verbose output" << std::endl;
    std::cout << "cellframe-node-config -d | --dry-run" << std::endl;
    std::cout << "\t do not actual do a file-system commands" << std::endl;
    std::cout << "cellframe-node-config -i | --init /path/to/cellframe-node.setup" << std::endl;
    std::cout << "\t do initial configuration based on provided setup script" << std::endl;
    std::cout << "cellframe-node-config -e | --exec <command> [and <command> [and <command>]...]" << std::endl;
    std::cout << "\t execute provided commands. "  << std::endl<< std::endl;
    std::cout << "Allowed commands:"  << std::endl;
    std::cout << "\tnetwork <netname> ensure on|off"  << std::endl;
    std::cout << "\t\t enable | disable <netname> network"  << std::endl;
    std::cout << "\tnet_list all|on|off"  << std::endl;
    std::cout << "\t\t on - active networks. off - not active networks. all or nothing - all network"  << std::endl;
    std::cout << "\tconfig  <configname>  <section>  <param> ensure  <value>"  << std::endl;
    std::cout << "\t\t set a parameter <param> in section <section> in config <configname> to <value>"  << std::endl;
    std::cout << "\t\t Possible configs: \"cellframe-node\",  \"<netname>\""  << std::endl;
    std::cout << "\tservice  enable"  << std::endl;
    std::cout << "\t\t set cellframe-node to autostart on boot"  << std::endl;
    std::cout << "\tservice  disable"  << std::endl;
    std::cout << "\t\t remove cellframe-node from autostart on boot"  << std::endl;
    std::cout << "\tservice  start"  << std::endl;
    std::cout << "\t\t start cellframe-node (if registred as service!)"  << std::endl;
    std::cout << "\tservice  stop"  << std::endl;
    std::cout << "\t\t stop cellframe-node (if registred as service!)"  << std::endl;
    std::cout << "\tservice  status"  << std::endl;
    std::cout << "\t\t get service & process statuses"  << std::endl;
}

std::unique_ptr<CAbstractScriptCommand> parse_line_to_cmd(std::string line, int line_no, int flags) {
        auto cmd  = CAbstractScriptCommand::build(line);
        
        if (!cmd)
            throw std::invalid_argument("setup file line " + std::to_string(line_no) + " << {" +line +"} >> error: unknown command");            
        
        if (flags & F_VERBOSE)  std::cout << "[V] Command: " << cmd->represent() <<std::endl;
        return cmd;
}

std::vector <std::unique_ptr<CAbstractScriptCommand> > parse_setup_file(const  std::string &init_file_name, int flags)
{
    std::ifstream infile(init_file_name);
    std::vector <std::unique_ptr<CAbstractScriptCommand> > res; 
    size_t line_num = 0;

    if (flags & F_VERBOSE)  std::cout << "[V] Parsing "<<init_file_name << " as setup-script" << std::endl;
        
    for( std::string line; std::getline( infile, line ); line_num++)
    {
        trim(line);
        line = line.substr(0, line.find("#")); //skip comments 
        if(line.empty()) continue; //skip empties  
        res.push_back(std::move(parse_line_to_cmd(line, line_num, flags)));
    }
        
    return res;
}

void print_cond_stack(std::vector < std::unique_ptr<CAbstractScriptCommand>> &condition_stack)
{
 std::cout << "[VE] Condition stack: [";
                for (auto &a : condition_stack)
                    std::cout << "{" << a->represent() << "} ";
                
                std::cout << "] "<<std::endl;
}

bool run_commands(std::vector <std::unique_ptr<CAbstractScriptCommand>> &commands, int interactive, int flags)
{
    //dry_run for conditions check
    std::vector<std::unique_ptr <CAbstractScriptCommand>> condition_stack;
    for (auto &cmd : commands)
    {   
        if (cmd->is_condition_open() || cmd->is_condition_close()) {
            
            if (cmd->is_condition_open()) condition_stack.push_back(std::move(cmd));  
            else if (cmd->is_condition_close()) condition_stack.pop_back();
            if (flags & F_VERBOSE) print_cond_stack(condition_stack);
            continue;
        }
        
        if (condition_stack.size() > 0)
        {   
            //execute only of condition passed
            if (condition_stack.back()->execute(!interactive, flags)) cmd->execute(!interactive, flags);
        } else
        {
            //no condition in stack, exec command
            cmd->execute(!interactive, flags);
        }
    }
    return true;
}


void populate_variables()
{
    variable_storage["HOST_OS"] = HOST_OS;
    variable_storage["HOSTNAME"] = getHostName();
    variable_storage["CONFIGS_PATH"] = getNodeConfigPath();
    variable_storage["NODE_BINARY_PATH"] = getNodeBinaryPath();
}

int init_configs(int argc, char *argv[], int flags)
{   
    //--init already exists, give me filename
    std::string init_file_name = getCmdOption(argv, argv+argc, "--init", "-i");

    std::string node_intall_path = getCmdOption(argv, argv+argc, "--path", "-p");
    
    if (!node_intall_path.empty())
    {
        variable_storage["CONFIGS_PATH"] = node_intall_path;
    }

    bool non_interactive = cmdOptionExists(argv, argv+argc, "--non-interactive") || cmdOptionExists(argv, argv+argc, "-n");

    if (init_file_name.empty())
    {
        std::cout << "No setup file provided for init procedure, see --help" << std::endl;
        return -1;
    }

    if (!fs::exists(fs::path{init_file_name}))
    {
        std::cout << "Setup file "  << init_file_name << " not found" << std::endl;
        return -1;
    }
    
    std::cout << "Cellframe-node configs install path: " << variable_storage["CONFIGS_PATH"] << std::endl;
    
    auto commands = parse_setup_file(init_file_name, flags);
    
    run_commands(commands, !non_interactive, flags);

    return 0;

}       

int main(int argc, char * argv[])
{
    populate_variables();

    if(cmdOptionExists(argv, argv+argc, "-h") || cmdOptionExists(argv, argv+argc, "--help"))
    {
        print_help();
        return 0;
    }

    int flags = 0;  
    if (cmdOptionExists(argv, argv+argc, "--verbose") || cmdOptionExists(argv, argv+argc, "-v")) flags = flags | F_VERBOSE;
    
    if (cmdOptionExists(argv, argv+argc, "--vars") || cmdOptionExists(argv, argv+argc, "-s")) {
        for (auto v: variable_storage)
        {
            std::cout << v.first << "="<<v.second<<std::endl;
        }   
        return 0; 
    }

    if (cmdOptionExists(argv, argv+argc, "--dryrun") || cmdOptionExists(argv, argv+argc, "-d")) flags = flags | F_DRYRUN;


    if(cmdOptionExists(argv, argv+argc, "-i") || cmdOptionExists(argv, argv+argc, "--init"))
    {
        return init_configs(argc, argv, flags);
    }



    if(cmdOptionExists(argv, argv+argc, "-e") || cmdOptionExists(argv, argv+argc, "--exec"))
    {
        std::string option = "-e";
        if (cmdOptionExists(argv, argv+argc, "--exec")) option = "--exec";


        auto pos = std::find(argv, argv+argc, option);
        std::vector <std::string> commands_lines; 
        std::string curr_cmd; 
        while (pos != argv+argc-1)
        {
            pos++;

            if (std::string(*pos) == "and")  { commands_lines.push_back(curr_cmd); curr_cmd = "";  continue; }
            curr_cmd += *pos;
            curr_cmd += " ";
        }
        commands_lines.push_back(curr_cmd);
        std::vector <std::unique_ptr<CAbstractScriptCommand> > script_cmds; 
        for (int i =0; i< commands_lines.size(); i++) {
            script_cmds.push_back(parse_line_to_cmd(commands_lines[i], i, flags));
        }

        run_commands(script_cmds, false, flags);
        return 0;
    }

    
    print_help();
    return 0;
}

