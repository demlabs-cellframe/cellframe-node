/*
 * Authors:
 * Dmitriy A. Gearasimov <kahovski@gmail.com>
 * DeM Labs Inc.   https://demlabs.net
 * DeM Labs Open source community https://github.com/demlabsinc
 * Copyright  (c) 2017-2019
 * All rights reserved.

 This file is part of DAP (Distributed Applications Platform) the open source project

    DAP (Distributed Applications Platform) is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    DAP is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with any DAP based project.  If not, see <http://www.gnu.org/licenses/>.
*/
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <getopt.h>
#include <string.h>

#include "dap_common.h"
#include "dap_config.h"
#include "dap_cert.h"
#include "dap_cert_file.h"
#include "dap_chain_wallet.h"
#include "dap_file_utils.h"
#include "json.h"



int main(int argc, const char **argv)
{
  dap_set_appname("cellframe-node");

    // get relative path to config
    int l_rel_path = 0;
    if (argv[1] && argv[2] && !dap_strcmp("-B" , argv[1])) {
        g_sys_dir_path = (char*)argv[2];
        l_rel_path = 1;
    }

    if (!g_sys_dir_path) {
    #ifdef DAP_OS_WINDOWS
        g_sys_dir_path = dap_strdup_printf("%s/%s", regGetUsrPath(), dap_get_appname());
    #elif DAP_OS_MAC
        g_sys_dir_path = dap_strdup_printf("/Applications/CellframeNode.app/Contents/Resources");
    #elif DAP_OS_UNIX
        g_sys_dir_path = dap_strdup_printf("/opt/%s", dap_get_appname());
    #endif
    }





  dap_config_close(g_config);
  return -1;
}