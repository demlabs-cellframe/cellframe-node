#include "CellframeConfigFile.h"

#include <any>
#include <chrono>
#include <functional>
#include <iomanip>
#include <map>
#include <memory>
#include <regex>
#include <stdexcept>
#include <string>
#include <vector>

#include <cerrno>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <iostream>

namespace utils {

std::string escape(const std::string &str);

struct IPlaceholder {
    virtual std::string resolve(const std::vector<std::any> &args) const = 0;
    virtual const std::string &getPattern() const = 0;

    virtual ~IPlaceholder() = default;
};

class ArgCountError : public std::runtime_error {
public:
    explicit ArgCountError(const std::string &msg) : std::runtime_error(msg) {}
    ArgCountError() : std::runtime_error("Wrong number of arguments provided") {}
};

template <typename... Args>
class Placeholder : public IPlaceholder {
public:
    using FuncType = std::function<std::string(Args...)>;

    Placeholder(std::string p, FuncType r) : pattern_(std::move(p)), resolver_(std::move(r)) {}

    const std::string &getPattern() const override { return pattern_; }

    std::string resolve(const std::vector<std::any> &args) const override {
        if (args.size() != sizeof...(Args)) throw ArgCountError();
        return invoke(args, std::index_sequence_for<Args...>{});
    }

private:
    std::string pattern_;
    FuncType resolver_;

    template <size_t... I>
    std::string invoke(std::vector<std::any> const &args, std::index_sequence<I...>) const {
        return resolver_(std::any_cast<Args>(args[I])...);
    }
};

class SubstitutionError : public std::runtime_error {
public:
    explicit SubstitutionError(const std::string &msg): std::runtime_error(msg) {}
    SubstitutionError() : std::runtime_error("Error executing the replacing of the placeholder") {
    }
};

class PlaceholderManager {
public:
    typedef std::string(EscapingFnctTp)(const std::string &str);

    void addPlaceholder(const std::shared_ptr<IPlaceholder> &placeholder) {
        placeholders_[placeholder->getPattern()] = placeholder;
    }

    void setEscapingFnct(std::function<EscapingFnctTp> escapingFnct) {
        escapingFnct_ = escapingFnct;
    }

    std::string replacePlaceholders(
        std::string input, const std::map<std::string, std::vector<std::any>> &args = {}) {
        for (const auto &itPh : placeholders_)
        {
            replaceEachPh(input, args, itPh.second);
        }
        return input;
    }

private:
    std::map<std::string, std::shared_ptr<IPlaceholder>> placeholders_;

    void replaceEachPh(std::string &input,
                       const std::map<std::string, std::vector<std::any>> &args,
                       const std::shared_ptr<IPlaceholder> &ph) {
        static const std::vector<std::any> empty{};

        const std::string &phStr = ph->getPattern();
        std::regex regex(escapingFnct_(phStr));
        auto it = args.find(phStr);
        const std::vector<std::any> &vArgs = it != args.end() ? it->second : empty;
        std::string fmt;

        try {
            fmt = ph->resolve(vArgs);
            try {
                input = std::regex_replace(input, regex, fmt);
            } catch (...) {
                throw SubstitutionError();
            }
        } catch (const ArgCountError &) {
        }
    }

private:
    std::function<EscapingFnctTp> escapingFnct_{utils::escape};
};


inline std::string escape(const std::string &str) {
    std::regex exp("\\{");
    std::string res = std::regex_replace(str, exp, "\\{");
    exp = std::regex("\\}");
    res = std::regex_replace(res, exp, "\\}");
    return res;
}

}

fs::path get_config_path(EPathConfigType pathType)
{
    fs::path resultPath;
    switch (pathType)
    {
    case CFG_NODE:
        resultPath = fs::path{variable_storage["CONFIGS_PATH"]}/"share"/"configs";
        break;
    case CFG_NODE_TEMPLATE:
        resultPath = fs::path{variable_storage["CONFIGS_PATH"]}/"etc";
        break;
    case CFG_NETWORK:
        resultPath = fs::path{variable_storage["CONFIGS_PATH"]}/"etc"/"network/";
        break;
    case CFG_NETWORK_TEMPLATE:
        resultPath = fs::path{variable_storage["CONFIGS_PATH"]}/"share"/"configs"/"network/";
        break;                    
    default:
        break;
    }
    return resultPath;
}

fs::path config_path(const std::string &name, ENetworkConfigType type, ENetworkConfigState state) {
    if (name == "cellframe-node")
    {   if (state == CFG_TEMPLATE)
            return fs::path{variable_storage["CONFIGS_PATH"]}/"share"/"configs"/"cellframe-node.cfg";
        else
            return fs::path{variable_storage["CONFIGS_PATH"]}/"etc"/"cellframe-node.cfg";
    }
    switch (type)
    {
    case CFG_GENERAL:
        if (state == CFG_ON) return fs::path{variable_storage["CONFIGS_PATH"]}/"etc"/"network/"/(name + ".cfg");
        if (state == CFG_OFF) return fs::path{variable_storage["CONFIGS_PATH"]}/"etc"/"network/"/(name + ".cfg.dis");
        if (state == CFG_TEMPLATE) return fs::path{variable_storage["CONFIGS_PATH"]}/"share"/"configs"/"network/"/(name + ".cfg");
        break;
    case CFG_MAINCHAIN:
        return fs::path{variable_storage["CONFIGS_PATH"]}/"etc"/"network/"/name/"main.cfg";
    case CFG_ZEROCHAIN:
        return fs::path{variable_storage["CONFIGS_PATH"]}/"etc"/"network/"/name/"zerochain.cfg";

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

bool CellframeConfigurationFile::exists(const std::string & group, const std::string & param, std::string *value, int *line_no, bool *group_exists)
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
        
        if (is_grp_decl && group_found)
        {
            if (flags & F_VERBOSE)  std::cout << "[VC] No param in group [" << group_name<<"], group ends at  " << current_line-1 <<  std::endl;
            if (line_no) *line_no = current_line-1;
            if (group_exists) *group_exists = group_found;
            return false;
        }

        if (!group_found) continue;
        
        auto res = parse_param_value(line);    
        if (res.param == param)
        {
            if (flags & F_VERBOSE)  std::cout << "[VC] in group [" << group_name<<"] found "
                          << res.param
                          << ":" <<res.val
                          << " at line "
                          << current_line << std::endl;
            if (group_exists) *group_exists = group_found;
            if (value) *value = res.val;
            if (line_no) *line_no = current_line;
            return true;
        }
    }
    
    if (line_no) *line_no = current_line-1;

    if (group_exists)
        *group_exists = group_found;

    return false;
}


std::string CellframeConfigurationFile::set(const std::string & group, const std::string & param, const std::string &value)
{
    if (flags & F_VERBOSE)  std::cout << "[VC] set ["
                  << group << "] "<<param<<"="<<value << std::endl;

    int line_set_to;
    bool group_exists = false;
    bool param_exists = exists(group, param, nullptr, &line_set_to, &group_exists);
    if (param_exists) lines[line_set_to] = param+"="+value;
    else 
    {   
        if (!group_exists)
        {
            lines.emplace(lines.begin()+line_set_to, "["+group+"]");
            line_set_to += 1;
        }
        
        lines.emplace(lines.begin()+line_set_to, param+"="+value);
        lines.emplace(lines.begin()+line_set_to + 1, "\n");
    }
    return lines[line_set_to];
}


#include <string>

class exclusive_lock_file
{
public:
    // Throws if unable to acquire the lock
    exclusive_lock_file(const std::string& filename);

    virtual ~exclusive_lock_file();

private:
    exclusive_lock_file(const exclusive_lock_file&) = delete; // not construction-copyable
    exclusive_lock_file& operator=(const exclusive_lock_file&) = delete; // not assignment-copyable

    const std::string filename;
#ifdef _WIN32
    const void* lock;
#else
    int fd;
#endif
};

#include <stdexcept>

#ifdef _WIN32
#include <windows.h>
#else // _WIN32
#include <sys/file.h>
#include <unistd.h>
#endif // _WIN32

exclusive_lock_file::exclusive_lock_file(const std::string& filename)
    : filename(filename)
#ifdef _WIN32
    , lock(CreateFileA(filename.c_str(), GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, 0, NULL))
#endif
{
#ifdef _WIN32
    const bool success = (lock != INVALID_HANDLE_VALUE);
#else // _WIN32
    fd = open(filename.c_str(), O_RDWR | O_CREAT, 0666);
    if (fd < 0) {
        throw std::runtime_error("Cannot open file " + filename + ".");
    }
    const bool success = flock(fd, LOCK_EX | LOCK_NB) == 0;
    if (!success) {
        close(fd);
        fd = -1;
    }
#endif // _WIN32
    if (!success) {
        throw std::runtime_error("Cannot open file " + filename + " for exclusive access.");
    }
}

exclusive_lock_file::~exclusive_lock_file()
{
#ifdef _WIN32
    if (lock != INVALID_HANDLE_VALUE) {
        CloseHandle((HANDLE) lock);
        std::remove(filename.c_str());
    }
#else
    if (fd >= 0) {
        flock(fd, LOCK_UN);
        close(fd);
        std::remove(filename.c_str());
    }
#endif
}

bool CellframeConfigurationFile::save()
{
    if (flags & F_VERBOSE)  std::cout << "[VC] saving " << this->lines.size() << " lines to " << this->path << std::endl;
    if (flags & F_DRYRUN) {
        for (auto l : lines) std::cout << l << std::endl;
        return true;
    };
    exclusive_lock_file lock("write.lock"); //RAII, will unlock at exit
    std::ofstream file(path);

    if (file) {
        for (auto l : lines) file << l << std::endl;
        file.close();
        return true;
    } else {
        std::cout << "Error: " << std::strerror(errno) << '\n';
        return false;
    }
}


void CellframeConfigurationFile::replace_placeholders(std::map<std::string, std::string> data)
{
    if (flags & F_VERBOSE)  std::cout << "[VC] replacing placeholders in" << this->path<< std::endl;
    
    int current_line = -1;
    
    for( auto line : lines)
    {
        current_line ++;
        trim(line);
        line = line.substr(0, line.find("#")); //skip comments 
        if(line.empty()) continue; //skip empties  
        auto nline = substitute_variables(line);
        lines[current_line] = nline;
    }
}

std::string substitute_variables(const std::string &string)
{
    utils::PlaceholderManager pman;
    for (auto var: variable_storage){
        pman.addPlaceholder(std::make_shared<utils::Placeholder<>>(
            std::string("\\${"+var.first+"}"), [=] { return var.second; }));
    }
    return pman.replacePlaceholders(string);
}
