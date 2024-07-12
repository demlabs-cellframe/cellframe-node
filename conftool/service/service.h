#include <algorithm>
#include <map>
#include <string>
#include <iostream>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <vector>
#include <stdexcept>

enum EServiceStatus{
    ENABLED,
    DISABLED,
};

enum EServiceType{
    NODE,
    DIAG,
};

struct CServiceControl
{
    CServiceControl(EServiceType sevice){this->service = service;}
    bool enable();
    bool disable();
    EServiceStatus serviceStatus();
    bool start();
    bool stop();
    bool restart();    

    private:
        EServiceType service;
};