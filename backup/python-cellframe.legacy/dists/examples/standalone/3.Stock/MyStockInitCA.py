#!/usr/bin/python3
from CellFrame.libCellFrame import *
from string import Template
import os
import sys

tmp_dir = os.getcwd() + "/tmp"
var_dir = os.getcwd() + "/var"
app_name = "MyStock"
init_json_string = Template("""{
    "modules": ["Core","Crypto"],
    "Core": {
        "config_dir": "${tmp_dir}",
        "log_level": "L_DEBUG",
        "application_name": "${app_name}"
    }
}
""")

tpl_vars={
    "var_dir":var_dir,
    "tmp_dir":tmp_dir,
    "app_name":app_name
}

print("begin")
init( init_json_string.substitute(tpl_vars) )
counter=0

for arg in sys.argv:
    counter+=1
    print("  arg"+str(counter)+"="+arg)
print("end")
