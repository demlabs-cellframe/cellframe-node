/*
 * Authors:
 * Dmitriy A. Gearasimov <kahovski@gmail.com>
 * DeM Labs Inc.   https://demlabs.net
 * DeM Labs Open source community https://github.com/demlabsinc
 * Copyright  (c) 2017-2019
 * All rights reserved.

 This file is part of DAP (Deus Applications Prototypes) the open source project

 DAP (Deus Applicaions Prototypes) is free software: you can redistribute it and/or modify
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

#pragma once

#ifndef whitespace
#define whitespace(c) (((c) == ' ') || ((c) == '\t'))
#endif

/*
 *  Initialize readline (and terminal if not already).
 */
int rl_initialize(void);

/**
 *  Strip whitespace from the start and end of STRING.  Return a pointer into STRING.
 */
char * rl_stripwhite(char *string);

/**
 *  Read a line of input.  Prompt with PROMPT.  An empty PROMPT means none.
 *  A return value of NULL means that EOF was encountered.
 */
char *rl_readline(const char *prompt);

/**
 *  Place STRING at the end of the history list.
 */
void add_history(const char *string);

int parse_shell_options(char **argv, int arg_start, int arg_end);

