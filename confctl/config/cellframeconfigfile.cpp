#include "cellframeconfigfile.h"

fs::path config_path(const std::string &name, ENetworkConfigType type, ENetworkConfigState state) {
    if (name == "cellframe-node")
    {   if (state == CFG_TEMPLATE)
            return fs::path{CELLFRAME_NODE_INSTALL_PATH}/"share"/"configs"/"cellframe-node.cfg";
        else
            return fs::path{CELLFRAME_NODE_INSTALL_PATH}/"etc"/"cellframe-node.cfg";
    }
    switch (type)
    { 
        case CFG_GENERAL:
            if (state == CFG_ON) return fs::path{CELLFRAME_NODE_INSTALL_PATH}/"etc"/"network/"/(name + ".cfg");        
            if (state == CFG_OFF) return fs::path{CELLFRAME_NODE_INSTALL_PATH}/"etc"/"network/"/(name + ".cfg.dis");
            if (state == CFG_TEMPLATE) return fs::path{CELLFRAME_NODE_INSTALL_PATH}/"share"/"configs"/"network/"/(name + ".cfg");
            break;
        case CFG_MAINCHAIN:
            return fs::path{CELLFRAME_NODE_INSTALL_PATH}/"etc"/"network/"/name/"main.cfg";        
        case CFG_ZEROCHAIN:
            return fs::path{CELLFRAME_NODE_INSTALL_PATH}/"etc"/"network/"/name/"zerochain.cfg";

    }
    throw std::invalid_argument("cfg for such params cant be detectd");
}

CellframeConfigurationFile::CellframeConfigurationFile(fs::path filepath, int flags):flags(flags) {
    
    if (!fs::exists(filepath))
        throw std::invalid_argument(string_format("Config path [%s] not exitsts", filepath.c_str()));

    std::ifstream infile(filepath);
    
    size_t line_num = 0;
    for( std::string line; std::getline( infile, line ); line_num++)
    {
        this->lines.push_back(line);
    }

    if (flags & F_VERBOSE)  std::cout << "[VC] Loaded "<<line_num<<" lines form " << filepath << std::endl;
    this->path  = filepath;
}

bool is_group_decl(const std::string line, std::string *gname)
{
    std::string trimmed_line = line; 

    auto tokens = tokenize(trimmed_line, std::regex("="));

    if (tokens.size()>1) return false;

    if (tokens[0][0]!='[') return false;
    
    std::string group_name = tokens[0].substr(tokens[0].find('[')+1, tokens[0].find(']')-1);
    trim(group_name);
    if (group_name.empty()) return false;
    
    if (gname) *gname = group_name;
    return true;
}
struct cfg_pair {
    std::string param;
    std::string val;
};

cfg_pair parse_param_value(const std::string line)
{
    std::string trimmed_line = line; 
    if (line.find("=") == line.npos) throw std::invalid_argument("config line expected to be key=value");

    auto tokens = tokenize(trimmed_line, std::regex("="));

    trim(tokens[0]);
    if (tokens.size() < 2)
        tokens.push_back("");
        
    return {tokens[0], tokens[1]};
}

bool CellframeConfigurationFile::exists(const std::string & group, const std::string & param, std::string *value, int *line_no)
{
    if (flags & F_VERBOSE)  std::cout << "[VC] Check for existanse [" << group<<"] "<<param << " in "<<this->path <<std::endl;
    
    bool group_found = false;
    int current_line = -1;
    std::string group_name;
    for( auto line : lines)
    {
        current_line ++;

        trim(line);
        line = line.substr(0, line.find("#")); //skip comments 
        if(line.empty()) continue; //skip empties  
    

        bool is_grp_decl = is_group_decl(line, &group_name);
        if (is_grp_decl && !group_found)
        {
            if (flags & F_VERBOSE)  std::cout << "[VC] Found group [" << group_name<<"] " << std::endl;
            if (group_name == group) group_found = true;
            continue;
        }
        
        if (!group_found) continue;
        
        if (is_grp_decl && group_found)
        {
            if (line_no) *line_no = current_line-1;
            return false;
        }


        auto res = parse_param_value(line);    
        if (res.param == param)
        {
            if (flags & F_VERBOSE)  std::cout << "[VC] in group [" << group_name<<"] found "
                                                << res.param 
                                                << ":" <<res.val 
                                                << " at line " 
                                                << current_line << std::endl;
            if (value) *value = res.val;
            if (line_no) *line_no = current_line;
            return true;
        }
    }
        
    return false;
}


std::string CellframeConfigurationFile::set(const std::string & group, const std::string & param, const std::string &value)
{
    if (flags & F_VERBOSE)  std::cout << "[VC] set [" 
                            << group << "] "<<param<<"="<<value << std::endl;

    int line_set_to;
    bool param_exists = exists(group, param, nullptr, &line_set_to);
    if (param_exists) lines[line_set_to] = param+"="+value;
    else lines.emplace(lines.begin()+line_set_to, param+"="+value);
    return lines[line_set_to];
}

bool CellframeConfigurationFile::save()
{
    if (flags & F_VERBOSE)  std::cout << "[VC] saving " << this->lines.size() << " lines to " << this->path << std::endl;
    if (flags & F_DRYRUN) {
        for (auto l : lines) std::cout << l << std::endl;
        return true;
    };

    std::ofstream file(path);
    for (auto l : lines) file << l << std::endl;
    file.close();
    return true;
}
